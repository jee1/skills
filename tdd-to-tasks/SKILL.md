---
name: tdd-to-tasks
description: >-
  Decomposes a validated prd-to-tdd Technical Design Document (Ch.6 AC + tests,
  APIs, entities, flows) into an implementation task checklist with RTM traceability.
  Use when the user asks for tasks, implementation breakdown, or work items after
  TDD, or gives a path to docs/design/*-tdd.md plus task derivation.
---

# TDD → Tasks

Produces **implementation task checklist** only. No code changes. No auto handoff to `executing-plans` unless user asks separately.

**Prerequisite:** Source TDD must pass `prd-to-tdd` validation (`validate-tdd.py` exit `0`, strict + `--narrative` preferred).

## References (read when needed)

| File | When |
|------|------|
| [tasks-template.md](tasks-template.md) | Before drafting |
| [decomposition-rules.md](decomposition-rules.md) | Phase 2 decomposition |
| [examples.md](examples.md) | When unsure about granularity or RTM |

## Checklist

```
TDD → Tasks Progress:
- [ ] Phase 1: Load TDD + run validate-tdd.py (must pass)
- [ ] Phase 2: Extract Ch.5–6 inventory (components, API, entities, flow, AC, tests)
- [ ] Phase 3: Draft tasks.md (Phases + RTM + Dependencies)
- [ ] Phase 4: validate-tasks.py pass (--tdd for cross-check)
- [ ] Phase 5: Save docs/tasks/YYYY-MM-DD-<feature>-tasks.md
- [ ] STOP — do not start implementation
```

---

## Phase 1 — TDD Ingest

| Input | Action |
|-------|--------|
| Path `docs/design/YYYY-MM-DD-<feature>-tdd.md` | Read file |
| User names feature only | Glob `docs/design/*-<feature>-tdd.md`; ask if ambiguous |
| No TDD | Stop — run `prd-to-tdd` first |

Run validator from **prd-to-tdd** skill package:

```bash
python ../prd-to-tdd/scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md
python ../prd-to-tdd/scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md --narrative
```

(When installed: `python ~/.cursor/skills/prd-to-tdd/scripts/validate-tdd.py …`)

**Stop if:** validator exit `1`, missing Ch.6 `### 인수조건` / `### 테스트`, or `validation_passed: false` without user override.

Extract from TDD frontmatter: `feature`, `mode`, `title`, `prd_source`. Copy `generated_at` date for tasks filename.

---

## Phase 2 — Decompose

Read [decomposition-rules.md](decomposition-rules.md). Build an internal inventory (user-visible outline optional):

1. **Ch.5 components** — names + (신규|기존)
2. **Ch.6 API rows** — endpoints, error codes
3. **Ch.6 entities** — tables, migrations
4. **Ch.6 flow** — happy path steps + error branches
5. **Ch.6 인수조건** — AC ID, priority (Must/Should), 완료 판정
6. **Ch.6 테스트** — Test ID, AC ID, layer, CI gate

### Phase layout (required)

| Phase | Contents |
|-------|----------|
| **Phase 0: Setup** | branch, flags, config, test harness if greenfield |
| **Phase 1: Foundation** | migrations, shared types, interfaces blocking all AC |
| **Phase 2+** | **One phase per Must AC** (name: `AC-n — short title`) |
| **Phase N: Should AC** | Should-priority ACs (if any) |
| **Phase N+1: CI & docs** | CI wiring, README/runbook if needed |

Within each AC phase, order tasks:

1. Write test (when Ch.6 CI gate = `yes` for linked T-n)
2. Implement (file paths from TDD code refs + Ch.6)
3. Wire / integrate

**Task ID:** `TK-001`, `TK-002`, … (never reuse Ch.6 test IDs `T-1`, `T-2`).

**Task line format:**

```markdown
- [ ] TK-003 [P] [AC-1] Implement PaymentGateway.refund in `src/payments/gateway.ts` — proves T-1
```

| Token | Meaning |
|-------|---------|
| `[P]` | Parallel-safe (no unfinished dependency) |
| `[AC-n]` | ≥1 AC per implementation task |
| `` `path` `` | Required on implement/wire tasks (not on pure test scaffold) |
| `proves T-n` | Links to Ch.6 test row |

---

## Phase 3 — Draft

1. Read [tasks-template.md](tasks-template.md)
2. Create `docs/tasks/` if missing
3. Fill **추적 매트릭스 (RTM)**: every Must AC row → Task IDs + Test IDs
4. Fill **Dependencies**: `TK-004 blockedBy TK-003` for sequential work
5. **Done when** block: all Must AC satisfied; CI-gated tests green

Filename: `docs/tasks/YYYY-MM-DD-<feature_slug>-tasks.md` (same date slug as source TDD).

---

## Phase 4 — Script Validation

From this skill package:

```bash
python scripts/validate-tasks.py docs/tasks/YYYY-MM-DD-<feature>-tasks.md \
  --tdd docs/design/YYYY-MM-DD-<feature>-tdd.md
```

- Exit `0` → Phase 5
- Exit `1` → fix, re-run
- `--tdd` cross-checks AC/Test coverage against Ch.6 (recommended)

---

## Phase 5 — Save & STOP

Tell user:

- Path to `tasks.md` and source TDD path
- Must AC count vs Task count; CI-gated test count
- Phase order summary (Foundation → AC phases)
- Optional next steps (**only if user asks**): `tasks-to-issues` (Issue Spec + tracker), `writing-plans`, `executing-plans`

**STOP.** Do not implement or create PRs.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| TDD lacks AC/test tables | Stop — extend TDD via `prd-to-tdd` Phase 4 gate |
| Ch.4 `권장(미확정)` forks | Add tasks prefixed `[blocked]` or note in Dependencies until Ch.7 resolved |
| Huge feature | Split tasks.md by bounded context; one RTM per file; note in frontmatter |

---

## Integration

- **prd-to-tdd** — upstream TDD + `validate-tdd.py`
- **Serena** — verify `path` targets exist (brownfield) before marking paths in tasks
- **tasks-to-issues** — Issue Spec + GitHub/Jira/Paperclip (user-initiated only)
- **executing-plans** / **writing-plans** — downstream after Issue Spec + plan (user-initiated only)
