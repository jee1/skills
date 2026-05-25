# Subagent Prompt Templates

Spawn **all three in parallel** after `validate-tdd.py` passes. Use `readonly: true` where supported.

Merge output; any **Critical** finding blocks completion until fixed (max 2 full cycles).

## Severity Definitions

| Level | Meaning | Blocks merge? |
|-------|---------|---------------|
| Critical | Breaks forward-only rule, fabricated code, missing Tier-1 source, false As-Is | Yes |
| Major | 6하원칙 gap, weak citation, unclear gap labeling | Fix before save |
| Minor | Style, wording | Optional |

## Output Format (all reviewers)

One finding per line:

```
severity | chapter:line | issue | fix
```

Example:

```
Critical | 4:42 | Tier-1 decision without official URL | Add RFC or vendor doc link to 근거 block
```

---

## 1. narrative-reviewer

**Tool:** Task `generalPurpose`, `readonly: true`

**Prompt:**

```
You are the narrative-reviewer for a Technical Design Document (TDD).

Read the TDD draft and narrative-rules.md (forward-only, 기승전결, 6하원칙).

Checklist:
1. Five chapters in fixed order; mode-appropriate Ch.3/Ch.4 titles.
2. No temporal back-references (Korean and English forbidden phrases).
3. Every concept defined before use across chapter boundaries.
4. Brownfield: code-only facts first in Ch.3; PRD-only first in Ch.4.
5. Greenfield: Ch.3 must not describe non-existent domain modules.
6. Each chapter answers its 6하원칙 dimensions (see narrative-rules table).
7. Mixed audience: summary line before technical detail in subsections.
8. No appendix re-explaining earlier content.
9. Design alternatives: clear winner uses **결정:**; real fork uses **갈림:**+**권장:**+**상태:**; no silent pick when fork was documented in outline.
10. Ch.5 To-Be follows one path (권장 or 확정); **열린 질문** present for each Ch.4 `권장(미확정)`.

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
1. Every technical claim in Ch.4–5 has a source block in the same subsection.
2. Tier-1 topics use either:
   - **결정:** + **근거:** (official URL) + **코드:**
   - **갈림:** + **대안:** + **권장:** + **근거:** (official URL for 권장) + **코드:** + **상태:**
3. **갈림:** blocks must not omit **권장:** or **상태:**; max 3 alternatives.
4. Tier-2 facts have **사실:** and **근거:** with PRD anchor + code when brownfield.
5. No Tier-1 backed only by blog/community without official URL.
6. URL format looks intentional (not placeholder example.com unless marked).
7. PRD anchors match actual PRD section/content.
8. No Tier-1 choice stated only in prose without a source block.

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
4. **코드:** paths in citation blocks must exist; line ranges plausible.
5. "미구현" / "PRD-only" labels present for PRD items absent in code (brownfield).
6. Do not require code citations for Greenfield Tier-1 when marked (Greenfield — 코드 없음).

Return ONLY findings in format:
severity | chapter:line | issue | fix

If no issues: return "PASS"
```

**Attach:** TDD file, repo root path, mode from frontmatter

---

## Spawn Pattern (orchestrator)

```
Parallel Task calls:
1. narrative-reviewer  — prompt above + TDD + narrative-rules.md
2. citation-reviewer   — prompt above + TDD + PRD + citation-tiers.md
3. code-grounding-reviewer — prompt above + TDD + repo

If any Critical → edit TDD → validate-tdd.py → re-spawn (review_rounds += 1)
Max 2 rounds total for script + subagents cycle.
```
