import importlib.util
import re
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "validate_tasks", Path(__file__).with_name("validate-tasks.py")
)
assert _SPEC and _SPEC.loader
v = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(v)

TDD_FIXTURE = """---
title: "TDD: test"
feature: order-cancel-api
mode: brownfield
prd_source: "docs/prd/order-cancel.md"
generated_at: 2026-05-25
validation_passed: true
review_rounds: 0
---

# Test

## 6. 상세설계

### 인수조건

| AC ID | PRD | 인수조건 | 우선순위 | 완료 판정 |
|-------|-----|----------|----------|-----------|
| AC-1 | [source:prd#cancel-flow] | Given paid When cancel Then refund | Must | T-1 passes |
| AC-2 | [source:prd#idempotency] | Given same key When retry Then same response | Must | T-2 passes |

### 테스트

| Test ID | AC ID | Layer | 시나리오 | Fixture / Mock | CI gate |
|---------|-------|-------|----------|----------------|---------|
| T-1 | AC-1 | integration | paid refund | stripe mock | yes |
| T-2 | AC-2 | integration | idempotent | redis | yes |

## 7. 마무리
"""

TASKS_FIXTURE = """---
title: "Tasks: test"
feature: order-cancel-api
mode: brownfield
tdd_source: "docs/design/2026-05-25-order-cancel-tdd.md"
prd_source: "docs/prd/order-cancel.md"
generated_at: 2026-05-25
validation_passed: false
---

# Tasks: test

> **Source TDD:** docs/design/2026-05-25-order-cancel-tdd.md
> **Done when:** all Must AC satisfied

## 추적 매트릭스 (RTM)

| PRD | AC | Task IDs | Test IDs | Component |
|-----|-----|----------|----------|-----------|
| [source:prd#cancel-flow] | AC-1 | TK-003, TK-004 | T-1 | PaymentGateway |
| [source:prd#idempotency] | AC-2 | TK-005, TK-006 | T-2 | CancelHandler |

## Dependencies

```text
TK-004 blockedBy TK-003
```

## Phase 0: Setup

- [ ] TK-001 [P] [AC-1] Add fixtures in `tests/integration/setup.ts`

## Phase 1: Foundation

- [ ] TK-002 [AC-1] Migration V004 in `migrations/V004.sql`

## Phase 2: AC-1 — refund

- [ ] TK-003 [AC-1] Add test in `tests/integration/cancel_test.ts` — proves T-1
- [ ] TK-004 [AC-1] Implement refund in `src/payments/gateway.ts` — proves T-1

## Phase 3: AC-2 — idempotency

- [ ] TK-005 [AC-2] Add test in `tests/integration/cancel_test.ts` — proves T-2
- [ ] TK-006 [AC-2] Wire handler in `src/orders/cancel_handler.ts` — proves T-2
"""


class ValidateTasksTests(unittest.TestCase):
    def test_valid_fixture_passes_with_tdd(self) -> None:
        errors = v.validate(TASKS_FIXTURE, TDD_FIXTURE)
        self.assertEqual(errors, [], [str(e) for e in errors])

    def test_ac_untasked_fails(self) -> None:
        broken = re.sub(
            r"^- \[ \] TK-00[56].*\n",
            "",
            TASKS_FIXTURE,
            flags=re.M,
        )
        errors = v.validate(broken, TDD_FIXTURE)
        codes = {e.code for e in errors}
        self.assertIn("ac-untasked", codes)

    def test_missing_rtm_fails(self) -> None:
        broken = TASKS_FIXTURE.replace("## 추적 매트릭스 (RTM)", "## Trace")
        errors = v.validate(broken, None)
        codes = {e.code for e in errors}
        self.assertIn("rtm-missing", codes)

    def test_implement_without_path_fails(self) -> None:
        broken = TASKS_FIXTURE.replace("`src/payments/gateway.ts`", "gateway module")
        errors = v.validate(broken, None)
        codes = {e.code for e in errors}
        self.assertIn("no-file-path", codes)


if __name__ == "__main__":
    unittest.main()
