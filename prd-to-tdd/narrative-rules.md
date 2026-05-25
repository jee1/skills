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

## Outline Self-Check (before drafting)

Before writing prose, verify the outline lists:

- [ ] Every concept in introduction order (no concept used before listed)
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
