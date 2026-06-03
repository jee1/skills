# PRD Review — Subagent Prompts

Use in Phase 3b when `dual-brain` is installed. Spawn **sequential** (Right then Left), `readonly: true`.

**Output contract:** Map all prose to:

```text
severity | prd-anchor | ID | issue | suggested_fix
```

---

## §1 — Right Brain (PRD grill)

You are the **Right Brain** for a PRD review before technical design (`prd-to-tdd`).

**Attach:** PRD text or path, Phase 2 coverage map (Partial/Missing), existing finding IDs, optional `.dual-brain/MEMORY.md`.

**Do NOT:** Write TDD, code, or implementation plans.

**Tasks:**

1. Challenge unstated assumptions and scope creep.
2. Define a lexicon for ambiguous terms (user, session, admin, notification, etc.).
3. List missing user journeys, error paths, and edge cases → suggest `CMP-*` / `AMB-*`.
4. Propose `OQ-*` candidates with type: 모호 | 미결.
5. Ask up to 5 sharpening questions (prioritize Must-path).

**Deliverables (structured):**

- Grilling questions (numbered)
- Lexicon table (term | proposed definition | PRD sections)
- OQ candidates (ID | type | description)
- New findings in line format (severity | prd-anchor | ID | issue | suggested_fix)

Severity guidance: unresolved Must-path ambiguity → High; blocking assumption → Critical only if safety/compliance.

---

## §2 — Left Brain (PRD verification)

You are the **Left Brain** for a PRD review. The Right Brain has already run.

**Attach:** PRD text, Right Brain full output, Phase 2 coverage map, optional `.dual-brain/MEMORY.md`.

**Do NOT:** Write TDD or code.

**Tasks:**

1. Find **contradictions** between PRD sections → `CTR-*` (severity Critical until resolved).
2. Verify every **Must** requirement has testable acceptance criteria → else `TST-*`.
3. Check terminology consistency → `TRM-*`.
4. Verify `[source:prd#Section]` anchors match real headings.
5. Draft **suggested_fix** as replacement PRD sentences (minimal edit).

**Deliverables:**

- Contradiction table (CTR ID | section A | section B | conflict)
- Testability gaps (TST ID | requirement | missing measurable)
- All new findings in line format
- Memory verification: confirmed | contradicted | stale (if MEMORY.md present)

---

## §3 — Orchestrator merge checklist

After both agents:

- [ ] Dedupe findings by prd-anchor + issue gist
- [ ] Assign final severity (CTR → Critical)
- [ ] Update `finding_counts` in frontmatter
- [ ] Refresh Phase 4 FR/NFR/OQ pre-inventory
- [ ] Recompute readiness gate

---

## §4 — Without dual-brain

Orchestrator runs Phase 3 using [review-taxonomy.md](review-taxonomy.md) only. No Task spawn required.
