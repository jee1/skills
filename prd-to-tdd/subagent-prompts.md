# Subagent Prompt Templates

After `validate-tdd.py` strict (+ `--narrative` when used) passes, pick **one** Phase 6 path — see [SKILL.md](SKILL.md) Phase 6 and [dual-brain-integration.md](dual-brain-integration.md):

| Path | When | Spawn |
|------|------|-------|
| **Mode A (default)** | `dual-brain` skill not on disk, or user did not request compact review | §1–3 **in parallel** |
| **Mode B (compact)** | `dual-brain/SKILL.md` exists **and** user asked dual-brain or prefers compact review | §4 first (sequential), then §1 only if narrative doubt |

Use `readonly: true` where supported. Merge output; any **Critical** finding blocks completion until fixed (max 2 full cycles).

## Severity Definitions

| Level | Meaning | Blocks merge? |
|-------|---------|---------------|
| Critical | Breaks forward-only rule, fabricated code, missing Tier-1 source, false As-Is, **strict depth rubric failure** | Yes |
| Major | 6하원칙 gap, weak citation, unclear gap labeling, missing auth/error detail | Fix before save |
| Minor | Style, wording | Optional |

## Output Format (all reviewers)

One finding per line:

```
severity | chapter:line | issue | fix
```

Example:

```
Critical | 4:42 | Tier-1 decision without official URL | Add RFC or vendor doc to **참고:** with annotation
```

---

## 1. narrative-reviewer

**Tool:** Task `generalPurpose`, `readonly: true`

**Prompt:**

```
You are the narrative-reviewer for a Technical Design Document (TDD).

Read the TDD draft and narrative-rules.md (forward-only, 기승전결, 6하원칙).

Checklist:
1. Eight chapters in fixed order (1–8); H2 titles: Overview, Background, Requirements, Existing Solution (or Starting Point), Proposed Solution, Alternatives Considered, Detailed Design, Rollout and Open Items.
2. Ch.5 has ### Architecture Overview (or 아키텍처 개요), ### Components and Responsibilities, ### Data Flow — **no** Decision Summary.
3. Ch.6 has ### Decision Summary (or 결정 요약) + Tier-1 ADR cards; Shape A/B per citation-tiers.md.
4. Ch.7 has ### APIs and Interfaces, ### Data Model, ### Core Processing Flow, ### Acceptance Criteria, ### Tests.
5. Ch.8 has ### Rollout and Milestones, ### Risks, ### Open Questions.
6. No temporal back-references (Korean and English forbidden phrases).
7. Component names first appear in Ch.5; Ch.7 reuses exact names.
8. Brownfield: Ch.4 Existing Solution = code reality; Ch.5 labels PRD gaps.
9. Greenfield: Ch.4 must not describe fictional production modules.
10. No `요약:`, `#### 한눈에`, or `### TL;DR` in Ch.2–8.
11. Design alternatives only in Ch.6; Ch.5 one To-Be path; 권장(미확정) → Ch.8 Open Questions.
12. Ch.3: #### Functional Requirements (FR) + #### Traceability Matrix (RTM); every Must FR → RTM → Ch.7 AC.
13. Ch.3 `OQ-*` each appears in Ch.8 ### Open Questions.
14. Front matter H2: ## 목차 (or Table of Contents) → ## How to Read This Doc → ## 1. Overview.
15. Ch.5 transition mermaid before Architecture Overview; Ch.5 Data Flow mermaid; Ch.7 Core Flow mermaid with branches.
16. Bridges Ch.2→3→4→5→6→7 feel causal in order.
17. No > **사실:** in Ch.5–7; Tier-2 `[ref:A-n]` + Appendix A; Ch.6 Tier-1 → Appendix B.
18. Qualitative: reads like one story front-to-back (기승전결).
19. Literal tilde in prose uses \\~ (e.g. \\~3분).
20. Do not re-check items already enforced by `validate-tdd.py --narrative` unless semantic doubt remains.
29. Qualitative: reads like one story front-to-back; no telegraphic fragments a new teammate could not follow.
30. Literal tilde in body prose/tables uses \\~ (e.g. A\\~Z, \\~3분); no bare ~ outside code fences — prevents strikethrough pairing.
31. Do not re-check items already enforced by `validate-tdd.py --narrative` unless the script passed with semantic doubt (e.g. bridge feels weak, RTM looks complete but AC conditions are vague).

Return ONLY findings in format:
severity | chapter:line | issue | fix

If no issues: return "PASS"
```

**Attach:** TDD file path, `narrative-rules.md`

---

## 2. citation-reviewer

**Tool:** Task `generalPurpose`, `readonly: true`

**Prompt:**

```
You are the citation-reviewer for a Technical Design Document (TDD).

Read the TDD draft, citation-tiers.md, and the source PRD text.

Checklist:
1. Every technical claim in Ch.2–6 has traceability (Ch.2 FR/RTM `[source:prd#…]`; Ch.4–6 Tier-1 cards or Tier-2 [ref:A-n]).
2. Tier-1 topics use decision cards (citation-tiers.md):
   - Shape A: metadata table with | 결정 | + **근거 설명:** (prose, not URL-only) + **참고:** (official URL + per-link annotation) + code row
   - Shape B: metadata table with | 갈림 | + alternatives comparison table (≥2 rows) + **권장 이유:** + **참고:** + **상태:**
