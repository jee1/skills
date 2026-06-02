---
name: tasks-to-issues
description: >-
  Draft per-AC Issue Specs from validated tasks.md + TDD, validate spec_ready,
  then register GitHub/Jira/Paperclip issues for plan/implement handoff.
  Use after tdd-to-tasks, or when user asks to create issues from tasks/TDD
  with confirmed execution specs.
---

# Tasks → Issue Specs → Tracker Issues

Produces **Issue Spec** documents and (optionally) tracker issues. No implementation code unless user asks separately.

**Prerequisite chain:**

1. TDD passes `prd-to-tdd` → `validate-tdd.py`
2. Tasks pass `tdd-to-tasks` → `validate-tasks.py --tdd`

## References

| File | When |
|------|------|
| [issue-spec-template.md](issue-spec-template.md) | Per-AC Story spec |
| [infra-issue-spec-template.md](infra-issue-spec-template.md) | Setup/Foundation |
| [issue-spec-rules.md](issue-spec-rules.md) | Slicing + registration order |

## Checklist

```
Tasks → Issues Progress:
- [ ] Phase 1: Confirm tasks.md + TDD validators pass
- [ ] Phase 2: generate-issue-specs.py (draft, spec_ready: false)
- [ ] Phase 3: Human fills Behavior + Interfaces; resolve Open questions
- [ ] Phase 4: validate-issue-spec.py --tdd --tasks (exit 0)
- [ ] Phase 5: Set spec_ready: true in frontmatter; re-validate
- [ ] Phase 6: Register tracker issues (dry-run list → user approval → gh/Jira)
- [ ] STOP — Plan/Implement only when user asks (writing-plans / executing-plans)
```

---

## Phase 1 — Prerequisites

```bash
python ../prd-to-tdd/scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md
python ../tdd-to-tasks/scripts/validate-tasks.py docs/tasks/YYYY-MM-DD-<feature>-tasks.md \
  --tdd docs/design/YYYY-MM-DD-<feature>-tdd.md
```

**Stop if** either validator exits `1`.

---

## Phase 2 — Draft Issue Specs

From this skill package:

```bash
python scripts/generate-issue-specs.py docs/tasks/YYYY-MM-DD-<feature>-tasks.md \
  --tdd docs/design/YYYY-MM-DD-<feature>-tdd.md \
  --output-dir docs/issues \
  --foundation
```

Options:

- `--include-should` — also emit Should-priority AC specs
- `--dry-run` — print paths only

Output: `docs/issues/YYYY-MM-DD-<feature>-AC-n-spec.md` (+ optional `…-foundation-spec.md`).

---

## Phase 3 — Human completion

Before `spec_ready: true`, edit each spec:

1. **Behavior (in scope)** — slice TDD Ch.6 flow/errors for this AC only
2. **Interfaces & code** — paths from TDD + tasks backticks
3. **Open questions** — `(none)` / `없음` only when Ch.7 does not block this AC
4. **Dependencies** — align with tasks.md `blockedBy`

---

## Phase 4 — Validate

```bash
python scripts/validate-issue-spec.py docs/issues/YYYY-MM-DD-<feature>-AC-1-spec.md \
  --tdd docs/design/YYYY-MM-DD-<feature>-tdd.md \
  --tasks docs/tasks/YYYY-MM-DD-<feature>-tasks.md
```

Repeat per spec file (or loop in shell). Exit `0` required.

---

## Phase 5 — spec_ready

Set frontmatter `spec_ready: true` only after Phase 4 passes and human sign-off.

Re-run validator (catches open questions when `spec_ready: true`).

---

## Phase 6 — Register tracker issues

**Do not create issues until Phase 5 is done.**

### Dry-run (required)

Present a table:

| Type | Title | Spec path | Blocked by |
|------|-------|-----------|------------|
| Epic | Feature: … | TDD + tasks links | — |
| Story | [AC-1] … | `docs/issues/…-AC-1-spec.md` | foundation # / TK-003 |
| Infra | Foundation | `…-foundation-spec.md` | — |

Get user approval.

### GitHub (example)

```bash
gh issue create --title "[AC-1] paid cancel refund and inventory release" \
  --label "spec-ready,ac/AC-1,feature/order-cancel-api" \
  --body "$(cat <<'EOF'
## Spec
- Issue spec: `docs/issues/2026-05-25-order-cancel-api-AC-1-spec.md` (spec_ready: true)
- TDD: `docs/design/2026-05-25-sample-order-cancel-tdd.md`
- Tasks: `docs/tasks/2026-05-25-sample-order-cancel-tasks.md`

## Done when
Test T-1 passes in CI
EOF
)"
```

**Safety:** Only create issues in the repo matching `git remote origin` (same rule as speckit-taskstoissues).

### Jira

- Epic = `feature`
- Story = AC spec (`ac_id` in custom field or labels)
- Link `blocks` from Dependencies / `blocked_by`

### Paperclip

Use `blockedByIssueIds` for graph edges; assign by specialty per `paperclip-converting-plans-to-tasks`.

---

## Downstream (user-initiated only)

| Step | Skill | Input |
|------|-------|-------|
| Plan | `writing-plans` | One Issue Spec + its TK list |
| Implement | `executing-plans` | `docs/superpowers/plans/…-AC-n-plan.md` |

Record plan path in spec **Traceability** table after plan is written.

---

## Error handling

| Situation | Action |
|-----------|--------|
| TDD Ch.7 blocks AC | Keep `spec_ready: false`; note in Open questions |
| TK mismatch | Fix tasks.md or spec Implementation tasks; re-validate |
| No Must AC in TDD | Stop — fix TDD via prd-to-tdd |

---

## Integration

- **tdd-to-tasks** — upstream tasks + RTM
- **prd-to-tdd** — upstream TDD
- **writing-plans** / **executing-plans** — downstream per issue
- **speckit-taskstoissues** — different path layout (`specs/`); prefer this skill for `docs/tasks/`
