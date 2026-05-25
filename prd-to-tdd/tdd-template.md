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

<!-- Who, Why, When; PRD source -->

## 2. 배경과 문제

<!-- What, Where from PRD; no implementation -->

## 3. 현재 시스템

<!-- Brownfield: As-Is. Greenfield: rename to "## 3. 시작점" -->

## 4. 갭과 설계 전환

<!-- Brownfield. Greenfield: "## 4. 설계 결정". Tier-1 **결정:** / **갈림:** blocks -->

## 5. 상위설계

<!-- See design-sections.md — required ### subsections below -->

### 아키텍처 개요

### 구성요소 및 책임

### 데이터 흐름

## 6. 상세설계

### API 및 인터페이스

### 데이터 모델

### 핵심 처리 흐름

## 7. 마무리

### 롤아웃·일정

### 리스크

### 열린 질문
```

## Chapter Title Variants by Mode

| Mode | Chapter 3 H2 | Chapter 4 H2 | Chapters 5–7 |
|------|--------------|--------------|--------------|
| `brownfield` | `## 3. 현재 시스템` | `## 4. 갭과 설계 전환` | 동일 |
| `greenfield` | `## 3. 시작점` | `## 4. 설계 결정` | 동일 |

Chapters 1, 2, 5, 6, 7 titles are **identical** in both modes.

## Filename Convention

`docs/design/YYYY-MM-DD-{{feature_slug}}-tdd.md`

See [design-sections.md](design-sections.md) for subsection content rules.
