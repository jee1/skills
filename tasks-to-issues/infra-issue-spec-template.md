# Infra Issue Spec Template

For **Phase 0: Setup** and **Phase 1: Foundation** (no single AC). Filename:
`docs/issues/YYYY-MM-DD-<feature_slug>-foundation-spec.md`

```markdown
---
title: "Issue Spec: Foundation — {feature_title}"
feature: {feature_slug}
ac_id: none
priority: infra
tdd_source: "docs/design/YYYY-MM-DD-{feature_slug}-tdd.md"
tasks_source: "docs/tasks/YYYY-MM-DD-{feature_slug}-tasks.md"
generated_at: YYYY-MM-DD
spec_ready: false
blocked_by: []
---

# Issue Spec: Foundation — {feature_title}

## Goal

Enable AC implementation phases (migrations, flags, fixtures, shared types).

## Done when

- All Foundation-phase TK lines in tasks.md are checked
- AC phases are unblocked per Dependencies in tasks.md

## Implementation tasks

- [ ] TK-001 …
- [ ] TK-002 …
- [ ] TK-003 …

## Dependencies

```text
(none) or TK-003 blockedBy TK-002
```

## Out of scope

- AC-1, AC-2, … (handled in per-AC issue specs)

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | docs/design/…-tdd.md |
| Tasks | docs/tasks/…-tasks.md |
```
