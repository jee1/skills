# Design: prd-to-tdd Strict Depth Profile

**Date:** 2026-05-25  
**Status:** Implemented  
**Scope:** Enforce substantive Ch.5–6 content when generating TDD from PRD.

---

## Problem

Ch.5–6 subsections existed structurally but passed validation with thin content (single-line data flows, no API tables, no error branches). Root causes:

- `validate-tdd.py` checked headers only, not depth
- `examples.md` showed `…` for Ch.5–6 good examples
- Phase 3 outline did not require Ch.5–6 mapping tables

## Decision

Adopt **strict profile (A)** as default validation:

- Mechanical gates in `validate-tdd.py` (default strict; `--lenient` for legacy)
- Depth rubric in `design-sections.md`
- Mandatory `outline-template.md` before Phase 4
- Full Ch.5–6 good/bad examples in `examples.md`
- Subagent narrative-reviewer items 13–17 for semantic depth

## Strict gates (summary)

| Check | Minimum |
|-------|---------|
| ### 요약: | Every Ch.5–6 subsection |
| Subsection length | 120 chars |
| Source block | Per substantive ### |
| Ch.5 components | ≥2 named, brownfield (신규/기존) |
| Ch.5 data flow | ≥3 numbered steps |
| Ch.6 API | Markdown table ≥3 data rows |
| Ch.6 data model | Field table ≥3 rows |
| Ch.6 processing | ≥2 error/retry lines |
| Ch.5→Ch.6 | Every component name referenced in Ch.6 |

## Files changed

- `prd-to-tdd/scripts/validate-tdd.py` — `check_design_depth()`, `--lenient`
- `prd-to-tdd/design-sections.md` — depth rubric
- `prd-to-tdd/outline-template.md` — new
- `prd-to-tdd/tdd-template.md` — scaffolding
- `prd-to-tdd/examples.md` — Ch.5–6 good/bad
- `prd-to-tdd/SKILL.md` — Phase 3 gate, Phase 4 expansion rule
- `prd-to-tdd/subagent-prompts.md` — depth checklist
- `prd-to-tdd/narrative-rules.md`, `citation-tiers.md` — outline/citation alignment
- `docs/design/*-sample-*-tdd.md` — expanded reference outputs

## Out of scope

- Separate 4th subagent (depth covered by script + narrative-reviewer)
- Auto handoff to `writing-plans`
