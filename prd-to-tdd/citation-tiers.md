# Citation Tiers

Every technical claim in **Chapters 2–6** must be traceable. Tier depends on claim type. Tier-1 uses Ch.4 blockquotes; Tier-2 uses `[ref:A-n]` inline with a row in **Appendix A** (see readability profile in [design-sections.md](design-sections.md)).

**Chapter roles:** Ch.4 = decisions; Ch.5 = high-level To-Be; Ch.6 = interfaces/schemas/flows. See [design-sections.md](design-sections.md).

## Tier-1 — Core Design Decisions

**When required:** architecture choice, security model, datastore, auth strategy, protocol, breaking change, major library adoption.

Use **one of two block shapes** (see [narrative-rules.md](narrative-rules.md) decision tree):

### Shape A — Single clear choice (`> **결정:**`)

**Required elements:**
- `> **결정:**` one clear sentence
- `> **근거:**` at least one **official** URL (RFC, vendor docs, framework reference)
- `> **코드:**` `path:line` if brownfield relevant code exists; or `(Greenfield — 코드 없음)`
- `> **상태:** 확정` (optional but recommended)

### Shape B — Documented fork (`> **갈림:**`)

Use when 2–3 viable options exist and no clear winner without stakeholder input.

**Required elements:**
- `> **갈림:**` topic name
- `> **대안:**` (A) … (B) … — max 3 options, one line each
- `> **권장:**` (A|B|…) + one-sentence why
- `> **근거:**` official URL supporting the **권장** option
- `> **코드:**` as in Shape A
- `> **상태:** 권장(미확정)` until user confirms; then rewrite as Shape A with `> **상태:** 확정`

After user confirms a Tier-1 fork, replace Shape B with Shape A in the same subsection.

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
- Inline tag in body: `[ref:A-n]` where `n` matches Appendix A row ID
- Appendix A row: 주장 (one line), PRD anchor, code location when brownfield, external URL when applicable

**Placement by chapter:**

| Chapter | Format |
|---------|--------|
| Ch.2–3 | `[ref:A-n]` inline; row in Appendix A |
| Ch.4 | Tier-1 blockquotes only (not Tier-2 **사실:**) |
| Ch.5–6 | `[ref:A-n]` inline; **no** `> **사실:**` blockquotes |
| Appendix A | Canonical table (ID, 주장, PRD, Code, URL) |
| Appendix B | Verbatim Ch.4 Tier-1 blockquotes |

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
> **근거:** [source:community, confidence:low](https://example.com/post) + `src/foo.ts:10`
```

Never use community-only sources for Tier-1 decisions.

## Code Location Format

- Single line: `` `src/module/file.ts:42` ``
- Range: `` `src/module/file.ts:12-28` ``
- Symbol optional in prose; line required

## Prohibited

- Ch.4 bullet with Tier-1 content and no `**결정:**` / `**갈림:**` block in Ch.4
- Ch.2–6 technical claim with `[ref:A-n]` but no matching Appendix A row
- `> **사실:**` blockquotes in Ch.5–6 (use Appendix A instead)
- Tier-1 decision with only PRD reference (must add official URL)
- Fabricated URLs or paths
- Picking one Tier-1 option in prose without `**결정:**` or `**갈림:**` block
- `**갈림:**` without `**권장:**` and `**상태:**`
- Multiple parallel To-Be designs in Ch.5 for the same fork

## Appendix A coverage (strict + readability)

Each Ch.5–6 ### with a markdown table or ≥120 chars should cite ≥1 `[ref:A-n]` when stating PRD/code facts. Every `[ref:A-n]` in the body (Ch.2–6) must resolve to an Appendix A row. Enforced by `validate-tdd.py --readability`.
