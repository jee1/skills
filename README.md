# Agent Skills

Cursor Agent Skills maintained in this repository.

## Skills

| Skill | Description |
|-------|-------------|
| [prd-to-tdd](prd-to-tdd/) | PRD + codebase → TDD (7 chapters: 상위설계, 상세설계, 마무리) |

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
├── prd-to-tdd/           # Skill package (SKILL.md + references + scripts)
└── docs/
    ├── superpowers/specs/   # Design specs
    └── design/              # Sample / reference TDD outputs
```

## Maintaining a skill

1. Edit files under `<skill-name>/` in this repo.
2. Re-run install symlink if the target path changed.
3. Validate script (example):

   ```bash
   python prd-to-tdd/scripts/validate-tdd.py docs/design/2026-05-25-sample-order-cancel-tdd.md
   # strict (default) enforces Ch.5–6 depth; add --lenient for legacy drafts
   ```

Design spec for `prd-to-tdd`: [docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md](docs/superpowers/specs/2026-05-25-prd-to-tdd-skill-design.md). Strict depth profile: [docs/superpowers/specs/2026-05-25-prd-to-tdd-strict-depth-design.md](docs/superpowers/specs/2026-05-25-prd-to-tdd-strict-depth-design.md).
