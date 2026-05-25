# TDD Output Template

Copy this skeleton. Replace `{{placeholders}}`. Write chapters **in order**; complete one before starting the next.

```markdown
---
title: "TDD: {{feature_title}}"
feature: {{feature_slug}}
mode: {{brownfield|greenfield}}
prd_source: "{{path_or_google_docs_url}}"
generated_at: {{YYYY-MM-DD}}
validation_passed: false
review_rounds: 0
---

# {{feature_title}} — Technical Design Document

## 1. 서문

<!-- Who reads this, Why now, When this applies, PRD source one line -->

## 2. 배경과 문제

<!-- What problem (PRD), Where in product scope. No implementation yet. -->

## 3. 현재 시스템

<!-- Brownfield only. As-Is: architecture, data flow, key components. Tier-2 sources. -->
<!-- Greenfield: rename H2 to "## 3. 시작점" — scaffold, deps, empty dirs only. -->

## 4. 갭과 설계 전환

<!-- Brownfield: PRD↔code gaps; Tier-1 as **결정:** or **갈림:**+**권장:** -->
<!-- Greenfield: rename to "## 4. 설계 결정" — same block shapes -->
<!-- Ch.5 To-Be follows 권장/확정 only; 열린 질문 for 권장(미확정) -->

## 5. 목표 설계와 마무리

<!-- To-Be architecture, interfaces, rollout timing, risks, open questions. -->
```

## Chapter Title Variants by Mode

| Mode | Chapter 3 H2 | Chapter 4 H2 |
|------|--------------|--------------|
| `brownfield` | `## 3. 현재 시스템` | `## 4. 갭과 설계 전환` |
| `greenfield` | `## 3. 시작점` | `## 4. 설계 결정` |

Chapters 1, 2, 5 titles are identical in both modes.

## Filename Convention

`docs/design/YYYY-MM-DD-{{feature_slug}}-tdd.md`

Example: `docs/design/2026-05-25-order-cancel-api-tdd.md`
