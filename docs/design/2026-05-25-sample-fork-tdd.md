---
title: "TDD: Fork Sample"
feature: fork-sample
mode: greenfield
prd_source: "docs/prd/x.md"
generated_at: 2026-05-25
validation_passed: false
review_rounds: 0
---

# Fork Sample — Technical Design Document

## 1. 서문
Doc for validator test.

## 2. 배경과 문제
Need a database.

## 3. 시작점
Empty src.

## 4. 설계 결정

> **갈림:** Primary datastore
> **대안:** (A) PostgreSQL (B) MongoDB
> **권장:** (A) PostgreSQL — transactions required
> **근거:** [source:pg](https://www.postgresql.org/docs/current/)
> **코드:** (Greenfield — 코드 없음)
> **상태:** 권장(미확정)

## 5. 상위설계

### 아키텍처 개요
요약: 단일 API 프로세스 + PostgreSQL.

### 구성요소 및 책임
- **ApiServer** (신규): HTTP
- **PostgreSQL** (신규): persistence

> **사실:** PostgreSQL을 권장 datastore로 가정한다.
> **근거:** [source:prd#data] + (Greenfield — 코드 없음)

### 데이터 흐름
Client → ApiServer → PostgreSQL

## 6. 상세설계

### API 및 인터페이스
`GET /health` — liveness

### 데이터 모델
`items(id, name)` — draft

> **사실:** items 테이블은 PostgreSQL relational model을 따른다.
> **근거:** [source:pg](https://www.postgresql.org/docs/current/)

### 핵심 처리 흐름
Health check returns 200.

## 7. 마무리

### 롤아웃·일정
TBD after DB choice.

### 리스크
Wrong DB choice → migration cost.

### 열린 질문

- **최종 선택 필요:** Primary datastore — PostgreSQL(권장) vs MongoDB
