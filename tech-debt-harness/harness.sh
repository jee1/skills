#!/usr/bin/env bash
# 기술 부채 하네스 — audit → issue → fix → PR
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$SCRIPT_DIR/scripts"
HARNESS="$SCRIPT_DIR/harness.sh"
WORKSPACE="$(pwd)"
DATE="$(date +%Y-%m-%d)"
OUT_DIR="$WORKSPACE/docs/tech-debt"
RAW="$OUT_DIR/${DATE}-raw-audit.json"
AUDIT="${AUDIT:-$OUT_DIR/${DATE}-audit.json}"
REGISTRY="$OUT_DIR/registry.json"

require_issue() {
  if [[ -z "${ISSUE:-}" ]]; then
    echo "ISSUE=<번호> 필요" >&2
    exit 1
  fi
}

# ── 복사용 다음 단계 안내 ─────────────────────────────────────────────
print_next() {
  local step="${1:-}"
  local issue_ref="${ISSUE:-<번호>}"
  case "$step" in
    after_audit)
      cat <<EOF

──────────────── 다음 단계 (복사해서 실행) ────────────────
cd "$WORKSPACE"
"$HARNESS" run
────────────────────────────────────────────────────────────
EOF
      ;;
    after_enrich)
      cat <<EOF

──────────────── 다음 단계 (복사해서 실행) ────────────────
cd "$WORKSPACE"
AUDIT="$AUDIT" "$HARNESS" continue
DRY_RUN=1 "$HARNESS" issue
────────────────────────────────────────────────────────────
EOF
      ;;
    after_continue)
      cat <<EOF

──────────────── 다음 단계 (복사해서 실행) ────────────────
cd "$WORKSPACE"
DRY_RUN=1 "$HARNESS" issue
"$HARNESS" issue
────────────────────────────────────────────────────────────
EOF
      ;;
    after_issue)
      cat <<EOF

──────────────── 다음 단계 (승인 후, 복사해서 실행) ────────────────
cd "$WORKSPACE"
# 1) GitHub에서 이슈에 tech-debt-approved 라벨 추가
# 2) 처리 시작 (브랜치 생성):
ISSUE=$issue_ref "$HARNESS" fix-start
# 3) 코드 수정 후:
"$HARNESS" fix-verify
"$HARNESS" fix-commit
ISSUE=$issue_ref "$HARNESS" fix-pr
────────────────────────────────────────────────────────────
EOF
      ;;
    after_fix_start)
      cat <<EOF

──────────────── 다음 단계 (복사해서 실행) ────────────────
cd "$WORKSPACE"
# 코드 수정 (에이전트 또는 직접) 후:
"$HARNESS" fix-verify
"$HARNESS" fix-commit
ISSUE=$issue_ref "$HARNESS" fix-pr
────────────────────────────────────────────────────────────
EOF
      ;;
    after_fix_verify)
      cat <<EOF

──────────────── 다음 단계 (복사해서 실행) ────────────────
cd "$WORKSPACE"
"$HARNESS" fix-commit
ISSUE=$issue_ref "$HARNESS" fix-pr
────────────────────────────────────────────────────────────
EOF
      ;;
    after_fix_commit)
      cat <<EOF

──────────────── 다음 단계 (복사해서 실행) ────────────────
cd "$WORKSPACE"
ISSUE=$issue_ref "$HARNESS" fix-pr
────────────────────────────────────────────────────────────
EOF
      ;;
    *)
      ;;
  esac
}

run_continue() {
  python3 "$SCRIPTS/validate-audit.py" "$AUDIT"
  python3 "$SCRIPTS/prioritize.py" --audit "$AUDIT" --print-top
  python3 "$SCRIPTS/sync-registry.py" --workspace "$WORKSPACE" --audit "$AUDIT" --registry "$REGISTRY"
}

usage() {
  cat <<EOF
사용법: harness.sh <명령> [옵션]

등록 파이프라인:
  run            audit → enrich → validate → prioritize → sync
  audit / enrich / continue / validate / prioritize / sync
  issue          GitHub 이슈 등록 (DRY_RUN=1 미리보기)

이슈 처리 파이프라인 (승인 후):
  fix-start      tech-debt-approved 확인 → 브랜치 생성 (ISSUE 필수)
  fix-verify     테스트 실행
  fix-commit     변경 커밋
  fix-pr         push + PR 생성 (ISSUE 또는 .active-fix.json)
  fix            fix-start → (수동 수정) 안내 — 한 번에 끝나지 않음

기타:
  check-approval ISSUE=<번호>

환경 변수:
  AUDIT, ISSUE, DRY_RUN, FORCE_ENRICH, ALLOW_DIRTY

예:
  cd ~/git/myrepo && ~/.cursor/skills/tech-debt-harness/harness.sh run
  ~/.cursor/skills/tech-debt-harness/harness.sh issue
  ISSUE=638 ~/.cursor/skills/tech-debt-harness/harness.sh fix-start
  ~/.cursor/skills/tech-debt-harness/harness.sh fix-verify
  ~/.cursor/skills/tech-debt-harness/harness.sh fix-commit
  ISSUE=638 ~/.cursor/skills/tech-debt-harness/harness.sh fix-pr
EOF
}

