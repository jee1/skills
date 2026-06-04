# Narrative Rules — Design Doc + 기승전결

Output is a **Google Design Doc** skeleton (8 numbered H2 chapters). Prose must read **front to back** like a novel: each chapter builds on the prior one. **Forward-only** — no temporal back-references.

Detail rules for Proposed / Alternatives / Detailed Design: [design-sections.md](design-sections.md).

## Document skeleton (Design Doc)

| # | H2 (brownfield) | H2 (greenfield) | Design Doc section |
|---|-----------------|-----------------|-------------------|
| 1 | Overview | Overview | Overview + `### Goals / Non-Goals` |
| 2 | Background | Background | Background / Context |
| 3 | Requirements | Requirements | Requirements trace (PRD extension) |
| 4 | Existing Solution | Starting Point | Existing solution |
| 5 | Proposed Solution | Proposed Solution | Proposed solution (architecture) |
| 6 | Alternatives Considered | Alternatives Considered | Alternatives + ADR cards |
| 7 | Detailed Design | Detailed Design | Detailed design + testability |
| 8 | Rollout and Open Items | Rollout and Open Items | Rollout, risks, open questions |

**Write order (Phase 4):** Ch.5 Proposed → Ch.6 Alternatives → Ch.7 Detailed (then Ch.8 if not drafted with Ch.1–4).

**Read order:** Ch.1 → Ch.2 → Ch.3 → Ch.4 → Ch.5 → Ch.6 → Ch.7 → Ch.8 (linear). Optional skim: Ch.5 diagram → Ch.6 `### Decision Summary` → Ch.7 AC.

## 기승전결 (narrative arc)

| Chapter | Role | Narrative job |
|---------|------|---------------|
| 1 Overview | 起 | Why this doc; who reads; PRD source; Goals/Non-Goals |
| 2 Background | 起→承 | Problem, scope, motivation (prose only) |
| 3 Requirements | 承 | FR/NFR/RTM tables — bridge to existing/proposed |
| 4 Existing / Starting Point | 承 | As-Is or scaffold; FR **구현 상태** grounding |
| 5 Proposed Solution | 转 | Gap → to-be; HLD diagrams; **no** decision cards |
| 6 Alternatives Considered | 转→结 | Tier-1 ADR cards after architecture is shown |
| 7 Detailed Design | 结 (micro) | APIs, entities, flows, AC, tests |
| 8 Rollout and Open Items | 结 (close) | Deploy, risks, `OQ-*` from Ch.3 |

## Layer rules (what goes where)

| Layer | Chapter | Belongs | Does **not** belong |
|-------|---------|---------|---------------------|
| Requirements | Ch.3 | `FR-*`, RTM, `OQ-*` draft | Tier-1 decision cards |
| As-Is | Ch.4 | Code/scaffold reality | Target architecture diagrams |
| **Proposed** | Ch.5 | Gap, mermaid, `### Architecture Overview`, components, data flow | `### Decision Summary`, ADR cards |
| **Alternatives** | Ch.6 | `### Decision Summary`, Shape A/B cards | Duplicate HLD from Ch.5 |
| **Detail** | Ch.7 | APIs, entities, flow, AC, tests, optional `### Cross-cutting Concerns` | New major component names |

Ch.6 opening **must** state that decisions **implement Ch.5** (e.g. “The Proposed Solution in Ch.5 requires …; this chapter locks Tier-1 choices.”).

## 6하원칙 (embedded in prose — no labels)

Never prefix lines with `Who:` / `Why:` / `누가:` / `왜:`. Answer inside normal sentences.

| Chapter | Must answer (in prose) |
|---------|------------------------|
| 1 | Who reads this, why now, PRD source |
| 2 | What problem, where (scope) |
| 3 | (tables carry REQ IDs; lead prose bridges to Ch.4) |
| 4 | What exists today |
| 5 | What changes; target structure |
| 6 | Which Tier-1 choices; why; alternatives |
| 7 | Interfaces, entities, how; what proves done |
| 8 | When rollout; risks; remaining questions |

**Minimum prose:** Ch.2, Ch.4, Ch.5, Ch.6 each **≥8 sentences** in non-table body (`--narrative`). Ch.3 may be table-heavy if lead prose ≥80 chars.

## Chapter bridges

The **last sentence** of chapter N must connect to the **first sentence** of chapter N+1 (shared domain noun or `때문`, `따라`, `현재`, `PRD`, `미구현`, `갭`, …).

Forbidden: `앞서`, `위에서`, `see above`, `later in this document` — **restate** context instead.

## Anti-label policy (Ch.2–8 body)

| Forbidden | Allowed |
|-----------|---------|
| `요약:` line prefix | Topic `###` titles |
| `#### 한눈에` | Ch.6 `### Decision Summary` (index table only) |
| `### TL;DR` in body | `## 목차`, `## How to Read`, Ch.1 `### Goals / Non-Goals` |
| `Who:` / `Why:` labels | `[ref:A-n]`, Ch.6 decision cards |

## Prose-then-table (Ch.5–7)

Each `###` subsection: lead prose first (Ch.5 architecture ###: ≥2 sentences; Ch.7: ≥1), then mermaid/tables.

Ch.7 may include a **dev index table** after chapter intro (no `###` heading), introduced in prose.

## Forward-only rules

1. No temporal back-reference (validator list in `validate-tdd.py`).
2. Define before use — component names first in Ch.5, reused in Ch.7.
3. **Brownfield:** code wins on PRD conflict; label in Ch.5 gap prose.
4. **Greenfield:** Ch.4 = scaffold only; no fictional As-Is modules.
5. Appendices A/B = citation archives only — no repair narrative.

## Front matter (before `## 1. Overview`)

1. `## 목차`
2. `## How to Read This Doc`

No prose between `#` title and `## 목차`.

## Ch.1 Overview

- Opening paragraph (3–5 sentences) before `### Goals / Non-Goals`
- No `### 목차` or `### How to Read` inside Ch.1

## Flow diagrams (`--narrative`)

| Location | Diagram |
|----------|---------|
| Ch.5 (before `### Architecture Overview`) | as-is → gap → to-be |
| Ch.5 `### Architecture Overview` | component box mermaid |
| Ch.5 `### Data Flow` | sequence/flow mermaid |
| Ch.7 `### Core Processing Flow` | flowchart with ≥2 error branches |

## Design alternatives

| Situation | Ch.6 format | Ch.5–7 | Ch.8 |
|-----------|-------------|--------|------|
| Single winner | Shape A card | Ch.5 shows chosen structure | Standard |
| Real fork | Shape B + `권장(미확정)` | Ch.5 shows **권장** path only | Open Questions |
| Tier-1 high impact | Ask user (Phase 3b) | After confirm | Standard |

## Outline self-check (Phase 3)

- [ ] Requirements inventory complete (Ch.3 rows)
- [ ] Ch.5 ≥2 component names; Ch.7 APIs/entities/flows/AC/tests mapped
- [ ] Bridge plan: Ch.2→3, 3→4, 4→5, 5→6, 6→7 sketched
- [ ] Tier-1 tags land in Ch.6; user confirm for `needs-user-confirm`

## Literal tilde (`~`)

Write **`\\~`** in prose/tables (`A\\~Z`, `\\~3분`). Bare `~` breaks Markdown strikethrough. OK inside ` ``` ` fences.
