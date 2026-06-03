# Dual-Brain Integration (optional)

`prd-review` works **without** the `dual-brain` skill. This file defines an optional path when `dual-brain` is installed.

**Source of truth:** `~/.cursor/skills/dual-brain/SKILL.md` (also `~/.codex/`, `~/.agents/`).

---

## Availability check

Probe in order; first existing path wins:

1. `~/.cursor/skills/dual-brain/SKILL.md`
2. `~/.codex/skills/dual-brain/SKILL.md`
3. `~/.agents/skills/dual-brain/SKILL.md`

| Result | Action |
|--------|--------|
| **Found** | May use Phase 3b below |
| **Not found** | Orchestrator-only Phase 3; `dual_brain_used: false` in report |

Optional: load `<target-project>/.dual-brain/MEMORY.md` during Right/Left steps per dual-brain SKILL.

---

## When to use dual-brain path

| Signal | Suggestion |
|--------|------------|
| User says `dual brain`, `dual-brain` | **Use** |
| ≥3 `AMB-*` or any `CTR-*` | **Use** |
| Large PRD (>2000 words) or many actors | **Use** |
| Short, single-flow PRD, few findings | **Skip** (orchestrator enough) |
| dual-brain not on disk | **Never** simulate personas |

---

## Phase 3b — Right Brain then Left Brain (sequential)

**Order is fixed:** Right → Left → orchestrator merge. Left never runs before Right.

### Step 0 — Task packet (orchestrator)

Pass to both agents:

- PRD path or excerpt + section list
- Phase 2 coverage map (Partial/Missing rows)
- Draft finding IDs already identified in Phase 3
- `feature_slug`, product context from PRD title/background

### Step 1 — Right Brain (Task, readonly)

Read `dual-brain/SKILL.md` § Right Brain persona.

**PRD-specific deliverables:**

1. **Grilling questions** — assumptions, blind spots, unstated edge cases
2. **Lexicon** — ambiguous terms → canonical definitions
3. **Macro-context** — who wins/loses, scope creep risks
4. **OQ candidates** — map to `AMB-*` / `CMP-*`
5. **Creative alternatives** — 1–2 scope or UX options (for clarification, not TDD design)

### Step 2 — Left Brain (Task, readonly)

Input: task packet + **full Right Brain output**.

**PRD-specific deliverables:**

1. **Contradiction audit** — section pairs → `CTR-*`
2. **Testability audit** — Must items without pass/fail → `TST-*`
3. **Traceability** — missing anchors, duplicate FRs
4. **Terminology** — inconsistent nouns → `TRM-*`
5. **Suggested fix text** — concrete PRD sentence rewrites

### Step 3 — Mediation (once, if needed)

If Left refutes a Right core premise (e.g., PRD says X in §2 and ¬X in §5), one Right re-pass or orchestrator labels `CTR-*` Critical.

### Step 4 — Merge (orchestrator)

Convert all brain output to:

```text
severity | prd-anchor | ID | issue | suggested_fix
```

Update finding counts in frontmatter. Set `dual_brain_used: true`.

---

## Phase 3b — Mode B subagent prompts

When using Task tool, attach [subagent-prompts.md](subagent-prompts.md) §1–2 instead of pasting full dual-brain SKILL.

---

## Install dual-brain (operators)

```bash
git clone https://github.com/sleeplesshan/dual-brain.git ~/.cursor/skills/dual-brain
```

Not required for `prd-review` symlink:

```bash
ln -sfn "$(pwd)/prd-review" ~/.cursor/skills/prd-review
```
