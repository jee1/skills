# Examples — Good vs Bad TDD Excerpts

## Brownfield — Good (forward-only)

```markdown
## 3. 현재 시스템

요약: 주문 취소는 API 한 endpoint에서 상태만 바꾸며, 환불은 호출하지 않는다.

`POST /orders/{id}/cancel` 핸들러는 `OrderService.cancel`을 호출한다.

> **사실:** 취소 시 status만 `cancelled`로 변경한다.
> **근거:** [source:prd#cancel-flow] + `src/orders/cancel_handler.ts:8-22`

## 4. 갭과 설계 전환

요약: PRD는 환불 연동을 요구하지만, 코드에는 결제 모듈 호출이 없다.

PRD는 취소 시 자동 환불을 요구한다. 코드는 status 변경만 수행하므로 환불 연동은 미구현이다.

> **결정:** 취소 API에 PaymentGateway.refund 호출을 추가한다.
> **근거:** [source:stripe-refunds](https://stripe.com/docs/api/refunds)
> **코드:** `src/orders/cancel_handler.ts:18` (현재 status 변경만)
```

**Why good:** Ch.3 establishes code reality; Ch.4 first mentions PRD gap; no "as above".

---

## Brownfield — Bad

```markdown
## 4. 갭과 설계 전환

앞서 설명한 것처럼 환불이 없으므로 Stripe를 붙인다.

> **결정:** Stripe 사용
> **근거:** PRD
```

**Violations:** back-reference "앞서"; Tier-1 without official URL; gap not labeled in Ch.4 introduction.

---

## Greenfield — Good

```markdown
## 3. 시작점

요약: 도메인 코드는 없고, Node 20 + TypeScript 보일러플레이트만 있다.

`package.json`에 express와 typescript가 선언되어 있다. `src/` 디렉터리는 비어 있다. 애플리케이션 서비스나 DB 스키마는 존재하지 않는다.

> **사실:** 런타임 의존성은 express 4.x이다.
> **근거:** [source:prd#stack] + `package.json:14-20`

## 4. 설계 결정

요약: PRD의 REST API 요구에 맞춰 express 라우터 구조를 채택한다.

> **결정:** Express 4 기반 단일 API 프로세스로 시작한다.
> **근거:** [source:express-routing](https://expressjs.com/en/guide/routing.html)
> **코드:** (Greenfield — 코드 없음)
```

**Why good:** Ch.3 honest empty state; Ch.4 decisions with official URL; no fictional modules.

---

## Greenfield — Bad

```markdown
## 3. 시작점

UserService와 OrderRepository가 src/services에 있다.
```

**Violation:** fabricates modules that do not exist in greenfield repo.

---

## Mixed Audience — Good subsection pattern

```markdown
### 결제 연동

요약: 외부 PG 한 곳만 사용하고, webhook으로 최종 상태를 맞춘다.

Webhook 수신 endpoint는 `POST /webhooks/payment`로 분리한다. 서명 검증은 PG 문서의 HMAC-SHA256 방식을 따른다.
```

First line = PM; rest = dev.

---

## Multiple options — Good (documented fork)

```markdown
## 4. 설계 결정

요약: 저장소는 PostgreSQL과 MongoDB가 모두 가능하나, 트랜잭션 요구로 PostgreSQL을 권장한다.

PRD는 주문·재고·결제 간 일관성을 요구한다. 스키마 유연성만으로는 이 요구를 충족하기 어렵다.

> **갈림:** Primary datastore
> **대안:** (A) PostgreSQL — ACID 트랜잭션 (B) MongoDB — 문서 기반 유연 스키마
> **권장:** (A) PostgreSQL — PRD의 cross-entity 트랜잭션 요구
> **근거:** [source:postgresql-transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
> **코드:** (Greenfield — 코드 없음)
> **상태:** 권장(미확정)

## 5. 상위설계

요약: PostgreSQL 기준 단일 API + DB 2-tier.

### 아키텍처 개요
…

### 구성요소 및 책임
…

### 데이터 흐름
…

## 6. 상세설계

### API 및 인터페이스
…

### 데이터 모델
PostgreSQL `orders` / `items` draft …

### 핵심 처리 흐름
…

## 7. 마무리

### 롤아웃·일정
…

### 리스크
…

### 열린 질문

- **최종 선택 필요:** Primary datastore — PostgreSQL(권장) vs MongoDB 확정 필요
```

**Why good:** alternatives visible; one To-Be path (권장); open question matches `권장(미확정)`.

---

## Multiple options — Bad

```markdown
## 4. 설계 결정

PostgreSQL 또는 MongoDB를 사용할 수 있다. MongoDB로 진행한다.

> **결정:** MongoDB
```

**Violations:** other viable option ignored without `**갈림:**`; no rationale for rejecting PostgreSQL when PRD implies transactions.

---

## Multiple options — Bad (silent auto-pick)

```markdown
## 4. 설계 결정

> **결정:** Redis를 캐시로 사용한다.
```

**Violation:** when Kafka/RabbitMQ were equally viable and PRD silent — should be `**갈림:**` or user confirm first.
