---
name: prd-to-tdd
description: >-
  Analyzes PRD and codebase into a forward-only Google Design Doc (8 chapters).
  Paths: standard | enhanced | full — auto-selected from complexity after Phase 2
  unless user says standard/enhanced/full. full = dual-brain pre-draft + Left Brain
  then 3 parallel reviewers. Requires dual-brain skill for enhanced/full.
  Use for TDD, Design Doc, 기술설계서, or PRD path/URL.
---

# PRD → Design Doc (TDD)

Produces a **Design Document** (saved as `*-tdd.md` for pipeline compatibility). **Google Design Doc** is the chapter skeleton; **기승전결 + forward-only** govern prose.

No implementation plans, tasks, or code changes. No auto handoff to `writing-plans` or SDD.

**Recommended upstream:** **`prd-review`** on the PRD first.

## References

| File | When |
|------|------|
| [narrative-rules.md](narrative-rules.md) | Skeleton, narrative, forward-only |
| [tdd-template.md](tdd-template.md) | Before drafting |
| [design-sections.md](design-sections.md) | Ch.3, 5, 6, 7 depth |
| [outline-template.md](outline-template.md) | Phase 3 |
| [citation-tiers.md](citation-tiers.md) | Ch.6–7 citations |
| [subagent-prompts.md](subagent-prompts.md) | Phase 6 |
| [path-selection.md](path-selection.md) | **standard / enhanced / full** auto-pick + overrides |
| [dual-brain-integration.md](dual-brain-integration.md) | dual-brain phases 2b–3c and Phase 6 modes |
| [examples.md](examples.md) | Tone samples (may lag new H2 names) |

## Checklist

```
PRD → Design Doc:
- [ ] Step 0: User override? (standard | enhanced | full) — path-selection.md
- [ ] Phase 1: PRD ingest
- [ ] Phase 2: Repo analysis + mode
- [ ] Path pick: complexity_score → standard | enhanced | full (announce once)
- [ ] Phase 2b: Analysis brief (enhanced & full only)
- [ ] Phase 3: Outline
- [ ] Phase 3b: Right Brain grill (enhanced & full) | orchestrator-only (standard)
- [ ] Phase 3b′: User confirm Tier-1 forks (if any)
- [ ] Phase 3c: Left Brain blueprint (enhanced & full only)
- [ ] Phase 4: Draft Ch.1–8
- [ ] Phase 5–5b: validate-tdd.py strict + --narrative
- [ ] Phase 6: Mode A | B | C per path, ≤2 rounds
- [ ] Phase 7: Save; report path + score; optional MEMORY.md
- [ ] STOP
```

---

## Phase 1 — PRD Ingest

| Input | Action |
|-------|--------|
| Local `*.md` / `*.txt` | Read file |
| Google Docs URL | `gws-shared` + `gws-docs` |
| Unclear | Ask once |

Extract: `feature_slug`, title, requirements, PRD anchors. Classify **FR** / **NFR** / **constraint** / **OQ** (`FR-1`, `NFR-1`, `CON-1`, `OQ-1`).

---

## Phase 2 — Code Analysis + Mode

**Serena first**; full repo scope. Internal notes only: entry points, modules, data stores, `path:line`, test layout.

| Mode | Signals |
|------|---------|
| **greenfield** | Scaffold only or user says greenfield |
| **brownfield** | Domain code beyond boilerplate |

Frontmatter `mode`. Ch.4 title: **Existing Solution** (brownfield) or **Starting Point** (greenfield).

**Code-first:** PRD↔code conflict → code wins; label gap in **Ch.5**.

**Greenfield:** no fictional modules in Ch.4.

---

## Path Selection (after Phase 2)

Follow [path-selection.md](path-selection.md).

1. Apply **user override** if present (`full` / `enhanced` / `standard`).
2. If `dual-brain/SKILL.md` **missing** → **standard** only.
3. Else compute **complexity_score** from Phase 1–2 signals → auto map:
   - **≥ 8** → **full**
   - **4–7** → **enhanced**
   - **≤ 3** + trivial greenfield (no gaps, no forks) → **standard**
   - **≤ 3** + brownfield or any gap → **enhanced**
4. Tell user once: `prd-to-tdd path: … (score: N, reason: …)` before Phase 3.

Store in draft frontmatter when known: `prd_to_tdd_path`, `complexity_score`.

| Path | 2b / 3b / 3c | Phase 6 |
|------|----------------|---------|
| **standard** | Skip | Mode A — §1–3 parallel |
| **enhanced** | Run | Mode B — §4, optional §1 |
| **full** | Run | Mode C — §4 then §1–3 parallel, dedupe |

---

## Phase 2b — Dual-Brain Analysis (enhanced & full)

**Skip when** path is **standard**.

After Phase 2, run [dual-brain-integration.md](dual-brain-integration.md) Phase 2b:

1. Memory intake from `<target-repo>/.dual-brain/MEMORY.md` if present.
2. **Right Brain** then **Left Brain** (sequential) — prompts in [subagent-prompts.md](subagent-prompts.md) §6–7.
3. Produce an **Analysis Brief** (internal): gaps, lexicon, Tier-1 candidates, PRD blind spots, verified `path:line` facts.

