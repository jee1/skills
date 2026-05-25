# Narrative Rules — Forward-Only TDD

TDD prose must read **front to back like a novel**. Each chapter assumes only what earlier chapters established.

## 기승전결 Mapping

| Chapter | Role | Reader takeaway |
|---------|------|-----------------|
| 1. 서문 | 起 | Why this document exists |
| 2. 배경과 문제 | 起→承 | What problem and scope (from PRD) |
| 3. 현재 시스템 / 시작점 | 承 | What exists today (code or scaffold) |
| 4. 갭과 설계 전환 / 설계 결정 | 转 | Why we change or choose; core decisions |
| 5. 목표 설계와 마무리 | 结 | How the target looks; when and risks |

## 6하원칙 per Chapter

| Chapter | Who | What | When | Where | Why | How |
|---------|-----|------|------|-------|-----|-----|
| 1 | ✓ | | ✓ | | ✓ | |
| 2 | | ✓ | | ✓ | | |
| 3 | | ✓ | | | | ✓ (current) |
| 4 | | ✓ | | | ✓ | ✓ (target direction) |
| 5 | | ✓ | ✓ | | | ✓ (target detail) |

Every chapter must visibly answer its required dimensions (one sentence minimum).

## Forward-Only Rules

1. **No temporal back-reference** — never point backward or forward in time:
   - Forbidden (KO): 앞서, 위에서, 아래에서, 후술, 나중에, 상기, 전술
   - Forbidden (EN): as mentioned, see above, see below, later, previously, aforementioned

2. **Define before use** — introduce a term, acronym, or component name before using it in another role.

3. **Brownfield ordering**
   - Code-only reality → first in Ch.3
   - PRD-only requirement → first in Ch.4 as `미구현` or `PRD-only`
   - Conflict → code wins; label in Ch.4

4. **Greenfield ordering**
   - Ch.3 states explicitly: no application/domain code yet
   - Do not invent modules, services, or tables that do not exist
   - Ch.4 introduces design decisions from PRD + stack constraints

5. **No repair appendix** — do not add a section that re-explains earlier chapters.

6. **Mixed audience pattern** — within each subsection:
   - First line: plain-language summary (PM-readable)
   - Following lines: technical detail (developer/audit)

## Design Alternatives — When Multiple Options Exist

Do **not** silently pick one option when the fork is real. Use the decision tree below.

### Decision tree (apply in Phase 3 outline)

| Situation | Ch.4 format | Ch.5 | User ask? |
|-----------|-------------|------|-----------|
| **Single clear winner** — code, PRD, or constraints favor one option | `> **결정:**` block | To-Be follows that decision | No |
| **Real fork** — 2–3 viable options, no clear winner | `> **갈림:**` + `> **대안:**` + `> **권장:**` + `> **상태:**` | To-Be follows **권장**; list item under **열린 질문** if `권장(미확정)` | No |
| **Tier-1 high impact fork** — auth, datastore, breaking API, major dependency contract | Same as fork; after user answers use `> **결정:**` + `> **상태:** 확정` | To-Be uses confirmed choice | **Yes — once, before Ch.4 draft** |

**Single clear winner signals:** existing code pattern to extend; PRD mandates one approach; repo already depends on one stack; one option fails a hard constraint.

**Real fork signals:** PRD silent or ambiguous; multiple options fit code/ops constraints; trade-offs are balanced.

**Tier-1 high impact (ask user):** choice affects security boundary, data durability, public API contract, or migration cost beyond one sprint. Present **2–3 options + agent recommendation** in the question; do not draft Ch.4–5 for that topic until answered.

### Ch.4 source block shapes

**Confirmed single choice** — see [citation-tiers.md](citation-tiers.md) `> **결정:**`.

**Multiple options (documented fork):**

```markdown
> **갈림:** Primary datastore
> **대안:** (A) PostgreSQL — ACID, relational model (B) MongoDB — flexible schema
> **권장:** (A) PostgreSQL — PRD requires cross-entity transactions
> **근거:** [source:postgresql-transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
> **코드:** (Greenfield — 코드 없음)
> **상태:** 권장(미확정)
```

**After user confirms Tier-1 fork:**

```markdown
> **결정:** PostgreSQL을 primary datastore로 채택한다.
> **근거:** [source:postgresql-docs](https://www.postgresql.org/docs/current/)
> **코드:** (Greenfield — 코드 없음)
> **상태:** 확정
```

### Ch.5 rules for forks

- **To-Be (목표 설계)** always follows **권장** or **확정** choice — never an unnamed option.
- If any Ch.4 block has `> **상태:** 권장(미확정)`, Ch.5 **열린 질문** must include matching “최종 선택 필요” item naming the **갈림** topic.
- Do not present three parallel To-Be architectures; one narrative path only.

## Outline Self-Check (before drafting)

Before writing prose, verify the outline lists:

- [ ] Every concept in introduction order (no concept used before listed)
- [ ] Each Tier-1 topic tagged: `single` | `multi-recommend` | `needs-user-confirm`
- [ ] User confirmation obtained for all `needs-user-confirm` items before Ch.4 draft
- [ ] Tier-1 decisions all scheduled for Ch.4
- [ ] PRD↔code gaps (brownfield) or PRD→decisions (greenfield) enumerated
- [ ] No chapter depends on information from a later chapter

## Common Violations

| Bad | Good |
|-----|------|
| "As described in section 3, the auth module…" (in Ch.5) | Restate the needed fact in one sentence, then continue |
| "We will explain the database schema later" | Present schema when first needed, in order |
| PRD requirement in Ch.5 with no prior mention | First mention in Ch.4 as PRD requirement |
| Fictional `UserService` in greenfield Ch.3 | "No domain services exist; only empty `src/`" |
