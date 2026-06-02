import importlib.util
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "validate_issue_spec", Path(__file__).with_name("validate-issue-spec.py")
)
assert _SPEC and _SPEC.loader
v = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(v)

TDD_FIXTURE = Path(__file__).resolve().parents[2] / "docs/design/2026-05-25-sample-order-cancel-tdd.md"
TASKS_FIXTURE = Path(__file__).resolve().parents[2] / "docs/tasks/2026-05-25-sample-order-cancel-tasks.md"

SPEC_AC1 = """---
title: "Issue Spec: AC-1 — paid cancel"
feature: order-cancel-api
ac_id: AC-1
priority: Must
tdd_source: "docs/design/2026-05-25-sample-order-cancel-tdd.md"
tasks_source: "docs/tasks/2026-05-25-sample-order-cancel-tasks.md"
generated_at: 2026-05-25
spec_ready: false
blocked_by: []
---

# Issue Spec: AC-1 — paid cancel

## Acceptance

Given paid 주문 When cancel 호출 Then Stripe refund 후 재고 release, status=cancelled

**PRD:** [source:prd#cancel-flow]

## Done when

- Test T-1 passes in CI

## Tests

| Test ID | Layer | Scenario | Fixture / Mock | CI gate |
|---------|-------|----------|----------------|---------|
| T-1 | integration | paid cancel | stripe mock | yes |

## Behavior (in scope)

- Happy path: refund then inventory release

## Interfaces & code

- `PaymentGateway.refund` — `src/payments/gateway.ts`
- `OrderService.cancel` — `src/orders/service.ts`

## Implementation tasks

- [ ] TK-004 [AC-1] Add test in `tests/integration/order_cancel_test.ts` — proves T-1
- [ ] TK-005 [AC-1] Implement refund in `src/payments/gateway.ts` — proves T-1
- [ ] TK-006 [AC-1] Extend cancel in `src/orders/service.ts` — proves T-1

## Dependencies

```text
TK-005 blockedBy TK-004
```

## Out of scope

- AC-2, AC-3

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | docs/design/2026-05-25-sample-order-cancel-tdd.md |
| Tasks | docs/tasks/2026-05-25-sample-order-cancel-tasks.md |
"""


class TestValidateIssueSpec(unittest.TestCase):
    def test_valid_ac1_with_cross_check(self) -> None:
        tdd = TDD_FIXTURE.read_text(encoding="utf-8")
        tasks = TASKS_FIXTURE.read_text(encoding="utf-8")
        errors = v.validate(SPEC_AC1, tdd, tasks)
        self.assertEqual(errors, [], [str(e) for e in errors])

    def test_spec_ready_blocks_open_questions(self) -> None:
        bad = SPEC_AC1.replace("spec_ready: false", "spec_ready: true").replace(
            "- (none)", "- partial refund policy TBD"
        )
        errors = v.validate(bad, None, None)
        codes = {e.code for e in errors}
        self.assertIn("open-questions-blocking", codes)

    def test_missing_acceptance(self) -> None:
        bad = SPEC_AC1.replace("## Acceptance", "## Summary")
        errors = v.validate(bad, None, None)
        codes = {e.code for e in errors}
        self.assertIn("section-missing", codes)


if __name__ == "__main__":
    unittest.main()
