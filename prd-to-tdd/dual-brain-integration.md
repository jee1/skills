# Dual-Brain Integration

`prd-to-tdd` supports three pipeline paths: **standard**, **enhanced**, **full**. See **[path-selection.md](path-selection.md)** for auto-selection (complexity score after Phase 2) and user overrides.

| Path | dual-brain pre-draft | Phase 6 |
|------|----------------------|---------|
| **standard** | — | 3 reviewers parallel |
| **enhanced** | 2b, 3b, 3c | Left Brain (+ narrative if doubt) |
| **full** | 2b, 3b, 3c | Left Brain **then** 3 reviewers parallel |

**Protocol source:** `~/.cursor/skills/dual-brain/SKILL.md` (also `~/.codex/`, `~/.agents/`, `~/.claude/`).

**Project memory:** `<target-repo>/.dual-brain/MEMORY.md` — advisory; **code and PRD beat stale memory**.

**dual-brain missing** → only **standard** is available (no 2b/3c).

---

## Path selection (quick)

1. User override? → see [path-selection.md](path-selection.md) Step 0  
2. Probe dual-brain SKILL on disk  
3. After Phase 1–2, compute **complexity_score** → auto **standard | enhanced | full**  
4. Announce path once before Phase 3  

Do **not** default to enhanced when score ≥ 8 — use **full**.

---

## Enhanced & full — shared phase map

```text
Phase 1 PRD ingest
Phase 2 Code analysis + mode
Phase 2b Dual-brain analysis (Right → Left)     ← NEW
Phase 3 Outline (uses 2b notes)
Phase 3b Right Brain grill (Tier-1 + scope)   ← expanded
Phase 3b′ User confirm (needs-user-confirm only)
Phase 3c Left Brain design blueprint          ← NEW
Phase 4 Draft Ch.1–8 (uses 3c blueprint)
Phase 5 validate-tdd.py (+ --narrative)
Phase 6 review (Mode B enhanced | Mode C full)
Phase 7 Save & report
```

**Standard** skips **2b**, **3b** spawn, **3c**; orchestrator **3b′** only; Phase 6 Mode A.

---

## Phase 2b — Dual-brain analysis (enhanced & full only)

**Goal:** Deepen PRD understanding and code grounding **before** the outline. Output is **internal notes** (not pasted into the TDD verbatim).

1. **Memory intake** — dual-brain SKILL § Step 0A on `<target-repo>/.dual-brain/MEMORY.md`.
2. **Task context** — Step 0B: feature slug, PRD summary, mode (brownfield/greenfield), repo scope.
3. **Right Brain** — Task `generalPurpose`, `readonly: true`, prompt [subagent-prompts.md](subagent-prompts.md) §6.
   - Deliverables: grilling questions, lexicon, macro-context, PRD blind spots, memory suspicions, creative structure hints.
4. **Left Brain** — Task sequential after Right Brain, prompt §7.
   - Deliverables: verified gaps (path:line), PRD↔code conflicts (code wins), mode check, component/API candidates, risk list.
5. **Orchestrator synthesis** — One-page **Analysis Brief** used in Phase 3–4:
   - Confirmed facts vs assumptions
   - Gap list (brownfield) / decision list (greenfield)
   - Recommended Ch.6 Tier-1 topics + tags
   - Lexicon table (ambiguous PRD terms → definition)
   - Open questions for Ch.8

Do **not** skip Phase 2 Serena/code scan; 2b **interprets** Phase 2 evidence.

---

## Phase 3b — Right Brain grill (enhanced & full)

**When enhanced or full:** run **always** after outline draft (even if no `needs-user-confirm`).

| Outline signal | Right Brain focus |
|----------------|-------------------|
| `needs-user-confirm` | Alternatives, blind spots, user message draft |
| `multi-recommend` | Challenge 권장 vs rejected; missing PRD constraints |
| `single` only | Still grill scope, NFR, testability, Ch.3 FR completeness |
| Brownfield + gaps | Challenge “미구현” labels and hidden dependencies |
| Greenfield | Challenge stack assumptions and fictional scope creep |

1. Memory intake (Hot/Warm only if relevant).
2. Spawn Right Brain — [subagent-prompts.md](subagent-prompts.md) §8 + outline + Analysis Brief + PRD excerpt.
3. Use output to:
   - Refine outline rows (FR, RTM, Ch.5–7 mapping)
   - Structure **user confirmation** when `needs-user-confirm` exists
   - Add OQ-* rows for unresolved grills → Ch.8 later

