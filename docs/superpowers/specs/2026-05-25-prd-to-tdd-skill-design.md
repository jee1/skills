# Design: `prd-to-tdd` Skill

**Date:** 2026-05-25  
**Status:** Superseded in part — **source of truth:** `prd-to-tdd/SKILL.md` (7 chapters, Ch.2 `### 요구사항 분석`, strict + `--narrative` validation). This file retains historical context; do not use the 5-chapter outline below for new work.  
**Scope:** Agent skill that ingests PRD (Markdown / Google Docs), analyzes codebase, and writes a forward-only Technical Design Document (TDD).

---

## 1. Problem & Goal

Teams receive PRDs in Google Docs or Markdown. Before implementation, they need a **Technical Design Document** that:

- Grounds design in **actual code** when code exists (code-first).
- Reads like a **linear narrative** — each section builds on prior sections; no backward setup (“as mentioned above”, “see later”).
- Follows **기승전결** and **6하원칙** (who, what, when, where, why, how).
- Cites sources in **tiers** — official docs for core decisions; PRD + code locations elsewhere.
- Serves **mixed readers** (PM, developers, audit) in one document without separate siloed sections.

This skill produces TDD only. It does **not** generate implementation plans, tasks, or code changes.

---

## 2. Requirements Summary

| Dimension | Decision |
|-----------|----------|
| Audience | Mixed (PM, dev, audit) — one doc, linear flow |
| PRD input | Local Markdown + Google Docs URL via `gws`, auto-detect |
| Output | `docs/design/YYYY-MM-DD-<feature>-tdd.md` |
| Code analysis | Full repository |
| Citations | Tiered: Tier-1 (core decisions) = official URLs; Tier-2 = PRD ref + `path:line` |
| PRD vs code | **Code-first** — note PRD gaps/inconsistencies |
| Post-TDD | Standalone — no auto handoff to `writing-plans` or SDD |
| Validation | **Approach 3:** script (mechanical) + **3 parallel subagents** (semantic) |
| Greenfield | Auto-detect; adapt Chapter 3 (시작점) when no domain code |
| **Design alternatives** | Single winner → `**결정:**`; real fork → `**갈림:**`+`**권장:**`; Tier-1 high impact → ask user before Ch.4 |

---

## 3. Skill Identity

| Field | Value |
|-------|-------|
| **Name** | `prd-to-tdd` |
| **Install path** | `~/.cursor/skills/prd-to-tdd/` |
| **Triggers** | “PRD 분석해서 TDD”, “Technical Design Document”, “기술설계서”, PRD path/URL + design request |
| **Related skills** | `gws-shared`, `gws-docs`, Serena (code exploration) |
| **Out of scope** | Implementation plans, tasks, code edits, PRD authoring |

---

## 4. Repository Mode Detection

After Phase 2 (code analysis), classify repository mode:

### Brownfield signals

- Domain/business logic modules present under `src/`, `app/`, `lib/`, etc.
- Non-trivial services, models, or API handlers beyond boilerplate.

### Greenfield signals

- No domain code; only scaffold (`package.json`, empty `src/`, README, CI config).
- User explicitly states “new project” / “greenfield”.

### Mode behavior

| Aspect | Brownfield | Greenfield |
|--------|------------|------------|
| Frontmatter `mode` | `brownfield` | `greenfield` |
| Chapter 3 title | `3. 현재 시스템` | `3. 시작점` |
| Chapter 3 content | As-Is from code | Scaffold, deps, empty structure; **no fictional As-Is** |
| Chapter 4 focus | PRD ↔ code gaps | PRD requirements → initial design decisions |
| Code-first rule | Code overrides PRD on conflict | PRD + explicit constraints (README, stack) when no app code |
| `code-grounding-reviewer` | Claims match repo | **No fabricated modules**; only describe what exists |

---

## 5. Narrative Structure (5 Chapters)

Chapter order is **fixed**. No reordering. Subsections allowed within chapters only.

| Ch | 기승전결 | 6하원칙 | Primary readers | Content |
|----|----------|---------|-----------------|---------|
| **1. 서문** | 起 | Who, Why, When | All | Why this doc exists, who reads it, PRD source one-liner |
| **2. 배경과 문제** | 起→承 | What, Where | PM, dev | PRD problem & scope (intent only, no implementation) |
| **3. 현재 시스템 / 시작점** | 承 | What, How (current) | Dev, audit | Brownfield: As-Is architecture & data flow. Greenfield: starting point |
| **4. 갭과 설계 전환** | 转 | Why, How (target) | All | Brownfield: gaps & decisions. Greenfield: PRD → design choices. **Tier-1 citations here** |
| **5. 목표 설계와 마무리** | 结 | How, When | Dev, PM | To-Be architecture, interfaces, risks, open questions |

