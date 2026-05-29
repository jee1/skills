# Examples — order-cancel (excerpt)

Source TDD (hypothetical Ch.6 AC/test rows): `docs/design/2026-05-25-sample-order-cancel-tdd.md`

## RTM excerpt

| PRD | AC | Task IDs | Test IDs | Component |
|-----|-----|----------|----------|-----------|
| [source:prd#cancel-flow] | AC-1 | TK-004, TK-005, TK-006 | T-1 | PaymentGateway, OrderService |
| [source:prd#idempotency] | AC-2 | TK-007, TK-008 | T-2 | CancelHandler |

## Phase excerpt

```markdown
## Phase 1: Foundation

- [ ] TK-003 Migration V004 add `cancelled_at` to `orders` in `migrations/V004_orders_cancelled_at.sql`

## Phase 2: AC-1 — paid cancel triggers refund and inventory release

- [ ] TK-004 [AC-1] Add integration test paid cancel refund path in `tests/integration/order_cancel_test.ts` — proves T-1
- [ ] TK-005 [AC-1] Implement `PaymentGateway.refund` in `src/payments/gateway.ts` — proves T-1
- [ ] TK-006 [AC-1] Extend `OrderService.cancel` paid branch in `src/orders/service.ts` — proves T-1

## Phase 3: AC-2 — duplicate Idempotency-Key returns same response

- [ ] TK-007 [AC-2] Add integration test idempotent retry in `tests/integration/order_cancel_test.ts` — proves T-2
- [ ] TK-008 [AC-2] Propagate Idempotency-Key in `src/orders/cancel_handler.ts` — proves T-2
```

## Bad vs good task lines

**Bad** — no path, no AC, vague:

```markdown
- [ ] TK-004 Implement refund logic
```

**Good:**

```markdown
- [ ] TK-005 [AC-1] Implement `PaymentGateway.refund` calling Stripe API in `src/payments/gateway.ts` — proves T-1
```
