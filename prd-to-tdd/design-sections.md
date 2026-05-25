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

Write all three subsections. Each opens with a **요약:** line.

### 아키텍처 개요

- System context: where this feature sits in the product
- Layering (API / service / data / external)
- Diagram **required** (mermaid): box-level only, no field-level detail
- Reflect **확정** or **권장** choices from Ch.4 only
- End subsection with `#### 한눈에` (3 PM-readable bullets)
- Tier-2 facts: `[ref:A-n]` inline (Appendix A), not `> **사실:**`

### 구성요소 및 책임

- List each component/module by name (first appearance if new)
- One-line responsibility per component
- External systems (PG, queue, auth provider) and trust boundaries
- Brownfield: note **신규** vs **기존** per component
- Tier-2: `[ref:A-n]` where mapping to code or PRD

### 데이터 흐름

- Main happy-path flow across components (numbered steps)
- Key inputs/outputs at boundaries (not field schemas — those go in Ch.6)
- Async vs sync boundaries (webhook, queue)

---

## Chapter 6 — 상세설계 (required ### subsections)

**Reference mode:** Open with `### 스펙 인덱스` (before other ###). In each subsection: **요약:** → tables first → ≤2 sentences prose → `[ref:A-n]` for Tier-2.

Drill down into components named in Ch.5. Each ### opens with **요약:**.

### API 및 인터페이스

- Endpoints, RPC, events, or public method signatures
- Request/response shape at field level (tables or bullet lists)
- Authn/authz per endpoint
- Idempotency, pagination, rate limits if applicable
- Tier-2: `[ref:A-n]`; link to OpenAPI/vendor docs in Appendix A URL column

### 데이터 모델

- Tables, collections, or entities with fields and types
- Keys, indexes, constraints, relationships
- Migration note one line if brownfield schema change

### 핵심 처리 흐름

- Step logic for main use cases (cancel, refund, etc.)
- State transitions (allowed states + triggers)
- Error branches at high granularity (which error code / retry)
- Sequence acceptable; must reference components from Ch.5 by same name

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
| Opens with **요약:** | First content line |
| Substance | ≥120 characters per ### |
| Tier-2 trace | `[ref:A-n]` in body + Appendix A row (readability profile) |

### Chapter 5 — 상위설계

| Subsection | Minimum content |
|------------|-----------------|
| **아키텍처 개요** | **요약:** + system context + named layers; **required** mermaid (box-level only); `#### 한눈에` (3 bullets) |
| **구성요소 및 책임** | **요약:** + ≥2 components as `- **Name** (신규\|기존): responsibility`; brownfield: every component labeled |
| **데이터 흐름** | **요약:** + ≥3 numbered steps (`1.` …); mark `(async)` on webhook/queue boundaries |

### Chapter 6 — 상세설계

| Subsection | Minimum content |
|------------|-----------------|
| **API 및 인터페이스** | **요약:** + markdown table per endpoint (see below); auth column required when HTTP |
| **데이터 모델** | **요약:** + entity field table (≥3 field rows) with types and constraints |
| **핵심 처리 흐름** | **요약:** + happy path + ≥2 error/retry branches; state table if lifecycle exists |

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

## Readability profile (enforced by `validate-tdd.py --readability`)

| Area | Rule |
|------|------|
| Ch.1 | `### TL;DR`, `### Goals / Non-Goals`, `### 이 문서 읽는 법`, `### 목차` |
| Ch.4 | `### 결정 요약` table ≥1 data row |
| Ch.5 | mermaid fence in ### 아키텍처 개요; `#### 한눈에` (3 bullets) per ### |
| Ch.6 | `### 스펙 인덱스` table before other ###; tables before prose |
| Ch.5–6 | No `> **사실:**`; use `[ref:A-n]` |
| Appendices | A required; B required when Ch.4 has blockquotes |

Strict depth rubric (120 chars, tables, components) unchanged. Inline `> **사실:**` per Ch.5–6 ### **removed** — replaced by Appendix A coverage.
