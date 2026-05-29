# Citation Tiers

Every technical claim in **Chapters 2–6** must be traceable. Tier depends on claim type. Tier-1 uses Ch.4 **decision cards** (see below); Tier-2 uses `[ref:A-n]` inline with a row in **Appendix A** (see readability profile in [design-sections.md](design-sections.md)).

**Chapter roles:** Ch.4 = decisions; Ch.5 = high-level To-Be; Ch.6 = interfaces/schemas/flows. See [design-sections.md](design-sections.md).

## Tier-1 — Core Design Decisions

**When required:** architecture choice, security model, datastore, auth strategy, protocol, breaking change, major library adoption.

Use **one of two card shapes** per topic (see [narrative-rules.md](narrative-rules.md) decision tree). Each Tier-1 topic is a `### {주제}` subsection **after** `### 결정 요약`.

**Do not** stack bare blockquote lines (`> **결정:**` …) as the primary layout — readers cannot scan them. Blockquotes are **legacy** only; new TDDs use decision cards.

---

### Shape A — Single clear choice

**Structure (in order):**

1. **Lead prose** — 1–2 sentences: why this topic matters for PRD/code
2. **Metadata table**

| 항목 | 내용 |
|------|------|
| 결정 | {one clear sentence} |
| 상태 | 확정 |
| 코드 | `{path:line}` or `(Greenfield — 코드 없음)` |

3. **`**근거 설명:**`** — ≥2 sentences in normal prose explaining **why** this choice fits PRD, code reality, and constraints. Links alone are not enough.
4. **`**참고:**`** — official URLs, each with a **one-line annotation** (what the reader should take from that doc)

**Example (Brownfield):**

```markdown
### JWT 인증 방식

PRD는 모바일·SPA 클라이언트를 지원하므로, 브라우저 쿠키만으로는 cross-origin API 호출을 처리하기 어렵다.

| 항목 | 내용 |
|------|------|
| 결정 | 기존 세션 쿠키에 JWT access + refresh rotation을 추가한다 |
| 상태 | 확정 |
| 코드 | `src/auth/session.py:18` — 현재 HttpOnly 쿠키 세션 |

**근거 설명:** Access token은 각 API 호출마다 Bearer 헤더로 전달되어 무상태 확장이 가능하다. Refresh rotation은 탈취된 refresh token 재사용을 탐지할 수 있어 PRD의 세션 보안 요구를 충족한다. 기존 쿠키 세션 코드는 refresh endpoint까지 점진 이전 대상으로 남긴다.

**참고:** [RFC 6750 Bearer Token](https://datatracker.ietf.org/doc/html/rfc6750) — Bearer 헤더 표준; [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) — OAuth2/JWT 구현 패턴
```

**Example (Greenfield):**

```markdown
### Primary datastore

| 항목 | 내용 |
|------|------|
| 결정 | PostgreSQL을 primary datastore로 채택한다 |
| 상태 | 확정 |
| 코드 | (Greenfield — 코드 없음) |

**근거 설명:** PRD는 주문·재고·결제 간 트랜잭션 일관성을 요구한다. PostgreSQL ACID 트랜잭션이 cross-entity 업데이트를 단일 commit으로 묶을 수 있다.

**참고:** [PostgreSQL Documentation](https://www.postgresql.org/docs/current/) — 트랜잭션·제약 모델
```

---

### Shape B — Documented fork

Use when 2–3 viable options exist and no clear winner without stakeholder input.

**Structure (in order):**

1. **Lead prose** — why this fork exists
2. **Metadata table**

| 항목 | 내용 |
|------|------|
| 갈림 | {topic name} |
| 권장 | (A) … |
| 상태 | 권장(미확정) |
| 코드 | `{path:line}` or `(Greenfield — 코드 없음)` |

3. **Alternatives comparison table** — **required**; one row per option (max 3)

| 대안 | 설명 | 장점 | 단점 | PRD/코드 적합도 |
|------|------|------|------|-----------------|
| (A) … | … | … | … | 높음 — … |
| (B) … | … | … | … | 낮음 — … |

4. **`**권장 이유:**`** — ≥2 sentences: why the recommended option wins **for this PRD/codebase**
5. **`**참고:**`** — official URL(s) supporting the **권장** option, with one-line annotations

After user confirms, rewrite as Shape A with `상태: 확정` and remove the alternatives table (or mark rejected options in prose).

**Example:**