**Do not** write Ch.6 `### Decision Summary` cards for `needs-user-confirm` topics until the user picks.

**Standard path:** orchestrator-only Phase 3b per [SKILL.md](SKILL.md) — no Right Brain spawn.

---

## Phase 3c — Left Brain design blueprint (enhanced & full only)

**Goal:** Verified skeleton for **Ch.5 → Ch.6 → Ch.7** before prose drafting.

1. Inputs: Analysis Brief, refined outline, Right Brain grill output, PRD, repo (Serena paths).
2. Spawn Left Brain — [subagent-prompts.md](subagent-prompts.md) §9.
3. **Blueprint** sections (orchestrator keeps as Phase 4 scratchpad):
   - Ch.5: gap narrative bullets, transition mermaid labels, component list, data-flow steps (≥5)
   - Ch.6: Decision Summary table draft + Tier-1 card fields (no final prose yet if user confirm pending)
   - Ch.7: API table skeleton, entity fields, error branches (≥2), AC IDs + conditions, test matrix
4. Resolve Left Brain vs Right Brain conflicts once (dual-brain SKILL § Step 3); code/PRD win over memory.

Phase 4 must **follow** the blueprint on **enhanced/full**; deviations need a note in Ch.8 Open Questions.

---

## Phase 4 — Drafting with dual-brain (enhanced & full)

Orchestrator writes the TDD (not delegated wholesale). Use:

| Source | Use in draft |
|--------|----------------|
| Analysis Brief | Ch.2–4 tone, gap honesty, lexicon |
| Outline + blueprint | Ch.5–7 structure |
| Right Brain grill | Ch.8 OQ, Non-Goals, Risks |
| Left Brain verification | `path:line`, Tier-1 **참고:** URLs, AC wording |

**Order unchanged:** Ch.1→4, then Ch.5→6→7, Ch.8, appendices.

After draft, optional **light Left Brain pass** (orchestrator self-check against §9 checklist) before Phase 5 — no extra spawn unless Major issues found in self-read.

---

## Phase 6 — Review modes

After `validate-tdd.py` strict + `--narrative` exit `0`. Map findings to `severity | chapter:line | issue | fix`. Max 2 rounds.

### Mode A — path **standard**

Three parallel tasks — [subagent-prompts.md](subagent-prompts.md) §1–3.

### Mode B — path **enhanced**

| Step | Agent | Prompt |
|------|-------|--------|
| 1 | left-brain-verification-reviewer | §4 (sequential) |
| 2 | narrative-reviewer | §1 only if semantic doubt |

### Mode C — path **full**

| Step | Agent | Prompt |
|------|-------|--------|
| 1 | left-brain-verification-reviewer | §4 (sequential) |
| 2 | narrative + citation + code-grounding | §1–3 **parallel** |
| 3 | Orchestrator | Dedupe per [path-selection.md](path-selection.md) |

Phase 7 report examples:

- `path: standard | validation: script + 3 reviewers`
- `path: enhanced | validation: script + 2b/3b/3c + left-brain [+ narrative]`
- `path: full | validation: script + 2b/3b/3c + left-brain + 3 reviewers (deduped)`

---

## Script vs dual-brain

| Concern | Phase 5 script | Phase 2b/3c/6 |
|---------|----------------|---------------|
| H2 order, FR/RTM, depth gates | strict | blueprint pre-check |
| Narrative bridges, mermaid | `--narrative` | Right Brain grill + narrative-reviewer |
| path:line, fiction, code-first | partial | Left Brain 2b + 6 |
| Tier-1 URL, PRD anchors | partial | Left Brain 3c + 6 |
| Story / 기승전결 | `--narrative` | narrative-reviewer if doubt |

---

## Memory auto-save (enhanced & full)

After Phase 7 (or when durable project facts emerged), orchestrator may update `<target-repo>/.dual-brain/MEMORY.md` per dual-brain SKILL § Step 4A:

- Architecture decisions from Ch.6 (confirmed only)
- Rejected alternatives
- Feature vocabulary from lexicon
- Do **not** store PRD secrets or credentials

Ask the user what to remove or adjust after saving.

---

## Install dual-brain (operators)

```bash
git clone https://github.com/sleeplesshan/dual-brain.git ~/.cursor/skills/dual-brain
# or: ln -sfn /path/to/dual-brain ~/.cursor/skills/dual-brain
```

`prd-to-tdd` symlink (unchanged):

```bash
ln -sfn "$(pwd)/prd-to-tdd" ~/.cursor/skills/prd-to-tdd
```
