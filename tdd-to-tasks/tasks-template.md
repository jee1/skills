# Tasks Template

Copy structure below. Replace `{placeholders}`. Task IDs: `TK-001` … Test IDs from TDD: `T-1` …

```markdown
---
title: "Tasks: {feature_title}"
feature: {feature_slug}
mode: brownfield | greenfield
tdd_source: "docs/design/YYYY-MM-DD-{feature_slug}-tdd.md"
prd_source: "{from TDD frontmatter}"
generated_at: YYYY-MM-DD
validation_passed: false
---

# Tasks: {feature_title}

> **Source TDD:** docs/design/YYYY-MM-DD-{feature_slug}-tdd.md
> **Done when:** all **Must** AC rows in TDD Ch.6 are satisfied; every Ch.6 test with **CI gate = yes** is green in CI

## 추적 매트릭스 (RTM)

| PRD | AC | Task IDs | Test IDs | Component / scope |
|-----|-----|----------|----------|---------------------|
| [source:prd#…] | AC-1 | TK-003, TK-004 | T-1 | PaymentGateway |
| [source:prd#…] | AC-2 | TK-005, TK-006 | T-2 | OrderService |

## Dependencies

```text
TK-004 blockedBy TK-003
TK-006 blockedBy TK-005
```

## Phase 0: Setup

- [ ] TK-001 Create feature branch and enable flag `{flag_name}` in staging config
- [ ] TK-002 [P] Add test fixtures for cancel flow in `{test_path}`

## Phase 1: Foundation

- [ ] TK-003 Migration `{migration_id}` add `{column}` to `{table}` in `{migration_path}`

## Phase 2: AC-1 — {short title from AC row}

- [ ] TK-004 [AC-1] Add integration test for {scenario} in `{test_path}` — proves T-1
- [ ] TK-005 [AC-1] Implement {component}.{method} in `{src_path}` — proves T-1

## Phase 3: AC-2 — {short title}

- [ ] TK-006 [AC-2] … — proves T-2

## Phase N: CI & docs

- [ ] TK-00N Wire CI job `{ci_command}` for T-1, T-2
```

## Required sections

| Section | Rule |
|---------|------|
| Frontmatter | `title`, `feature`, `mode`, `tdd_source`, `prd_source`, `generated_at`, `validation_passed` |
| Blockquote | Source TDD path + Done when |
| RTM | ≥1 row per **Must** AC from TDD |
| Dependencies | List sequential blocks (may be empty if none) |
| Phases | Phase 0 + Phase 1 + ≥1 AC phase |
| Tasks | `- [ ] TK-nnn` checklist lines only under phases |

## RTM rules

- **PRD** column: copy from TDD Ch.6 AC table `[source:prd#…]`
- **Task IDs**: every Must AC has ≥2 TK IDs (test + implement typical) unless user asked for minimal slice
- **Test IDs**: copy from TDD Ch.6; every CI gate `yes` test appears in ≥1 task line (`proves T-n`)
