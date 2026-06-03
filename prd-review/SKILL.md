---
name: prd-review
description: >-
  Reviews a PRD for ambiguity, internal contradictions, missing acceptance
  criteria, and TDD-readiness before prd-to-tdd. Produces a structured review
  report with FR/NFR/OQ draft inventory and a readiness gate. Optional dual-brain
  (Right=assumptions/gaps, Left=consistency/testability). Use when the user asks
  to review a PRD, find ambiguous or conflicting requirements, PRD quality gate,
  or "PRD 검토" / "모호성" / "상충" before technical design.
---

# PRD Review (TDD-readiness gate)

Makes the PRD clear enough that `prd-to-tdd` can classify requirements, trace PRD anchors, and avoid inventing `OQ-*` during TDD drafting.

**Does NOT:** Write TDD, implementation plans, or tasks. **Does NOT** replace `idea2planning` authoring.

**Pipeline:** `idea2planning` → **prd-review** → `prd-to-tdd` → `tdd-to-tasks`

## References

| File | When |
|------|------|
| [review-taxonomy.md](review-taxonomy.md) | Phase 2 coverage scan |
| [report-template.md](report-template.md) | Phase 5 report |
| [dual-brain-integration.md](dual-brain-integration.md) | Phase 3b if dual-brain installed |
| [subagent-prompts.md](subagent-prompts.md) | Phase 3b Mode B |
| `~/.agents/skills/gws-shared/SKILL.md` | Google Docs PRD ingest |

## Checklist

```
PRD Review Progress:
- [ ] Phase 1: PRD ingest + feature_slug
- [ ] Phase 2: Taxonomy coverage map (Clear / Partial / Missing)
- [ ] Phase 3: Findings inventory (AMB / CTR / CMP / TST / TRM / SCP)
- [ ] Phase 3b: dual-brain Right→Left (optional)
- [ ] Phase 4: Draft FR/NFR/OQ pre-inventory for prd-to-tdd
- [ ] Phase 5: Write review report + readiness gate
- [ ] Phase 5b: validate-prd-review.py pass (if report written)
- [ ] Phase 6 (optional): Clarification loop (≤5 questions)
- [ ] STOP — suggest prd-to-tdd only if gate ≠ blocked
```

---

## Phase 1 — PRD Ingest

Same input rules as `prd-to-tdd` Phase 1:

| Input | Action |
|-------|--------|
| Local `*.md` / `*.txt` | Read file |
| Google Docs URL (`docs.google.com/document/`) | Read `gws-shared`, then `gws docs` per `gws-docs` |
| Unclear | Ask user once |

Extract: `feature_slug`, title, section headings for `[source:prd#Section]` anchors, word count.

**Stop if:** empty PRD or gws auth failure.

**Early warning:** If PRD is outline-only (<300 words, no acceptance criteria, no user flows) → set gate `blocked` in Phase 5 and recommend completing PRD via `idea2planning` before re-review.

---

## Phase 2 — Coverage Scan

Load [review-taxonomy.md](review-taxonomy.md). For each category mark **Clear / Partial / Missing**.

Prioritize categories that block `prd-to-tdd`:

- Functional scope & measurable success
- User flows (happy + error)
- Acceptance criteria testability
- NFR with targets (not "fast", "stable")
- Edge cases & failure handling
- Explicit out-of-scope
- Terminology consistency

Keep an internal coverage map; surface it in the Phase 5 report § Coverage map.

---

## Phase 3 — Structured Findings

Classify every issue with stable IDs:

| ID prefix | Meaning | Typical severity |
|-----------|---------|------------------|
| `AMB-n` | Ambiguity (multiple interpretations) | High if Must-path |
| `CTR-n` | Contradiction between PRD sections | Critical |
| `CMP-n` | Completeness (missing flow, edge, actor) | High |
| `TST-n` | Untestable requirement | High |
| `TRM-n` | Terminology drift | Medium |
| `SCP-n` | Scope unclear (in/out) | High |

**Required finding line format:**

```text
severity | prd-anchor | ID | issue | suggested_fix
```

Severity: `Critical` | `High` | `Medium` | `Low`.

### Scans (non-exhaustive)

**Vague words** (flag unless quantified in the same sentence): 빠르게, 직관적, 적절히, 필요시, 가능하면, 대략, seamless, robust, user-friendly, ASAP, improve, optimize, better, simple, fast, stable.

**Contradictions:** same entity with conflicting rules; scope both "must" and "never"; inconsistent dates, roles, or limits.

**Testability:** no pass/fail condition; AC buried in prose without Given/When/Then or measurable outcome.

