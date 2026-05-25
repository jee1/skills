import importlib.util
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "validate_tdd", Path(__file__).with_name("validate-tdd.py")
)
assert _SPEC and _SPEC.loader
v = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(v)


FRONTMATTER = """---
title: "TDD: test"
feature: test
mode: brownfield
prd_source: "x"
generated_at: 2026-05-25
validation_passed: false
review_rounds: 0
---

# Test — Technical Design Document
"""

MINIMAL_NARRATIVE_BODY = """
## 1. 서문

### 목차

1. [서문](#1-서문)
2. [배경과 문제](#2-배경과-문제)

### 이 문서 읽는 법

| 독자 | 먼저 볼 곳 | 목표 |
|------|-----------|------|
| PM | Ch.1 opening → Ch.5 diagram | ~3분 |
| Dev | Ch.4 → Ch.6 tables | ~5분 |
| Audit | Ch.4 결정 요약 → Appendix A | ~3분 |

This document describes the order cancel feature for PM, developers, and audit readers.
The PRD requires refund orchestration when a paid order is cancelled on the B2C web API.
We will roll out behind a feature flag after staging validation completes successfully.

### Goals / Non-Goals

**Goals:**
- Provide cancel API with refund
- Restore inventory on cancel
- Support idempotent retries

**Non-Goals:**
- Partial refund policy
- Bulk admin cancel

## 2. 배경과 문제

Customers on the B2C web shop must cancel orders before and after payment under defined rules.
The product scope is limited to the public order API and excludes marketplace seller tools.
Operations teams need predictable refund behavior when a paid order moves to cancelled status.
Support volume spikes when cancel and refund paths disagree with what the PRD promises.
Inventory must return to sellable stock when a line item is released after cancel.
The PRD document defines cancel-flow steps and inventory restoration as mandatory outcomes.
This feature affects checkout, order history, and customer service dashboards equally.
Engineering will implement cancel as an orchestrated server-side workflow rather than a UI-only change.

## 3. 현재 시스템

The order service exposes POST /orders/{id}/cancel for authenticated shoppers today.
Cancel currently updates the order row to cancelled without calling any payment gateway module.
Inventory release is not triggered consistently when status changes on paid orders in production.
The cancel handler validates JWT bearer tokens and forwards work to OrderService synchronously.
OrderService loads the order entity, rejects duplicate cancel attempts, and persists status only.
Payment intent identifiers exist on paid orders but no refund API integration is wired yet.
Operations rely on manual Stripe dashboard refunds when customers complain about stuck paid cancels.
Because the PRD now requires automated refund on paid cancel, the current system is incomplete.

## 4. 갭과 설계 전환

PRD mandates refund when status is paid, yet code never invokes PaymentGateway.refund during cancel.
The gap is therefore PRD-only refund orchestration missing from OrderService.cancel implementation.
We will extend cancel to call Stripe refunds before inventory release for paid orders only.
Pending orders continue to skip refund and only transition status with inventory release unchanged.
This direction preserves existing auth boundaries and adds a new PaymentGateway adapter module.
Staging will validate timeout handling before the feature flag enables production traffic.
Audit readers can trace the refund decision in the summary table and Appendix B block below.

### 결정 요약

| # | 주제 | 선택 | 상태 | 상세 |
|---|------|------|------|------|
| 1 | Refund | PaymentGateway.refund | 확정 | block below |

> **결정:** Add PaymentGateway.refund to cancel flow for paid orders.
> **근거:** https://example.com/docs/refunds
> **코드:** `src/orders/cancel_handler.ts:18`
> **상태:** 확정

Brownfield teams will ship the adapter behind cancel_refund_enabled after staging soak time.

## 5. 상위설계

### 아키텍처 개요

Ch.4 chose Stripe refund orchestration, so the cancel path stays a thin API over OrderService.
Clients authenticate with JWT; OrderService coordinates PaymentGateway and InventoryService before commit.
The diagram shows only box-level boundaries because field schemas live in the detailed design chapter.

```mermaid
flowchart LR
  Client --> CancelHandler
  CancelHandler --> OrderService
  OrderService --> PaymentGateway
  OrderService --> InventoryService
```

### 구성요소 및 책임

OrderService remains the orchestrator while CancelHandler keeps HTTP concerns isolated from PG details.
PaymentGateway encapsulates Stripe refund calls and retry enqueue on timeout events from the PG vendor.
InventoryService continues to own stock release semantics defined in the existing internal inventory API.

- **CancelHandler** (기존): HTTP cancel endpoint and idempotency header forwarding
- **OrderService** (기존): status transitions and paid-branch refund orchestration
- **PaymentGateway** (신규): Stripe refund API with retry queue on timeout
- **InventoryService** (기존): release line items after successful refund branch

### 데이터 흐름

Paid cancels refund first because PRD cancel-flow orders payment reversal before stock release.
The synchronous path returns explicit error codes when PG or inventory fails without partial commits.
Each numbered step below reuses the component names introduced in the responsibility subsection above.

1. Client calls CancelHandler with JWT and optional Idempotency-Key
2. CancelHandler invokes OrderService.cancel for the order id
3. OrderService calls PaymentGateway.refund when status is paid
4. OrderService calls InventoryService.release for all line items
5. OrderService persists cancelled status and cancelled_at timestamp

## 6. 상세설계

The following table maps endpoints, entities, and primary error codes for implementers.

| Endpoint / Interface | Entity | Error codes |
|----------------------|--------|-------------|
| POST /orders/{id}/cancel | orders | 404, 409, 502 |

### API 및 인터페이스

CancelHandler validates Bearer JWT, forwards to OrderService, and surfaces PG timeout as retryable 502.

#### `POST /orders/{id}/cancel`

| Field | Type | Required | Note |
|-------|------|----------|------|
| id | path UUID | yes | order id |
| Idempotency-Key | header string | no | safe retry |
| Authorization | header Bearer | yes | JWT access token |

| Code | HTTP | When | Client action | Retry? |
|------|------|------|---------------|--------|
| ORDER_NOT_FOUND | 404 | invalid id | fix request | no |
| ALREADY_CANCELLED | 409 | duplicate | show status | no |
| PAYMENT_TIMEOUT | 502 | PG timeout | retry same key | yes |

See [ref:A-1].

### 데이터 모델

Orders table stores payment_intent_id for paid rows and cancelled_at when cancel completes.
Migration V004 adds cancelled_at without rewriting historical status values for reporting.

#### `orders`

| Field | Type | Nullable | Constraint | Notes |
|-------|------|----------|------------|-------|
| id | uuid | no | PK | |
| status | enum | no | pending/paid/cancelled | |
| payment_intent_id | string | yes | Stripe reference | paid only |
| cancelled_at | timestamptz | yes | set on cancel | migration V004 |

### 핵심 처리 흐름

OrderService.cancel loads the order, rejects already cancelled rows, then runs refund and inventory branches.

**Happy path:** OrderService loads order → rejects cancelled → PaymentGateway.refund if paid → InventoryService.release → persist cancelled.

**Errors:**
- PaymentGateway timeout → enqueue retry job, return 502 PAYMENT_TIMEOUT
- InventoryService.release failure → compensating refund attempt, return 500 INVENTORY_RELEASE_FAILED

## 7. 마무리

### 롤아웃·일정

Staging validation for one week, then production with cancel_refund_enabled flag default off.

### 리스크

| Risk | Impact | Mitigation |
|------|--------|------------|
| PG timeout | stuck cancel | retry queue + 502 |

### 열린 질문

- Partial refund policy remains undefined in PRD.

## 부록 A. 출처·코드 위치

| ID | 주장 | PRD | Code | External URL |
|----|------|-----|------|--------------|
| A-1 | Idempotent cancel | prd | `src/a.ts:1` | |

## 부록 B. Ch.4 결정 전문

> **결정:** Add PaymentGateway.refund to cancel flow for paid orders.
> **근거:** https://example.com/docs/refunds
> **코드:** `src/orders/cancel_handler.ts:18`
> **상태:** 확정
"""


