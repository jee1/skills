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
## 목차

1. [서문](#1-서문)
2. [배경과 문제](#2-배경과-문제)

## 이 문서 읽는 법

| 독자 | 먼저 볼 곳 | 목표 |
|------|-----------|------|
| PM | ## 1. 서문 opening → Ch.5 diagram | \\~3분 |
| Dev | Ch.4 → Ch.6 tables | \\~5분 |
| Audit | Ch.4 결정 요약 → Appendix A | \\~3분 |

## 1. 서문

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

### 요구사항 분석

The following tables refine PRD cancel-flow into traceable requirement IDs before we compare the codebase in the next chapter.
Each Must functional requirement will later map to acceptance criteria and CI-gated tests in the detailed design chapter.

#### 기능 요구 (FR)

| FR ID | PRD | 요구 설명 (shall) | 우선순위 | 구현 상태 | 비고 |
|-------|-----|-------------------|----------|-----------|------|
| FR-1 | [source:prd#cancel-flow] | Paid orders shall trigger a full refund before status moves to cancelled | Must | 미구현 | Ch.4 gap |
| FR-2 | [source:prd#cancel-flow] | Cancel shall restore inventory for all line items after successful cancel | Must | 미구현 | Inventory path |
| FR-3 | [source:prd#idempotency] | Duplicate cancel with the same Idempotency-Key shall not double-refund | Must | 부분 | Header not forwarded |

#### 비기능 요구 (NFR)

| NFR ID | PRD | 요구 | 목표치 | 검증 방법 (개략) |
|--------|-----|------|--------|------------------|
| NFR-1 | [source:prd#auth] | Cancel API requires JWT bearer authentication | Enforced on every request | Integration test with 401 |

#### 제약·가정·의존성

| 유형 | ID | 내용 | 영향 |
|------|-----|------|------|
| 제약 | CON-1 | Scope is B2C web order API only | Excludes admin bulk cancel |
| 가정 | ASM-1 | Stripe payment_intent_id is stored on paid orders | Refund integration |

#### 추적성 매트릭스 (RTM)

| PRD 앵커 | REQ ID | (예정) AC ID | 설계 반영 (Ch.5–6) | 테스트 |
|----------|--------|--------------|-------------------|--------|
| [source:prd#cancel-flow] | FR-1 | AC-1 | PaymentGateway.refund on paid branch | T-1 |
| [source:prd#cancel-flow] | FR-2 | AC-2 | InventoryService.release after refund | T-2 |
| [source:prd#idempotency] | FR-3 | AC-3 | Idempotency-Key forwarded, no double refund | T-3 |

The FR implementation status column is validated against the current system description in the following chapter.

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
Audit readers can trace the refund decision in the summary table and Appendix B decision card.

```mermaid
flowchart LR
  AsIs[Status-only cancel] --> Gap[Missing refund path]
  Gap --> ToBe[Orchestrated refund cancel]
```

### 결정 요약

| # | 주제 | 선택 | 상태 | 근거 한줄 |
|---|------|------|------|-----------|
| 1 | Refund | PaymentGateway.refund | 확정 | Stripe refund API matches paid cancel PRD requirement |

### 환불 연동

Paid cancel must invoke PaymentGateway.refund before inventory release to satisfy PRD cancel-flow.

| 항목 | 내용 |
|------|------|
| 결정 | Add PaymentGateway.refund to cancel flow for paid orders |
| 상태 | 확정 |
| 코드 | `src/orders/cancel_handler.ts:18` — status-only cancel today |

**근거 설명:** The Stripe Refunds API creates refunds against payment_intent identifiers already stored on paid order rows. Status-only cancel leaves PRD refund orchestration unimplemented and forces manual dashboard refunds in operations.

**참고:** [Stripe Refunds API](https://example.com/docs/refunds) — payment_intent refund creation semantics

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

```mermaid
sequenceDiagram
  Client->>CancelHandler: POST cancel
  CancelHandler->>OrderService: cancel(orderId)
  OrderService->>PaymentGateway: refund if paid
  OrderService->>InventoryService: release
```

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

```mermaid
flowchart TD
  Start[Load order] --> Paid{status paid?}
  Paid -->|yes| Refund[PaymentGateway.refund]
  Paid -->|no| Inv[InventoryService.release]
  Refund -->|timeout| E502[502 PAYMENT_TIMEOUT]
  Refund --> Inv
  Inv -->|fail| E500[500 INVENTORY_RELEASE_FAILED]
  Inv --> Done[Persist cancelled]
```

**Happy path:** OrderService loads order → rejects cancelled → PaymentGateway.refund if paid → InventoryService.release → persist cancelled.

**Errors:**
- PaymentGateway timeout → enqueue retry job, return 502 PAYMENT_TIMEOUT
- InventoryService.release failure → compensating refund attempt, return 500 INVENTORY_RELEASE_FAILED

### 인수조건

Acceptance criteria define when cancel-with-refund is done for PM, QA, and audit readers. Each row maps to PRD cancel-flow and names the test that proves completion in CI before rollout.

| AC ID | PRD | 인수조건 | 우선순위 | 완료 판정 |
|-------|-----|----------|----------|-----------|
| AC-1 | [source:prd#cancel-flow] | Given a paid order, When POST /orders/{id}/cancel, Then PaymentGateway.refund is called and status becomes cancelled | Must | T-1 passes in CI |
| AC-2 | [source:prd#cancel-flow] | Given an already cancelled order, When POST cancel again, Then HTTP 409 ALREADY_CANCELLED and no second refund | Must | T-2 passes in CI |
| AC-3 | [source:prd#idempotency] | Given the same Idempotency-Key, When POST cancel is retried, Then the same 200 body and no second refund | Must | T-3 passes in CI |

### 테스트

Integration tests exercise HTTP boundaries with stripe mock and test DB, while unit tests cover OrderService branching without external IO. Every AC below has a merge-blocking CI gate before production traffic uses cancel_refund_enabled.

| Test ID | AC ID | Layer | 시나리오 | Fixture / Mock | CI gate |
|---------|-------|-------|----------|----------------|---------|
| T-1 | AC-1 | integration | paid cancel triggers refund and inventory release | `tests/integration/cancel.test.ts` + stripe mock | yes |
| T-2 | AC-2 | unit | duplicate cancel returns conflict without refund | OrderService fixture | yes |
| T-3 | AC-3 | integration | same Idempotency-Key twice, no double refund | redis idempotency store | yes |

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

### 환불 연동

Paid cancel must invoke PaymentGateway.refund before inventory release to satisfy PRD cancel-flow.

| 항목 | 내용 |
|------|------|
| 결정 | Add PaymentGateway.refund to cancel flow for paid orders |
| 상태 | 확정 |
| 코드 | `src/orders/cancel_handler.ts:18` — status-only cancel today |

**근거 설명:** The Stripe Refunds API creates refunds against payment_intent identifiers already stored on paid order rows. Status-only cancel leaves PRD refund orchestration unimplemented and forces manual dashboard refunds in operations.

**참고:** [Stripe Refunds API](https://example.com/docs/refunds) — payment_intent refund creation semantics
"""


class TestRequirementTraceability(unittest.TestCase):
    def test_must_fr_missing_from_rtm_fails(self):
        doc = FRONTMATTER + MINIMAL_NARRATIVE_BODY.replace(
            "| [source:prd#idempotency] | FR-3 | AC-3 | Idempotency-Key forwarded, no double refund | T-3 |\n",
            "",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=True)
            codes = [e.code for e in errors]
            self.assertIn("must-fr-rtm-missing", codes)
        finally:
            path.unlink()

    def test_sample_order_cancel_passes_traceability(self):
        sample = Path(__file__).resolve().parents[2] / "docs/design/2026-05-25-sample-order-cancel-tdd.md"
        if not sample.is_file():
            self.skipTest("sample TDD not in repo")
        errors = v.validate(sample, strict=True, narrative=True)
        codes = [e.code for e in errors]
        self.assertEqual(
            [],
            [c for c in codes if c.startswith("must-fr") or c.startswith("oq-ch7")],
            [str(e) for e in errors],
        )


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

    def test_ch1_nested_frontmatter_fails(self):
        legacy = MINIMAL_NARRATIVE_BODY.replace(
            "## 1. 서문\n\nThis document",
            "## 1. 서문\n\n### 목차\n\n1. bad\n\nThis document",
            1,
        )
        doc = FRONTMATTER + legacy
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=True, narrative=True)
            codes = [e.code for e in errors]
            self.assertIn("ch1-nested-frontmatter", codes)
        finally:
            path.unlink()


    def test_unescaped_tilde_fails(self):
        doc = FRONTMATTER + MINIMAL_NARRATIVE_BODY.replace(
            "B2C web shop",
            "B2C web shop (A~Z scope)",
            1,
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=False, narrative=False)
            codes = [e.code for e in errors]
            self.assertIn("unescaped-tilde", codes)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
