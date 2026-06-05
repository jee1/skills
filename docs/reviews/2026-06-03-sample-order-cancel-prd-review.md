---
feature: order-cancel
prd_source: docs/sample-prd-order-cancel.md
reviewed_at: 2026-06-03
readiness: needs-clarification
prd_review_path: standard
complexity_score: 2
phase_6_mode: A
dual_brain_used: false
finding_counts:
  critical: 0
  high: 1
  medium: 0
  low: 0
  amb: 1
  ctr: 0
  cmp: 0
  tst: 0
  trm: 0
  scp: 0
fr_draft_count: 2
oq_draft_count: 1
---

# PRD Review — 주문 취소

## Executive summary

Gate **needs-clarification** on **standard** path (Mode A, score 2): one Must-path ambiguity (partial refund policy). No contradictions. Safe to run `prd-to-tdd` if user accepts documenting OQ-1 in Ch.8.

## Coverage map

| Category | Status | Notes |
|----------|--------|-------|
| Problem statement | Clear | User pain stated |
| Goals & success criteria | Partial | Missing p99 target |
| User roles | Clear | Customer + admin |
| In-scope features | Clear | Cancel + refund |
| Out-of-scope | Clear | Returns after delivery |
| Primary user journey | Clear | ≥5 steps |
| Alternative paths | Partial | Partial shipment only implied |
| Error / empty states | Partial | Generic error copy |
| Acceptance criteria | Partial | Refund edge not testable |
| NFR (performance, security) | Partial | Latency without p99 |
| Edge cases | Partial | Split shipment |
| Terminology | Clear | Consistent order/refund terms |

## Findings

| severity | prd-anchor | ID | issue | suggested_fix |
|----------|------------|-----|-------|---------------|
| High | [source:prd#Refund] | AMB-1 | Partial refund rules undefined | Add table: order state → refund % |

## Contradictions (CTR-*)

None identified.

## Pre-inventory for prd-to-tdd

### Functional requirements (FR)

| FR ID | PRD | 요구 (shall) | 우선순위 | 비고 |
|-------|-----|--------------|----------|------|
| FR-1 | [source:prd#Cancel] | User shall cancel order before shipment | Must | … |
| FR-2 | [source:prd#Refund] | System shall refund per policy | Must | blocked by AMB-1 |

### Non-functional requirements (NFR)

| NFR ID | PRD | 요구 | 목표치 | 검증 |
|--------|-----|------|--------|------|
| NFR-1 | [source:prd#Performance] | Cancel API latency | p99 < 500ms | load test |

### Open / ambiguous (OQ)

| ID | 유형 | 설명 | prd-review finding |
|----|------|------|-------------------|
| OQ-1 | 모호 | Partial refund policy | AMB-1 |

## Clarification questions

1. For partially shipped orders, what refund % applies?
   - **Recommended:** Full refund for unshipped lines only; shipped lines follow return policy.

## Recommended next step

| Gate | Action |
|------|--------|
| needs-clarification | Resolve OQ-1 in PRD, re-run prd-review, then `prd-to-tdd` |
