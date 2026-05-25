# TDD Layout, Paragraphs, and Diagrams — Design Spec

**Status:** Implemented  
**Date:** 2026-05-25  
**Scope:** `prd-to-tdd` skill — document structure, paragraph readability, flow diagrams  
**Builds on:** [2026-05-25-tdd-narrative-profile-design.md](2026-05-25-tdd-narrative-profile-design.md)  
**Supersedes:** Ch.1 “scan-first inside `## 1. 서문`” (`### 목차` → `### 이 문서 읽는 법` → opening → Goals)

---

## 1. Problem

Readers report three friction points in generated TDDs:

1. **Navigation inside 서문** — `목차` and `이 문서 읽는 법` sit under `## 1. 서문`, so skimmers must enter the narrative chapter before seeing the map.
2. **Wall-of-text chapters** — Ch.2–4 are often one long paragraph; Markdown renderers show no visual breaks even when sentence count meets `--narrative` minima.
3. **Flows as lists only** — Cancel/orchestration paths are hard to follow without diagrams beyond Ch.5 box architecture.

---

## 2. Goals / Non-Goals

**Goals:**

- H1-level **front matter** (`## 목차`, `## 이 문서 읽는 법`) before numbered chapter `## 1. 서문`.
- Ch.1 contains **opening prose + Goals / Non-Goals** only (pure 起 entry).
- **Paragraph-level** breaks in Ch.2–4 (2–4 paragraphs per chapter; no run-on blocks).
- **Four mermaid diagrams** under `--narrative`: Ch.4 transition, Ch.5 architecture (existing), Ch.5 data flow, Ch.6 core processing flow with error branches.

**Non-Goals:**

- Auto-generated TOC from headings.
- HTML/CSS or renderer-specific line-break hacks.
- Embedded PNG/SVG assets (mermaid in fenced blocks only).
- Requiring four diagrams in **strict** profile (strict keeps Ch.5 architecture mermaid only).

---

## 3. Document Structure

### 3.1 Top-level outline

```markdown
# {title} — Technical Design Document

## 목차
…

## 이 문서 읽는 법
| 독자 | … |

## 1. 서문
{opening paragraph — no ### heading, 3–5 sentences}

### Goals / Non-Goals
…

## 2. 배경과 문제
…
```

### 3.2 Rules

| Rule | Detail |
|------|--------|
| Front matter order | `## 목차` → `## 이 문서 읽는 법` → `## 1. 서문` |
| No prose before `## 목차` | Only blank lines allowed after document `#` title |
| Ch.1 forbidden | `### 목차`, `### 이 문서 읽는 법` (use H2 front matter instead) |
| Ch.1 allowed | Untitled opening paragraph, `### Goals / Non-Goals` |
| TOC anchors | Link to `#1-서문`, `#2-배경과-문제`, … appendices unchanged |
| Reader table | Update “먼저 볼 곳” to reference front matter + `## 1. 서문` opening |

### 3.3 기승전결 mapping (unchanged roles)

| Block | Role |
|-------|------|
| `## 목차`, `## 이 문서 읽는 법` | Wayfinding (non-narrative) |
| `## 1. 서문` | 起 — why this document exists |
| Ch.2–7 | Unchanged narrative arc |

---

## 4. Paragraph / Line-Break Policy

### 4.1 Authoring (SKILL + narrative-rules)

- **Ch.2, Ch.3, Ch.4** body (exclude tables, blockquotes, mermaid): **2–4 paragraphs**, separated by **one blank line** (`\n\n`).
- **One paragraph:** **1–4 sentences** recommended; split when a fifth sentence would stay in the same block.
- **Ch.1 opening**, **Ch.5–7** lead prose: same paragraph style encouraged; **mandatory checks only on Ch.2–4**.

### 4.2 Validator (`--narrative` only)

Prose extraction: strip tables, fences, blockquotes, headings; split on `\n\n+`.

| Error code | Condition |
|------------|-----------|
| `ch234-paragraph-runon` | Any single prose paragraph in Ch.2, Ch.3, or Ch.4 has **≥5** sentences |
| `ch234-paragraph-sparse` | Any of Ch.2, Ch.3, Ch.4 has **<2** prose paragraphs |

Sentence counting reuses existing `_split_sentences` / `_count_sentences` helpers on paragraph slices.

---

## 5. Diagram Policy (Option C)

### 5.1 Required mermaid locations (`--narrative`)

