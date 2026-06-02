---
title: "Issue Spec: AC-1 — paid cancel refund and inventory release"
feature: order-cancel-api
ac_id: AC-1
priority: Must
tdd_source: "docs/design/2026-05-25-sample-order-cancel-tdd.md"
tasks_source: "docs/tasks/2026-05-25-sample-order-cancel-tasks.md"
generated_at: 2026-05-25
spec_ready: false
blocked_by: []
---

# Issue Spec: AC-1 — paid cancel refund and inventory release

## Acceptance

Given paid 주문 When cancel 호출 Then Stripe refund 후 재고 release, status=cancelled

**PRD:** [source:prd#cancel-flow]

## Done when

- Test T-1 passes

## Tests

| Test ID | Layer | Scenario | Fixture / Mock | CI gate |
|---------|-------|----------|----------------|---------|
| T-1 | integration | paid cancel → refund + inventory | stripe mock, orders seed | yes |

## Behavior (in scope)

- **Happy path:** Load order → reject if already cancelled → if `paid`, call `PaymentGateway.refund` → `InventoryService.release` → persist `status=cancelled` and `cancelled_at`
- **Out of scope for AC-1:** Idempotency retry (AC-2), PG timeout / 502 (AC-3)

## Interfaces & code

- `PaymentGateway.refund` — `src/payments/gateway.ts`
- `OrderService.cancel` (paid branch) — `src/orders/service.ts`
- `InventoryService.release` — `src/inventory/service.ts`
- Integration test — `tests/integration/order_cancel_test.ts`

## Implementation tasks

- [ ] TK-004 [AC-1] Add integration test paid cancel path in `tests/integration/order_cancel_test.ts` — proves T-1
- [ ] TK-005 [AC-1] Implement `PaymentGateway.refund` in `src/payments/gateway.ts` — proves T-1
- [ ] TK-006 [AC-1] Extend `OrderService.cancel` paid branch in `src/orders/service.ts` — proves T-1

## Dependencies

```text
TK-004 blockedBy TK-003
TK-005 blockedBy TK-004
TK-006 blockedBy TK-005
```

## Out of scope

- AC-2, AC-3
- Ch.7 items not required for this AC

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | docs/design/2026-05-25-sample-order-cancel-tdd.md |
| Tasks | docs/tasks/2026-05-25-sample-order-cancel-tasks.md |
| Plan | _(after writing-plans)_ `docs/superpowers/plans/2026-05-25-order-cancel-api-AC-1-plan.md` |
| Tracker | _(after register)_ |