3. Fork cards must not omit alternatives table or **권장 이유:**; max 3 alternative rows.
4. Tier-2 facts in Ch.2–3 use [ref:A-n] + Appendix A; Ch.5–6 use [ref:A-n] only (no > **사실:**).
5. No Tier-1 backed only by blog/community without official URL in **참고:**.
6. URL format looks intentional (not placeholder example.com unless marked).
7. PRD anchors match actual PRD section/content.
8. No Tier-1 choice stated only in prose without a decision card.
9. Ch.5–6 content matches design-sections.md (high-level in 5, detail in 6).
10. Ch.6 ### 인수조건 traces each AC to PRD; conditions are verifiable (not vague “works correctly”).
11. Ch.6 ### 테스트 maps every AC to ≥1 test with layer + CI gate.

Return ONLY findings in format:
severity | chapter:line | issue | fix

If no issues: return "PASS"
```

**Attach:** TDD file, PRD text or path, `citation-tiers.md`

---

## 3. code-grounding-reviewer

**Tool:** Task `cavecrew-reviewer` or `generalPurpose`, `readonly: true`

**Prompt:**

```
You are the code-grounding-reviewer for a Technical Design Document (TDD).

Read the TDD draft and verify claims against the actual repository.
Respect frontmatter `mode`: brownfield | greenfield.

Checklist:
1. Code-first: where PRD and code conflict, TDD must side with code and label gap.
2. Brownfield Ch.3: every As-Is component/flow traceable to path:line in repo.
3. Greenfield Ch.3: only scaffold exists (package.json, CI, empty src) — flag fictional services.
4. **코드:** row in decision card metadata must exist; line ranges plausible.
5. "미구현" / "PRD-only" labels present for PRD items absent in code (brownfield).
6. Do not require code citations for Greenfield Tier-1 when marked (Greenfield — 코드 없음).
7. Ch.5 As-Is vs To-Be: Ch.5–6 describe target state only; current state stays in Ch.3.
8. Component/API names in Ch.6 must appear in Ch.5 first.

Return ONLY findings in format:
severity | chapter:line | issue | fix

If no issues: return "PASS"
```

**Attach:** TDD file, repo root path, mode from frontmatter

---

## 4. left-brain-verification-reviewer (Mode B only)

**Tool:** Task `generalPurpose` or `cavecrew-reviewer`, `readonly: true`

**When:** `dual-brain` skill installed; replaces citation-reviewer + code-grounding-reviewer in one pass.

**Prompt:**

```
You are the left-brain-verification-reviewer for a Technical Design Document (TDD).

Combine citation + code-grounding checks. Read dual-brain/SKILL.md Left Brain persona if available;
otherwise follow this checklist strictly.

Read: TDD draft, citation-tiers.md, source PRD, repository (respect frontmatter mode: brownfield | greenfield).

Citation checklist:
1. Ch.2–6 claims traceable (FR/RTM [source:prd#…]; Ch.4–6 Tier-1 cards or Tier-2 [ref:A-n]).
2. Tier-1 decision cards: Shape A/B per citation-tiers.md; **참고:** has official URL + annotation; fork cards have alternatives + **권장 이유:**.
3. No Tier-1 backed only by blog/community without official URL.
4. PRD anchors match actual PRD section/content.
5. Ch.6 ### 인수조건: verifiable Given/When/Then; Ch.6 ### 테스트 maps every AC to ≥1 test + layer + CI gate.

Code-grounding checklist:
6. Code-first: PRD vs code conflict → TDD sides with code; gap labeled.
7. Brownfield Ch.3: As-Is traceable to path:line; **코드:** row in decision cards plausible.
8. Greenfield Ch.3: no fictional services; Tier-1 may omit code when marked (Greenfield — 코드 없음).
9. Ch.5–6 target state only; component/API names in Ch.6 appear in Ch.5 first.
10. "미구현" / "PRD-only" where PRD items absent in code (brownfield).

Do not re-litigate items already enforced by validate-tdd.py unless semantic doubt.

Return ONLY findings in format:
severity | chapter:line | issue | fix

If no issues: return "PASS"
```

**Attach:** TDD file, PRD text or path, `citation-tiers.md`, repo root, mode from frontmatter; optional `dual-brain/SKILL.md`

---

## 5. narrative-reviewer (optional in Mode B)

Same prompt as §1. **Spawn when:**

- Mode A: always (parallel with §2–3)
- Mode B: only if `--narrative` passed **but** bridges, AC wording, or story flow still feel weak after script pass

If Mode B and script narrative checks are clean with no doubt: **skip** §5.

---

## Spawn Pattern (orchestrator)

### Mode A — Default (dual-brain not required)

```
Parallel Task calls:
1. narrative-reviewer       — §1 + TDD + narrative-rules.md
2. citation-reviewer        — §2 + TDD + PRD + citation-tiers.md
3. code-grounding-reviewer  — §3 + TDD + repo

If any Critical → edit TDD → validate-tdd.py (strict + --narrative) → re-spawn
Max 2 rounds total for script + subagents cycle.

Phase 7 report: validation: script + 3 reviewers (default)
```

### Mode B — Compact (dual-brain installed)

```
Probe ~/.cursor|~/.codex|~/.agents/skills/dual-brain/SKILL.md — if missing, use Mode A.

Sequential:
1. left-brain-verification-reviewer — §4 + TDD + PRD + citation-tiers.md + repo

Optional (parallel with nothing else required):
2. narrative-reviewer — §1 only if semantic doubt after --narrative pass

If any Critical → edit TDD → validate-tdd.py → re-spawn (same max 2 rounds)

Phase 7 report: validation: script + dual-brain compact (left-brain [+ narrative])
```

### dual-brain unavailable

```
Do not simulate Right/Left Brain personas. Use Mode A only.
Tell user once in Phase 7: dual-brain: not installed — default reviewers
```