```markdown
### Primary datastore

PRD는 주문·재고·결제 간 일관성을 요구한다. 문서 DB와 RDBMS 모두 기술적으로 가능하나 트랜잭션 모델이 다르다.

| 항목 | 내용 |
|------|------|
| 갈림 | Primary datastore |
| 권장 | (A) PostgreSQL |
| 상태 | 권장(미확정) |
| 코드 | (Greenfield — 코드 없음) |

| 대안 | 설명 | 장점 | 단점 | PRD/코드 적합도 |
|------|------|------|------|-----------------|
| (A) PostgreSQL | 관계형 RDBMS | ACID 트랜잭션, JOIN | 스키마 변경 비용 | 높음 — PRD §3.2 cross-entity 트랜잭션 |
| (B) MongoDB | 문서 DB | 스키마 유연, 빠른 iteration | 멀ti-doc 트랜잭션 제약 | 낮음 — 주문·재고 동시 갱신 요구 |

**권장 이유:** PRD는 주문 생성 시 재고 차감과 결제 상태를 하나의 유닛으로 처리하도록 명시한다. PostgreSQL 단일 트랜잭션으로 이 흐름을 직접 표현할 수 있다.

**참고:** [PostgreSQL Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html) — ACID 보장 범위
```

---

### `### 결정 요약` (audit index)

Before decision cards, keep the summary table for PM/audit scan:

| # | 주제 | 선택 | 상태 | 근거 한줄 |
|---|------|------|------|-----------|
| 1 | … | … | 확정 | … |

The **근거 한줄** column mirrors the first sentence of `**근거 설명:**` (or `**권장 이유:**` for forks) — not a bare URL.

---

## Tier-2 — Supporting Facts

**When required:** field lists, component descriptions, status enums, non-controversial mappings.

**Required elements:**
- Inline tag in body: `[ref:A-n]` where `n` matches Appendix A row ID
- Appendix A row: 주장 (one line), PRD anchor, code location when brownfield, external URL when applicable

**Placement by chapter:**

| Chapter | Format |
|---------|--------|
| Ch.2–3 | `[ref:A-n]` inline; row in Appendix A |
| Ch.4 | Tier-1 decision cards only (not Tier-2 **사실:**) |
| Ch.5–6 | `[ref:A-n]` inline; **no** `> **사실:**` blockquotes |
| Appendix A | Canonical table (ID, 주장, PRD, Code, URL) |
| Appendix B | Verbatim Ch.4 decision card sections (`###` + tables + prose) |

**Example (body):**

```markdown
status enum은 PRD와 일치한다 [ref:A-2].
```

**Example (Appendix A row):**

```markdown
| A-2 | status enum은 pending, paid, shipped, delivered, cancelled | [source:prd#order-status] | `src/orders/state.ts:12-28` | |
```

PRD anchor format: `[source:prd#section-slug]` or `[source:prd:line-range]` if from file.

## Community Sources (Tier-2 only)

Blogs, Stack Overflow, etc.:

```markdown
**참고:** [community post, confidence:low](https://example.com/post) — third-party pattern; verify against vendor docs
```

Never use community-only sources for Tier-1 **참고:** links.

## Code Location Format

- Single line: `` `src/module/file.ts:42` ``
- Range: `` `src/module/file.ts:12-28` ``
- Symbol optional in prose; line required

## Prohibited

- Ch.4 Tier-1 as a wall of `> **결정:**` blockquotes without metadata table + **근거 설명:**
- **근거 설명:** or **권장 이유:** with only URLs and no prose
- **참고:** URLs without one-line annotation per link
- **갈림** without alternatives comparison table (≥2 rows) and **권장 이유:**
- Ch.2–6 technical claim with `[ref:A-n]` but no matching Appendix A row
- `> **사실:**` blockquotes in Ch.5–6 (use Appendix A instead)
- Tier-1 decision with only PRD reference (must add official URL in **참고:**)
- Fabricated URLs or paths
- Picking one Tier-1 option in prose without a decision card
- Multiple parallel To-Be designs in Ch.5 for the same fork

## Appendix A coverage (strict + narrative)

Each Ch.5–6 ### with a markdown table or ≥120 chars should cite ≥1 `[ref:A-n]` when stating PRD/code facts. Every `[ref:A-n]` in the body (Ch.2–6) must resolve to an Appendix A row. Enforced by `validate-tdd.py --narrative`.
