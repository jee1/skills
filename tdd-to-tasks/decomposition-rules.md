# Decomposition Rules — TDD Ch.6 → Tasks

Map validated TDD sections to `TK-nnn` tasks. Prefer **fewer, merge-ready tasks** (1 PR ≈ 1 task) over 2-minute micro-steps.

---

## Source → task type

| TDD source | Task type | Notes |
|------------|-----------|-------|
| Ch.6 **데이터 모델** + migration note | `Migration`, `Model`, `Repository` | Foundation phase; blocks AC phases |
| Ch.6 **API** endpoint table | `Route`, `Handler`, `DTO`, `Auth`, `Error mapping` | One handler task may cover route + service call |
| Ch.5 **(신규)** component | `Create module` + tests | New file paths from TDD code refs or inferred package |
| Ch.5 **(기존)** component | `Modify` + regression test | Cite existing `path:line` from TDD |
| Ch.6 **핵심 처리 흐름** happy path | `Orchestration` in service layer | Align step order with flow numbered list |
| Ch.6 **Errors** (≥2 branches) | `Error handler`, `Retry queue`, `Compensating call` | One task per distinct client-visible error code if non-trivial |
| Ch.6 **인수조건** Must row | Phase boundary | Phase title includes AC ID + short 인수조건 phrase |
| Ch.6 **인수조건** Should row | Later phase | After all Must phases |
| Ch.6 **테스트** CI gate **yes** | `Write test` task **before** implement task | Same AC phase; reference `proves T-n` |
| Ch.6 **테스트** CI gate **no** | Manual QA task or note in AC phase | Optional TK line |

---

## AC phase recipe

For each **Must** AC (from Ch.6 table):

1. Read **완료 판정** — if it names `T-n`, that test is mandatory in tasks
2. Add **test task** if layer is unit/integration/e2e and CI gate is yes
3. Add **implement tasks** covering API + service + external calls referenced in flow for that AC
4. Add **wire task** if AC spans multiple components (handler → service → gateway)

Minimum **2 TK lines** per Must AC (test + implement) when CI gate is yes for linked test.

---

## Foundation phase recipe

Always include before AC phases when any of:

- Migration mentioned in Ch.6 데이터 모델
- New shared type/enum used by ≥2 components
- New interface introduced in Ch.4/Ch.5 (e.g. PaymentGateway)

Foundation tasks **block** all AC phases via Dependencies.

---

## Setup phase recipe

| Mode | Typical tasks |
|------|----------------|
| **greenfield** | scaffold test runner, CI stub, env sample |
| **brownfield** | feature flag, local config, extend existing test module |

---

## Parallelism `[P]`

Mark `[P]` when:

- Different files, no shared migration lock
- No `blockedBy` edge between parallel tasks

Do **not** mark `[P]` on migration + code using new schema.

---

## Blocked / open decisions

If TDD Ch.4 row has `상태: 권장(미확정)` affecting this AC:

- Prefix task description `[blocked]` OR
- Omit implement tasks; add Dependency note: `TK-nnn blockedBy Ch.7 decision: {topic}`

---

## What not to do

- Do not invent AC IDs or Test IDs not in TDD
- Do not create tasks without `` `file/path` `` for code-changing work
- Do not duplicate TDD prose — task line = imperative + path + AC/Test link
- Do not use `T-1` as Task ID — use `TK-001` and `proves T-1` for tests
