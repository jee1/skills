# PRD Review Report Template

Copy into `docs/reviews/YYYY-MM-DD-<feature_slug>-prd-review.md` in the **target project**.

```markdown
---
feature: <feature_slug>
prd_source: <path or Google Docs URL>
reviewed_at: YYYY-MM-DD
readiness: ready | needs-clarification | blocked
dual_brain_used: true | false
finding_counts:
  critical: 0
  high: 0
  medium: 0
  low: 0
  amb: 0
  ctr: 0
  cmp: 0
  tst: 0
  trm: 0
  scp: 0
fr_draft_count: 0
oq_draft_count: 0
---

# PRD Review — <title>

## Executive summary

(2–4 sentences: readiness gate, blocker count, whether `prd-to-tdd` is recommended.)

## Coverage map

| Category | Status | Notes |
|----------|--------|-------|
| Problem statement | Clear / Partial / Missing | … |
| Goals & success criteria | … | … |
| User roles | … | … |
| In-scope features | … | … |
| Out-of-scope | … | … |
| Primary user journey | … | … |
| Error / empty states | … | … |
| Acceptance criteria | … | … |
| NFR (performance, security, …) | … | … |
| Edge cases | … | … |
| Terminology | … | … |

## Findings

| severity | prd-anchor | ID | issue | suggested_fix |
|----------|------------|-----|-------|---------------|
| High | [source:prd#…] | AMB-1 | … | … |

## Contradictions (CTR-*)

(Required section when any CTR exists; else write "None identified.")

| ID | Section A | Section B | conflict | resolution |
|----|-----------|-----------|----------|------------|
| CTR-1 | … | … | … | … |

## Pre-inventory for prd-to-tdd

### Functional requirements (FR)

| FR ID | PRD | 요구 (shall) | 우선순위 | 비고 |
|-------|-----|--------------|----------|------|
| FR-1 | [source:prd#…] | … | Must | … |

### Non-functional requirements (NFR)

| NFR ID | PRD | 요구 | 목표치 | 검증 |
|--------|-----|------|--------|------|
| NFR-1 | [source:prd#…] | … | … | … |

### Open / ambiguous (OQ)

| ID | 유형 | 설명 | prd-review finding |
|----|------|------|-------------------|
| OQ-1 | 모호 | … | AMB-1 |

### RTM draft (optional)

| PRD 앵커 | REQ ID | AC ID | 비고 |
|----------|--------|-------|------|
| [source:prd#…] | FR-1 | TBD | … |

### Tier-1 fork candidates (needs-user-confirm)

| Topic | Why fork | Tag |
|-------|----------|-----|
| … | … | needs-user-confirm |

## Clarification questions

(When `readiness: needs-clarification` — numbered, with recommended answer per question.)

1. …
   - **Recommended:** …

## Recommended next step

| Gate | Action |
|------|--------|
| ready | Run `prd-to-tdd` with `<prd_path>`; attach this review for FR/OQ seed |
| needs-clarification | Resolve OQ-* or run Phase 6 clarification; re-run prd-review |
| blocked | Rewrite PRD sections listed under CTR/AMB; consider `idea2planning` |
```