cmd="${1:-}"
shift || true

case "$cmd" in
  audit)
    python3 "$SCRIPTS/run-audit.py" --workspace "$WORKSPACE" --output "$RAW"
    print_next after_audit
    ;;
  enrich)
    extra=()
    [[ "${FORCE_ENRICH:-0}" == "1" ]] && extra+=(--force)
    python3 "$SCRIPTS/mechanical-enrich.py" --raw "$RAW" --output "$AUDIT" "${extra[@]}"
    print_next after_enrich
    ;;
  continue)
    run_continue
    print_next after_continue
    ;;
  validate)
    python3 "$SCRIPTS/validate-audit.py" "$AUDIT"
    ;;
  prioritize)
    python3 "$SCRIPTS/prioritize.py" --audit "$AUDIT" --print-top
    ;;
  sync)
    python3 "$SCRIPTS/sync-registry.py" --workspace "$WORKSPACE" --audit "$AUDIT" --registry "$REGISTRY"
    ;;
  issue)
    extra=()
    [[ "${DRY_RUN:-0}" == "1" ]] && extra+=(--dry-run)
    [[ -n "${ITEM_ID:-}" ]] && extra+=(--item-id "$ITEM_ID")
    python3 "$SCRIPTS/create-issue.py" --workspace "$WORKSPACE" --audit "$AUDIT" "${extra[@]}"
    print_next after_issue
    ;;
  check-approval)
    require_issue
    python3 "$SCRIPTS/check-approval.py" --workspace "$WORKSPACE" --issue "$ISSUE"
    ;;
  fix-start)
    require_issue
    extra=()
    [[ "${DRY_RUN:-0}" == "1" ]] && extra+=(--dry-run)
    python3 "$SCRIPTS/start-fix.py" --workspace "$WORKSPACE" --issue "$ISSUE" "${extra[@]}"
    print_next after_fix_start
    ;;
  fix-verify)
    extra=()
    [[ -n "${TEST_CMD:-}" ]] && extra+=(--cmd "$TEST_CMD")
    python3 "$SCRIPTS/verify-fix.py" --workspace "$WORKSPACE" "${extra[@]}"
    print_next after_fix_verify
    ;;
  fix-commit)
    extra=()
    [[ "${DRY_RUN:-0}" == "1" ]] && extra+=(--dry-run)
    [[ -n "${COMMIT_MSG:-}" ]] && extra+=(--message "$COMMIT_MSG")
    python3 "$SCRIPTS/fix-commit.py" --workspace "$WORKSPACE" "${extra[@]}"
    print_next after_fix_commit
    ;;
  fix-pr)
    extra=()
    [[ "${DRY_RUN:-0}" == "1" ]] && extra+=(--dry-run)
    pr_args=(--workspace "$WORKSPACE")
    [[ -n "${ISSUE:-}" ]] && pr_args+=(--issue "$ISSUE")
    python3 "$SCRIPTS/create-pr.py" "${pr_args[@]}" "${extra[@]}"
    ;;
  fix)
    require_issue
    "$0" fix-start
    echo ""
    echo "※ 코드 수정은 자동화되지 않습니다. 수정 후 fix-verify → fix-commit → fix-pr 실행"
    ;;
  run|mechanical)
    python3 "$SCRIPTS/run-audit.py" --workspace "$WORKSPACE" --output "$RAW"
    extra=()
    [[ "${FORCE_ENRICH:-0}" == "1" ]] && extra+=(--force)
    if [[ -f "$AUDIT" && "${FORCE_ENRICH:-0}" != "1" ]]; then
      echo "audit.json 이미 있음 → enrich 스킵 ($AUDIT). 덮어쓰려면 FORCE_ENRICH=1"
    else
      python3 "$SCRIPTS/mechanical-enrich.py" --raw "$RAW" --output "$AUDIT" "${extra[@]}"
    fi
    run_continue
    echo ""
    echo "✓ run 완료: $AUDIT"
    print_next after_continue
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    echo "알 수 없는 명령: $cmd" >&2
    usage >&2
    exit 1
    ;;
esac
