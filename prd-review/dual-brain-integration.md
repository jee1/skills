# Dual-Brain Integration

`prd-review` supports three pipeline paths: **standard**, **enhanced**, **full**. See **[path-selection.md](path-selection.md)** for auto-selection (complexity score after Phase 2) and user overrides.

| Path | Phase 3b dual-brain | Phase 6 |
|------|---------------------|---------|
| **standard** | — | 3 PRD reviewers parallel (§5–7) |
| **enhanced** | §1 Right → §2 Left **mandatory** | Left Brain (§2); optional §5 |
| **full** | §1 Right → §2 Left **mandatory** | §5–7 parallel (3b complete) |

**Protocol source:** `~/.cursor/skills/dual-brain/SKILL.md` (also `~/.codex/`, `~/.agents/`, `~/.claude/`).

**Project memory:** `<target-project>/.dual-brain/MEMORY.md` — advisory; **PRD text beats stale memory**.

**dual-brain missing** → only **standard** is available (no Phase 3b).

---

## Path selection (quick)

1. User override? → see [path-selection.md](path-selection.md) Step 0  
2. Probe dual-brain SKILL on disk  
3. After Phase 1–2, compute **complexity_score** → auto **standard | enhanced | full**  
4. Announce path once before Phase 3  

Do **not** default to enhanced when score ≥ 8 — use **full**.

---

## Enhanced & full — Phase 3b map

```text
Phase 1 PRD ingest
Phase 2 Coverage scan + complexity signals
Path pick (standard | enhanced | full)
Phase 3 Orchestrator draft findings
Phase 3b §1 Right Brain → §2 Left Brain    ← enhanced & full only
Phase 4 Pre-inventory draft
Phase 6 Subagent review (A | B | C)
Phase 5 Report + gate
Phase 5b validate-prd-review.py
Phase 7 Clarification (optional)
```

**Standard** skips Phase 3b; Phase 6 Mode A (§5–7 parallel).

---

## Phase 3b — Right Brain then Left Brain (mandatory on enhanced & full)

**Goal:** Deepen PRD critique before Phase 6 and report. Output merges into findings — not pasted verbatim into Executive summary.

### Step 0 — Task packet (orchestrator)

Pass to both agents:

- PRD path or full text + section list
- Phase 2 coverage map (all Partial/Missing rows)
- Phase 3 draft finding IDs and lines
- `feature_slug`, `prd_review_path`, word count
- Optional `.dual-brain/MEMORY.md` excerpts

### Step 1 — Right Brain (§1)

Read `dual-brain/SKILL.md` § Right Brain persona. Spawn Task per [subagent-prompts.md](subagent-prompts.md) §1.

**PRD-specific deliverables:**

1. Grilling questions — assumptions, blind spots, unstated edge cases
2. Lexicon — ambiguous terms → canonical definitions
3. Macro-context — who wins/loses, scope creep risks
4. OQ candidates — map to `AMB-*` / `CMP-*`
5. Creative alternatives — 1–2 scope or UX options (for clarification, not TDD design)

### Step 2 — Left Brain (§2)

Input: task packet + **full Right Brain output**.

Read `dual-brain/SKILL.md` § Left Brain persona. Spawn Task per §2.

**PRD-specific deliverables:**

1. Contradiction audit — section pairs → `CTR-*`
2. Testability audit — Must items without pass/fail → `TST-*`
3. Traceability — missing anchors, duplicate FRs
4. Terminology — inconsistent nouns → `TRM-*`
5. Suggested fix text — concrete PRD sentence rewrites

### Step 3 — Mediation (once, if needed)

If Left refutes a Right core premise (e.g., PRD says X in §2 and ¬X in §5), one Right re-pass or orchestrator labels `CTR-*` Critical.

### Step 4 — Merge (orchestrator)

Convert all brain output to finding line format. Update counts. Set `dual_brain_used: true`.

On **full** path, Phase 6 Mode C runs §5–7 only — Phase 3b already completed §1→§2. Merge Phase 3b findings as input; dedupe aggressively.

---

## When to skip dual-brain

| Condition | Action |
|-----------|--------|
| Path is **standard** | Skip Phase 3b; `dual_brain_used: false` |
| dual-brain SKILL not on disk | Force **standard**; skip Phase 3b |
| User forced enhanced/full but no dual-brain | Downgrade to **standard**; explain once |

Do **not** simulate Right/Left personas without the skill when user expected dual-brain — use Phase 6 §5–7 instead.

---

## Install dual-brain (operators)

```bash
git clone https://github.com/sleeplesshan/dual-brain.git ~/.cursor/skills/dual-brain
```

Symlink prd-review:

```bash
ln -sfn "$(pwd)/prd-review" ~/.cursor/skills/prd-review
```
