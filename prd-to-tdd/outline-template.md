# Phase 3 Outline Template — Ch.5–6 Mapping

Complete this **before Phase 4 drafting**. Every row must expand into Ch.5 or Ch.6 prose. Do not start drafting until minimum row counts are met.

## Minimum row counts (strict profile)

| Artifact | Minimum | Rule |
|----------|---------|------|
| Ch.5 components | ≥2 (≥1 per PRD actor/system) | Names fixed here; Ch.6 uses same names |
| Ch.6 APIs/events | ≥1 per user-facing action | Each maps to one Ch.5 component owner |
| Ch.6 entities | ≥1 per persisted object | Field names listed here become Ch.6 table rows |
| Primary flow steps | ≥5 | Same step numbers in Ch.5 ### 데이터 흐름 and Ch.6 ### 핵심 처리 흐름 |
| Error branches | ≥2 | Listed here; expanded in Ch.6 flow + API error table |
| Acceptance criteria | ≥1 per functional PRD requirement (min ≥2 rows) | Verifiable pass/fail; Ch.6 ### 인수조건 |
| Tests | ≥1 test row per AC (min ≥2 rows) | Maps AC → layer + scenario; Ch.6 ### 테스트 |

## PRD traceability

Every functional requirement in the PRD must map to ≥1 row below. Tag with `[source:prd#…]`.

---

## Requirements inventory (Ch.2 ### 요구사항 분석)

Complete before Ch.4 drafting. IDs here become Ch.2 tables; AC IDs filled in Phase 4 Ch.6.

| Type | Minimum | Rule |
|------|---------|------|
| FR rows | ≥2 (≥1 per functional PRD requirement) | `FR-1`, `FR-2`, …; each has `[source:prd#…]` |
| NFR rows | ≥1 when PRD mentions performance/security/availability | `NFR-1`, … |
| CON/ASM/DEP | ≥1 row total when constraints exist in PRD | `CON-*`, `ASM-*`, `DEP-*` |
| RTM rows | ≥2 | Every Must FR → ≥1 RTM row; AC ID may be `TBD` until Ch.6 |

### Functional requirements (FR)

| FR ID | PRD | 요구 설명 (shall) | 우선순위 | 구현 상태 (brownfield) | 비고 |
|-------|-----|-------------------|----------|------------------------|------|
| FR-1 | [source:prd#…] | … | Must | 미구현 | … |

### Non-functional requirements (NFR)

| NFR ID | PRD | 요구 | 목표치 | 검증 방법 |
|--------|-----|------|--------|-----------|
| NFR-1 | [source:prd#…] | … | … | … |

### Constraints / assumptions / dependencies

| 유형 | ID | 내용 | 영향 |
|------|-----|------|------|
| … | … | … | … |

### Open / ambiguous (link to Ch.7)

| ID | 유형 | 설명 | 처리 |
|----|------|------|------|
| OQ-1 | 모호 | … | Ch.7 |

### RTM (draft)

| PRD 앵커 | REQ ID | AC ID | Ch.5–6 hook | Test ID |
|----------|--------|-------|-------------|---------|
| [source:prd#…] | FR-1 | TBD | … | TBD |

---

## Concepts (introduction order)

1. …
2. …

## Tier-1 decisions (Ch.4)

| Topic | Tag | Notes |
|-------|-----|-------|
| … | single / multi-recommend / needs-user-confirm | … |

## Ch.5 components (names fixed)

| Component | 신규/기존 | Responsibility | Trust boundary | PRD |
|-----------|-----------|----------------|----------------|-----|
| **ExampleService** | 기존 | … | internal | [source:prd#…] |

## Ch.6 APIs / events

| Method | Path or Event | Owner component | Auth | PRD |
|--------|---------------|-----------------|------|-----|
| POST | `/example` | **ExampleService** | Bearer | [source:prd#…] |

## Ch.6 entities

| Entity | Key fields (name:type) | Notes | PRD |
|--------|------------------------|-------|-----|
| `examples` | id:uuid, status:enum | … | [source:prd#…] |

## Primary flow + errors

| Step | From → To | Sync/async | Ch.6 detail | PRD |
|------|-----------|------------|-------------|-----|
| 1 | Client → API | sync | happy path | … |
| … | … | … | … | … |

## Error branches (≥2)

| Condition | HTTP / code | Handler | Retry? | PRD |
|-----------|-------------|---------|--------|-----|
| PG timeout | 502 + `PAYMENT_TIMEOUT` | queue retry | yes | … |

## Acceptance criteria (Ch.6 ### 인수조건)

Every functional PRD requirement → ≥1 AC row. Use **Given / When / Then** or an equally verifiable pass/fail statement.

| AC ID | PRD | 인수조건 | 우선순위 | 완료 판정 |
|-------|-----|----------|----------|-----------|
| AC-1 | [source:prd#…] | Given … When … Then … | Must | Test T-1 passes |

## Tests (Ch.6 ### 테스트)

Each AC must have ≥1 test row. Brownfield: note existing test file paths from repo.

| Test ID | AC ID | Layer | 시나리오 | Fixture / Mock | CI gate |
|---------|-------|-------|----------|----------------|---------|
| T-1 | AC-1 | integration | … | stripe mock + test DB | yes |

## Brownfield gaps / Greenfield decisions

- …
