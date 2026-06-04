# Dual-Brain Integration (optional)

`prd-to-tdd` works **without** the `dual-brain` skill. This file defines an **optional** path when `dual-brain` is installed and the orchestrator chooses to use it.

**Source of truth for dual-brain protocol:** `~/.cursor/skills/dual-brain/SKILL.md` (also `~/.codex/skills/dual-brain/`, `~/.agents/skills/dual-brain/`).

---

## Availability check (orchestrator, before Phase 3b or 6)

Probe in order; **first existing path wins**:

1. `~/.cursor/skills/dual-brain/SKILL.md`
2. `~/.codex/skills/dual-brain/SKILL.md`
3. `~/.agents/skills/dual-brain/SKILL.md`

| Result | Action |
|--------|--------|
| **Found** | May use dual-brain paths below if user asked for dual-brain **or** Tier-1 forks are high-impact |
| **Not found** | Use **default** Phase 3b (orchestrator asks user) and Phase 6 (**3 parallel subagents**). Do not simulate dual-brain personas. Tell user once: `dual-brain` not installed — using standard reviewers. |

Optional project memory: `<target-project>/.dual-brain/MEMORY.md` — load per dual-brain SKILL during Right/Left steps only.

---

## When to use dual-brain path

| Signal | Suggestion |
|--------|------------|
| User says `dual brain`, `dual-brain`, `left brain right brain` | **Use** dual-brain path |
| Phase 3 outline has ≥1 `needs-user-confirm` Tier-1 fork | **Phase 3b:** Right Brain grill before user message |
| Brownfield + many PRD↔code gaps | **Phase 6:** Left Brain verification |
| Simple greenfield, script already passed narrative | **Skip** narrative-reviewer; Left Brain only |
| `dual-brain` skill not on disk | **Never** use this file's spawn pattern — default only |

---

## Phase 3b — Right Brain (optional, sequential)

**Only if** dual-brain skill exists **and** outline has `needs-user-confirm` items.

1. Read `dual-brain/SKILL.md` § Step 0A–0B (memory intake + task definition).
2. Spawn **one** Task `generalPurpose`, `readonly: true` with Right Brain persona from dual-brain SKILL + outline + PRD summary + `.dual-brain/MEMORY.md` if present.
3. Use Right Brain output to structure the **user confirmation message** (alternatives, 권장, blind spots).
4. **Do not** draft Ch.6 Alternatives decision cards for those topics until user answers.

If dual-brain missing: follow [SKILL.md](SKILL.md) Phase 3b (orchestrator-only) — unchanged.

---

## Phase 6 — Two modes

### Mode A — Default (always valid)

Spawn **three** Task agents **in parallel** — see [subagent-prompts.md](subagent-prompts.md) §1–3.

Use when: dual-brain not installed, user did not request dual-brain, or Left Brain path already ran and found nothing extra.

### Mode B — Compact (dual-brain installed)

After `validate-tdd.py` strict + `--narrative` exit `0`:

| Step | Agent | Replaces | Skip when |
|------|-------|----------|-----------|
| 1 | **left-brain-verification-reviewer** | citation-reviewer + code-grounding-reviewer | never on this path |
| 2 | **narrative-reviewer** | — | `--narrative` passed **and** no semantic doubt |

- Step 1: **sequential** Task (read repo + PRD + TDD).
- Step 2: optional parallel only if narrative pass needed.

Prompt: [subagent-prompts.md](subagent-prompts.md) §4–5.

**Output contract (both modes):** merge only lines matching:

```text
severity | chapter:line | issue | fix
```

Map dual-brain prose to this format before merge. **Critical** → edit → Phase 5 → Phase 6 again (max 2 rounds).

---

## Script vs reviewers (compact path)

| Concern | Phase 5 script | Phase 6 compact |
|---------|----------------|-----------------|
| Headers, depth, FR→RTM→AC, OQ→Ch.8 | strict | — (trust script) |
| `요약:`, tilde, mermaid placement | strict + `--narrative` | narrative-reviewer only if doubtful |
| Tier-1 URL, PRD anchor match | partial | left-brain-verification |
| path:line, fiction, code-first | — | left-brain-verification |
| Story flow / weak bridges | `--narrative` partial | narrative-reviewer if spawned |

---

## Phase 7 — Report path used

Tell user which validation path ran:

- `validation: script + 3 reviewers (default)`
- `validation: script + dual-brain compact (left-brain [+ narrative])`
- `dual-brain: not installed — default reviewers`

---

## Install dual-brain (operators)

```bash
git clone https://github.com/sleeplesshan/dual-brain.git ~/.cursor/skills/dual-brain
# or: ln -sfn /path/to/dual-brain ~/.cursor/skills/dual-brain
```

Not required for `prd-to-tdd` symlink:

```bash
ln -sfn "$(pwd)/prd-to-tdd" ~/.cursor/skills/prd-to-tdd
```
