---
title: "TDD: 주문 취소 API"
feature: order-cancel-api
mode: brownfield
prd_source: "docs/prd/order-cancel.md"
generated_at: 2026-05-25
validation_passed: true
review_rounds: 0
---

# 주문 취소 API — Technical Design Document

## 1. 서문

이 문서는 PM, 백엔드 개발자, 감사 담당자가 주문 취소 기능의 기술 설계를 공유하기 위해 작성한다. PRD `docs/prd/order-cancel.md`를 2026-05-25 기준으로 반영한다.

### TL;DR

B2C 웹 주문 API에서 paid 상태 취소 시 환불과 재고 복구가 필요하다. `OrderService.cancel`에 `PaymentGateway.refund` 연동을 추가한다. Staging 검증 후 feature flag로 production에 롤아웃한다.

### Goals / Non-Goals

**Goals:**
- paid/pending 주문 취소 API 제공
- Stripe 환불 및 재고 복구 orchestration
- Idempotent cancel (Idempotency-Key)

**Non-Goals:**
- partial refund 정책 (PRD 미정)
- B2B·관리자 bulk cancel

### 이 문서 읽는 법

| 독자 | 먼저 볼 곳 | 목표 |
|------|-----------|------|
| PM | TL;DR → [§5](#5-상위설계) diagram | ~2분 |
| Dev | [§4](#4-갭과-설계-전환) → [§6](#6-상세설계) 스펙 인덱스 | ~5분 |
| 감사 | [§4](#4-갭과-설계-전환) 결정 요약 → [부록 A](#부록-a-출처코드-위치) | ~3분 |

### 목차

1. [서문](#1-서문)
2. [배경과 문제](#2-배경과-문제)
3. [현재 시스템](#3-현재-시스템)
4. [갭과 설계 전환](#4-갭과-설계-전환)
5. [상위설계](#5-상위설계)
6. [상세설계](#6-상세설계)
7. [마무리](#7-마무리)
- [부록 A. 출처·코드 위치](#부록-a-출처코드-위치)
- [부록 B. Ch.4 결정 전문](#부록-b-ch4-결정-전문)

## 2. 배경과 문제

요약: 고객이 결제 완료 전·후 특정 조건에서 주문을 취소할 수 있어야 한다.

PRD는 취소 시 재고 복구와 paid 상태 환불을 요구한다. 범위는 B2C 웹 주문 API이다 [ref:A-1].

## 3. 현재 시스템

요약: 취소 endpoint는 status만 변경하며 환불은 없다.

`POST /orders/{id}/cancel`은 `OrderService.cancel`을 호출한다. 취소 시 status만 cancelled로 변경한다 [ref:A-2].

## 4. 갭과 설계 전환

요약: PRD의 환불 요구는 코드에 없으므로 PG 연동을 추가한다.

PRD는 paid 상태 취소 시 환불을 요구한다. 코드는 status 변경만 하므로 환불 연동은 미구현이다.

### 결정 요약

| # | 주제 | 선택 | 상태 | 상세 |
|---|------|------|------|------|
| 1 | 환불 연동 | PaymentGateway.refund | 확정 | 아래 **결정** block |

> **결정:** 취소 API에 PaymentGateway.refund 호출을 추가한다.
> **근거:** [source:stripe-refunds](https://stripe.com/docs/api/refunds)
> **코드:** `src/orders/cancel_handler.ts:18`
> **상태:** 확정

## 5. 상위설계

### 아키텍처 개요

요약: B2C 주문 취소는 API → OrderService → PaymentGateway·InventoryService 3계층으로 처리한다.

클라이언트 요청은 API layer에서 JWT 인증 후 OrderService로 전달된다. Service layer는 상태 전이를 orchestration하고, Data layer는 PostgreSQL orders 테이블을 사용한다. External layer는 Stripe PG와 InventoryService 내부 API를 호출한다 [ref:A-3].

```mermaid
flowchart LR
  Client --> CancelHandler
  CancelHandler --> OrderService
  OrderService --> PaymentGateway
  OrderService --> InventoryService
  OrderService --> PostgreSQL[(orders)]
```

#### 한눈에
- JWT 인증 후 CancelHandler가 OrderService에 위임한다
- paid 취소 시 Stripe 환불 후 재고 복구한다
- PostgreSQL orders 테이블에 최종 상태를 저장한다

### 구성요소 및 책임

요약: CancelHandler·OrderService·PaymentGateway·InventoryService 네 구성요소가 취소·환불·재고를 분담한다.

- **CancelHandler** (기존): `POST /orders/{id}/cancel` HTTP, 입력 검증, Idempotency-Key 전달
- **OrderService** (기존): 주문 상태 전이 orchestration, paid 분기에서 PaymentGateway 호출
- **PaymentGateway** (신규): Stripe refund API 호출, PG timeout 시 retry queue enqueue
- **InventoryService** (기존): line item 기준 재고 release [ref:A-4]

#### 한눈에
- CancelHandler는 HTTP 경계만 담당한다
- PaymentGateway는 신규 Stripe 연동 모듈이다
- InventoryService는 기존 재고 API를 재사용한다

### 데이터 흐름

요약: 취소 요청은 인증 → 상태 검증 → (paid 시) 환불 → 재고 복구 → DB 저장 순으로 처리한다.

1. Client → **CancelHandler**: `POST /orders/{id}/cancel` + JWT
2. **CancelHandler** → **OrderService**: cancel(orderId)
3. **OrderService**: status 검증; paid이면 **PaymentGateway**.refund (sync)
4. **OrderService** → **InventoryService**.release (sync)
5. **OrderService** → DB: status=cancelled, cancelled_at (sync)

paid 상태 취소 시 환불 후 재고 복구 순서는 PRD cancel-flow와 일치한다 [ref:A-5].

#### 한눈에
- happy path는 동기 호출 5단계이다
- paid일 때만 PaymentGateway를 호출한다
- 최종 DB commit 전에 재고 복구를 완료한다

## 6. 상세설계

### 스펙 인덱스

| Endpoint / Interface | Entity | Error codes |
|----------------------|--------|-------------|
| POST /orders/{id}/cancel | orders | 404, 409, 502 |

### API 및 인터페이스

요약: cancel endpoint는 Bearer 인증·idempotent하며 paid일 때만 refund를 트리거한다.

**CancelHandler**는 JWT 검증 후 **OrderService**에 위임한다.

#### `POST /orders/{id}/cancel`

| Field | Type | Required | Note |
|-------|------|----------|------|
| id | path UUID | yes | order id |
| Idempotency-Key | header string | no | duplicate cancel safe |
| Authorization | header Bearer | yes | JWT access token |

| Code | HTTP | When | Client action | Retry? |
|------|------|------|---------------|--------|
| ORDER_NOT_FOUND | 404 | invalid id | fix request | no |
| ALREADY_CANCELLED | 409 | status cancelled | show status | no |
| PAYMENT_TIMEOUT | 502 | PG timeout | retry with same key | yes |

Idempotency-Key 중복 시 동일 200 응답을 반환한다 [ref:A-6].

### 데이터 모델

요약: orders 테이블에 cancelled_at을 추가하고 status enum을 PRD와 일치시킨다.

#### `orders`

| Field | Type | Nullable | Constraint | Notes |
|-------|------|----------|------------|-------|
| id | uuid | no | PK | |
| status | enum | no | pending/paid/cancelled/… | PRD §order-status |
| payment_intent_id | string | yes | FK logical → Stripe | paid orders only |
| cancelled_at | timestamptz | yes | set on cancel | migration V004 |

status enum은 pending, paid, shipped, delivered, cancelled 다섯 값이다 [ref:A-7].

### 핵심 처리 흐름

요약: OrderService.cancel이 happy path와 PG·재고 실패 분기를 처리한다.

**Happy path:** **OrderService** loads order → reject if cancelled → if paid call **PaymentGateway**.refund → **InventoryService**.release → persist cancelled + cancelled_at.

**Errors:**
- **PaymentGateway** timeout → enqueue retry job, return 502 PAYMENT_TIMEOUT; client may retry with Idempotency-Key
- **InventoryService**.release failure → compensating refund call, return 500 INVENTORY_RELEASE_FAILED; no status change

PG timeout 시 retry queue에 refund job을 적재한다 [ref:A-8].

## 7. 마무리

### 롤아웃·일정

Staging 1주 검증 후 production. Feature flag `cancel_refund_enabled`.

### 리스크

| Risk | Impact | Mitigation |
|------|--------|------------|
| PG timeout | 취소 stuck | retry queue + 502 to client |
| Partial refund policy gap | CS 혼선 | Ch.7 열린 질문으로 확정 대기 |

### 열린 질문

- partial refund 정책은 PRD에 미정의이다.

## 부록 A. 출처·코드 위치

| ID | 주장 | PRD | Code | External URL |
|----|------|-----|------|--------------|
| A-1 | PRD 범위는 B2C 웹 주문 API | [source:prd#scope] | | |
| A-2 | 취소 시 status만 cancelled로 변경 | [source:prd#cancel-flow] | `src/orders/cancel_handler.ts:8-22` | |
| A-3 | Stripe refund는 payment_intent 기준 | | `src/orders/cancel_handler.ts:18` | https://stripe.com/docs/api/refunds |
| A-4 | InventoryService.release가 재고 복구 | [source:prd#inventory] | `src/inventory/service.ts:40-55` | |
| A-5 | paid 취소 시 환불 후 재고 복구 순서 | [source:prd#cancel-flow] | `src/orders/cancel_handler.ts:8-22` | |
| A-6 | Idempotency-Key 중복 시 동일 200 | | `src/orders/cancel_handler.ts:8` | https://stripe.com/docs/api/idempotent_requests |
| A-7 | status enum 5값 | [source:prd#order-status] | `src/orders/state.ts:12-28` | |
| A-8 | PG timeout 시 retry queue 적재 | [source:prd#cancel-flow] | `src/orders/cancel_handler.ts:18` | |

## 부록 B. Ch.4 결정 전문

> **결정:** 취소 API에 PaymentGateway.refund 호출을 추가한다.
> **근거:** [source:stripe-refunds](https://stripe.com/docs/api/refunds)
> **코드:** `src/orders/cancel_handler.ts:18`
> **상태:** 확정
