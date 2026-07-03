#!/usr/bin/env bash
# 기술 부채 하네스 — 기계 단계 (audit → prioritize → sync → issue)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$SCRIPT_DIR/scripts"
WORKSPACE="$(pwd)"
DATE="$(date +%Y-%m-%d)"
OUT_DIR="$WORKSPACE/docs/tech-debt"
RAW="$OUT_DIR/${DATE}-raw-audit.json"
AUDIT="$OUT_DIR/${DATE}-audit.json"
REGISTRY="$OUT_DIR/registry.json"

usage() {
  cat <<'EOF'
사용법: harness.sh <명령> [옵션]

명령:
  audit          정적 분석 실행 → raw-audit.json
  validate       점수화 audit JSON 검증 (AUDIT 경로 필요)
  prioritize     audit 항목 우선순위 정렬
  sync           open 이슈 스킵 / 해결 항목 제거 (registry)
  issue          상위 항목 GitHub 이슈 생성 (--dry-run 지원)
  check-approval 이슈에 tech-debt-approved 있는지 확인 (ISSUE=<번호>)
  mechanical     audit → (에이전트 점수화) → validate → prioritize → sync

환경 변수:
  AUDIT          점수화 audit JSON 경로 (기본: docs/tech-debt/<오늘>-audit.json)
  ITEM_ID        issue 명령 시 부채 ID 지정
  ISSUE          check-approval 시 이슈 번호
  DRY_RUN        1 이면 issue dry-run

`mechanical` 이후 에이전트 워크플로:
  1. raw audit → 점수화 audit ($AUDIT) 작성 (SKILL.md Phase 2)
  2. ./harness.sh validate && ./harness.sh prioritize && ./harness.sh sync
  3. ./harness.sh issue  (tech-debt-approved 전까지 STOP)
EOF
}

cmd="${1:-}"
shift || true

AUDIT="${AUDIT:-$OUT_DIR/${DATE}-audit.json}"

case "$cmd" in
  audit)
    python3 "$SCRIPTS/run-audit.py" --workspace "$WORKSPACE" --output "$RAW"
    echo "다음: 에이전트가 $AUDIT 로 enrichment (SKILL.md Phase 2)"
    ;;
  validate)
    python3 "$SCRIPTS/validate-audit.py" "${AUDIT}"
    ;;
  prioritize)
    python3 "$SCRIPTS/prioritize.py" --audit "${AUDIT}" --print-top
    ;;
  sync)
    python3 "$SCRIPTS/sync-registry.py" --workspace "$WORKSPACE" --audit "${AUDIT}" --registry "$REGISTRY"
    ;;
  issue)
    extra=()
    [[ "${DRY_RUN:-0}" == "1" ]] && extra+=(--dry-run)
    [[ -n "${ITEM_ID:-}" ]] && extra+=(--item-id "$ITEM_ID")
    python3 "$SCRIPTS/create-issue.py" --workspace "$WORKSPACE" --audit "${AUDIT}" "${extra[@]}"
    ;;
  check-approval)
    if [[ -z "${ISSUE:-}" ]]; then
      echo "ISSUE=<번호> 필요" >&2
      exit 1
    fi
    python3 "$SCRIPTS/check-approval.py" --workspace "$WORKSPACE" --issue "$ISSUE"
    ;;
  mechanical)
    python3 "$SCRIPTS/run-audit.py" --workspace "$WORKSPACE" --output "$RAW"
    echo "STOP: 에이전트가 $AUDIT 에 점수화 audit 작성 후 실행:"
    echo "  AUDIT=$AUDIT $0 validate && AUDIT=$AUDIT $0 prioritize && AUDIT=$AUDIT $0 sync"
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
