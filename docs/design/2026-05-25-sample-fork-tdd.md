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

## 5. 목표 설계와 마무리

PostgreSQL schema draft.

### 열린 질문

- **최종 선택 필요:** Primary datastore — PostgreSQL(권장) vs MongoDB
