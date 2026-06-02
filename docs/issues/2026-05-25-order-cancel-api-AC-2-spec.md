---
title: "Issue Spec: AC-2 — idempotent cancel retry"
feature: order-cancel-api
ac_id: AC-2
priority: Must
tdd_source: "docs/design/2026-05-25-sample-order-cancel-tdd.md"
tasks_source: "docs/tasks/2026-05-25-sample-order-cancel-tasks.md"
generated_at: 2026-05-25
spec_ready: false
blocked_by: []
---

# Issue Spec: AC-2 — idempotent cancel retry

## Acceptance

Given 동일 Idempotency-Key When cancel 재시도 Then 동일 200 body, 중복 refund 없음

**PRD:** [source:prd#cancel-flow]

## Done when

- Test T-2 passes

## Tests

| Test ID | Layer | Scenario | Fixture / Mock | CI gate |
|---------|-------|----------|----------------|---------|
| T-2 | integration | same Idempotency-Key twice | redis idempotency store | yes |

## Behavior (in scope)

- **Happy path:** Second `cancel` with the same `Idempotency-Key` returns the same 200 body as the first successful cancel
- **Constraint:** No duplicate Stripe refund for the same payment intent

## Interfaces & code

- `CancelHandler` (Idempotency-Key propagation) — `src/orders/cancel_handler.ts`
- Integration test — `tests/integration/order_cancel_test.ts`

## Implementation tasks

- [ ] TK-007 [AC-2] Add integration test Idempotency-Key retry in `tests/integration/order_cancel_test.ts` — proves T-2
- [ ] TK-008 [AC-2] Propagate Idempotency-Key in `src/orders/cancel_handler.ts` — proves T-2

## Dependencies

```text
TK-008 blockedBy TK-007
```

## Out of scope

- AC-1, AC-3
- Ch.7 items not required for this AC

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | docs/design/2026-05-25-sample-order-cancel-tdd.md |
| Tasks | docs/tasks/2026-05-25-sample-order-cancel-tasks.md |
| Plan | _(after writing-plans)_ `docs/superpowers/plans/2026-05-25-order-cancel-api-AC-2-plan.md` |
| Tracker | _(after register)_ |
