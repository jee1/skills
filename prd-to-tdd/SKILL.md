---
name: prd-to-tdd
description: >-
  Analyzes PRD (Markdown or Google Docs via gws) and the full codebase to write
  a forward-only Design Document using the Google Design Doc skeleton (8 chapters),
  with 기승전결 narrative, tiered citations, and script + subagent validation.
  Use when the user asks for TDD, Design Doc, 기술설계서, or PRD path/URL plus design analysis.
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
| [dual-brain-integration.md](dual-brain-integration.md) | Optional 3b / 6 |
| [examples.md](examples.md) | Tone samples (may lag new H2 names) |

## Checklist

```
PRD → Design Doc:
- [ ] Phase 1: PRD ingest
- [ ] Phase 2: Repo analysis + mode
- [ ] Phase 3: Outline (Ch.5–7 mapping, Tier-1 tags)
- [ ] Phase 3b: User confirm Tier-1 forks (if any)
- [ ] Phase 4: Draft Ch.1–8 + appendices
- [ ] Phase 5: validate-tdd.py (strict)
- [ ] Phase 5b: validate-tdd.py --narrative
- [ ] Phase 6: Subagent review (≤2 rounds)
- [ ] Phase 7: Save docs/design/YYYY-MM-DD-<feature>-tdd.md
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

## Phase 3 — Outline

Use [outline-template.md](outline-template.md). **Do not start Phase 4 until minimum rows met.**

1. Concept introduction order
2. Tier-1 topics for **Ch.6**, tagged `single` | `multi-recommend` | `needs-user-confirm`
3. Gap list (brownfield) or decision list (greenfield)
4. Requirements inventory → **Ch.3**
5. Mapping tables → **Ch.5–7** (components, APIs, entities, flow, AC, tests)

Phase 4 design prose order: **Ch.5 Proposed → Ch.6 Alternatives → Ch.7 Detailed**.

---

## Phase 3b — User Confirmation

When outline has `needs-user-confirm`: present forks, get pick, then Shape A `확정` in Ch.6. Defer → Shape B + Ch.8 Open Questions.

Optional Right Brain: [dual-brain-integration.md](dual-brain-integration.md).

---

## Phase 4 — Draft

1. Read [tdd-template.md](tdd-template.md), [design-sections.md](design-sections.md), [narrative-rules.md](narrative-rules.md)
2. Write **Ch.1 → Ch.4** in order (Overview through Existing/Starting Point)
3. Write **Ch.5 → Ch.6 → Ch.7** (Proposed → Alternatives → Detailed)
4. Write **Ch.8** Rollout and Open Items
5. **Ch.3 Requirements:** FR/NFR/RTM after Ch.2 Background (Ch.2 has prose only)
6. **Ch.5:** gap prose, transition mermaid, Architecture / Components / Data Flow — **no** Decision Summary
7. **Ch.6:** intro links Ch.5; `### Decision Summary`; ADR cards ([citation-tiers.md](citation-tiers.md))
8. **Ch.7:** APIs, Data Model, Core Flow, AC, Tests; `[ref:A-n]` for Tier-2
9. Front matter: `## 목차` → `## How to Read This Doc` → `## 1. Overview`
10. Appendices A and B after Ch.8
11. Literal tilde: `\\~` in body text ([narrative-rules.md](narrative-rules.md))

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

See [subagent-prompts.md](subagent-prompts.md). Mode A: narrative + citation + code-grounding (parallel). Mode B: dual-brain compact.

Max 2 rounds; then `validation_passed: true` or stop with Critical list.

---

## Phase 7 — Save & Stop

Report: path, mode, validation, Ch.6 forks, Ch.3 FR/OQ count, Ch.7 AC/test summary.

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

- **prd-review**, **gws-shared**, **gws-docs**, **Serena**, **dual-brain** (optional)
- Maintainer spec: `docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md` (historical; **SKILL.md** is source of truth)
