# Issue Spec Template

Copy structure below. One file per **Story** (Must AC by default; Should AC only when scheduled).
Filename: `docs/issues/YYYY-MM-DD-<feature_slug>-<AC-id>-spec.md` (e.g. `…-AC-1-spec.md`).

```markdown
---
title: "Issue Spec: AC-1 — {short_title}"
feature: {feature_slug}
ac_id: AC-1
priority: Must
tdd_source: "docs/design/YYYY-MM-DD-{feature_slug}-tdd.md"
tasks_source: "docs/tasks/YYYY-MM-DD-{feature_slug}-tasks.md"
generated_at: YYYY-MM-DD
spec_ready: false
blocked_by: []
---

# Issue Spec: AC-1 — {short_title}

## Acceptance

{Copy TDD Ch.6 인수조건 row verbatim — Given/When/Then}

**PRD:** [source:prd#…]

## Done when

- {Copy TDD 완료 판정 column — e.g. Test T-1 passes in CI}

## Tests

| Test ID | Layer | Scenario | Fixture / Mock | CI gate |
|---------|-------|----------|----------------|---------|
| T-1 | integration | … | … | yes |

## Behavior (in scope)

- Happy path: …
- Error branches (only if required by this AC): …

## Interfaces & code

- `{Component}.{method}` — `{path/to/file.ts}`
- …

## Implementation tasks

- [ ] TK-004 … proves T-1
- [ ] TK-005 … proves T-1

## Dependencies

```text
TK-004 blockedBy TK-003
```

## Out of scope

- AC-2, AC-3, …
- Ch.7 open questions not resolved for this AC

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | docs/design/YYYY-MM-DD-{feature_slug}-tdd.md |
| Tasks | docs/tasks/YYYY-MM-DD-{feature_slug}-tasks.md |
| Plan | _(after writing-plans)_ `docs/superpowers/plans/YYYY-MM-DD-{feature_slug}-AC-1.md` |
| Tracker | _(after register)_ GitHub #{n} / Jira PROJ-n |
```

## Required sections

| Section | Rule |
|---------|------|
| Frontmatter | `title`, `feature`, `ac_id`, `priority`, `tdd_source`, `tasks_source`, `generated_at`, `spec_ready` |
| Acceptance | Verifiable condition; prefer Given/When/Then |
| Done when | Objective pass/fail tied to test or manual step |
| Tests | ≥1 row for this `ac_id`; CI gate column present |
| Behavior (in scope) | ≥1 bullet |
| Interfaces & code | ≥1 path in backticks on implement-related scope |
| Implementation tasks | ≥1 `- [ ] TK-nnn` with `[AC-n]` or `proves T-n` |
| Out of scope | Names other AC IDs or deferred work |
| Open questions | `(none)` / `없음` when `spec_ready: true` |
| Traceability | TDD + Tasks paths |

## `spec_ready: true` gate

Set only when ALL hold:

1. `validate-issue-spec.py` exits `0` (with `--tdd` and `--tasks`)
2. No blocking Ch.7 item affects this AC
3. Human reviewed Acceptance / Done when / Tests
4. `blocked_by` issues or TK blockers are created or linked

## Non-AC issues (Setup / Foundation)

Use [infra-issue-spec-template.md](infra-issue-spec-template.md) when the deliverable is not tied to a single AC (migrations, flags, CI wiring).
