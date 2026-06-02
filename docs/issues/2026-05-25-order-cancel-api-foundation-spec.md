---
title: "Issue Spec: Foundation — 주문 취소 API"
feature: order-cancel-api
ac_id: none
priority: infra
tdd_source: "docs/design/2026-05-25-sample-order-cancel-tdd.md"
tasks_source: "docs/tasks/2026-05-25-sample-order-cancel-tasks.md"
generated_at: 2026-05-25
spec_ready: false
blocked_by: []
---

# Issue Spec: Foundation — 주문 취소 API

## Goal

Enable AC implementation phases (migrations, flags, fixtures).

## Done when

- All Setup + Foundation TK lines in tasks.md are complete
- AC phases unblocked per tasks.md Dependencies

## Implementation tasks

- [ ] TK-001 [P] [AC-1] Enable feature flag `cancel_refund_enabled` in staging config `config/staging.yaml`
- [ ] TK-002 [P] [AC-1] Add Stripe mock fixtures in `tests/integration/fixtures/stripe.ts`
- [ ] TK-003 [AC-1] Migration V004 add `cancelled_at` to orders in `migrations/V004_orders_cancelled_at.sql`

## Dependencies

```text
(none)
```

## Out of scope

- AC-1, AC-2, AC-3 (per-AC issue specs)

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | docs/design/2026-05-25-sample-order-cancel-tdd.md |
| Tasks | docs/tasks/2026-05-25-sample-order-cancel-tasks.md |
