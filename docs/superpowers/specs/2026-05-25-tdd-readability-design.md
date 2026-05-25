# Design: TDD Readability Profile (Triple-Audience)

**Date:** 2026-05-25  
**Status:** Implemented  
**Scope:** Improve readability of `prd-to-tdd` output for PM, backend developers, and audit readers **equally**, without splitting into multiple files or weakening strict depth coverage.

**Related specs:**

- `2026-05-25-prd-to-tdd-skill-design.md` — base TDD skill
- `2026-05-25-prd-to-tdd-strict-depth-design.md` — Ch.5–6 depth gates

---

## 1. Problem & Goal

### Problem

TDD documents produced by `prd-to-tdd` pass strict depth validation but feel hard to read for **all** target readers:

| Symptom | Root cause in current skill |
|---------|----------------------------|
| Repetitive, fatiguing scan | Every `###` follows `요약:` → prose → `> **사실:**` block |
| PM cannot grasp scope quickly | No TL;DR, Goals/Non-Goals, or reader paths in Ch.1 |
| Dev must hunt specs in prose | Ch.6 tables exist but are buried after narrative + blockquotes |
| Audit trail interrupts flow | Tier-2 citations inline in every Ch.5–6 subsection (strict rubric) |
| No visual anchor | Mermaid optional; sample TDDs have no diagrams |
| Forward-only forces repetition | Temporal back-refs forbidden; same facts re-stated per chapter |

User confirmed pain is **balanced across PM, dev, and audit** (not one dominant audience).

### Goal

One Markdown file (`docs/design/YYYY-MM-DD-<feature>-tdd.md`) where:

| Reader | Target | Path |
|--------|--------|------|
| PM | Understand problem, scope, architecture in ~2 min | Ch.1 TL;DR + Ch.5 diagram + `#### 한눈에` |
| Dev | Implement from specs in ~5 min | Ch.4 decisions + Ch.6 index + tables |
| Audit | Trace claims to PRD/code/URLs in ~3 min | Ch.4 decision table + Appendix A/B |

**Non-goals:**

- Multi-file Gerrit-style split (`index.md` + `solution-*.md`)
- Separate PM PDF or HTML renderer
- Relaxing strict depth minimums (tables, error branches, component cross-refs)
- Auto handoff to `writing-plans`

---

## 2. Design Principles

