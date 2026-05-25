# Citation Tiers

Every technical claim in **Chapters 4–5** must carry a source block. Tier depends on claim type.

## Tier-1 — Core Design Decisions

**When required:** architecture choice, security model, datastore, auth strategy, protocol, breaking change, major library adoption.

**Required elements:**
- `> **결정:**` one clear sentence
- `> **근거:**` at least one **official** URL (RFC, vendor docs, framework reference)
- `> **코드:**` `path:line` if brownfield relevant code exists; or `(Greenfield — 코드 없음)`

**Example (Brownfield):**

```markdown
> **결정:** 기존 세션 쿠키 대신 JWT access + refresh rotation을 추가한다.
> **근거:** [source:rfc6750](https://datatracker.ietf.org/doc/html/rfc6750), [source:fastapi-security](https://fastapi.tiangolo.com/tutorial/security/)
> **코드:** `src/auth/session.py:18` (현재 쿠키 세션)
```

**Example (Greenfield):**

```markdown
> **결정:** PostgreSQL을 primary datastore로 채택한다.
> **근거:** [source:postgresql-docs](https://www.postgresql.org/docs/current/)
> **코드:** (Greenfield — 코드 없음)
```

**Official URL examples:** `*.gov`, `datatracker.ietf.org`, `developer.mozilla.org`, `docs.*`, `cloud.google.com`, GitHub **official** org docs.

## Tier-2 — Supporting Facts

**When required:** field lists, component descriptions, status enums, non-controversial mappings.

**Required elements:**
- `> **사실:**` one sentence
- `> **근거:**` PRD anchor + code location when brownfield

**Example:**

```markdown
> **사실:** 주문 상태는 pending, paid, shipped, delivered, cancelled 다섯 값이다.
> **근거:** [source:prd#order-status] + `src/orders/state.ts:12-28`
```

PRD anchor format: `[source:prd#section-slug]` or `[source:prd:line-range]` if from file.

## Community Sources (Tier-2 only)

Blogs, Stack Overflow, etc.:

```markdown
> **근거:** [source:community, confidence:low](https://example.com/post) + `src/foo.ts:10`
```

Never use community-only sources for Tier-1 decisions.

## Code Location Format

- Single line: `` `src/module/file.ts:42` ``
- Range: `` `src/module/file.ts:12-28` ``
- Symbol optional in prose; line required

## Prohibited

- Ch.4–5 bullet with technical content and no source block within the same subsection
- Tier-1 decision with only PRD reference (must add official URL)
- Fabricated URLs or paths
