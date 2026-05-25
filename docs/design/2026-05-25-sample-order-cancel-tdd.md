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

## 2. 배경과 문제

요약: 고객이 결제 완료 전·후 특정 조건에서 주문을 취소할 수 있어야 한다.

PRD는 취소 시 재고 복구와 paid 상태 환불을 요구한다. 범위는 B2C 웹 주문 API이다.

> **사실:** PRD 범위는 B2C 웹 주문 API이다.
> **근거:** [source:prd#scope]

## 3. 현재 시스템

요약: 취소 endpoint는 status만 변경하며 환불은 없다.

`POST /orders/{id}/cancel`은 `OrderService.cancel`을 호출한다.

> **사실:** 취소 시 status만 cancelled로 변경한다.
> **근거:** [source:prd#cancel-flow] + `src/orders/cancel_handler.ts:8-22`

## 4. 갭과 설계 전환

요약: PRD의 환불 요구는 코드에 없으므로 PG 연동을 추가한다.

PRD는 paid 상태 취소 시 환불을 요구한다. 코드는 status 변경만 하므로 환불 연동은 미구현이다.

> **결정:** 취소 API에 PaymentGateway.refund 호출을 추가한다.
> **근거:** [source:stripe-refunds](https://stripe.com/docs/api/refunds)
> **코드:** `src/orders/cancel_handler.ts:18`
> **상태:** 확정

## 5. 상위설계

### 아키텍처 개요

요약: B2C 주문 취소는 API → OrderService → PaymentGateway·InventoryService 3계층으로 처리한다.

클라이언트 요청은 API layer에서 JWT 인증 후 OrderService로 전달된다. Service layer는 상태 전이를 orchestration하고, Data layer는 PostgreSQL orders 테이블을 사용한다. External layer는 Stripe PG와 InventoryService 내부 API를 호출한다.

> **사실:** Stripe refund API는 payment_intent 기준으로 환불을 생성한다.
> **근거:** [source:stripe-refunds](https://stripe.com/docs/api/refunds) + `src/orders/cancel_handler.ts:18`

### 구성요소 및 책임

요약: CancelHandler·OrderService·PaymentGateway·InventoryService 네 구성요소가 취소·환불·재고를 분담한다.

- **CancelHandler** (기존): `POST /orders/{id}/cancel` HTTP, 입력 검증, Idempotency-Key 전달
- **OrderService** (기존): 주문 상태 전이 orchestration, paid 분기에서 PaymentGateway 호출
- **PaymentGateway** (신규): Stripe refund API 호출, PG timeout 시 retry queue enqueue
- **InventoryService** (기존): line item 기준 재고 release

> **사실:** InventoryService.release가 재고 복구를 담당한다.
> **근거:** [source:prd#inventory] + `src/inventory/service.ts:40-55`

### 데이터 흐름

요약: 취소 요청은 인증 → 상태 검증 → (paid 시) 환불 → 재고 복구 → DB 저장 순으로 처리한다.

1. Client → **CancelHandler**: `POST /orders/{id}/cancel` + JWT
2. **CancelHandler** → **OrderService**: cancel(orderId)
3. **OrderService**: status 검증; paid이면 **PaymentGateway**.refund (sync)
4. **OrderService** → **InventoryService**.release (sync)
5. **OrderService** → DB: status=cancelled, cancelled_at (sync)

> **사실:** paid 상태 취소 시 환불 후 재고 복구 순서는 PRD cancel-flow와 일치한다.
> **근거:** [source:prd#cancel-flow] + `src/orders/cancel_handler.ts:8-22`

## 6. 상세설계

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

> **사실:** Idempotency-Key 중복 시 동일 200 응답을 반환한다.
> **근거:** [source:stripe-idempotency](https://stripe.com/docs/api/idempotent_requests) + `src/orders/cancel_handler.ts:8`

### 데이터 모델

요약: orders 테이블에 cancelled_at을 추가하고 status enum을 PRD와 일치시킨다.

#### `orders`

| Field | Type | Nullable | Constraint | Notes |
|-------|------|----------|------------|-------|
| id | uuid | no | PK | |
| status | enum | no | pending/paid/cancelled/… | PRD §order-status |
| payment_intent_id | string | yes | FK logical → Stripe | paid orders only |
| cancelled_at | timestamptz | yes | set on cancel | migration V004 |

> **사실:** status enum은 pending, paid, shipped, delivered, cancelled 다섯 값이다.
> **근거:** [source:prd#order-status] + `src/orders/state.ts:12-28`

### 핵심 처리 흐름

요약: OrderService.cancel이 happy path와 PG·재고 실패 분기를 처리한다.

**Happy path:** **OrderService** loads order → reject if cancelled → if paid call **PaymentGateway**.refund → **InventoryService**.release → persist cancelled + cancelled_at.

**Errors:**
- **PaymentGateway** timeout → enqueue retry job, return 502 PAYMENT_TIMEOUT; client may retry with Idempotency-Key
- **InventoryService**.release failure → compensating refund call, return 500 INVENTORY_RELEASE_FAILED; no status change

> **사실:** PG timeout 시 retry queue에 refund job을 적재한다.
> **근거:** [source:prd#cancel-flow] + `src/orders/cancel_handler.ts:18`

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
