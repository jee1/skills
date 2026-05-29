---
title: "Tasks: 주문 취소 API"
feature: order-cancel-api
mode: brownfield
tdd_source: "docs/design/2026-05-25-sample-order-cancel-tdd.md"
prd_source: "docs/prd/order-cancel.md"
generated_at: 2026-05-25
validation_passed: true
---

# Tasks: 주문 취소 API

> **Source TDD:** docs/design/2026-05-25-sample-order-cancel-tdd.md
> **Done when:** all **Must** AC rows (AC-1, AC-2) satisfied; CI-gated tests T-1 and T-2 green

## 추적 매트릭스 (RTM)

| PRD | AC | Task IDs | Test IDs | Component / scope |
|-----|-----|----------|----------|-------------------|
| [source:prd#cancel-flow] | AC-1 | TK-004, TK-005, TK-006 | T-1 | PaymentGateway, OrderService |
| [source:prd#cancel-flow] | AC-2 | TK-007, TK-008 | T-2 | CancelHandler, OrderService |
| [source:prd#cancel-flow] | AC-3 | TK-009, TK-010 | T-3 | PaymentGateway retry queue |

## Dependencies

```text
TK-004 blockedBy TK-003
TK-005 blockedBy TK-004
TK-006 blockedBy TK-005
TK-008 blockedBy TK-007
TK-010 blockedBy TK-009
```

## Phase 0: Setup

- [ ] TK-001 [P] [AC-1] Enable feature flag `cancel_refund_enabled` in staging config `config/staging.yaml`
- [ ] TK-002 [P] [AC-1] Add Stripe mock fixtures in `tests/integration/fixtures/stripe.ts`

## Phase 1: Foundation

- [ ] TK-003 [AC-1] Migration V004 add `cancelled_at` to orders in `migrations/V004_orders_cancelled_at.sql`

## Phase 2: AC-1 — paid cancel refund and inventory release

- [ ] TK-004 [AC-1] Add integration test paid cancel path in `tests/integration/order_cancel_test.ts` — proves T-1
- [ ] TK-005 [AC-1] Implement `PaymentGateway.refund` in `src/payments/gateway.ts` — proves T-1
- [ ] TK-006 [AC-1] Extend `OrderService.cancel` paid branch in `src/orders/service.ts` — proves T-1

## Phase 3: AC-2 — idempotent cancel retry

- [ ] TK-007 [AC-2] Add integration test Idempotency-Key retry in `tests/integration/order_cancel_test.ts` — proves T-2
- [ ] TK-008 [AC-2] Propagate Idempotency-Key in `src/orders/cancel_handler.ts` — proves T-2

## Phase 4: AC-3 — PG timeout handling (Should)

- [ ] TK-009 [AC-3] Add integration test PG timeout stub in `tests/integration/order_cancel_test.ts` — proves T-3
- [ ] TK-010 [AC-3] Enqueue retry job on timeout in `src/payments/gateway.ts` — proves T-3

## Phase 5: CI & docs

- [ ] TK-011 [P] [AC-1] Wire CI job `npm run test:integration` for T-1 and T-2 in `.github/workflows/ci.yml`
