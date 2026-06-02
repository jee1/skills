---
title: "Issue Spec: AC-3 — PG timeout handling (Should)"
feature: order-cancel-api
ac_id: AC-3
priority: Should
tdd_source: "docs/design/2026-05-25-sample-order-cancel-tdd.md"
tasks_source: "docs/tasks/2026-05-25-sample-order-cancel-tasks.md"
generated_at: 2026-05-25
spec_ready: false
blocked_by: []
---

# Issue Spec: AC-3 — PG timeout handling (Should)

## Acceptance

Given PG timeout When cancel Then 502 PAYMENT_TIMEOUT, 주문 status 변경 없음

**PRD:** [source:prd#cancel-flow]

## Done when

- Test T-3 passes (manual staging)

## Tests

| Test ID | Layer | Scenario | Fixture / Mock | CI gate |
|---------|-------|----------|----------------|---------|
| T-3 | integration | PaymentGateway timeout | stripe timeout stub | no |

## Behavior (in scope)

- **Error path:** `PaymentGateway.refund` timeout → enqueue retry job → return **502 PAYMENT_TIMEOUT**; order `status` must not change to cancelled
- **Priority:** Should — schedule after Must AC-1/AC-2; manual staging gate for T-3

## Interfaces & code

- `PaymentGateway.refund` (timeout + retry enqueue) — `src/payments/gateway.ts`
- Integration test — `tests/integration/order_cancel_test.ts`

## Implementation tasks

- [ ] TK-009 [AC-3] Add integration test PG timeout stub in `tests/integration/order_cancel_test.ts` — proves T-3
- [ ] TK-010 [AC-3] Enqueue retry job on timeout in `src/payments/gateway.ts` — proves T-3

## Dependencies

```text
TK-010 blockedBy TK-009
```

## Out of scope

- AC-1, AC-2
- Ch.7 items not required for this AC

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | docs/design/2026-05-25-sample-order-cancel-tdd.md |
| Tasks | docs/tasks/2026-05-25-sample-order-cancel-tasks.md |
| Plan | _(after writing-plans)_ `docs/superpowers/plans/2026-05-25-order-cancel-api-AC-3-plan.md` |
| Tracker | _(after register)_ |
