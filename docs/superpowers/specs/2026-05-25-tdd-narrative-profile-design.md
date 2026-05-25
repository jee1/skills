# Design: TDD Narrative Profile (Story-First, No Meta-Labels)

**Date:** 2026-05-25  
**Status:** Implemented (Ch.1 subsection order superseded by [2026-05-25-tdd-layout-diagrams-design.md](2026-05-25-tdd-layout-diagrams-design.md))  
**Scope:** Restore the `prd-to-tdd` skill’s core promise — read front-to-back like a novel (기승전결, 6하원칙, forward-only background chain) — while keeping strict depth (tables, cross-refs, appendices). Replace label-driven readability (요약, 한눈에, TL;DR) with self-explanatory prose.

**Supersedes (partially):** `2026-05-25-tdd-readability-design.md` — navigation lanes and anti-blockquote rules carry forward; **meta-label requirements are removed**.

**Related specs:**

- `2026-05-25-prd-to-tdd-skill-design.md` — base TDD skill
- `2026-05-25-prd-to-tdd-strict-depth-design.md` — Ch.5–6 depth gates
- `2026-05-25-tdd-readability-design.md` — predecessor (Diátaxis / triple-audience)

---

## 1. Problem & Goal

### Problem (user feedback)

After implementing the readability profile, TDD output is easier to scan but **fails the original narrative contract**:

| Symptom | Root cause |
|---------|------------|
| Does not read like a novel; chapters feel disconnected | Readability optimized **structure** (labels, bullets, table-first) over **causal prose** |
| 기승전결 / 6하원칙 not felt in the text | Rules exist in `narrative-rules.md` but validator enforces **labels**, not story dimensions |
| Content too compressed to convey meaning | Ch.6 `≤2 sentences` + telegraphic Ch.2–3; substance gates are char-count, not explanation depth |
| Meta-labels do not help understanding | `요약:`, `#### 한눈에`, `### TL;DR`, `Who`/`Why` — reader should infer role from prose |

User confirmed:

- **Scope:** all chapters (Ch.1–7), not only early or late sections (**D**)
- **Length:** **2×+ prose** acceptable if tables and appendices remain (**C**)
- **Labels:** role titles in body are **not required**; content must speak for itself

### Goal

One Markdown file (`docs/design/YYYY-MM-DD-<feature>-tdd.md`) where:

1. Reading **Ch.1 → Ch.7 in order** feels like one story: earlier facts become background for later sections (forward-only, no temporal back-refs).
2. **기승전결** is experienced in chapter order, not only in a mapping table.
3. **6하원칙** is answered **inside paragraphs** (no `Who:` / `Why:` labels).
4. **Strict depth** unchanged: mermaid, named components, API/entity/error tables, Ch.4 Tier-1 blockquotes, Appendix A/B.
5. **No meta-label crutches** in Ch.2–7 body (see §4 exceptions for Ch.1 navigation and Ch.4 audit index).

### Non-goals

- Splitting into multiple files
- Relaxing table / error-branch / component cross-ref minimums
- Replacing Appendix A/B with inline `> **사실:**` in Ch.5–6 (keep readability rule: Tier-2 via `[ref:A-n]`)
- Auto handoff to `writing-plans`
- English `What`/`Why` section headers (forbidden same as Korean meta-labels)

---

## 2. Design Principles

1. **Prose carries the story; tables carry the spec** — Each `###` opens with connected sentences; tables follow when field-level truth is needed.
2. **Show, don’t label** — If a paragraph is a summary, it reads as one; no `요약:` prefix.
3. **One fact, one canonical home** — Narrative states intent and causality; Ch.6 tables hold field truth; Appendix A holds Tier-2 audit rows (from readability spec).
4. **Bridges, not back-refs** — Forbidden: “앞서”, “see above”. Required: restate or extend prior facts so the next chapter stands alone **forward**.
5. **Navigation meta ≠ body meta** — Ch.1 may keep Goals, reader paths, TOC for **wayfinding**; Ch.2+ body must not use role labels.

---

## 3. Document Architecture

### Ch.1 — 서문 (scan-first navigation, then entry)

**Required order:**

1. `### 목차` — first subsection in Ch.1 (no prose before it)
2. `### 이 문서 읽는 법` — reader path table
3. **Opening paragraph** (no subsection title): 3–5 sentences — scope, outcome, rollout hint; must lead into Ch.2
4. `### Goals / Non-Goals`

