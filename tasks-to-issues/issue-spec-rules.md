# Issue Spec Rules

## Granularity

| Tracker issue | Issue Spec | Notes |
|---------------|------------|-------|
| Epic | — | Links feature TDD + tasks.md only |
| Story | 1× AC spec (Must default) | `ac_id: AC-n` |
| Infra story | 1× foundation spec | `ac_id: none`, `priority: infra` |
| Sub-task | Optional | Prefer TK checklist inside Story spec |

## Slicing from TDD Ch.6

For `ac_id: AC-n`, copy into the spec:

1. **인수조건** table row → Acceptance + Done when
2. **테스트** rows where AC ID column matches → Tests table
3. **핵심 처리 흐름** bullets / mermaid branches that AC needs → Behavior
4. **API** / **데이터 모델** rows touched by that AC → Interfaces & code
5. **Errors** subsection rows for client-visible codes in that AC → Behavior

Do not paste full TDD into the issue body; link `tdd_source` and keep the spec self-contained for plan/implement.

## Slicing from tasks.md

1. Find `## Phase …: AC-n —` (or RTM row for AC-n)
2. Copy all `- [ ] TK-…` lines with `[AC-n]` into Implementation tasks
3. Copy `blockedBy` lines involving those TK IDs into Dependencies

## Registration order

```text
validate-tdd → validate-tasks --tdd
  → generate-issue-specs (draft, spec_ready: false)
  → human review → spec_ready: true + validate-issue-spec
  → create tracker issues (summary + spec path)
  → writing-plans (per issue, on demand)
  → executing-plans
```

## GitHub issue body (minimal)

```markdown
## Spec
- Issue spec: `docs/issues/…-AC-1-spec.md` (spec_ready: true)
- TDD: `docs/design/…-tdd.md`
- Tasks: `docs/tasks/…-tasks.md`

## Done when
(Single line from spec Done when section)
```

Labels: `spec-ready`, `ac/AC-1`, `feature/<slug>`.