### Mixed-audience pattern (within each chapter)

Use **summary line → technical detail** — PM can stop after the summary; developers read through.

### Forward-only rules (`narrative-rules.md`)

1. **No temporal back-reference:** forbid “앞서”, “위에서”, “후술”, “나중에”, “as mentioned”, “see below”.
2. **Define before use:** every term/concept introduced before first use.
3. **PRD-only items (Brownfield):** first appear in Ch.4 as “미구현” or “PRD-only”.
4. **Code-only items (Brownfield):** first appear in Ch.3; contrasted in Ch.4.
5. **No appendix that re-explains earlier chapters.**

---

## 6. Citation Tiers (`citation-tiers.md`)

### Tier-1 — Core design decisions (required)

Applies to: architecture choices, security model, data store selection, auth strategy, breaking changes.

Format:

```markdown
> **결정:** JWT + refresh rotation 채택
> **근거:** [source:oauth2-bearer-token-usage](https://datatracker.ietf.org/doc/html/rfc6750)
> **코드:** (없음 — Greenfield) 또는 `src/auth/middleware.ts:42`
```

Must include at least one **official** URL (RFC, framework docs, vendor API reference).

### Tier-2 — Supporting facts

Applies to: component descriptions, data field lists, non-controversial mappings.

Format:

```markdown
> **사실:** 주문 상태는 5단계
> **근거:** [source:prd#주문-상태-정의] + `src/orders/state.ts:12-28`
```

### Prohibited

- Uncited technical claims in Ch.4–5.
- Blog/SO unless marked `[source:community, confidence:low]` and not used for Tier-1.

---

## 7. Workflow

```
[1] PRD ingest
      ↓
[2] Full-repo analysis + mode detection (brownfield | greenfield)
      ↓
[3] Outline (5 chapters + concept introduction order)
      ↓
[4] Draft TDD (chapter by chapter, template-driven)
      ↓
[5] scripts/validate-tdd.py  ──fail──→ fix → [5]
      ↓ pass
[6] 3 subagents in parallel ──critical──→ fix → [5] (max 2 rounds)
      ↓
[7] Save docs/design/YYYY-MM-DD-<feature>-tdd.md
```

### Phase 1 — PRD ingest

| Input pattern | Action |
|---------------|--------|
| Local path `*.md`, `*.txt` | Read file |
| Google Docs URL | `gws docs documents get` per `gws-shared` / `gws-docs` |
| Ambiguous | Ask user once |

Extract: feature name (for filename), scope, requirements list, constraints.

### Phase 2 — Code analysis

- Serena first: `get_symbols_overview`, `find_symbol`, `find_referencing_symbols`.
- Map: entry points, modules, data stores, external integrations.
- Emit internal **analysis notes** (not saved as TDD) with `path:line` refs for drafting.
- Set `mode: brownfield | greenfield`.

### Phase 3 — Outline

Before prose, produce ordered list:

- Concepts per chapter (introduction order).
- Tier-1 decision candidates for Ch.4.
- PRD↔code gap list (Brownfield) or PRD→decision list (Greenfield).

Self-check outline against narrative-rules before drafting.

### Phase 4 — Draft

Write using `tdd-template.md`. One chapter at a time; do not skip ahead.

### Phase 5 — Script validation

```bash
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md
```

Checks:

- YAML frontmatter: `mode`, `prd_source`, `generated_at`
- Required H2 headers (5 chapters; Ch.3 title variant by mode)
- Forbidden back-reference regex patterns
- `[source:...]` block syntax
- Tier-1 keywords near decision blocks have URL or explicit `(Greenfield — no code yet)`

Exit codes: `0` pass, `1` fail with line numbers.

### Phase 6 — Subagent validation (parallel)

Spawn all three; merge findings; **Critical** blocks merge.

#### 6a. `narrative-reviewer`

- **Type:** `generalPurpose` (readonly)
- **Inputs:** TDD draft + `narrative-rules.md`
- **Checks:** 기승전결 flow, 6하원칙 coverage per chapter, define-before-use, no back-reference (semantic, beyond regex)

#### 6b. `citation-reviewer`

- **Type:** `generalPurpose` (readonly)
- **Inputs:** TDD + PRD text + `citation-tiers.md`
- **Checks:** Tier-1/2 compliance, no orphan claims in Ch.4–5, URL plausibility

#### 6c. `code-grounding-reviewer`

- **Type:** `cavecrew-reviewer` or `generalPurpose` (readonly)
- **Inputs:** TDD + repo (Brownfield: verify As-Is; Greenfield: no fake modules)
- **Checks:** Code-first (B), every As-Is claim traceable, PRD gaps honestly labeled

**Retry policy:** Max **2** full validate cycles (script + subagents). After 2 failures, save draft with frontmatter `validation_passed: false` and present unresolved Critical list to user.

