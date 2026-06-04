---
name: prd-to-tdd
description: >-
  Analyzes PRD (Markdown or Google Docs via gws) and the full codebase to write
  a forward-only Design Document (Google Design Doc 8 chapters, 기승전결 narrative).
  When dual-brain is installed, uses Enhanced path by default: Phase 2b analysis,
  Right Brain grill, Left Brain blueprint before draft, compact Left Brain review.
  Use for TDD, Design Doc, 기술설계서, or PRD path/URL plus design analysis.
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
| [dual-brain-integration.md](dual-brain-integration.md) | **Enhanced path** when dual-brain installed (2b, 3b, 3c, 6) |
| [examples.md](examples.md) | Tone samples (may lag new H2 names) |

## Checklist

```
PRD → Design Doc:
- [ ] Path: probe dual-brain/SKILL.md → Enhanced (default if found) | Standard
- [ ] Phase 1: PRD ingest
- [ ] Phase 2: Repo analysis + mode
- [ ] Phase 2b: Dual-brain analysis brief (Enhanced only)
- [ ] Phase 3: Outline (Ch.5–7 mapping, Tier-1 tags; use 2b brief)
- [ ] Phase 3b: Right Brain grill (Enhanced) or skip to 3b′ only
- [ ] Phase 3b′: User confirm Tier-1 forks (if needs-user-confirm)
- [ ] Phase 3c: Left Brain design blueprint (Enhanced only)
- [ ] Phase 4: Draft Ch.1–8 + appendices (follow 3c blueprint)
- [ ] Phase 5: validate-tdd.py (strict)
- [ ] Phase 5b: validate-tdd.py --narrative
- [ ] Phase 6: Mode B (Enhanced) or Mode A (Standard), ≤2 rounds
- [ ] Phase 7: Save + report path used; optional .dual-brain/MEMORY.md update
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

## Phase 2b — Dual-Brain Analysis (Enhanced path)

**Skip when** Standard path or user said `no dual-brain`.

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

## Phase 3b — Right Brain Grill (Enhanced path)

When dual-brain is installed, run **before** user confirmation — see [dual-brain-integration.md](dual-brain-integration.md) Phase 3b and [subagent-prompts.md](subagent-prompts.md) §8.

Refine outline from grill output; add `OQ-*` for unresolved items.

**Standard path:** skip spawn; go to Phase 3b′ when needed.

---

## Phase 3b′ — User Confirmation

When outline has `needs-user-confirm`: present forks (use Right Brain structured message if Enhanced), get pick, then Shape A `확정` in Ch.6. Defer → Shape B + Ch.8 Open Questions.

---

## Phase 3c — Left Brain Design Blueprint (Enhanced path)

After outline + 3b (+ 3b′ if applicable), spawn Left Brain — [subagent-prompts.md](subagent-prompts.md) §9.

Keep blueprint as Phase 4 scratchpad: Ch.5–7 skeleton (components, flow steps, API/AC/test tables, Ch.6 decision fields). **Do not start Phase 4 without blueprint on Enhanced path.**

---

## Phase 4 — Draft

1. Read [tdd-template.md](tdd-template.md), [design-sections.md](design-sections.md), [narrative-rules.md](narrative-rules.md)
2. **Enhanced:** expand [Phase 3c blueprint](dual-brain-integration.md) into prose; apply Analysis Brief lexicon and gaps
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

Probe dual-brain skill at run start ([dual-brain-integration.md](dual-brain-integration.md)).

| Path | Phase 6 |
|------|---------|
| **Enhanced** (dual-brain on disk; default) | **Mode B** — left-brain-verification (§4), then narrative (§1) if doubt |
| **Standard** | **Mode A** — §1–3 parallel |

User override: `standard reviewers` → Mode A even if dual-brain installed.

Max 2 rounds; then `validation_passed: true` or stop with Critical list.

---

## Phase 7 — Save & Stop

Report: path, **validation path** (Enhanced vs Standard), mode, Ch.6 forks, Ch.3 FR/OQ count, Ch.7 AC/test summary. If Enhanced: note whether 2b/3b/3c ran and any `.dual-brain/MEMORY.md` updates.

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
