---
title: "TDD: 주문 취소 API"
feature: order-cancel-api
mode: brownfield
prd_source: "docs/prd/order-cancel.md"
generated_at: 2026-05-25
validation_passed: false
review_rounds: 0
---

# 주문 취소 API — Technical Design Document

## 1. 서문

이 문서는 PM, 백엔드 개발자, 감사 담당자가 주문 취소 기능의 기술 설계를 공유하기 위해 작성한다. PRD `docs/prd/order-cancel.md`를 2026-05-25 기준으로 반영한다.

## 2. 배경과 문제

요약: 고객이 결제 완료 전·후 특정 조건에서 주문을 취소할 수 있어야 한다.

PRD는 취소 시 재고 복구와 paid 상태 환불을 요구한다. 범위는 B2C 웹 주문 API이다.

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

요약: API → OrderService → PaymentGateway + InventoryService 3계층으로 취소·환불·재고를 처리한다.

주문 취소 요청은 API layer에서 인증 후 OrderService로 전달된다. paid 주문은 PaymentGateway를 통해 환불하고, InventoryService로 재고를 복구한다.

### 구성요소 및 책임

- **CancelHandler** (기존): HTTP endpoint, 입력 검증
- **OrderService** (기존): 주문 상태 전이 orchestration
- **PaymentGateway** (신규): Stripe refund API 호출
- **InventoryService** (기존): 재고 release

> **사실:** InventoryService.release가 재고 복구를 담당한다.
> **근거:** [source:prd#inventory] + `src/inventory/service.ts:40-55`

### 데이터 흐름

1. Client → `POST /orders/{id}/cancel`
2. OrderService 상태 검증
3. paid이면 PaymentGateway.refund
4. InventoryService.release
5. Order status → cancelled

## 6. 상세설계

### API 및 인터페이스

요약: cancel endpoint는 idempotent하며 paid일 때만 refund를 트리거한다.

`POST /orders/{id}/cancel`

| Field | Type | Note |
|-------|------|------|
| id | path UUID | order id |
| Idempotency-Key | header | optional |

Response 200: `{ "status": "cancelled" }`

> **사실:** Stripe refund는 payment_intent 기준으로 생성한다.
> **근거:** [source:stripe-refunds](https://stripe.com/docs/api/refunds)

### 데이터 모델

`orders.status`: pending | paid | cancelled | …

취소 시 `cancelled_at` timestamp 추가 (migration 필요).

### 핵심 처리 흐름

1. Load order; reject if already cancelled
2. If status == paid → PaymentGateway.refund(order.payment_intent_id)
3. InventoryService.release(order.line_items)
4. Persist status cancelled + cancelled_at

## 7. 마무리

### 롤아웃·일정

Staging 1주 검증 후 production. Feature flag `cancel_refund_enabled`.

### 리스크

- PG timeout → retry queue (미구현, 열린 질문)

### 열린 질문

- partial refund 정책은 PRD에 미정의이다.