### Phase 7 — Save

Path: `docs/design/YYYY-MM-DD-<feature>-tdd.md`

Frontmatter example:

```yaml
---
title: "TDD: 주문 취소 API"
feature: order-cancel-api
mode: brownfield
prd_source: "https://docs.google.com/document/d/xxx/edit"
generated_at: 2026-05-25
validation_passed: true
review_rounds: 1
---
```

---

## 8. File Structure

```
~/.cursor/skills/prd-to-tdd/
├── SKILL.md                    # Workflow, triggers, checklist, subagent spawn instructions
├── narrative-rules.md          # Forward-only + 기승전결 + 6하원칙
├── citation-tiers.md           # Tier-1 / Tier-2 formats
├── tdd-template.md             # Output skeleton with frontmatter
├── subagent-prompts.md         # Prompt templates for 3 reviewers
├── examples.md                 # Good vs bad narrative excerpts
└── scripts/
    └── validate-tdd.py         # Mechanical validation
```

### SKILL.md responsibilities

- Trigger description (third person, WHAT + WHEN).
- Phase checklist (copyable).
- When to read which reference file.
- Subagent spawn blocks (copy from `subagent-prompts.md`).
- Greenfield vs Brownfield branch at Phase 2.
- Explicit **STOP** after save — no implementation handoff.

### `scripts/validate-tdd.py` responsibilities

- Stdlib-only Python 3 (no external deps).
- CLI: path to TDD markdown.
- JSON or human-readable stderr on failure.
- Configurable forbidden phrases list at top of script.

### `subagent-prompts.md` structure

For each reviewer:

1. Role one-liner
2. Input files to attach
3. Checklist (numbered)
4. Output format: `severity | chapter:line | issue | fix`
5. Severity definitions: Critical / Major / Minor

---

## 9. TDD Output Template (abbreviated)

See `tdd-template.md` in skill package. Skeleton:

```markdown
---
title: "TDD: {{feature_title}}"
feature: {{feature_slug}}
mode: {{brownfield|greenfield}}
prd_source: "{{path_or_url}}"
generated_at: {{YYYY-MM-DD}}
validation_passed: false
review_rounds: 0
---

# {{feature_title}} — Technical Design Document

## 1. 서문
<!-- Who, Why, When; PRD source -->

## 2. 배경과 문제
<!-- What, Where from PRD; no implementation -->

## 3. {{현재 시스템 | 시작점}}
<!-- Brownfield: As-Is | Greenfield: scaffold only -->

## 4. {{갭과 설계 전환 | 설계 결정}}
<!-- Tier-1 citations required for decisions -->

## 5. 목표 설계와 마무리
<!-- To-Be, interfaces, risks, open questions -->
```

---

## 10. Error Handling

| Situation | Behavior |
|-----------|----------|
| PRD unreachable (gws auth fail) | Stop; point to `gws-shared` auth steps |
| Empty PRD | Stop; ask user for content |
| Repo too large for one pass | Prioritize modules matching PRD keywords, document scope limit in Ch.1 |
| PRD ↔ code irreconcilable | Code-first; list conflicts in Ch.4; do not hide |
| Validation fails 2× | Save draft with `validation_passed: false`; show Critical list |
| User wants Google Docs output | Out of scope (Markdown only per requirements) |

---

## 11. Testing the Skill (post-implementation)

Per `writing-skills` TDD for skills:

1. **RED:** Run agent on sample PRD + sample repo without skill — expect backward references, missing citations.
2. **GREEN:** Same scenario with skill — expect 5-chapter TDD, script pass, subagents no Critical.
3. **Scenarios:**
   - Brownfield: small repo with partial PRD coverage
   - Greenfield: empty `src/` + PRD only
   - Google Docs URL (mock or real gws)
   - PRD/code conflict (code-first labeling)

---

## 12. Implementation Plan (next step)

After user approves this spec:

1. Create `~/.cursor/skills/prd-to-tdd/` directory tree.
2. Implement `SKILL.md` (< 500 lines) with progressive disclosure to reference files.
3. Implement `validate-tdd.py`.
4. Write `subagent-prompts.md` with three reviewer templates.
5. Add `examples.md` with one Brownfield and one Greenfield mini-example.
6. Run skill verification scenarios (Section 11).

**Note:** User chose no automatic handoff to `writing-plans`. Implementation of the skill itself is a separate task after spec approval.

---

## 13. Spec Self-Review

| Check | Status |
|-------|--------|
| Placeholders / TBD | None |
| Internal consistency | Mode branching aligned with code-first and 5-chapter flow |
| Scope | Single skill package; no implementation plan generation |
| Ambiguity | Ch.3 title variant documented; retry limit = 2 rounds |

---

*End of design spec.*
