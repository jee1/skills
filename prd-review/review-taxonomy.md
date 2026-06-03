# PRD Review Taxonomy

Use in Phase 2. Mark each row **Clear**, **Partial**, or **Missing**.  
**Partial** or **Missing** on bold rows usually produces Phase 3 findings.

## Coverage categories

### Functional scope & behavior

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Problem statement** | User problem in 1–2 testable sentences; not solution-first | Vague benefit, no user pain |
| **Goals & success criteria** | Measurable outcomes (metric, threshold, timeframe) | "Increase engagement", "better UX" |
| **User roles / personas** | Named actors with distinct permissions or goals | "Users" only, mixed admin/end-user |
| **In-scope features** | Each feature as step-based behavior | Summary bullets only |
| **Out-of-scope** | Explicit Non-Goals / not included list | Absent or "TBD" |

### Domain & data

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Entities & attributes** | Key objects named with fields | Implied only in UI copy |
| **Identity & uniqueness** | IDs, keys, dedup rules stated | "Same user" undefined |
| **Lifecycle / states** | State machine or enum + transitions | "Status" without values |
| **Volume / scale** | Order-of-magnitude assumptions | No scale guidance |

### Interaction & UX flow

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Primary user journey** | ≥5 ordered steps, sync points clear | One paragraph narrative |
| **Alternative paths** | Branches documented | Happy path only |
| **Error / empty / loading** | Per-state behavior | "Show error" without copy/action |
| **Accessibility / i18n** | Stated or explicitly N/A for scope | Assumed |

### Non-functional quality

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Performance** | Latency/throughput targets + measurement | "Fast", "<500ms" without p95/p99 |
| **Scalability** | Limits, sharding, rate limits | "Handle growth" |
| **Reliability** | Uptime, retry, idempotency | "Highly available" |
| **Security & privacy** | AuthN/Z, data classification, retention | "Secure" only |
| **Observability** | Logs, metrics, alerts | Omitted for backend features |
| **Compliance** | Regulatory constraints named | Assumed |

### Integration & dependencies

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **External APIs** | Services, failure modes, timeouts | "Integrate with X" |
| **Data import/export** | Formats, validation | Hand-wavy |
| **Versioning / compatibility** | Breaking change policy | Unspecified |

### Edge cases & failure

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Negative scenarios** | ≥2 explicit failure branches | None |
| **Concurrency / conflicts** | Last-write-wins or merge rules | Silent |
| **Rate limits / throttling** | Limits and user-visible behavior | Omitted |

### Constraints & tradeoffs

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Technical constraints** | Stack, hosting, timeline bounds | Missing for greenfield |
| **Rejected alternatives** | Why not approach B | Only one option |
| **Dependencies** | Blocking teams/systems | Hidden |

### Terminology & consistency

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Glossary** | One term per concept | client/customer/user interchange |
| **Priority labels** | Must/Should/Could or P0/P1 defined | All "important" |

### Completion signals (TDD-critical)

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **Acceptance criteria** | Per Must feature: pass/fail checks | Prose only, no AC section |
| **Definition of Done** | Reviewable checklist | "When QA approves" |

### Placeholders

| Category | Clear when | Partial / Missing signals |
|----------|------------|---------------------------|
| **TODO / TBD** | Zero blocking TBD on Must path | TBD on core flows |
| **Ambiguous adjectives** | Quantified or removed | robust, intuitive, seamless |

---

## Severity guidance (Phase 3)

| Severity | When to use |
|----------|-------------|
| **Critical** | `CTR-*`; conflicting Must requirements; safety/compliance gap |
| **High** | Must-path `AMB-*`, `CMP-*`, `TST-*`, `SCP-*` |
| **Medium** | Should-path gaps; `TRM-*` without behavior impact |
| **Low** | Style, minor wording; no implementation fork |

---

## Mapping to prd-to-tdd IDs

| Review | prd-to-tdd |
|--------|------------|
| `AMB-*`, unresolved | `OQ-*` type 모호 |
| `CTR-*`, unresolved | `OQ-*` type 상충 |
| `CMP-*`, unresolved | `OQ-*` type 미결 |
| `FR` pre-inventory row | `FR-*` in Ch.2 |
| `needs-user-confirm` tag | Phase 3b fork |