Use the brief in Phase 3 outline and Phase 4 prose. Do not paste agent dialogue into the TDD.

---

## Phase 3 — Outline

Use [outline-template.md](outline-template.md). **Do not start Phase 4 until minimum rows met.**

1. Concept introduction order
2. Tier-1 topics for **Ch.6**, tagged `single` | `multi-recommend` | `needs-user-confirm`
3. Gap list (brownfield) or decision list (greenfield)
4. Requirements inventory → **Ch.3**
5. Mapping tables → **Ch.5–7** (components, APIs, entities, flow, AC, tests)

Phase 4 design prose order: **Ch.5 Proposed → Ch.6 Alternatives → Ch.7 Detailed**.

---

## Phase 3b — Right Brain Grill (enhanced & full)

When path is **enhanced** or **full**, run **before** user confirmation — [dual-brain-integration.md](dual-brain-integration.md), [subagent-prompts.md](subagent-prompts.md) §8.

**Standard path:** orchestrator-only outline check; go to Phase 3b′ when needed.

---

## Phase 3b′ — User Confirmation

When outline has `needs-user-confirm`: present forks (use Right Brain message on enhanced/full), get pick, then Shape A `확정` in Ch.6. Defer → Shape B + Ch.8 Open Questions.

---

## Phase 3c — Left Brain Design Blueprint (enhanced & full)

After outline + 3b (+ 3b′ if applicable), spawn Left Brain — [subagent-prompts.md](subagent-prompts.md) §9.

Keep blueprint as Phase 4 scratchpad. **Do not start Phase 4 on enhanced/full without blueprint.**

---

## Phase 4 — Draft

1. Read [tdd-template.md](tdd-template.md), [design-sections.md](design-sections.md), [narrative-rules.md](narrative-rules.md)
2. **enhanced/full:** expand Phase 3c blueprint; apply Analysis Brief lexicon and gaps
3. Write **Ch.1 → Ch.4** in order (Overview through Existing/Starting Point)
4. Write **Ch.5 → Ch.6 → Ch.7** (Proposed → Alternatives → Detailed)
5. Write **Ch.8** Rollout and Open Items
6. **Ch.3 Requirements:** FR/NFR/RTM after Ch.2 Background (Ch.2 has prose only)
7. **Ch.5:** gap prose, transition mermaid, Architecture / Components / Data Flow — **no** Decision Summary
8. **Ch.6:** intro links Ch.5; `### Decision Summary`; ADR cards ([citation-tiers.md](citation-tiers.md))
9. **Ch.7:** APIs, Data Model, Core Flow, AC, Tests; `[ref:A-n]` for Tier-2
10. Front matter: `## 목차` → `## How to Read This Doc` → `## 1. Overview`
11. Appendices A and B after Ch.8
12. Literal tilde: `\\~` in body text ([narrative-rules.md](narrative-rules.md))

Filename: `docs/design/YYYY-MM-DD-<feature_slug>-tdd.md`

---

## Phase 5 — Validation

```bash
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md --narrative
```

Both must exit `0` before Phase 6.

---

## Phase 6 — Subagent Review

Use path chosen in [path-selection.md](path-selection.md). See [subagent-prompts.md](subagent-prompts.md).

| Path | Phase 6 mode |
|------|----------------|
| **standard** | **A** — narrative + citation + code-grounding (parallel) |
| **enhanced** | **B** — left-brain (§4); narrative (§1) if doubt |
| **full** | **C** — left-brain (§4), then §1–3 parallel; dedupe findings |

Max 2 rounds; then `validation_passed: true` or stop with Critical list.

---

## Phase 7 — Save & Stop

Report: `prd_to_tdd_path`, `complexity_score`, mode, validation summary, Ch.6 forks, Ch.3 FR/OQ count, Ch.7 AC/test summary. Note 2b/3b/3c and Phase 6 mode (A/B/C). Optional `.dual-brain/MEMORY.md` updates on enhanced/full.

Optional next step (mention only): **`tdd-to-tasks`**.

**STOP** — no implementation unless asked.

---

## Quick Reference — 8 Chapters (Design Doc)

| # | Brownfield H2 | Greenfield H2 | 기승전결 |
|---|---------------|---------------|----------|
| 1 | Overview | Overview | 起 |
| 2 | Background | Background | 起→承 |
| 3 | Requirements | Requirements | 承 |
| 4 | Existing Solution | Starting Point | 承 |
| 5 | Proposed Solution | Proposed Solution | 转 |
| 6 | Alternatives Considered | Alternatives Considered | 转→结 |
| 7 | Detailed Design | Detailed Design | 结 |
| 8 | Rollout and Open Items | Rollout and Open Items | 结 |

---

## Integration

- **prd-review**, **gws-shared**, **gws-docs**, **Serena**, **dual-brain** (Enhanced path when installed — [dual-brain-integration.md](dual-brain-integration.md))
- Maintainer spec: `docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md` (historical; **SKILL.md** is source of truth)
