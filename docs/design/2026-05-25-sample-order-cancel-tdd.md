---
title: "TDD: 주문 취소 API"
feature: order-cancel-api
mode: brownfield
prd_source: "docs/prd/order-cancel.md"
generated_at: 2026-05-25
validation_passed: false
review_rounds: 0
---

# 주문 취소 API — Technical Design Document

## 1. 서문

이 문서는 PM, 백엔드 개발자, 감사 담당자가 주문 취소 기능의 기술 설계를 공유하기 위해 작성한다. PRD `docs/prd/order-cancel.md`를 2026-05-25 기준으로 반영한다.

## 2. 배경과 문제

요약: 고객이 결제 완료 전 주문을 취소할 수 있어야 한다.

PRD는 취소 시 재고 복구와 선택적 환불을 요구한다. 범위는 B2C 웹 주문 API이다.

## 3. 현재 시스템

요약: 취소 endpoint는 status만 변경하며 환불은 없다.

`POST /orders/{id}/cancel`은 `OrderService.cancel`을 호출한다.

> **사실:** 취소 시 status만 cancelled로 변경한다.
> **근거:** [source:prd#cancel-flow] + `src/orders/cancel_handler.ts:8-22`

## 4. 갭과 설계 전환

요약: PRD의 환불 요구는 코드에 없으므로 PG 연동을 추가한다.

PRD는 paid 상태 취소 시 환불을 요구한다. 코드는 status 변경만 하므로 환불 연동은 미구현이다.

> **결정:** 취소 API에 PaymentGateway.refund 호출을 추가한다.
> **근거:** [source:stripe-refunds](https://stripe.com/docs/api/refunds)
> **코드:** `src/orders/cancel_handler.ts:18`

## 5. 목표 설계와 마무리

요약: cancel → refund → inventory restore 순으로 처리한다.

Webhook으로 환불 완료 후 최종 status를 확정한다. 롤아웃은 staging 1주 후 production이다.

> **사실:** inventory restore는 기존 InventoryService.release를 재사용한다.
> **근거:** [source:prd#inventory] + `src/inventory/service.ts:40-55`

열린 질문: partial refund 정책은 PRD에 미정의이다.
