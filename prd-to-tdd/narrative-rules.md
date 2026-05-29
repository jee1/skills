# Narrative Rules — Story-First TDD

TDD prose must read **front to back like a novel**. Each chapter builds on what earlier chapters established. **Do not use role labels** (`요약:`, `#### 한눈에`, `Who:`/`Why:`) — the reader should infer purpose from the writing.

Detail rules for Ch.5–6: [design-sections.md](design-sections.md).

## 기승전결 Mapping

| Chapter | Role | Narrative job |
|---------|------|---------------|
| 1. 서문 | 起 | Opening paragraph + scope; why this document exists |
| 2. 배경과 문제 | 起→承 | Problem and scope in connected prose |
| 3. 현재 시스템 / 시작점 | 承 | What exists today (code or scaffold) |
| 4. 갭과 설계 전환 / 설계 결정 | 转 | Gap → why change; Tier-1 decisions |
| 5. 상위설계 | 结 (macro) | Target architecture as a consequence of Ch.4 |
| 6. 상세설계 | 结 (micro) | Spec tables, **acceptance criteria**, **tests** grounded in Ch.5 names |
| 7. 마무리 | 结 (close) | Rollout, risks, open questions |

## 6하원칙 (embedded in prose — no labels)

Answer each dimension **inside normal sentences**. Never prefix lines with `Who:` / `Why:` / `누가:` / `왜:`.

| Chapter | Must answer (in prose) |
|---------|------------------------|
| 1 | Who reads this, why now, PRD source |
| 2 | What problem, where (scope/boundary) |
| 3 | What exists, how it works today |
| 4 | What changes, why, how (direction) |
| 5 | What the target system does, how at high level |
| 6 | What interfaces/entities exist, how in detail; **what proves done** (AC + tests) |
| 7 | When rollout, how to deploy, remaining risks |

**Minimum:** Ch.2, Ch.3, Ch.4 each **≥8 sentences** of non-table body (enforced by `--narrative`).

## Chapter bridges

The **last sentence** of chapter N must connect to the **first sentence** of chapter N+1:

- Shared domain noun (order, payment, API, …), **or**
- Explicit consequence words: `때문`, `따라`, `현재`, `PRD`, `미구현`, `갭`, …

Forbidden: temporal back-refs (`앞서`, `위에서`, `see above`) — **restate** needed context instead.

## Anti-label policy (Ch.2–7 body)

| Forbidden | Allowed |
|-----------|---------|
| `요약:` line prefix | Topic `###` titles (e.g. `### API 및 인터페이스`) |
| `#### 한눈에` | Ch.4 `### 결정 요약` (audit index table only) |
| `### TL;DR` in body | `## 목차`, `## 이 문서 읽는 법`, Ch.1 `### Goals / Non-Goals` |
| `Who:` / `Why:` / `누가:` / `왜:` … | `[ref:A-n]`, Ch.4 Tier-1 decision cards |

## Prose-then-table (Ch.5–6)

Each `###` subsection:

1. **Lead prose** — Ch.5: ≥2 sentences before diagram/lists/tables; Ch.6: ≥1 sentence before tables
2. **Structure** — mermaid (Ch.5 architecture), tables, numbered flows
3. **Tier-2** — `[ref:A-n]` inline; Appendix A row; **no** `> **사실:**` in Ch.5–6

Ch.6 may include a **dev index table** right after the chapter intro paragraph (no `###` heading). Introduce it in prose: “아래 표는 …”.

## Forward-Only Rules

1. **No temporal back-reference** — see forbidden list in validator (`validate-tdd.py`).
2. **Define before use** — introduce terms and component names before reusing them.
3. **Brownfield:** code reality in Ch.3; PRD-only in Ch.4 as `미구현`; conflict → code wins, labeled in Ch.4.
4. **Greenfield:** Ch.3 states no domain code; Ch.4 introduces decisions from PRD + stack.
5. **No repair appendix** — Appendix A/B are citation archives only.
6. **Static anchors OK** — `[§6](#6-상세설계)`, `[ref:A-3]`; not “see above”.

## Front matter (before ## 1. 서문)

1. `## 목차` — document map (first H2 after `#` title)
2. `## 이 문서 읽는 법` — reader path table

No prose between `#` title and `## 목차`.

## Ch.1 서문

- **Opening paragraph** (no subsection title): 3–5 sentences before `### Goals / Non-Goals`
- **Do not use** `### TL;DR`, `### 목차`, or `### 이 문서 읽는 법` inside Ch.1

Opening must lead into Ch.2.

## Paragraph breaks (Ch.2–4)

- **2–4 paragraphs** per chapter, separated by one blank line
- **1–4 sentences** per paragraph (split before a fifth sentence in the same block)
- Enforced by `--narrative` (`ch234-paragraph-runon`, `ch234-paragraph-sparse`)

## Flow diagrams (`--narrative`)

| Location | Diagram |
|----------|---------|
| Ch.4 (before `### 결정 요약`) | as-is → gap → to-be transition |
| Ch.5 `### 아키텍처 개요` | component box diagram (strict too) |
| Ch.5 `### 데이터 흐름` | sequence or flow mermaid |
| Ch.6 `### 핵심 처리 흐름` | flowchart with ≥2 error branches |

## Design Alternatives — When Multiple Options Exist

Use the decision tree in Phase 3 outline (unchanged):

| Situation | Ch.4 format | Ch.5–6 | Ch.7 |
|-----------|-------------|--------|------|
| Single clear winner | Shape A decision card | Follows decision | Standard |
| Real fork | Shape B + alternatives table + `권장(미확정)` | Follows **권장** | 열린 질문 |
| Tier-1 high impact | Ask user first | After confirm | Standard |

Ch.5–6 follow **one** narrative path (권장 or 확정). Component **names** first appear in Ch.5 prose; Ch.6 reuses them.

## Outline Self-Check (before drafting)

- [ ] Concept introduction order (outline rows)
- [ ] Ch.5 ≥2 component names; Ch.6 APIs/entities/flows/AC/tests mapped
- [ ] Bridge plan: last line of Ch.2→3, 3→4, 4→5 sketched
- [ ] Tier-1 in Ch.4; user confirm for `needs-user-confirm`
- [ ] No chapter depends on a later chapter

## Markdown — literal tilde (`~`)

Many Markdown renderers treat **unescaped** `~` as strikethrough delimiters and pair them across the document. A range like `A~Z` early in the file can turn everything until the next bare `~` (e.g. `~3분` in a table) into strikethrough.

**Rule:** Any tilde meant to appear as text must be written **`\\~`** (backslash + tilde).

| Use case | Write | Do not write |
|----------|-------|--------------|
| Range | `A\\~Z`, `1\\~5`, `v1\\~v2` | `A~Z` |
| Approximation | `\\~3분`, `\\~100ms` | `~3분` |
| Version span | `Node 18\\~20` | `Node 18~20` |

**Does not apply inside** fenced code blocks (`` ``` ``) — use normal `~` there.

Enforced by `validate-tdd.py` (`unescaped-tilde`).

## Common Violations

| Bad | Good |
|-----|------|
| `요약: API layer …` | “The cancel request enters through the API layer, which …” |
| `#### 한눈에` bullets repeating the section | One clear prose paragraph; tables hold spec |
| Ch.5 names a service never mentioned in Ch.4 | Ch.4 states the gap/decision that introduces the service |
| Telegraphic Ch.2 (“PRD requires X.”) | Full paragraph: who is affected, where in product, why it matters |
| `A~Z`, `~3분` in prose/tables | `A\\~Z`, `\\~3분` |