class TestStrictSourcePolicy(unittest.TestCase):
    def test_ch5_subsection_without_sasil_block_passes_strict(self):
        doc = FRONTMATTER + MINIMAL_NARRATIVE_BODY
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=True)
            codes = [e.code for e in errors]
            self.assertNotIn("subsection-no-yoyak", codes)
            self.assertNotIn("subsection-source-missing", codes)
        finally:
            path.unlink()


class TestNarrativeProfile(unittest.TestCase):
    def test_narrative_checks_pass(self):
        doc = FRONTMATTER + MINIMAL_NARRATIVE_BODY
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=True, narrative=True)
            self.assertEqual(errors, [], [str(e) for e in errors])
        finally:
            path.unlink()

    def test_forbidden_yoyak_fails_narrative(self):
        doc = FRONTMATTER + MINIMAL_NARRATIVE_BODY.replace(
            "Customers on the B2C",
            "요약: Customers on the B2C",
            1,
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=False, narrative=True)
            codes = [e.code for e in errors]
            self.assertIn("meta-yoyak", codes)
        finally:
            path.unlink()

    def test_ch1_legacy_order_fails_narrative(self):
        legacy = MINIMAL_NARRATIVE_BODY.replace(
            "## 1. 서문\n\n### 목차",
            "## 1. 서문\n\nThis document describes the order cancel feature for PM, developers, and audit readers.\n"
            "The PRD requires refund orchestration when a paid order is cancelled on the B2C web API.\n"
            "We will roll out behind a feature flag after staging validation completes successfully.\n\n"
            "### Goals / Non-Goals\n\n**Goals:**\n- Provide cancel API with refund\n\n**Non-Goals:**\n- Bulk admin cancel\n\n"
            "### 이 문서 읽는 법\n\n| 독자 | 먼저 볼 곳 | 목표 |\n| PM | Ch.5 | ~3분 |\n\n### 목차",
            1,
        ).replace(
            "This document describes the order cancel feature for PM, developers, and audit readers.\n"
            "The PRD requires refund orchestration when a paid order is cancelled on the B2C web API.\n"
            "We will roll out behind a feature flag after staging validation completes successfully.\n\n"
            "### Goals / Non-Goals",
            "### Goals / Non-Goals",
            1,
        )
        doc = FRONTMATTER + legacy
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=False, narrative=True)
            codes = [e.code for e in errors]
            self.assertIn("ch1-section-order", codes)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
