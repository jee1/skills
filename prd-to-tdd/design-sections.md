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
- Diagram optional (mermaid allowed): box-level only, no field-level detail
- Reflect **확정** or **권장** choices from Ch.4 only

### 구성요소 및 책임

- List each component/module by name (first appearance if new)
- One-line responsibility per component
- External systems (PG, queue, auth provider) and trust boundaries
- Brownfield: note **신규** vs **기존** per component

> **사실:** blocks with Tier-2 citations where mapping to code or PRD

### 데이터 흐름

- Main happy-path flow across components (numbered steps)
- Key inputs/outputs at boundaries (not field schemas — those go in Ch.6)
- Async vs sync boundaries (webhook, queue)

---

## Chapter 6 — 상세설계 (required ### subsections)

Drill down into components named in Ch.5. Each subsection opens with **요약:**.

### API 및 인터페이스

- Endpoints, RPC, events, or public method signatures
- Request/response shape at field level (tables or bullet lists)
- Authn/authz per endpoint
- Idempotency, pagination, rate limits if applicable

> **사실:** or **결정:** blocks; link to OpenAPI/vendor docs when relevant

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

For each feature, outline must list:

- [ ] Components to introduce in Ch.5 (names fixed before Ch.6)
- [ ] APIs/events for Ch.6
- [ ] Entities for Ch.6 data model
- [ ] Primary flow for Ch.5 data flow + Ch.6 detail
