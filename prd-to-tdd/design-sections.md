# Design Sections — Requirements, Proposed, Alternatives, Detail

Google **Design Doc** sections with PRD traceability extensions. See [narrative-rules.md](narrative-rules.md).

| Chapter | Design Doc | Level | Primary readers |
|---------|------------|-------|-----------------|
| **3** | Requirements | FR/NFR/RTM | PM, lead, audit |
| **5** | Proposed Solution | HLD | PM, dev, audit |
| **6** | Alternatives Considered | ADR (Tier-1) | Audit, lead |
| **7** | Detailed Design | LLD + AC + tests | Dev, QA |
| **8** | Rollout and Open Items | Closure | All |

**Ch.5 vs Ch.6:** Ch.5 = diagrams and component names only. Ch.6 = decision cards — not a second copy of HLD.

---

## Ch.3 Requirements

Placed after Ch.2 Background prose. Ch.2 has **no** requirement tables.

### Lead prose

- ≥2 sentences before first `####` table
- Last sentence bridges to Ch.4 (e.g. implementation status checked against existing code)

### Required blocks

| Block | Heading | Minimum (strict) |
|-------|---------|------------------|
| Functional | `#### Functional Requirements (FR)` | ≥2 rows; `FR-n` + `[source:prd#…]` |
| RTM | `#### Traceability Matrix (RTM)` | ≥2 rows |
| NFR | `#### Non-Functional Requirements (NFR)` | ≥1 row when PRD has NFR; else one sentence “NFR: none in scope” |
| Constraints | `#### Constraints / Assumptions / Dependencies` | ≥1 row when PRD has constraints |
| Open | `#### Ambiguity / Conflicts / Open (draft)` | When ambiguity exists; `OQ-*` → Ch.8 |

### Brownfield — `Impl. status` column

| Value | Meaning |
|-------|---------|
| Implemented | Code satisfies FR |
| Partial | Some paths only |
| Not implemented | PRD requires, code lacks |
| PRD-only | In PRD, not in code |
| Code-only | In code, not in PRD |

Every **Must** `FR-*` → RTM row → Ch.7 `AC-*` → Ch.7 `T-*`.

---

## Ch.5 Proposed Solution

### Lead chapter prose

- ≥8 sentences, 2–4 paragraphs before first `###`
- As-Is → gap → to-be ` ```mermaid ` **before** `### Architecture Overview`

### Required `###` subsections

| Subsection | Content |
|------------|---------|
| `### Architecture Overview` | ≥2 lead sentences + box diagram mermaid |
| `### Components and Responsibilities` | ≥2 components (`**Name** (existing|new)`) |
| `### Data Flow` | mermaid + ≥3 numbered steps |

**Forbidden in Ch.5:** `### Decision Summary`, Tier-1 ADR cards, `> **결정:**` stacks.

---

## Ch.6 Alternatives Considered

### Opening

- ≥2 sentences linking to Ch.5 Proposed Solution
- `### Decision Summary` table (≥1 data row)

### Decision cards

Per [citation-tiers.md](citation-tiers.md) Shape A or B under `### {topic}`.

---

## Ch.7 Detailed Design

### Required `###` subsections

| Subsection | Minimum (strict) |
|------------|------------------|
| `### APIs and Interfaces` | ≥3 API table data rows |
| `### Data Model` | ≥3 field rows per entity |
| `### Core Processing Flow` | mermaid + ≥2 error branches |
| `### Acceptance Criteria` | ≥2 AC rows; verifiable Given/When/Then |
| `### Tests` | ≥2 rows; layer + CI gate |

Optional: `### Cross-cutting Concerns` (security, privacy, observability).

Ch.7 reuses **exact component names** from Ch.5.

---

## Ch.8 Rollout and Open Items

| Subsection | Required |
|------------|----------|
| `### Rollout and Milestones` | yes |
| `### Risks` | table with ≥1 row |
| `### Open Questions` | every Ch.3 `OQ-*` listed |