| # | Section | Purpose | Suggested type |
|---|---------|---------|----------------|
| 1 | Ch.4 — after gap prose, **before** `### 결정 요약` | as-is → gap → target direction | `flowchart LR` or `stateDiagram-v2`, 3–7 nodes |
| 2 | Ch.5 `### 아키텍처 개요` | Component boundaries | `flowchart` (existing strict rule) |
| 3 | Ch.5 `### 데이터 흐름` | Happy-path sequence | `sequenceDiagram` or `flowchart`; **after** ≥2 lead sentences |
| 4 | Ch.6 `### 핵심 처리 흐름` | Happy + error branches | `flowchart TD` with decisions; aligns with ≥2 error branches (strict) |

Each diagram must be preceded by lead prose explaining why the diagram exists (existing Ch.5–6 lead-sentence rules apply).

### 5.2 Validator (`--narrative`)

| Error code | Condition |
|------------|-----------|
| `ch4-transition-diagram-missing` | No ` ```mermaid ` in Ch.4 before `### 결정 요약` |
| `ch5-mermaid-missing` | No mermaid in `### 아키텍처 개요` (existing) |
| `ch5-flow-diagram-missing` | No mermaid in `### 데이터 흐름` |
| `ch6-flow-diagram-missing` | No mermaid in `### 핵심 처리 흐름` |
| `ch6-flow-branches-weak` | Ch.6 flow mermaid has **<2** branch signals (heuristic: `\|yes\|`, `\|no\|`, `-->|`, or `alt`/`else` in sequenceDiagram) |

**Strict profile:** only `ch5-mermaid-missing` remains mandatory; other diagrams are narrative-only.

### 5.3 Naming

Diagram nodes must reuse component/state names already introduced in prose (forward-only rule unchanged).

---

## 6. Validation Profiles (1+α)

| Check | `validate-tdd.py` (strict) | `--narrative` |
|-------|------------------------------|---------------|
| Front matter order H1→목차→읽는법→1.서문 | Yes | Yes |
| Ch.1 has opening + Goals; no `### 목차` | Yes | Yes |
| Ch.2–4 sentence minima (≥8) | — | Yes (existing) |
| Ch.2–4 paragraph rules | — | Yes (new) |
| Ch.4/5/6 extra mermaid | — | Yes (new) |
| Ch.5 architecture mermaid | Yes | Yes |
| Depth tables, bridges, anti-labels | Yes / narrative | Yes |

---

## 7. Files to Change (implementation plan input)

| File | Change |
|------|--------|
| `prd-to-tdd/tdd-template.md` | Front matter H2; Ch.4/5/6 mermaid stubs |
| `prd-to-tdd/narrative-rules.md` | Front matter + paragraphs + diagram map |
| `prd-to-tdd/design-sections.md` | Rubric rows for paragraphs + diagrams |
| `prd-to-tdd/SKILL.md` | Phase 4 draft steps |
| `prd-to-tdd/subagent-prompts.md` | Review checklist |
| `prd-to-tdd/examples.md` | Good/bad paragraph + diagram excerpts |
| `prd-to-tdd/scripts/validate-tdd.py` | `check_front_matter()`, paragraph + diagram checks |
| `prd-to-tdd/scripts/test_validate_tdd.py` | Fixtures + regression tests |
| `docs/design/2026-05-25-sample-*-tdd.md` | Migrate structure, paragraphs, diagrams |
| `2026-05-25-tdd-narrative-profile-design.md` | Add superseded note for old Ch.1 order |

---

## 8. Acceptance Criteria

1. Sample TDDs pass `validate-tdd.py` (strict) and `validate-tdd.py --narrative`.
2. Rendered Markdown shows visible paragraph breaks in Ch.2–4 (blank lines in source).
3. Reader can skim `## 목차` and `## 이 문서 읽는 법` without scrolling through 서문 opening.
4. Ch.4 transition diagram visible before decision summary table.
5. No new meta-labels (`요약:`, `#### 한눈에`, `### TL;DR`) in Ch.2–7.

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Agent skips diagrams under token pressure | Subagent checklist + validator hard fail on `--narrative` |
| Over-long mermaid | Cap 3–7 nodes in SKILL guidance; box-level only in Ch.5 arch |
| Paragraph split hurts bridge heuristic | Bridges still use last/first sentence across chapter boundaries, not paragraphs |
| Legacy drafts fail strict front matter | `--lenient` unchanged; migration only for samples + docs |

---

## 10. Self-Review (2026-05-25)

- [x] No TBD placeholders in requirements sections
- [x] Consistent with narrative profile (anti-labels, bridges, Ch.4 summary table)
- [x] Scope bounded to prd-to-tdd package + sample docs
- [x] Strict vs narrative split explicit (§6)
- [x] Supersedes prior Ch.1 subsection order only; does not revert story-first prose rules
