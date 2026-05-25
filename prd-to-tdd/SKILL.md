---
name: prd-to-tdd
description: >-
  Analyzes PRD (Markdown or Google Docs via gws) and the full codebase to write
  a forward-only Technical Design Document (TDD) with 기승전결 narrative, tiered
  citations, and script + subagent validation. Use when the user asks for TDD,
  기술설계서, technical design from PRD, or PRD path/URL plus design analysis.
---

# PRD → TDD

Produces **Technical Design Document** only. No implementation plans, tasks, or code changes. No auto handoff to `writing-plans` or SDD.

## References (read when needed)

| File | When |
|------|------|
| [narrative-rules.md](narrative-rules.md) | Before outline and draft; attach to narrative-reviewer |
| [citation-tiers.md](citation-tiers.md) | When writing Ch.4–6; attach to citation-reviewer |
| [tdd-template.md](tdd-template.md) | Before drafting |
| [design-sections.md](design-sections.md) | Before drafting Ch.5–6 |
| [outline-template.md](outline-template.md) | Phase 3 — required Ch.5–6 mapping |
| [subagent-prompts.md](subagent-prompts.md) | Phase 6 spawn |
| [examples.md](examples.md) | When unsure about tone or structure |

## Checklist

Copy and track:

```
PRD → TDD Progress:
- [ ] Phase 1: PRD ingest
- [ ] Phase 2: Full-repo analysis + mode (brownfield | greenfield)
- [ ] Phase 3: Outline (concept order, gaps/decisions, Tier-1 tags)
- [ ] Phase 3b: User confirm Tier-1 forks (if any `needs-user-confirm`)
- [ ] Phase 4: Draft TDD (7 chapters + appendices, in order)
- [ ] Phase 5: validate-tdd.py pass (strict)
- [ ] Phase 5b: validate-tdd.py --readability pass
- [ ] Phase 6: 3 subagents parallel, no Critical (≤2 rounds)
- [ ] Phase 7: Save docs/design/YYYY-MM-DD-<feature>-tdd.md
- [ ] STOP — do not start implementation
```

---

## Phase 1 — PRD Ingest

Detect input automatically:

| Input | Action |
|-------|--------|
| Local `*.md` / `*.txt` path | Read file |
| Google Docs URL (`docs.google.com/document/`) | Read `~/.agents/skills/gws-shared/SKILL.md`, then `gws docs documents get` per `gws-docs` |
| Unclear | Ask user once |

Extract: `feature_slug`, title, requirements, constraints, PRD section anchors for citations.

**Stop if:** empty PRD or gws auth failure (point user to gws-shared).

---

## Phase 2 — Code Analysis + Mode

