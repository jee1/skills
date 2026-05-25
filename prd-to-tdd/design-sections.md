# Design Sections — 상위설계 & 상세설계

Chapters **5–7** deliver the target (To-Be) design after context (1–3) and decisions (4).

| Chapter | Name | Level | Reader |
|---------|------|-------|--------|
| **5** | 상위설계 | High-level | PM + dev + audit |
| **6** | 상세설계 | Low-level | Dev + audit |
| **7** | 마무리 | Closure | All |

**Forward-only rule:** Ch.5 names components and boundaries first; Ch.6 specifies interfaces and schemas for **those same components** — do not introduce a new major component in Ch.6 without introducing it in Ch.5.

---

## Chapter 5 — 상위설계 (required ### subsections)

Write all three subsections. Each opens with **lead prose** (≥2 sentences) — no `요약:` prefix.

### 아키텍처 개요

- Lead prose: why this shape follows Ch.4 decisions; where the feature sits in the product
- **Required** mermaid (box-level only)
- Tier-2: `[ref:A-n]` inline (Appendix A), not `> **사실:**`

### 구성요소 및 책임

- Lead prose introducing the component set, then `- **Name** (신규|기존): responsibility` bullets
- ≥2 named components; brownfield: every component labeled

### 데이터 흐름

- Lead prose on happy-path intent, then ≥3 numbered steps; mark `(async)` on queue/webhook boundaries

---

## Chapter 6 — 상세설계 (required ### subsections)

Optional **dev index table** after Ch.6 intro paragraph (no `###` heading), introduced in prose.

Each `###` opens with **≥1 lead sentence**, then tables. Drill down into Ch.5 component names.

### API 및 인터페이스

- Endpoint tables + error tables when HTTP; auth, idempotency as applicable
- Tier-2: `[ref:A-n]` + Appendix A URL column

### 데이터 모델

- Entity field tables (≥3 field rows), constraints, migration note if brownfield

### 핵심 처리 흐름

- Happy path + ≥2 error/retry branches; same component names as Ch.5

---

## Chapter 7 — 마무리 (required ### subsections)

### 롤아웃·일정

- Phases, feature flags, migration order, **When** (6하원칙)

### 리스크

- Technical and operational risks + mitigation one line each

### 열린 질문

- Unresolved items; **required** if any Ch.4 `권장(미확정)`
- Format: `- **최종 선택 필요:** …` or `- …`

No new Tier-1 decisions in Ch.7 unless escalated as open question.

---

## What NOT to put where

| Content | 상위설계 (5) | 상세설계 (6) |
|---------|-------------|-------------|
| Box diagram | ✓ | |
| Field-level schema | | ✓ |
| HTTP path + body fields | | ✓ |
| “PaymentService handles refunds” | ✓ | |
| Refund API request JSON | | ✓ |
| Tier-1 architecture fork | Ch.4 only | |

---

## Outline addition (Phase 3)

For each feature, outline must list (see [outline-template.md](outline-template.md)):

- [ ] Components to introduce in Ch.5 (names fixed before Ch.6)
- [ ] APIs/events for Ch.6
- [ ] Entities for Ch.6 data model
- [ ] Primary flow for Ch.5 data flow + Ch.6 detail
- [ ] ≥2 error branches mapped to Ch.6

**Phase 4 gate:** Do not draft until outline row counts meet minimums in outline-template.md.

---

## Depth rubric (strict profile — enforced by `validate-tdd.py`)

Default validation is **strict**. Use `python scripts/validate-tdd.py --lenient` only for legacy drafts.

### Every Ch.5–6 ### subsection

| Rule | Minimum |
|------|---------|
| Lead prose | ≥120 characters of non-table, non-mermaid body per ### (strict) |
| Tier-2 trace | `[ref:A-n]` in body + Appendix A row (`--narrative`) |

### Chapter 5 — 상위설계

| Subsection | Minimum content |
|------------|-----------------|
| **아키텍처 개요** | ≥2 lead sentences + mermaid (box-level) |
| **구성요소 및 책임** | ≥2 lead sentences + ≥2 `- **Name** (신규\|기존): …` |
| **데이터 흐름** | ≥2 lead sentences + ≥3 numbered steps |

### Chapter 6 — 상세설계

| Subsection | Minimum content |
|------------|-----------------|
| **API 및 인터페이스** | ≥1 lead sentence + API table (≥3 data rows) + error table when HTTP |
| **데이터 모델** | ≥1 lead sentence + entity table (≥3 field rows) |
| **핵심 처리 흐름** | ≥1 lead sentence + happy path + ≥2 error/retry branches |

### Required table schemas

**API (per endpoint):**

| Field | Type | Required | Note |
|-------|------|----------|------|

Plus error table when HTTP:

| Code | HTTP | When | Client action | Retry? |
|------|------|------|---------------|--------|

**Entity:**

| Field | Type | Nullable | Constraint | Notes |
|-------|------|----------|------------|-------|

**State (when lifecycle):**

| State | Enter trigger | Exit trigger | Side effects |
|-------|---------------|--------------|--------------|

### Cross-chapter rules

- Every **Name** in Ch.5 ### 구성요소 must appear ≥1× in Ch.6.
- No field-level HTTP body in Ch.5; no new major component in Ch.6 without Ch.5 row.
- PRD coverage: each functional requirement → ≥1 outline row → ≥1 sentence or table row in Ch.5–6.

See [examples.md](examples.md) § Ch.5–6 depth for full good/bad excerpts.

---

## Narrative profile (enforced by `validate-tdd.py --narrative`)

| Area | Rule |
|------|------|
| Ch.1 | `## 목차` → `## 이 문서 읽는 법` → opening ≥3 sentences → `### Goals / Non-Goals` |
| Ch.2–4 | Each ≥8 sentences; **2–4 paragraphs** (blank lines); bridges Ch.2→3, 3→4, 4→5 |
| Ch.4 | ` ```mermaid ` transition before `### 결정 요약`; summary table ≥1 row |
| Ch.5 | mermaid in ### 아키텍처 개요 + ### 데이터 흐름; ≥2 lead sentences per ### |
| Ch.6 | mermaid in ### 핵심 처리 흐름 (branching); ≥1 lead sentence per ### |
| Ch.2–7 | No `요약:`, `#### 한눈에`, 6하 labels |
| Doc | ≥40 non-table sentences total |
| Ch.5–6 | No `> **사실:**`; use `[ref:A-n]` |
| Appendices | A required; B when Ch.4 has blockquotes |

`--readability` is deprecated; prints warning and runs `--narrative`.

Strict depth (tables, components, errors) unchanged.
