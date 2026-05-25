# Subagent Prompt Templates

Spawn **all three in parallel** after `validate-tdd.py` passes. Use `readonly: true` where supported.

Merge output; any **Critical** finding blocks completion until fixed (max 2 full cycles).

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
1. Seven chapters in fixed order (1–7); mode-appropriate Ch.3/Ch.4 titles; Ch.5–7 titles identical across modes.
2. Ch.5 has ### 아키텍처 개요, ### 구성요소 및 책임, ### 데이터 흐름.
3. Ch.6 has ### API 및 인터페이스, ### 데이터 모델, ### 핵심 처리 흐름.
4. Ch.7 has ### 롤아웃·일정 (or 롤아웃 및 일정), ### 리스크, ### 열린 질문.
5. No temporal back-references (Korean and English forbidden phrases).
6. Every concept defined before use; component names first in Ch.5 before Ch.6 detail.
7. Brownfield: code-only facts first in Ch.3; PRD-only first in Ch.4.
8. Greenfield: Ch.3 must not describe non-existent domain modules.
9. Each chapter embeds its 6하 dimensions in prose (no Who:/Why: labels).
10. No `요약:`, `#### 한눈에`, or `### TL;DR` in Ch.2–7; Ch.4 `### 결정 요약` table only.
11. No appendix re-explaining earlier content.
12. Design alternatives: **결정:** / **갈림:** rules; Ch.5–6 follow one To-Be path; Ch.7 열린 질문 for 권장(미확정).
13. Strict depth: Ch.5–6 lead prose before tables/mermaid; Ch.5 ≥2 named components; Ch.5 flow ≥3 numbered steps.
14. Ch.6 API subsection has field-level markdown table + error codes when HTTP; data model has ≥3 field rows.
15. Ch.6 ### 핵심 처리 흐름 has ≥2 error/retry branches (not happy-path only).
16. Every Ch.5 component **Name** appears in Ch.6; no field-level detail in Ch.5; no new Ch.6 component absent from Ch.5.
17. Brownfield: each component bullet has (신규) or (기존).
18. Front matter H2: ## 목차 → ## 이 문서 읽는 법 → ## 1. 서문 (opening + Goals; no ### 목차 in Ch.1).
19. Ch.2–4 each ≥8 prose sentences in ≥2 paragraphs (blank lines between paragraphs).
20. Ch.4 mermaid transition before ### 결정 요약; Ch.5 data-flow mermaid; Ch.6 flow mermaid with branches.
21. Ch.2–4 bridges Ch.2→3, 3→4, 4→5 feel causal when read in order.
22. Ch.4 has ### 결정 요약 table aligned with blockquotes.
23. Ch.5 ### 아키텍처 개요 contains ```mermaid`; each Ch.5 ### has ≥2 lead sentences before structure.
22. Ch.6 each ### has ≥1 lead sentence before tables; no > **사실:** in Ch.5–6; Tier-2 uses [ref:A-n]; Appendix A/B complete.
23. Qualitative: reads like one story front-to-back; no telegraphic fragments a new teammate could not follow.

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
1. Every technical claim in Ch.4–6 has a source block in the same subsection.
2. Tier-1 topics use either:
   - **결정:** + **근거:** (official URL) + **코드:**
   - **갈림:** + **대안:** + **권장:** + **근거:** (official URL for 권장) + **코드:** + **상태:**
3. **갈림:** blocks must not omit **권장:** or **상태:**; max 3 alternatives.
4. Tier-2 facts have **사실:** and **근거:** with PRD anchor + code when brownfield.
5. No Tier-1 backed only by blog/community without official URL.
6. URL format looks intentional (not placeholder example.com unless marked).
7. PRD anchors match actual PRD section/content.
8. No Tier-1 choice stated only in prose without a source block.
9. Ch.5–6 content matches design-sections.md (high-level in 5, detail in 6).

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
7. Ch.5 As-Is vs To-Be: Ch.5–6 describe target state only; current state stays in Ch.3.
8. Component/API names in Ch.6 must appear in Ch.5 first.

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