**Tools:** Serena first (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`); full repo scope.

Build internal **analysis notes** (do not save as TDD): entry points, modules, data stores, integrations, `path:line` refs.

### Mode detection

| Mode | Signals |
|------|---------|
| **greenfield** | No domain code; scaffold only (`package.json`, empty `src/`, CI, README); or user says greenfield |
| **brownfield** | Business logic / services / models beyond boilerplate |

Set frontmatter `mode` accordingly. See design spec for Ch.3/Ch.4 title variants in [tdd-template.md](tdd-template.md).

**Code-first (brownfield):** on PRD↔code conflict, code wins; label gap in Ch.4.

**Greenfield:** PRD + stack constraints (README, deps) are ground truth; never invent modules in Ch.3.

---

## Phase 3 — Outline

Before prose, write an outline using [outline-template.md](outline-template.md) (user-visible or internal). **Do not start Phase 4 until minimum row counts are met.**

1. Concepts in **introduction order** (no use before define)
2. Tier-1 topics for Ch.4, each tagged:
   - `single` — one clear choice → use `> **결정:**`
   - `multi-recommend` — real fork → use `> **갈림:**` + `> **권장:**` + `> **상태:** 권장(미확정)`
   - `needs-user-confirm` — Tier-1 high impact → **ask user before Ch.4** (see below)
3. Brownfield: PRD↔code gap list | Greenfield: PRD→decision list
4. **Ch.5–6 mapping tables (required):**
   - Components (≥2 names, 신규/기존 for brownfield)
   - APIs/events (≥1 per user-facing action)
   - Entities (≥1 per persisted object, field names listed)
   - Primary flow (≥5 steps) + error branches (≥2)

Self-check against [narrative-rules.md](narrative-rules.md) outline checklist and [design-sections.md](design-sections.md) depth rubric.

---

## Phase 3b — User Confirmation (Tier-1 forks only)

**When:** outline has any `needs-user-confirm` item (auth, datastore, breaking API, major dependency contract, balanced trade-offs with no code/PRD tiebreaker).

**How:** One message per fork (or one message listing all forks). For each:

- Topic name
- 2–3 **대안** with one-line trade-off each
- **권장** + short rationale
- Ask user to pick or confirm recommendation

**Do not** draft Ch.4–5 for that topic until answered. After answer, tag as `single` and use `> **결정:**` + `> **상태:** 확정`.

If user defers (“나중에”), keep `> **갈림:**` + `> **상태:** 권장(미확정)` and add Ch.7 **열린 질문**.

---

## Phase 4 — Draft

1. Read [tdd-template.md](tdd-template.md), [design-sections.md](design-sections.md), [narrative-rules.md](narrative-rules.md)
2. Create `docs/design/` if missing
3. Write **one chapter at a time** in fixed order (1 → 7)
4. **Expand every Phase 3 outline row** into ≥1 sentence or table row in the mapped ### subsection — no orphan rows, no empty subsections
5. Ch.4: `**결정:**` or `**갈림:**` blocks from [citation-tiers.md](citation-tiers.md)
6. Ch.5 **상위설계**: all three ### subsections; meet [design-sections.md](design-sections.md) depth rubric (요약, ≥2 components, ≥3 flow steps)
7. Ch.6 **상세설계**: `### 스펙 인덱스` first; API field + error tables, entity field table, ≥2 error branches; every Ch.5 component name referenced; `[ref:A-n]` not inline blockquotes
8. Ch.7 **마무리**: rollout, risks table, 열린 질문 (for each Ch.4 `권장(미확정)`)
9. Ch.1: TL;DR, Goals/Non-Goals, reader path table, TOC (see [tdd-template.md](tdd-template.md))
10. Ch.4: `### 결정 요약` table
11. Ch.5: mermaid in ### 아키텍처 개요; `#### 한눈에` (3 bullets) after each Ch.5 ###
12. Write ## 부록 A and ## 부록 B after Ch.7
13. Each subsection: **요약:** (PM) → technical detail (dev) → `[ref:A-n]` for Tier-2 (Appendix A)

Filename: `docs/design/YYYY-MM-DD-<feature_slug>-tdd.md`

---

## Phase 5 — Script Validation

Run the validator from this skill package (repo: `skills/prd-to-tdd/`, installed: `~/.cursor/skills/prd-to-tdd/`):

```bash
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md --readability
```

Default is **strict** (Ch.5–6 depth rubric). Legacy drafts: add `--lenient` to skip depth checks. **Both commands** must exit `0` before Phase 6.

Use the path to `validate-tdd.py` inside the skill directory. `<feature>-tdd.md` lives in the **target project** under `docs/design/`.

- Exit `0` → Phase 6
- Exit `1` → fix reported lines, re-run
- Do not spawn subagents until script passes

---

## Phase 6 — Subagent Validation

Read [subagent-prompts.md](subagent-prompts.md). Spawn **three Task agents in parallel**:

1. **narrative-reviewer** — `generalPurpose`, readonly
2. **citation-reviewer** — `generalPurpose`, readonly
3. **code-grounding-reviewer** — `cavecrew-reviewer` or `generalPurpose`, readonly

Merge findings. **Critical** → edit TDD → Phase 5 → Phase 6 again.

- Increment frontmatter `review_rounds` each full cycle
- Max **2** cycles; then set `validation_passed: false`, save, show unresolved Critical list to user
- If clean: `validation_passed: true`

---

## Phase 7 — Save & Stop

Confirm file at `docs/design/YYYY-MM-DD-<feature>-tdd.md`.

Tell user:
- Path, mode, validation status, review rounds
- Ch.4: **확정** vs **권장(미확정)** forks
- Ch.5–6: one-line summary of architecture + key APIs
- Open questions from Ch.7

**STOP.** Do not offer implementation, tasks, or `writing-plans` unless user asks separately.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Huge repo | Prioritize PRD-keyword modules; note scope limit in Ch.1 |
| PRD/code irreconcilable | Code-first; list in Ch.4 |
| 2 failed validation rounds | Save draft, `validation_passed: false` |
| User wants Google Docs output | Out of scope (Markdown only) |

---

## Quick Reference — 7 Chapters

| # | Brownfield H2 | Greenfield H2 | 기승전결 |
|---|---------------|---------------|----------|
| 1 | 서문 | 서문 | 起 |
| 2 | 배경과 문제 | 배경과 문제 | 承 |
| 3 | 현재 시스템 | 시작점 | 承 |
| 4 | 갭과 설계 전환 | 설계 결정 | 转 |
| 5 | 상위설계 | 상위설계 | 结 |
| 6 | 상세설계 | 상세설계 | 结 |
| 7 | 마무리 | 마무리 | 结 |

Ch.5–6 subsection requirements: [design-sections.md](design-sections.md).

---

## Integration

- **gws-shared** + **gws-docs** — Google Docs PRD
- **Serena** — code exploration before full file reads
- **Task tool** — subagent reviewers (Phase 6)

Design spec (maintainers): `docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md` at the root of the agent-skills git repository.
