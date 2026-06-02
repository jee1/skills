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
| [design-sections.md](design-sections.md) | Before drafting Ch.2 ### 요구사항 분석 and Ch.5–6 |
| [outline-template.md](outline-template.md) | Phase 3 — required Ch.5–6 mapping |
| [subagent-prompts.md](subagent-prompts.md) | Phase 6 spawn (default 3 reviewers) |
| [dual-brain-integration.md](dual-brain-integration.md) | Optional Phase 3b/6 when `dual-brain` skill installed |
| [examples.md](examples.md) | When unsure about tone or structure |

## Checklist

Copy and track:

```
PRD → TDD Progress:
- [ ] Phase 1: PRD ingest
- [ ] Phase 2: Full-repo analysis + mode (brownfield | greenfield)
- [ ] Phase 3: Outline (concept order, gaps/decisions, Tier-1 tags)
- [ ] Phase 3b: User confirm Tier-1 forks (if any `needs-user-confirm`; optional Right Brain if dual-brain installed — see dual-brain-integration.md)
- [ ] Phase 4: Draft TDD (7 chapters + appendices, in order)
- [ ] Phase 5: validate-tdd.py pass (strict)
- [ ] Phase 5b: validate-tdd.py --narrative pass
- [ ] Phase 6: reviewers pass, no Critical (≤2 rounds) — default: 3 parallel OR compact: left-brain [+ narrative] if dual-brain available
- [ ] Phase 7: Save docs/design/YYYY-MM-DD-<feature>-tdd.md (note which Phase 6 path was used)
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

Extract: `feature_slug`, title, requirements, constraints, PRD section anchors for citations. Classify each PRD item as **FR** / **NFR** / **constraint** / **open question** (draft IDs: `FR-1`, `NFR-1`, `CON-1`, `OQ-1`).

**Stop if:** empty PRD or gws auth failure (point user to gws-shared).

---

## Phase 2 — Code Analysis + Mode

**Tools:** Serena first (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`); full repo scope.

Build internal **analysis notes** (do not save as TDD): entry points, modules, data stores, integrations, `path:line` refs, **existing test layout** (unit/integration/e2e paths, frameworks, CI commands).

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
   - `single` — one clear choice → decision card Shape A ([citation-tiers.md](citation-tiers.md))
   - `multi-recommend` — real fork → Shape B + `상태: 권장(미확정)`
   - `needs-user-confirm` — Tier-1 high impact → **ask user before Ch.4** (see below)
3. Brownfield: PRD↔code gap list | Greenfield: PRD→decision list
4. **Requirements inventory (required)** — see [outline-template.md](outline-template.md) § Requirements inventory; tag `needs-user-confirm` on ambiguous PRD items
5. **Ch.5–6 mapping tables (required):**
   - Components (≥2 names, 신규/기존 for brownfield)
   - APIs/events (≥1 per user-facing action)
   - Entities (≥1 per persisted object, field names listed)
   - Primary flow (≥5 steps) + error branches (≥2)
   - Acceptance criteria (≥1 per functional PRD requirement; min ≥2 rows)
   - Tests (≥1 per AC; min ≥2 rows with layer + CI gate)

Self-check against [narrative-rules.md](narrative-rules.md) outline checklist and [design-sections.md](design-sections.md) depth rubric.

---

## Phase 3b — User Confirmation (Tier-1 forks only)

**When:** outline has any `needs-user-confirm` item (auth, datastore, breaking API, major dependency contract, balanced trade-offs with no code/PRD tiebreaker).

**How:** One message per fork (or one message listing all forks). For each:

- Topic name
- 2–3 **대안** each with: 한 줄 설명 + 장점/단점 + PRD/코드 적합도
- **권장** + **권장 이유** (≥2 sentences, not URL-only)
- Ask user to pick or confirm recommendation

**Do not** draft Ch.4–5 for that topic until answered. After answer, rewrite as Shape A with `상태: 확정`.

If user defers (“나중에”), keep Shape B with `상태: 권장(미확정)` and add Ch.7 **열린 질문**.

### Optional — Right Brain (dual-brain installed only)