**Scope:** feature goals without explicit Non-Goals / Out of scope list.

---

## Phase 3b — Dual-Brain (optional)

Probe in order; first existing path wins:

1. `~/.cursor/skills/dual-brain/SKILL.md`
2. `~/.codex/skills/dual-brain/SKILL.md`
3. `~/.agents/skills/dual-brain/SKILL.md`

| Installed | Action |
|-----------|--------|
| Yes | Follow [dual-brain-integration.md](dual-brain-integration.md) — Right Brain then Left Brain, sequential |
| No | Orchestrator completes Phase 3; note `dual_brain_used: false` in report |

Map dual-brain prose to the finding line format before Phase 5.

Max **one** mediation round if Right and Left refute a core premise.

---

## Phase 4 — Pre-inventory (handoff to prd-to-tdd)

Draft tables for report § Pre-inventory (do not invent requirements absent from PRD):

- `FR-1..n` with `[source:prd#…]`, priority Must/Should, one-line **shall**
- `NFR-*` with measurable target or link to `TST-*` if missing
- `OQ-*` for unresolved `AMB`/`CTR`/`CMP` (types: 모호 | 상충 | 미결)
- Tag items that would become `needs-user-confirm` in `prd-to-tdd` Phase 3 outline

Optional RTM draft: PRD anchor → REQ ID → AC TBD.

---

## Phase 5 — Report + Readiness Gate

1. Create `docs/reviews/` in the **target project** if missing.
2. Write `docs/reviews/YYYY-MM-DD-<feature_slug>-prd-review.md` using [report-template.md](report-template.md).
3. Set frontmatter `readiness` per gate table below.

### Readiness gate

| Gate | Condition |
|------|-----------|
| **ready** | No `Critical`; no unresolved `CTR-*`; every **Must** FR has a testable acceptance path; taxonomy categories AC/scope/primary flow are not `Missing` |
| **needs-clarification** | No `Critical`; only `High`/`Medium`/`Low` remain; `OQ-*` listed with suggested answers |
| **blocked** | Any `Critical`; or ≥1 unresolved `CTR-*`; or any Must FR untestable; or primary user flow `Missing`; or outline-only PRD |

Frontmatter keys: `feature`, `prd_source`, `reviewed_at`, `readiness`, `finding_counts`, `dual_brain_used`.

Tell user:

- Gate status and whether to run `prd-to-tdd`
- Top 3 blockers if not `ready`
- Path to review report

**STOP** after Phase 5 unless user requests Phase 6.

---

## Phase 5b — Script Validation (recommended)

From this skill package (symlink: `~/.cursor/skills/prd-review/`):

```bash
python scripts/validate-prd-review.py docs/reviews/YYYY-MM-DD-<feature>-prd-review.md
```

Run in the **target project**; path is to the review file under `docs/reviews/`.

- Exit `0` → done
- Exit `1` → fix reported lines, re-run

---

## Phase 6 — Clarification Loop (optional)

Only if user wants PRD fixes **in this session**.

- Max **5** questions (one at a time; recommended option first — same spirit as `speckit-clarify`)
- After each answer: patch PRD only with user approval; log under `## Clarifications` in PRD or review report
- Re-run Phase 3–5 on changed sections; update gate

If user defers: keep `needs-clarification`; pass `OQ-*` to `prd-to-tdd` Ch.7.

---

## Integration

| Skill | Relationship |
|-------|----------------|
| **prd-to-tdd** | Run when gate is `ready`, or user accepts risk with documented `OQ-*` |
| **speckit-clarify** | Interactive rewrites; run **prd-review** first for full audit + gate |
| **ce-doc-review** | Broader brainstorm/plan docs; **prd-review** is PRD-specific |
| **dual-brain** | Optional; not a dependency |
| **idea2planning** | Author PRD before review if outline-only |

## Error Handling

| Situation | Action |
|-----------|--------|
| PRD outline-only | `blocked` + recommend `idea2planning` |
| dual-brain missing | Mode A orchestrator-only; not an error |
| User skips review | Warn: `prd-to-tdd` will multiply `OQ-*` and Phase 3b forks |
| User forces `prd-to-tdd` on `blocked` | Proceed only if user explicitly accepts risk; list blockers once |

---

## Quick Reference — Finding → Gate

| Finding | Blocks `ready`? |
|---------|-----------------|
| `CTR-*` unresolved | Yes → `blocked` |
| `Critical` severity | Yes → `blocked` |
| Must FR + `TST-*` | Yes → `blocked` |
| `AMB-*` only, with `OQ-*` | `needs-clarification` |
| `TRM-*` / `Low` only | May still be `ready` if Must paths testable |
