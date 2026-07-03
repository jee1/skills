# Agent Skills

Cursor Agent Skills maintained in this repository.

## Skills

| Skill | Description |
|-------|-------------|
| [prd-review](prd-review/) | PRD ambiguity/contradiction audit + TDD-readiness gate; optional [dual-brain](https://github.com/sleeplesshan/dual-brain) Right→Left — run before `prd-to-tdd` |
| [prd-to-tdd](prd-to-tdd/) | PRD + codebase → TDD (7 chapters); optional [dual-brain](https://github.com/sleeplesshan/dual-brain) compact review — falls back to 3 reviewers if not installed |
| [tdd-to-tasks](tdd-to-tasks/) | Validated TDD → implementation tasks (RTM, AC/Test traceability) |
| [tasks-to-issues](tasks-to-issues/) | Issue Spec per AC → validate → GitHub/Jira/Paperclip registration |
| [tech-debt-harness](tech-debt-harness/) | Static audit + tech-debt scoring → GitHub issue (label approval) → fix + PR |

## Install (Cursor)

Link a skill into your personal Cursor skills directory:

```bash
ln -sfn "$(pwd)/prd-to-tdd" ~/.cursor/skills/prd-to-tdd
```

Or install all skills under this repo:

```bash
for d in */; do
  name="${d%/}"
  case "$name" in docs|scripts|.git) continue ;; esac
  [ -f "$name/SKILL.md" ] && ln -sfn "$(pwd)/$name" ~/.cursor/skills/"$name"
done
```

Verify:

```bash
ls -la ~/.cursor/skills/prd-to-tdd/SKILL.md
```

## Repository layout

```text
skills/
├── README.md
├── prd-review/           # PRD quality gate before TDD (SKILL.md + references + scripts)
├── prd-to-tdd/           # Skill package (SKILL.md + references + scripts)
├── tdd-to-tasks/         # TDD → tasks skill + validate-tasks.py
├── tasks-to-issues/      # Issue Spec + validate-issue-spec.py + generate-issue-specs.py
├── tech-debt-harness/    # harness.sh + audit/issue scripts + label-gated fix workflow
└── docs/
    ├── superpowers/specs/   # Design specs
    ├── design/              # Sample / reference TDD outputs
    ├── tasks/               # Sample / reference task lists
    └── issues/              # Sample / reference Issue Specs (per AC)
```

## Maintaining a skill

1. Edit files under `<skill-name>/` in this repo.
2. Re-run install symlink if the target path changed.
3. Validate script (example):

   ```bash
   ./scripts/run-tests.sh
   python prd-review/scripts/validate-prd-review.py docs/reviews/YYYY-MM-DD-<feature>-prd-review.md
   python prd-to-tdd/scripts/validate-tdd.py docs/design/2026-05-25-sample-order-cancel-tdd.md
   python prd-to-tdd/scripts/validate-tdd.py docs/design/2026-05-25-sample-order-cancel-tdd.md --narrative
   # strict (default): Ch.5–6 depth + Must FR→RTM→AC + OQ→Ch.7; --lenient skips depth/front-matter extras
   python tdd-to-tasks/scripts/validate-tasks.py docs/tasks/2026-05-25-sample-order-cancel-tasks.md \
     --tdd docs/design/2026-05-25-sample-order-cancel-tdd.md
   python tasks-to-issues/scripts/generate-issue-specs.py docs/tasks/2026-05-25-sample-order-cancel-tasks.md \
     --tdd docs/design/2026-05-25-sample-order-cancel-tdd.md --output-dir docs/issues --foundation
   python tasks-to-issues/scripts/validate-issue-spec.py docs/issues/2026-05-25-order-cancel-api-AC-1-spec.md \
     --tdd docs/design/2026-05-25-sample-order-cancel-tdd.md \
     --tasks docs/tasks/2026-05-25-sample-order-cancel-tasks.md
   python tech-debt-harness/scripts/test_harness.py
   ./tech-debt-harness/harness.sh audit   # from target repo root
   ```

Design spec for `prd-to-tdd`: [docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md](docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md). Strict depth profile: [docs/superpowers/specs/2026-05-25-prd-to-tdd-strict-depth-design.md](docs/superpowers/specs/2026-05-25-prd-to-tdd-strict-depth-design.md).
