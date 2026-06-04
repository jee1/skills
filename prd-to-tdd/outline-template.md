# Phase 3 Outline — Design Doc Mapping

Complete **before Phase 4**. Minimum row counts are strict-profile gates.

**Enhanced path:** incorporate **Analysis Brief** (Phase 2b) and **Right Brain grill** (Phase 3b) into rows below before Phase 3c blueprint.

**Write order in Phase 4:** Ch.5 (Proposed) → Ch.6 (Alternatives) → Ch.7 (Detailed).

## Minimum row counts

| Artifact | Minimum | Rule |
|----------|---------|------|
| Ch.5 components | ≥2 | Names fixed here; Ch.7 reuses |
| Ch.7 APIs | ≥1 per user-facing action | Owner = Ch.5 component |
| Ch.7 entities | ≥1 per persisted object | Field names → Ch.7 tables |
| Primary flow steps | ≥5 | Same numbers in Ch.5 Data Flow + Ch.7 Core Flow |
| Error branches | ≥2 | Ch.7 flow + API error table |
| Acceptance criteria | ≥1 per functional PRD req (min ≥2 rows) | Ch.7 ### Acceptance Criteria |
| Tests | ≥1 per AC (min ≥2 rows) | Ch.7 ### Tests |

---

## Requirements inventory (Ch.3)

| Type | Minimum |
|------|---------|
| FR rows | ≥2 |
| NFR rows | ≥1 when PRD mentions NFR |
| RTM rows | ≥2 |

### Functional Requirements (FR)

| FR ID | PRD | Requirement (shall) | Priority | Impl. status | Notes |
|-------|-----|---------------------|----------|--------------|-------|

### RTM (draft)

| PRD anchor | REQ ID | AC ID | Ch.5–7 hook | Test ID |
|------------|--------|-------|-------------|---------|

---

## Concepts (introduction order)

1. …
2. …

## Tier-1 decisions (Ch.6)

| Topic | Tag | Notes |
|-------|-----|-------|
| … | single / multi-recommend / needs-user-confirm | … |

## Ch.5 components

| Component | new/existing | Responsibility | Trust boundary | PRD |
|-----------|--------------|----------------|----------------|-----|

## Ch.7 APIs

| Method | Path / Event | Owner | Auth | PRD |
|--------|--------------|-------|------|-----|

## Ch.7 entities

| Entity | Key fields | Notes | PRD |
|--------|------------|-------|-----|

## Flow + errors

| Step | From → To | Sync/async | Ch.7 detail | PRD |
|------|-----------|------------|-------------|-----|

## Acceptance criteria

| AC ID | PRD | Criterion | Priority | Done when |
|-------|-----|-----------|----------|-----------|

## Tests

| Test ID | AC ID | Layer | Scenario | CI gate |
|---------|-------|-------|----------|---------|

## Gaps (brownfield) / Decisions (greenfield)

- …
