# Path Selection — standard | enhanced | full

Orchestrator picks **one pipeline path** per run. Record in report frontmatter:

```yaml
prd_review_path: enhanced   # standard | enhanced | full
complexity_score: 6         # integer, from rubric below
phase_6_mode: B               # A | B | C
```

---

## Three paths (summary)

| Path | Phase 3b dual-brain | Phase 6 review |
|------|---------------------|----------------|
| **standard** | Skip | **3인 병렬** — ambiguity-scope + contradiction-consistency + testability-nfr |
| **enhanced** | Right → Left **mandatory** | **Left Brain** (§2), optional §5 if doubt |
| **full** | Right → Left **mandatory** | §5–7 parallel (Phase 3b already ran Left); dedupe |

**full** = enhanced pre-review (3b) + maximum Phase 6 coverage (not a substitute for dual-brain).

---

## Step 0 — User override (highest priority)

Parse the user message **before** scoring:

| User says | Force path |
|-----------|------------|
| `full`, `full review`, `full mode`, `풀 리뷰` | **full** |
| `enhanced`, `dual-brain`, `dual brain` | **enhanced** |
| `standard`, `standard reviewers`, `no dual-brain`, `빠르게` | **standard** |

If override conflicts with missing dual-brain (see Step 1), downgrade and explain once.

---

## Step 1 — dual-brain probe

Probe `dual-brain/SKILL.md` (cursor → codex → agents → claude paths in [dual-brain-integration.md](dual-brain-integration.md)).

| dual-brain | Allowed auto paths |
|------------|-------------------|
| **Not found** | **standard** only |
| **Found** | standard, enhanced, or full |

---

## Step 2 — Complexity score (after Phase 1 + Phase 2)

Compute **once** after PRD ingest and coverage scan. Cap repeated signals as noted.

| Signal | Points | Notes |
|--------|--------|-------|
| PRD **> 2000 words** | +2 | From Phase 1 word count |
| PRD **> 1000 words** | +1 | Additive with row above if both true |
| **≥ 3** distinct user roles / actors | +2 | admin, merchant, customer, … |
| **≥ 4** Must-level features or FR bullets | +1 | Count from PRD |
| **≥ 2** taxonomy categories **Missing** | +2 | From Phase 2 coverage map |
| **≥ 4** taxonomy categories **Partial** | +1 | |
| External **integration** keywords | +2 | payment, auth, webhook, pg, 환불, 결제, jwt, idempotency |
| **NFR** in PRD (security, SLA, compliance, PII) | +1 | |
| Audit / production keywords | +2 | audit, SOC, HIPAA, 프로덕션 필수 |
| Prior **prd-review** on same PRD was `blocked` | +2 | If user shared prior report |
| **Outline-only** PRD (<300 words, no AC) | +4 | Usually gate blocked; still score for path |
| Short PRD **< 500 words**, single actor, ≤2 features | −2 | Trivial discount |
| Single primary flow, all taxonomy **Clear** | −1 | |

**integration** keywords (any in PRD): `payment`, `stripe`, `auth`, `oauth`, `webhook`, `pg`, `환불`, `결제`, `jwt`, `idempotency`, `refund`, `billing`.

---

## Step 3 — Auto map score → path

Only when **no user override** from Step 0:

| Condition | Auto path |
|-----------|-----------|
| dual-brain **missing** | **standard** |
| score **≥ 8** | **full** |
| score **4–7** | **enhanced** |
| score **≤ 3** and trivial discount applied | **standard** |
| score **≤ 3** otherwise | **enhanced** |

**Default when dual-brain found and score ambiguous:** **enhanced**.

---

## Step 4 — Announce (once)

After Phase 2, before Phase 3:

```text
prd-review path: <standard|enhanced|full> (complexity_score: N, reason: …)
```

Reason examples:

- `full` — 2400 words + payment + 2 Missing taxonomy rows
- `enhanced` — brownfield scope, 3 Partial categories, score 5
- `standard` — 400 words, single flow, dual-brain missing

If user disagrees, apply override and continue.

---

## Phase 6 — Mode mapping

| Path | `phase_6_mode` | Spawn pattern |
|------|----------------|---------------|
| standard | **A** | [subagent-prompts.md](subagent-prompts.md) §5–7 **parallel** |
| enhanced | **B** | §2 Left Brain; optional §5 if orchestrator doubt |
| full | **C** | §2 **then** §5–7 parallel; dedupe |

**Full merge rules (Mode C):**

1. Run §5–7 parallel; collect findings (Phase 3b output in task packet).
2. Dedupe by `prd-anchor` + issue gist; keep **higher severity**.
3. If same anchor has conflicting fixes, prefer **contradiction** > testability > ambiguity for factual conflicts.

Max **2** full Phase 6 rounds before Phase 5 report. Critical findings block `ready` gate until resolved or downgraded with user acceptance.

---

## Examples

| Scenario | Score | Path |
|----------|-------|------|
| 350 words, 1 actor, cancel button only | 0 | standard |
| 1200 words, 2 actors, refund policy gaps | 5 | enhanced |
| 2500 words + Stripe + 3 Partial + security NFR | 10 | full |
| dual-brain missing, same as last row | — | standard |
