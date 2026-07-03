#!/usr/bin/env bash
# 스킬 validator unittest 일괄 실행 (pytest 불필요).
# 존재하는 테스트 파일만 실행 — 패키지 추가 전후 모두 CI green 유지.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SUITES=(
  prd-to-tdd/scripts/test_validate_tdd.py
  tdd-to-tasks/scripts/test_validate_tasks.py
  tasks-to-issues/scripts/test_validate_issue_spec.py
  tech-debt-harness/scripts/test_harness.py
)

run() {
  echo "==> $1"
  python3 "$1" -v
}

ran=0
for suite in "${SUITES[@]}"; do
  if [[ -f "$suite" ]]; then
    run "$suite"
    ran=$((ran + 1))
  else
    echo "==> skip (없음): $suite"
  fi
done

if [[ "$ran" -eq 0 ]]; then
  echo "실행할 테스트 스위트가 없습니다." >&2
  exit 1
fi

echo "스킬 unit test 통과."
