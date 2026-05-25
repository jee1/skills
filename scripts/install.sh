#!/usr/bin/env bash
# Install skills from this repo into ~/.cursor/skills/
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}"

mkdir -p "$TARGET"

install_skill() {
  local name="$1"
  local src="$REPO_ROOT/$name"
  local dest="$TARGET/$name"

  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "skip: $name (no SKILL.md)" >&2
    return 0
  fi

  ln -sfn "$src" "$dest"
  echo "linked: $dest -> $src"
}

if [[ $# -gt 0 ]]; then
  for name in "$@"; do
    install_skill "$name"
  done
else
  for dir in "$REPO_ROOT"/*/; do
    name="$(basename "$dir")"
    case "$name" in docs|scripts|.git) continue ;; esac
    install_skill "$name"
  done
fi

echo "Done. Skills directory: $TARGET"