1. **Same fact, one canonical home** — Narrative states intent; Ch.6 holds field-level truth; Appendix A holds Tier-2 traceability.
2. **Lanes, not files** — Reader paths are signposted in Ch.1; content stays in one artifact.
3. **Strict depth ≠ inline blockquotes** — Depth rubric checks substance; readability profile checks navigation and citation placement.
4. **Progressive disclosure** ([Google Tech Writing](https://developers.google.com/tech-writing/two/large-docs)) — Overview first, reference detail on demand, audit trail in appendix.
5. **Diátaxis alignment** ([diataxis.fr](https://diataxis.fr/start-here/)) — Ch.1–5 = explanation; Ch.6 = reference; Appendix = audit facts.

---

## 3. Document Architecture

```
Ch.1  서문 (entry — all readers)
  ├── TL;DR (3 sentences)
  ├── Goals / Non-Goals
  ├── 이 문서 읽는 법 (reader path table)
  └── 목차 (anchor links)

Ch.2–3  배경 · 현재/시작점 (narrative — minimal citations)

Ch.4  갭/설계 결정 (Tier-1 blockquotes + decision summary table)

Ch.5  상위설계 (diagram required + #### 한눈에 per H2)

Ch.6  상세설계 (reference mode: tables first, spec index at top)

Ch.7  마무리 (unchanged structure)

Appendix A  출처·코드 위치 (Tier-2 audit table)

Appendix B  Ch.4 결정 전문 (blockquote archive for audit)
```

---

## 4. Section Specifications

### 4.1 Chapter 1 — 서문 (expanded)

**Required subsections** (new `###` under Ch.1):

| Subsection | Content | Min |
|------------|---------|-----|
| `### TL;DR` | Problem / solution / impact — one sentence each | 3 sentences |
| `### Goals / Non-Goals` | Scope boundaries | ≥3 goals, ≥2 non-goals |
| `### 이 문서 읽는 법` | Reader path table (PM / Dev / Audit) | 3 rows |
| `### 목차` | Links to `## N.` and appendices | All H2 + appendices |

**Validation (readability profile):** presence checks only; no 120-char rubric on Ch.1.

### 4.2 Chapters 2–3 — Narrative

- Keep forward-only **temporal** ban (`앞서`, `see above`, etc.).
- **Allow static anchor refs:** e.g. `API 필드는 [§6.1](#61-api-및-인터페이스) 참고`.
- Tier-2 claims: use `[ref:A-n]` inline; full block in Appendix A (no `> **사실:**` in Ch.2–3 unless Tier-1 decision appears early — rare).

### 4.3 Chapter 4 — Decisions

**Unchanged:** Tier-1 `> **결정:**` / `> **갈림:**` blockquote shapes per `citation-tiers.md`.

**New:** `### 결정 요약` table after Ch.4 intro (before or after individual decision subsections):

| # | 주제 | 선택 | 상태 | 상세 |
|---|------|------|------|------|
| 1 | … | … | 확정 \| 권장(미확정) | §4.x or blockquote anchor |

**Appendix B:** Copy full Ch.4 blockquote text verbatim for audit archive (can be generated at save time or maintained in draft).

### 4.4 Chapter 5 — 상위설계

**Unchanged subsections:** 아키텍처 개요, 구성요소 및 책임, 데이터 흐름.

**New rules:**

| Rule | Detail |
|------|--------|
| Mermaid required | One `flowchart` or C4-style box diagram in `### 아키텍처 개요` |
| `#### 한눈에` | After each Ch.5 `##` content block (or after each `###` — pick one: **after H2 `## 5. 상위설계` closing all ###** OR per ###; **decision: per ###** for PM scan) |
| Tier-2 citations | `[ref:A-n]` only; no inline `> **사실:**` in Ch.5 |
| Diagram vs list | Numbered data flow may overlap diagram but must add boundary detail (async, auth) not visible in diagram |

**`#### 한눈에` format:** exactly 3 bullet lines, PM-readable, no field-level schema.

### 4.5 Chapter 6 — 상세설계 (reference mode)

**New at top of Ch.6** (before first `###`):

```markdown
### 스펙 인덱스

| Endpoint / Interface | Entity | Error codes |
|----------------------|--------|-------------|
| … | … | … |
```

**Per subsection:**

1. `요약:` (one line)
2. Tables (API, entity, state, error) — **first**
3. Prose ≤2 sentences below tables
4. Tier-2: `[ref:A-n]` footnotes, not blockquotes

**Strict depth gates unchanged:** API table rows, entity fields, error branches, Ch.5→Ch.6 name cross-ref.

### 4.6 Appendices

#### Appendix A — 출처·코드 위치

| ID | 주장 (one line) | PRD anchor | Code | External URL |
|----|-----------------|------------|------|--------------|
| A-1 | … | … | `path:line` | … |

- IDs: `A-1`, `A-2`, … sequential
- Every Tier-2 claim in Ch.2–6 must have a row
- Tier-1 URLs may duplicate Ch.4 blockquotes (acceptable)

#### Appendix B — Ch.4 결정 전문

- Verbatim blockquote blocks from Ch.4 for immutable audit trail
- If Ch.4 edited post-review, Appendix B must match

---

## 5. Citation Policy Changes

| Tier | Ch.2–3 | Ch.4 | Ch.5 | Ch.6 | Appendix |
|------|--------|------|------|------|----------|
| Tier-1 decision | — | blockquote + summary table | — | — | B (copy) |
| Tier-2 fact | `[ref:A-n]` | — | `[ref:A-n]` | `[ref:A-n]` | A (canonical) |

**Remove:** requirement for `> **사실:**` block per Ch.5–6 `###` in strict profile.

**Add:** Appendix A coverage check — all `[ref:A-n]` in body resolve; all substantive Ch.5–6 claims have refs.

---

## 6. Validation — Dual Profiles

`validate-tdd.py` gains **`--readability`** flag (default: strict depth only, unchanged).

When `--readability` is passed (recommended default after rollout):

| Check | Type |
|-------|------|
| Ch.1: TL;DR, Goals, Non-Goals, reader table, TOC | mechanical |
| Ch.4: `### 결정 요약` table ≥1 row | mechanical |
| Ch.5: mermaid code fence in 아키텍처 개요 | mechanical |
| Ch.5: `#### 한눈에` per ### (3 bullets) | mechanical |
| Ch.6: `### 스펙 인덱스` table | mechanical |
| Appendix A present; `[ref:A-n]` resolve | mechanical |
| Appendix B present if Ch.4 has blockquotes | mechanical |
| No `> **사실:**` in Ch.5–6 (warn or error) | mechanical |
| Appendix A covers all body refs | mechanical |

**Combined CI recommendation:**

```bash
python validate-tdd.py docs/design/YYYY-MM-DD-feature-tdd.md
python validate-tdd.py docs/design/YYYY-MM-DD-feature-tdd.md --readability
```

**`--lenient`:** still skips depth only; does not skip readability when `--readability` set.

---

## 7. Skill & Reference File Updates

| File | Change |
|------|--------|
| `prd-to-tdd/tdd-template.md` | Ch.1 subsections, Ch.6 spec index, appendices A/B, mermaid placeholder |
| `prd-to-tdd/narrative-rules.md` | Static anchor refs allowed; `#### 한눈에`; Ch.5–6 blockquote policy |
| `prd-to-tdd/citation-tiers.md` | Tier-2 → Appendix A; Ch.5–6 inline blockquote removed |
| `prd-to-tdd/design-sections.md` | Reference mode for Ch.6; readability rubric section |
| `prd-to-tdd/SKILL.md` | Phase 4 steps for appendices; Phase 5 `--readability` |
| `prd-to-tdd/examples.md` | Good/bad for readability patterns |
| `prd-to-tdd/subagent-prompts.md` | narrative-reviewer: scan test (PM 2-min, appendix coverage) |
| `prd-to-tdd/scripts/validate-tdd.py` | `--readability` implementation |
| `docs/design/*-sample-*-tdd.md` | Rewrite to new profile |

---

## 8. Implementation Phases

| Phase | Deliverable | Readers helped |
|-------|-------------|----------------|
| **P0** | Ch.1 template + SKILL Phase 4; sample TDD Ch.1 | PM, all |
| **P0** | Ch.5 mermaid required + sample diagram | PM, dev |
| **P1** | Appendix A/B + citation policy + Tier-2 migration | dev, audit |
| **P1** | Ch.4 summary table + Ch.6 spec index | PM, dev |
| **P1** | `validate-tdd.py --readability` | regression guard |
| **P2** | narrative-reviewer scan checklist | semantic quality |
| **P2** | Enable `--readability` as default in SKILL Phase 5 | — |

---

## 9. Success Criteria

- [ ] PM can answer “what are we building and what’s out of scope?” from Ch.1 + Ch.5 diagram without reading Ch.6
- [ ] Dev can locate all endpoints and error codes from Ch.6 spec index + tables without reading blockquotes
- [ ] Audit can map any Ch.5–6 `[ref:A-n]` to PRD/code/URL in Appendix A; Tier-1 in Appendix B
- [ ] Existing strict depth tests still pass on updated samples
- [ ] `--readability` passes on updated samples
- [ ] No increase in average subsection prose length vs current samples (shorter body, same information)

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Appendix A drift from body | Validator: unresolved `[ref:A-n]` = error |
| Authors skip appendix | Phase 5 gate: both profiles must pass before Phase 6 |
| Mermaid broken in GitHub | narrative-reviewer syntax check; simple flowchart only |
| Strict-depth reviewers assume blockquotes | Update `examples.md` and subagent prompts explicitly |

---

## 11. Out of Scope

- Multi-file design doc directories
- Google Docs TDD export
- Automated Appendix B sync tool (manual parity in Phase 4 draft step)
- Changing 7-chapter 기승전결 order
