# TDD Output Template

Copy this skeleton. Replace `{{placeholders}}`. Write chapters **in order**; complete one before starting the next.

Complete [outline-template.md](outline-template.md) **before** filling this template.

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

{{One paragraph: who, why, when, PRD source.}}

### TL;DR

{{Sentence 1: problem. Sentence 2: solution. Sentence 3: impact.}}

### Goals / Non-Goals

**Goals:**
- …
- …
- …

**Non-Goals:**
- …
- …

### 이 문서 읽는 법

| 독자 | 먼저 볼 곳 | 목표 |
|------|-----------|------|
| PM | TL;DR → [§5](#5-상위설계) diagram | ~2분 |
| Dev | [§4](#4-갭과-설계-전환) → [§6](#6-상세설계) 스펙 인덱스 | ~5분 |
| 감사 | [§4](#4-갭과-설계-전환) 결정 요약 → [부록 A](#부록-a-출처코드-위치) | ~3분 |

### 목차

1. [서문](#1-서문)
2. [배경과 문제](#2-배경과-문제)
3. [현재 시스템 / 시작점](#3-현재-시스템)
4. [갭과 설계 전환 / 설계 결정](#4-갭과-설계-전환)
5. [상위설계](#5-상위설계)
6. [상세설계](#6-상세설계)
7. [마무리](#7-마무리)
- [부록 A. 출처·코드 위치](#부록-a-출처코드-위치)
- [부록 B. Ch.4 결정 전문](#부록-b-ch4-결정-전문)

## 2. 배경과 문제

<!-- What, Where from PRD; no implementation -->

## 3. 현재 시스템

<!-- Brownfield: As-Is. Greenfield: rename to "## 3. 시작점" -->

## 4. 갭과 설계 전환

<!-- Brownfield. Greenfield: "## 4. 설계 결정". Tier-1 **결정:** / **갈림:** blocks -->

### 결정 요약

| # | 주제 | 선택 | 상태 | 상세 |
|---|------|------|------|------|
| 1 | … | … | 확정 | 아래 **결정** block |

## 5. 상위설계

### 아키텍처 개요

요약: …

```mermaid
flowchart LR
  Client --> ApiLayer
  ApiLayer --> ServiceLayer
  ServiceLayer --> DataLayer
```

#### 한눈에
- …
- …
- …

### 구성요소 및 책임

요약: …

| Component | 신규/기존 | Responsibility | Trust boundary |
|-----------|-----------|----------------|----------------|
| **Example** | 기존 | … | internal |

[ref:A-1]

#### 한눈에
- …
- …
- …

### 데이터 흐름

요약: …

1. …
2. …
3. …
<!-- Mark (async) for webhook/queue -->

#### 한눈에
- …
- …
- …

## 6. 상세설계

### 스펙 인덱스

| Endpoint / Interface | Entity | Error codes |
|----------------------|--------|-------------|
| … | … | … |

### API 및 인터페이스

요약: …

#### `POST /example`

| Field | Type | Required | Note |
|-------|------|----------|------|
| … | … | … | … |

| Code | HTTP | When | Client action | Retry? |
|------|------|------|---------------|--------|
| … | … | … | … | … |

[ref:A-2]

### 데이터 모델

요약: …

#### `examples`

| Field | Type | Nullable | Constraint | Notes |
|-------|------|----------|------------|-------|
| id | uuid | no | PK | … |

[ref:A-3]

### 핵심 처리 흐름

요약: …

**Happy path:** …

**Errors:**
- … (retry …)
- … (fail …)

[ref:A-4]

## 7. 마무리

### 롤아웃·일정

### 리스크

| Risk | Impact | Mitigation |
|------|--------|------------|

### 열린 질문

## 부록 A. 출처·코드 위치

| ID | 주장 | PRD | Code | External URL |
|----|------|-----|------|--------------|
| A-1 | … | … | `path:line` | … |

## 부록 B. Ch.4 결정 전문

<!-- Copy Ch.4 > **결정:** / **갈림:** blocks verbatim -->
```

## Chapter Title Variants by Mode

| Mode | Chapter 3 H2 | Chapter 4 H2 | Chapters 5–7 |
|------|--------------|--------------|--------------|
| `brownfield` | `## 3. 현재 시스템` | `## 4. 갭과 설계 전환` | 동일 |
| `greenfield` | `## 3. 시작점` | `## 4. 설계 결정` | 동일 |

Chapters 1, 2, 5, 6, 7 titles are **identical** in both modes.

## Filename Convention

`docs/design/YYYY-MM-DD-{{feature_slug}}-tdd.md`

See [design-sections.md](design-sections.md) for subsection content rules and strict depth rubric.
