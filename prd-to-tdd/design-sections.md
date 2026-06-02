# Design Sections — 요구사항 분석, 상위설계 & 상세설계

Chapters **2 (요구사항 분석)**, **5–7** structure *what* to build before *how* (4) and *how in detail* (6).

| Chapter | Name | Level | Reader |
|---------|------|-------|--------|
| **2** (###) | 요구사항 분석 | Requirements | PM, PO, lead, audit |
| **5** | 상위설계 | High-level | PM + dev + audit |
| **6** | 상세설계 | Low-level | Dev + audit |
| **7** | 마무리 | Closure | All |

**Forward-only rule:** Ch.5 names components and boundaries first; Ch.6 specifies interfaces and schemas for **those same components** — do not introduce a new major component in Ch.6 without introducing it in Ch.5.

---

## 요구사항 분석 vs 인수조건

| | Ch.2 `### 요구사항 분석` | Ch.6 `### 인수조건` |
|--|-------------------------|---------------------|
| Purpose | PRD 정제·분류·충돌·모호성·RTM | 완료의 객관적 판정 |
| ID | `FR-*`, `NFR-*`, `CON-*`, … | `AC-*` |
| Form | REQ tables + RTM | Given / When / Then |
| When | Before Ch.4 design forks | After Ch.5 component names exist |

Every **Must** `FR-*` → ≥1 RTM row → ≥1 `AC-*` in Ch.6 → ≥1 `T-*` in Ch.6 ### 테스트.

---

## Chapter 2 — `### 요구사항 분석` (required)

Placed **after** Ch.2 background prose (≥8 sentences, 2–4 paragraphs), **before** `## 3.`.

### Lead prose

- ≥2 sentences before the first table
- Last sentence must bridge to Ch.3 (e.g. FR **구현 상태** will be checked against code in the next chapter)

### Required blocks

| Block | Heading | Minimum (strict) |
|-------|---------|------------------|
| Functional | `#### 기능 요구 (FR)` | FR table ≥2 data rows; each row has `FR-n` + `[source:prd#…]` |
| Traceability | `#### 추적성 매트릭스 (RTM)` | ≥2 data rows linking PRD → REQ ID → (AC TBD or AC-n) |
| Non-functional | `#### 비기능 요구 (NFR)` | ≥1 row when PRD states NFR; else one prose sentence “NFR: none in PRD scope” |
| Constraints | `#### 제약·가정·의존성` | ≥1 row when PRD has constraints; else omit table + one sentence |
| Open items | `#### 모호·충돌·미결` | Required when ambiguity exists; `OQ-*` must appear in Ch.7 ### 열린 질문 |

### Brownfield — `구현 상태` column (FR table)

| Value | Meaning |
|-------|---------|
| 구현됨 | Code satisfies FR |
| 부분 | Some paths only |
| 미구현 | PRD requires, code lacks |
| PRD-only | In PRD, not in code (first labeled here, expanded in Ch.4) |
| 코드-only(문서화) | In code, not in PRD |

Greenfield: omit **구현 상태** column or use `N/A`.

### Phase 3

Copy [outline-template.md](outline-template.md) **Requirements inventory** into Ch.2 during Phase 4; do not invent FR IDs only in Ch.6.

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

### 인수조건

- Lead prose: AC are the **verifiable definition of done**; without them, implementation completeness cannot be judged
- Table: one row per functional PRD requirement (minimum ≥2 rows for strict profile)
- Each AC must be **objectively pass/fail** — use **Given / When / Then** or equivalent measurable criteria
- **완료 판정** column states how completion is verified (test ID, manual QA step, metric threshold)
- Tier-2: `[ref:A-n]` when citing PRD anchors; PRD column uses `[source:prd#…]`

**Required table schema:**

| AC ID | PRD | 인수조건 | 우선순위 | 완료 판정 |
|-------|-----|----------|----------|-----------|
| AC-1 | [source:prd#…] | Given … When … Then … | Must / Should | Test T-1 passes |

### 테스트

- Lead prose: which test layers (unit / integration / e2e) prove which ACs; brownfield: cite repo test conventions (`path` from Phase 2)
- Table: ≥1 test row per AC (minimum ≥2 rows for strict profile)
- **Layer** must be one of: `unit`, `integration`, `e2e` (or repo-equivalent)
- **CI gate** column: `yes` if merge-blocking, `no` if manual-only

**Required table schema:**

| Test ID | AC ID | Layer | 시나리오 | Fixture / Mock | CI gate |
|---------|-------|-------|----------|----------------|---------|
| T-1 | AC-1 | integration | … | … | yes |

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
| Acceptance criteria (Given/When/Then) | | ✓ |
| Test cases mapped to AC | | ✓ |
| Tier-1 architecture fork | Ch.4 only | |

---

## Outline addition (Phase 3)

For each feature, outline must list (see [outline-template.md](outline-template.md)):

- [ ] Requirements inventory (FR, NFR, RTM, open items) → Ch.2 ### 요구사항 분석
- [ ] Components to introduce in Ch.5 (names fixed before Ch.6)
- [ ] APIs/events for Ch.6
- [ ] Entities for Ch.6 data model
- [ ] Primary flow for Ch.5 data flow + Ch.6 detail
- [ ] ≥2 error branches mapped to Ch.6
- [ ] Acceptance criteria: ≥1 row per functional PRD requirement (outline → Ch.6 ### 인수조건)
- [ ] Tests: ≥1 row per AC with layer + CI gate (outline → Ch.6 ### 테스트)

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
| **인수조건** | ≥1 lead sentence + AC table (≥2 rows); each row has AC ID + PRD + verifiable condition + 완료 판정 |
| **테스트** | ≥1 lead sentence + test table (≥2 rows); each row maps Test ID → AC ID + layer + CI gate |

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
| Ch.6 | mermaid in ### 핵심 처리 흐름 (branching); ### 인수조건 + ### 테스트 tables; ≥1 lead sentence per ### |
| Ch.2–7 | No `요약:`, `#### 한눈에`, 6하 labels |
| Doc | ≥40 non-table sentences total |
| Ch.5–6 | No `> **사실:**`; use `[ref:A-n]` |
| Appendices | A required; B when Ch.4 has decision cards |

`--readability` is deprecated; prints warning and runs `--narrative`.

Strict depth (tables, components, errors) unchanged.