Before asking the user, if `~/.cursor/skills/dual-brain/SKILL.md` (or `~/.codex/`, `~/.agents/`) exists **and** outline has `needs-user-confirm` items:

1. Read [dual-brain-integration.md](dual-brain-integration.md) § Phase 3b
2. Read `dual-brain/SKILL.md`; run Right Brain Task (sequential) on fork list + PRD scope
3. Use grill output to enrich the confirmation message (do not skip user confirm)

If dual-brain is **not** installed: stay orchestrator-only above — **no failure**, no install required.

---

## Phase 4 — Draft

1. Read [tdd-template.md](tdd-template.md), [design-sections.md](design-sections.md), [narrative-rules.md](narrative-rules.md)
2. Create `docs/design/` if missing
3. Write **one chapter at a time** in fixed order (1 → 7)
4. **Ch.2:** after background prose, write `### 요구사항 분석` from Requirements inventory ([design-sections.md](design-sections.md)); end with a bridge sentence into Ch.3
5. **Expand every Phase 3 outline row** into ≥1 sentence or table row in the mapped ### subsection — no orphan rows, no empty subsections
6. Ch.4: decision cards (Shape A/B) from [citation-tiers.md](citation-tiers.md) — metadata table + **근거 설명** + **참고**; forks add alternatives table + **권장 이유**; reference Ch.2 `FR-*` / `OQ-*` where relevant
7. Ch.5 **상위설계**: lead prose (≥2 sentences per ###) then mermaid/lists; ≥2 components; ≥3 flow steps
8. Ch.6 **상세설계**: lead prose (≥1 sentence per ###) then tables; optional dev index table after chapter intro; ≥2 error branches; Ch.5 names in Ch.6; **### 인수조건** (each Must `FR-*` → ≥1 `AC-*`, verifiable pass/fail; update Ch.2 RTM AC column) + **### 테스트** (AC→test cases, layers, CI gate); `[ref:A-n]` not inline blockquotes
9. Ch.7 **마무리**: rollout, risks table, 열린 질문 (for each Ch.4 `권장(미확정)`)
10. Front matter: `## 목차` → `## 이 문서 읽는 법` → `## 1. 서문` (opening + Goals only)
11. Ch.2–4: ≥8 sentences each in **2–4 paragraphs** (blank line between paragraphs); Ch.2 tables live under `### 요구사항 분석` only
12. Ch.4: mermaid transition diagram before `### 결정 요약`
13. Ch.5: mermaid in ### 아키텍처 개요 and ### 데이터 흐름
14. Ch.6: mermaid flowchart in ### 핵심 처리 흐름 (error branches); ### 인수조건 + ### 테스트 after flow
15. Ch.4: `### 결정 요약` table (only allowed “summary” heading in body)
16. Ch.5: **no** `요약:` / `#### 한눈에`
17. Write ## 부록 A and ## 부록 B after Ch.7
18. Ch.2–4: embed 6ha in prose; chapter bridges (see narrative-rules.md)
19. Literal tilde in TDD body (ranges, approximations): write `\~` — e.g. `A\~Z`, `\~3분`. Bare `~` pairs with a later `~` and renders strikethrough (see narrative-rules.md)

Filename: `docs/design/YYYY-MM-DD-<feature_slug>-tdd.md`

---

## Phase 5 — Script Validation

Run the validator from this skill package (repo: `skills/prd-to-tdd/`; installed symlinks: `~/.cursor/skills/prd-to-tdd/`, `~/.codex/skills/prd-to-tdd/`, `~/.agents/skills/prd-to-tdd/`):

```bash
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md
python scripts/validate-tdd.py docs/design/YYYY-MM-DD-<feature>-tdd.md --narrative
```

Default is **strict** (Ch.5–6 depth rubric). Legacy drafts: add `--lenient` to skip depth checks. **`--readability` is deprecated** (alias for `--narrative`). Both strict and `--narrative` must exit `0` before Phase 6.

Use the path to `validate-tdd.py` inside the skill directory. `<feature>-tdd.md` lives in the **target project** under `docs/design/`.

- Exit `0` → Phase 6
- Exit `1` → fix reported lines, re-run
- Do not spawn subagents until script passes

---

## Phase 6 — Subagent Validation

Read [subagent-prompts.md](subagent-prompts.md). Choose **one** path:

### Path selection (start of Phase 6)

```
dual-brain SKILL.md exists on disk?
  ├─ NO  → Mode A (default): 3 parallel reviewers — always valid
  └─ YES → User asked dual-brain OR prefer compact review?
            ├─ YES → Mode B: left-brain-verification [+ optional narrative]
            └─ NO  → Mode A (default)
```

Full rules: [dual-brain-integration.md](dual-brain-integration.md).

### Mode A — Default (dual-brain not required)

Spawn **three** Task agents **in parallel**:

1. **narrative-reviewer** — `generalPurpose`, readonly
2. **citation-reviewer** — `generalPurpose`, readonly
3. **code-grounding-reviewer** — `cavecrew-reviewer` or `generalPurpose`, readonly

### Mode B — Compact (dual-brain skill installed)

After Phase 5 + 5b pass:

1. **left-brain-verification-reviewer** — `generalPurpose` or `cavecrew-reviewer`, readonly (replaces citation + code-grounding)
2. **narrative-reviewer** — only if `--narrative` passed but bridges/AC wording still feel weak; otherwise **skip**

Prompts: [subagent-prompts.md](subagent-prompts.md) §4–5.

### Script vs subagent scope

| Concern | Phase 5 `validate-tdd.py` | Mode A | Mode B |
|---------|---------------------------|--------|--------|
| Headers, depth, FR→RTM→AC, OQ→Ch.7 | strict | (script) | (script) |
| Back-ref, `요약:`, tilde, mermaid | strict + `--narrative` | narrative-reviewer | narrative if spawned |
| Tier-1 URL, PRD anchors | partial | citation-reviewer | left-brain-verification |
| path:line, code-first, greenfield fiction | — | code-grounding-reviewer | left-brain-verification |

All reviewers return `severity | chapter:line | issue | fix` only (see subagent-prompts.md).

Merge findings. **Critical** → edit TDD → Phase 5 → Phase 6 again.

- Increment frontmatter `review_rounds` each full cycle
- Max **2** cycles; then set `validation_passed: false`, save, show unresolved Critical list to user
- If clean: `validation_passed: true`

---

## Phase 7 — Save & Stop

Confirm file at `docs/design/YYYY-MM-DD-<feature>-tdd.md`.

Tell user:
- Path, mode, validation status, review rounds, **Phase 6 path** (default 3 reviewers | dual-brain compact | dual-brain unavailable → default)
- Ch.4: **확정** vs **권장(미확정)** forks
- Ch.2: FR count + open questions (`OQ-*`)
- Ch.6: AC count + test coverage summary (which ACs have CI-gated tests); RTM complete (FR → AC → T)
- Ch.5–6: one-line summary of architecture + key APIs
- Open questions from Ch.7
- Optional next step (mention only): run **`tdd-to-tasks`** skill → `docs/tasks/YYYY-MM-DD-<feature>-tasks.md`

**STOP.** Do not run `tdd-to-tasks`, implementation, or `writing-plans` unless user asks separately.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Huge repo | Prioritize PRD-keyword modules; note scope limit in Ch.1 |
| PRD/code irreconcilable | Code-first; list in Ch.4 |
| 2 failed validation rounds | Save draft, `validation_passed: false` |
| User wants Google Docs output | Out of scope (Markdown only) |
| `dual-brain` skill not on VM | Use Mode A (3 reviewers); state once in Phase 7 report — **not** an error |

---

## Quick Reference — 7 Chapters

| # | Brownfield H2 | Greenfield H2 | 기승전결 |
|---|---------------|---------------|----------|
| 1 | 서문 | 서문 | 起 |
| 2 | 배경과 문제 (+ ### 요구사항 분석) | 배경과 문제 (+ ### 요구사항 분석) | 承 |
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
- **dual-brain** (optional) — Phase 3b Right Brain + Phase 6 compact path; see [dual-brain-integration.md](dual-brain-integration.md). **Not a dependency.**

Design spec (maintainers): `docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md` at the root of the agent-skills git repository.