| Keep | Change / remove |
|------|-----------------|
| Goals / Non-Goals | Remove `### TL;DR` heading |
| `### 목차` | Move to **top** of Ch.1 (before reader paths and opening) |
| `### 이 문서 읽는 법` | Immediately after 목차; before opening paragraph |

### Ch.2–4 — 起 · 承 · 转 (pure narrative)

| Chapter | Narrative job | 6하 (embedded, not labeled) |
|---------|---------------|------------------------------|
| 2 배경과 문제 | Problem and scope in context | What, Where (and Why implicit in problem) |
| 3 현재/시작점 | As-is or greenfield starting point | What exists, How it works today |
| 4 갭/설계 결정 | Gap → decision; Tier-1 blockquotes | Why change, How (direction), decisions |

**Minimum (validator `--narrative`):**

- Ch.2, Ch.3, Ch.4 each: **≥8 sentences** in non-table body
- **Bridge heuristic:** last non-table sentence of Ch.N shares ≥1 significant token (component name, domain noun) with first sentence of Ch.N+1, OR Ch.N+1 first sentence explicitly names the gap/consequence of Ch.N (keyword list: `때문`, `따라`, `현재`, `PRD`, `미구현`, etc.)

**Ch.4 `### 결정 요약` table:** **Retained** as the **only** allowed “summary” heading — audit index only; must not duplicate full prose from blockquotes (pointer rows: #, topic, choice, status, anchor).

### Ch.5–6 — 结 (prose then reference)

Each required `###`:

1. **Lead prose** (no `요약:`):
   - Ch.5: **≥2 sentences** before mermaid or lists
   - Ch.6: **≥1 sentence** before tables
2. **Mermaid** in Ch.5 `### 아키텍처 개요` (strict, unchanged)
3. **Tables** after prose (API, entity, errors) — strict schemas unchanged
4. **Remove:** `#### 한눈에`, `### 스펙 인덱스` heading

**Ch.6 dev index:** Optional **single markdown table** immediately after Ch.6 chapter intro paragraph (before first `###`), introduced in prose (“아래 표는 …”). No `###` title for that table.

**Component names:** first defined in Ch.5 prose or bullet list; Ch.6 reuses same names (strict cross-ref unchanged).

### Ch.7 + appendices

- Ch.7: short prose acceptable; rollout table allowed
- Appendix A/B: unchanged (citation archive, not narrative rewrite)

---

## 4. Meta-Label Policy

### Forbidden in Ch.2–7 body (validator `--narrative`)

| Pattern | Example |
|---------|---------|
| Summary prefix | `요약:` at line start |
| PM skim block | `#### 한눈에` |
| TL;DR section | `### TL;DR` |
| 6하 labels | `Who:`, `What:`, `When:`, `Where:`, `Why:`, `How:` at line start (EN/KO) |

### Allowed

| Location | Allowed heading / pattern |
|----------|---------------------------|
| Ch.1 | `### Goals / Non-Goals`, `### 이 문서 읽는 법`, `### 목차` |
| Ch.4 | `### 결정 요약` (audit table only) |
| Ch.5–7 | Standard `##` / `###` **topic** titles (e.g. `### API 및 인터페이스`) — must describe **subject**, not **role** |
| Any | `[ref:A-n]`, Tier-1 blockquotes in Ch.4 |

---

## 5. Validation

### Profiles

| Command | Purpose |
|---------|---------|
| `validate-tdd.py <path>` | **Strict** — depth, tables, cross-refs, Ch.4 blockquotes, mermaid; **no** `요약:` / `한눈에` **requirements** |
| `validate-tdd.py <path> --narrative` | **Narrative** — strict + prose minima, bridges, anti-labels, document sentence count |

**Deprecation:** `--readability` prints warning and runs `--narrative` checks where mapped; remove alias in a future release.

### Strict profile changes

| Remove from strict | Rationale |
|--------------------|-----------|
| Mandatory `요약:` first line in Ch.5–6 `###` | Replaced by lead-prose rules under `--narrative` |
| Mandatory `#### 한눈에` | User rejection |
| Mandatory `### 스펙 인덱스` | User rejection |
| Mandatory Ch.1 `### TL;DR` | Replaced by opening paragraph rule under `--narrative` |

**Adjust:** `SUBSECTION_MIN_CHARS` applies to **prose portions** of each `###` (exclude table rows and mermaid fence content) to avoid padding via tables.

**Keep unchanged:** component count, flow steps, API/entity/error tables, Ch.4 summary table row count, Appendix A/B, mermaid, `[ref:A-n]` / no `> **사실:**` in Ch.5–6 (from readability).

### Narrative profile additions

| Check | Rule |
|-------|------|
| `ch2-min-sentences` | Ch.2 ≥8 sentences (non-table) |
| `ch3-min-sentences` | Ch.3 ≥8 sentences |
| `ch4-min-sentences` | Ch.4 ≥8 sentences (excluding blockquote-only lines optional: count prose outside `>`) |
| `ch-bridge-*` | Ch.2→3, 3→4, 4→5 bridges (heuristic) |
| `lead-prose-ch5` | Each Ch.5 `###`: ≥2 prose sentences before table/mermaid |
| `lead-prose-ch6` | Each Ch.6 `###`: ≥1 prose sentence before first table |
| `doc-min-sentences` | Whole doc ≥40 non-table sentences (baseline feature) |
| `forbidden-meta-label` | Regex scan for patterns in §4 |

### narrative-reviewer (subagent)

Add qualitative gates (not automatable):

1. Does Ch.2–4 read as 起·承·转 without needing headings to explain role?
2. Does Ch.5 architecture paragraph explain **why** this shape follows Ch.4 decisions?
3. Does Ch.6 implement **only** components already introduced in Ch.5?
4. Are there telegraphic fragments that fail to explain **to a new team member**?
5. Would removing all `###` titles still leave a traceable story (titles are waypoints, not crutches)?

---

## 6. Skill File Changes

| File | Action |
|------|--------|
| `narrative-rules.md` | Rewrite: story-first, bridges, anti-label, 6하 paragraph guide |
| `design-sections.md` | Replace `요약`/reference-mode with prose-then-table; update depth rubric |
| `tdd-template.md` | Label-free structure; Ch.1 opening paragraph |
| `examples.md` | Good/bad excerpts for narrative style (~2× sentence count) |
| `subagent-prompts.md` | Replace readability items 18–22 with narrative checks |
| `SKILL.md` | Phase 4: draft prose chapters then tables; Phase 5: strict + `--narrative` |
| `scripts/validate-tdd.py` | Implement §5; `--readability` alias |
| `scripts/test_validate_tdd.py` | Fixtures without `요약:`/`한눈에`; narrative pass/fail cases |
| `docs/design/2026-05-25-sample-*-tdd.md` | Migrate to narrative profile (~2× prose) |

---

## 7. Success Criteria

1. Sample TDDs pass `validate-tdd.py` and `validate-tdd.py --narrative`.
2. Sample order-cancel doc has **≥2×** non-table sentence count vs pre-migration baseline (~20 → ~40+).
3. No forbidden meta-labels in Ch.2–7 of samples.
4. PM/dev/audit reader paths in Ch.1 still valid (Goals, paths, TOC).
5. User can read Ch.1→7 once and describe: problem → as-is → gap → decision → architecture → spec → rollout **without** reading label headings.

---

## 8. Implementation Order (for writing-plans)

1. Update `narrative-rules.md` + `design-sections.md`
2. Update `validate-tdd.py` + `test_validate_tdd.py` (strict relax + `--narrative`)
3. Update `tdd-template.md`, `examples.md`, `subagent-prompts.md`, `SKILL.md`
4. Migrate sample TDDs; verify dual validation
5. Set this spec `Status: Implemented`; note supersession in readability spec header (one line)

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Validator bridges are brittle | Heuristic + narrative-reviewer qualitative gate |
| 2× length fatigue | Ch.1 reader paths unchanged; tables unchanged for skimming |
| Agent ignores prose minima | `--narrative` in CI / Phase 5 mandatory |
| Regression on strict depth | Do not lower table/component/error minimums |

---

## Appendix: Reader Paths (post-narrative)

| Reader | Path | Time |
|--------|------|------|
| PM | Ch.1 opening + Goals → Ch.5 mermaid + first prose paragraph per `###` | ~3 min |
| Dev | Ch.4 결정 요약 + Ch.6 tables (after skimming Ch.5 prose) | ~5 min |
| Audit | Ch.4 blockquotes + 결정 요약 + Appendix A/B | ~3 min |
