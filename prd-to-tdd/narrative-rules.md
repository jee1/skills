# Narrative Rules — Forward-Only TDD

TDD prose must read **front to back like a novel**. Each chapter assumes only what earlier chapters established.

## 기승전결 Mapping

| Chapter | Role | Reader takeaway |
|---------|------|-----------------|
| 1. 서문 | 起 | Why this document exists |
| 2. 배경과 문제 | 起→承 | What problem and scope (from PRD) |
| 3. 현재 시스템 / 시작점 | 承 | What exists today (code or scaffold) |
| 4. 갭과 설계 전환 / 설계 결정 | 转 | Why we change or choose; core decisions |
| 5. 상위설계 | 结 (macro) | Target architecture, components, data flow |
| 6. 상세설계 | 结 (micro) | APIs, schemas, processing logic |
| 7. 마무리 | 结 (close) | Rollout, risks, open questions |

Detail rules for Ch.5–6: [design-sections.md](design-sections.md).

## 6하원칙 per Chapter

| Chapter | Who | What | When | Where | Why | How |
|---------|-----|------|------|-------|-----|-----|
| 1 | ✓ | | ✓ | | ✓ | |
| 2 | | ✓ | | ✓ | | |
| 3 | | ✓ | | | | ✓ (current) |
| 4 | | ✓ | | | ✓ | ✓ (direction) |
| 5 | | ✓ | | | | ✓ (high-level) |
| 6 | | ✓ | | | | ✓ (detailed) |
| 7 | | | ✓ | | | ✓ (rollout) |

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

| Situation | Ch.4 format | Ch.5–6 To-Be | Ch.7 | User ask? |
|-----------|-------------|--------------|------|-----------|
| **Single clear winner** | `> **결정:**` | Follows that decision | Risks / rollout | No |
| **Real fork** | `> **갈림:**` + … + `> **상태:** 권장(미확정)` | Follows **권장** in 상위·상세 | **열린 질문** with “최종 선택 필요” | No |
| **Tier-1 high impact fork** | After user answer: `> **결정:**` + `> **상태:** 확정` | Uses confirmed choice | Standard | **Yes — before Ch.4** |

**Single clear winner signals:** existing code pattern to extend; PRD mandates one approach; repo already depends on one stack; one option fails a hard constraint.

**Real fork signals:** PRD silent or ambiguous; multiple options fit code/ops constraints; trade-offs are balanced.

**Tier-1 high impact (ask user):** choice affects security boundary, data durability, public API contract, or migration cost beyond one sprint. Present **2–3 options + agent recommendation** in the question; do not draft Ch.4–7 for that topic until answered.

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

### Ch.5–7 rules for forks

- **상위설계·상세설계** always follow **권장** or **확정** choice from Ch.4 — never an unnamed option.
- If any Ch.4 block has `> **상태:** 권장(미확정)`, Ch.7 **열린 질문** must include matching “최종 선택 필요” item.
- Do not present parallel To-Be architectures; one narrative path in Ch.5–6.
- Introduce component **names** in Ch.5 before API/schema detail in Ch.6.

## Outline Self-Check (before drafting)

Before writing prose, verify the outline lists:

- [ ] Every concept in introduction order (no concept used before listed)
- [ ] Ch.5 component list: ≥2 names (see outline-template.md)
- [ ] Ch.6 API/event list: ≥1 per user-facing action
- [ ] Ch.6 entity list: ≥1 per persisted object with field names
- [ ] Flow steps: ≥5 (same names in Ch.5 ### 데이터 흐름 and Ch.6 ### 핵심 처리 흐름)
- [ ] Error branches: ≥2 mapped to Ch.6
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
