# Path Selection — standard | enhanced | full

Orchestrator picks **one pipeline path** per run. Record it in Phase 7 and optional TDD frontmatter:

```yaml
prd_to_tdd_path: enhanced   # standard | enhanced | full
complexity_score: 6          # integer, from rubric below
```

---

## Three paths (summary)

| Path | Pre-draft (dual-brain) | Phase 6 review |
|------|------------------------|----------------|
| **standard** | Skip 2b, 3b spawn, 3c | **3인 병렬** — narrative + citation + code-grounding |
| **enhanced** | 2b → 3b → 3c | **Left Brain** (§4), then narrative (§1) only if doubt |
| **full** | 2b → 3b → 3c (same as enhanced) | **Left Brain** (§4) **then** **3인 병렬** (§1–3); merge deduped findings |

**full** = enhanced 작성 파이프라인 + maximum Phase 6 coverage (not a substitute for 2b/3c).

---

## Step 0 — User override (highest priority)

Parse the user message **before** scoring:

| User says | Force path |
|---------|------------|
| `full`, `full review`, `full mode`, `풀 리뷰` | **full** |
| `enhanced`, `dual-brain`, `dual brain` | **enhanced** |
| `standard`, `standard reviewers`, `no dual-brain`, `빠르게` | **standard** |

If override conflicts with missing dual-brain (see below), downgrade and explain once.

---

## Step 1 — dual-brain probe

Probe `dual-brain/SKILL.md` (cursor → codex → agents → claude paths in [dual-brain-integration.md](dual-brain-integration.md)).

| dual-brain | Allowed auto paths |
|------------|-------------------|
| **Not found** | **standard** only |
| **Found** | standard, enhanced, or full |

---

## Step 2 — Complexity score (after Phase 1 + Phase 2)

Compute **once** after PRD ingest and code analysis. Cap repeated signals as noted.

| Signal | Points | Notes |
|--------|--------|-------|
| **brownfield** | +2 | Domain code beyond scaffold |
| PRD↔code **gap** (each, max +4) | +1 | 미구현 / PRD-only; count from Phase 2 notes |
| **FR count ≥ 4** | +1 | Must-level functional reqs |
| **needs-user-confirm** Tier-1 (each, max +6) | +3 | From PRD + Phase 2/3 preview |
| **multi-recommend** Tier-1 ≥ 2 topics | +2 | Shape B likely |
| External **integration** | +2 | payment, auth, webhook, third-party API, queue |
| **NFR** in PRD (security, SLA, compliance) | +1 | |
| Audit / production keywords | +2 | user: audit, SOC, PII, 결제, 프로덕션 필수 |
| **greenfield** + FR ≤ 2 + no forks + gaps 0 | −3 | Trivial feature discount |
| Prior **prd-review** flagged Critical | +2 | If user ran prd-review and shared result |

**integration** keywords (any in PRD or scope): `payment`, `stripe`, `auth`, `oauth`, `webhook`, `pg`, `환불`, `결제`, `jwt`, `idempotency`.

---

## Step 3 — Auto map score → path

Only when **no user override** from Step 0:

| Condition | Auto path |
|-----------|-----------|
| dual-brain **missing** | **standard** |
| score **≥ 8** | **full** |
| score **4–7** | **enhanced** |
| score **≤ 3** and greenfield trivial row (−3 applied) and gaps = 0 | **standard** |
| score **≤ 3** otherwise (e.g. brownfield) | **enhanced** |
| score **0–3** with brownfield or any gap | **enhanced** (never auto-standard on brownfield) |

**Default when dual-brain found and score ambiguous:** **enhanced**.

---

## Step 4 — Announce (once)

Before Phase 3, tell the user briefly:

```text
prd-to-tdd path: <standard|enhanced|full> (complexity_score: N, reason: …)
```

Reason examples:

- `full` — brownfield + 5 gaps + 2× needs-user-confirm
- `enhanced` — brownfield + payment scope, score 6
- `standard` — greenfield scaffold, 2 FR, no Tier-1 forks

If user disagrees, apply override and continue.

---

## Phase 6 — Mode mapping

| Path | Spawn pattern |
|------|---------------|
| standard | [subagent-prompts.md](subagent-prompts.md) Mode A — §1–3 parallel |
| enhanced | Mode B — §4, optional §1 |
| full | Mode C — §4 then §1–3 parallel, dedupe |

**Full merge rules:**

1. Run §4 first; collect findings.
2. Run §1–3 parallel; collect findings.
3. Dedupe by `chapter:line` + issue gist; keep **higher severity**.
4. If same line has conflicting fixes, prefer **code-grounding** > citation > narrative for factual conflicts; narrative wins only for prose/bridge wording.

Max **2** full validate + review rounds (unchanged).

---

## Examples

| Scenario | Score | Path |
|----------|-------|------|
| Greenfield, 2 FR, express only, no forks | 0 | standard |
| Brownfield cancel API, 3 gaps, 1× confirm | 7 | enhanced |
| Brownfield + Stripe + 4 gaps + 2× confirm + NFR | 11 | full |
| dual-brain missing, same as last row | — | standard |
