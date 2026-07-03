#!/usr/bin/env bash
# 기술 부채 하네스 — audit → enrich → validate → prioritize → sync → issue
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

# ── 복사용 다음 단계 안내 ─────────────────────────────────────────────
print_next() {
  local step="${1:-}"
  case "$step" in
    after_audit)
      cat <<EOF

──────────────── 다음 단계 (복사해서 실행) ────────────────
# 한 번에 끝내기 (규칙 기반 점수화 + validate/prioritize/sync):
cd "$WORKSPACE"
"$HARNESS" run

# 또는 단계별:
"$HARNESS" enrich
AUDIT="$AUDIT" "$HARNESS" validate
AUDIT="$AUDIT" "$HARNESS" prioritize
AUDIT="$AUDIT" "$HARNESS" sync
DRY_RUN=1 "$HARNESS" issue

# 더 정밀한 점수화가 필요하면 Cursor 채팅에 붙여넣기:
# docs/tech-debt/${DATE}-raw-audit.json 을 점수화해서 audit.json 으로 enrichment 해줘
# (완료 후) AUDIT="$AUDIT" "$HARNESS" continue
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
# 승인 후 이슈에 tech-debt-approved 라벨 → 수정·PR (SKILL.md Phase 6+)
────────────────────────────────────────────────────────────
EOF
      ;;
    after_issue)
      cat <<EOF

──────────────── 다음 단계 ────────────────
GitHub 이슈에 tech-debt-approved 라벨이 붙으면 Cursor 채팅:
# 이슈 #<번호> 기술부채 수정하고 PR 올려줘
────────────────────────────────────────────────────────────
EOF
      ;;
    *)
      ;;
  esac
}

run_continue() {
  AUDIT="$AUDIT" python3 "$SCRIPTS/validate-audit.py" "$AUDIT"
  AUDIT="$AUDIT" python3 "$SCRIPTS/prioritize.py" --audit "$AUDIT" --print-top
  python3 "$SCRIPTS/sync-registry.py" --workspace "$WORKSPACE" --audit "$AUDIT" --registry "$REGISTRY"
}

usage() {
  cat <<EOF
사용법: harness.sh <명령> [옵션]

명령:
  run            ★ 권장: audit → enrich → validate → prioritize → sync (한 번에)
  audit          정적 분석만 → raw-audit.json
  enrich         raw → 규칙 기반 audit.json (--force 로 덮어쓰기)
  continue       validate → prioritize → sync (audit.json 이미 있을 때)
  validate       점수화 audit JSON 검증
  prioritize     audit 항목 우선순위 정렬
  sync           open 이슈 스킵 / 해결 항목 제거 (registry)
  issue          상위 항목 GitHub 이슈 생성
  check-approval 이슈에 tech-debt-approved 있는지 확인
  mechanical     audit + enrich 안내 (run 과 동일, 이름 호환)

환경 변수:
  AUDIT          점수화 audit JSON (기본: docs/tech-debt/<오늘>-audit.json)
  ITEM_ID        issue 시 부채 ID 지정
  ISSUE          check-approval 시 이슈 번호
  DRY_RUN        1 이면 issue dry-run
  FORCE_ENRICH   1 이면 enrich 시 기존 audit 덮어쓰기

예:
  cd ~/git/myrepo && ~/.cursor/skills/tech-debt-harness/harness.sh run
  DRY_RUN=1 ~/.cursor/skills/tech-debt-harness/harness.sh issue
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
    if [[ -z "${ISSUE:-}" ]]; then
      echo "ISSUE=<번호> 필요" >&2
      exit 1
    fi
    python3 "$SCRIPTS/check-approval.py" --workspace "$WORKSPACE" --issue "$ISSUE"
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
