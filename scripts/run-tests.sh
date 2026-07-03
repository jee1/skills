#!/usr/bin/env bash
# Run all skill validator unit tests (no pytest required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run() {
  echo "==> $1"
  python3 "$1" -v
}

run prd-to-tdd/scripts/test_validate_tdd.py
run tdd-to-tasks/scripts/test_validate_tasks.py
run tasks-to-issues/scripts/test_validate_issue_spec.py
run tech-debt-harness/scripts/test_harness.py

echo "All skill unit tests passed."
