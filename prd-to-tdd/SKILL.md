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
| [citation-tiers.md](citation-tiers.md) | When writing Ch.4–5; attach to citation-reviewer |
| [tdd-template.md](tdd-template.md) | Before drafting |
| [subagent-prompts.md](subagent-prompts.md) | Phase 6 spawn |
| [examples.md](examples.md) | When unsure about tone or structure |

## Checklist

Copy and track:

```
PRD → TDD Progress:
- [ ] Phase 1: PRD ingest
- [ ] Phase 2: Full-repo analysis + mode (brownfield | greenfield)
- [ ] Phase 3: Outline (concept order, gaps/decisions)
- [ ] Phase 4: Draft TDD (5 chapters, in order)
- [ ] Phase 5: validate-tdd.py pass
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

Before prose, write an outline (user-visible or internal):

1. Concepts in **introduction order** (no use before define)
2. Tier-1 decision list for Ch.4
3. Brownfield: PRD↔code gap list | Greenfield: PRD→decision list

Self-check against [narrative-rules.md](narrative-rules.md) outline checklist.

---

## Phase 4 — Draft

1. Read [tdd-template.md](tdd-template.md)
2. Create `docs/design/` if missing
3. Write **one chapter at a time** in fixed order
4. Ch.4–5: use source blocks from [citation-tiers.md](citation-tiers.md)
5. Each subsection: **summary line** (PM) → technical detail (dev)

Filename: `docs/design/YYYY-MM-DD-<feature_slug>-tdd.md`

---

## Phase 5 — Script Validation

Run the validator from this skill package (repo: `skills/prd-to-tdd/`, installed: `~/.cursor/skills/prd-to-tdd/`):

```bash
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md
```

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
- Summary of Ch.4 key decisions
- Open questions from Ch.5

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

## Quick Reference — 5 Chapters

| # | Brownfield H2 | Greenfield H2 | 기승전결 |
|---|---------------|---------------|----------|
| 1 | 서문 | 서문 | 起 |
| 2 | 배경과 문제 | 배경과 문제 | 承 |
| 3 | 현재 시스템 | 시작점 | 承 |
| 4 | 갭과 설계 전환 | 설계 결정 | 转 |
| 5 | 목표 설계와 마무리 | 목표 설계와 마무리 | 结 |

---

## Integration

- **gws-shared** + **gws-docs** — Google Docs PRD
- **Serena** — code exploration before full file reads
- **Task tool** — subagent reviewers (Phase 6)

Design spec (maintainers): `docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md` at the root of the agent-skills git repository.
