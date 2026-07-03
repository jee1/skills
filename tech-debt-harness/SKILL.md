---
name: tech-debt-harness
description: >-
  정적 도구 + tech-debt 스킬로 기술 부채를 찾고, 기계적으로 우선순위를 매긴 뒤
  GitHub 이슈(라벨 승인)를 등록하고 수정·PR까지 진행한다.
  tech-debt-harness/harness.sh 로 기계 단계 실행.
  "기술 부채 하네스", "tech debt harness", "기술부채 이슈", "tech-debt audit" 등에 사용.
---

# 기술 부채 하네스 (Tech-Debt Harness)

**현재 워크스페이스**에서 **감사 → 우선순위 → 이슈 → (승인) → 수정 → PR** 을 오케스트레이션한다.

**기계 단계:** `tech-debt-harness/harness.sh` (또는 이 패키지의 scripts).  
**판단 단계:** 에이전트가 `tech-debt` 스킬 + 코드베이스 분석.

**전제:** `gh` 인증 완료; `git remote origin` 이 의도한 레포와 일치.

## 빠른 시작 (터미널)

대상 레포 루트에서 **한 줄**로 기계 파이프라인 실행:

```bash
~/.cursor/skills/tech-debt-harness/harness.sh run
```

`audit` → 규칙 기반 `enrich` → `validate` → `prioritize` → `sync` 까지 자동.  
각 명령 끝에 **복사용 다음 단계**가 출력된다.

| 명령 | 설명 |
|------|------|
| `run` | 감사 파이프라인 전체 |
| `issue` | GitHub 이슈 등록 (`DRY_RUN=1` 미리보기) |
| `fix-start` | 승인 확인 + 작업 브랜치 (`ISSUE=` 필수) |
| `fix-verify` / `fix-commit` / `fix-pr` | 테스트 → 커밋 → PR |

**이슈 처리 (승인 후):**

```bash
ISSUE=638 ~/.cursor/skills/tech-debt-harness/harness.sh fix-start
~/.cursor/skills/tech-debt-harness/harness.sh fix-verify
~/.cursor/skills/tech-debt-harness/harness.sh fix-commit
ISSUE=638 ~/.cursor/skills/tech-debt-harness/harness.sh fix-pr
```

**에이전트 enrichment (선택):** 더 정밀한 점수·분할이 필요하면 Cursor 채팅에서 raw audit 점수화 요청 후 `harness.sh continue`.

## 참고 문서

| 파일 | 용도 |
|------|------|
| [harness-rules.md](harness-rules.md) | 안전 한도, 분할 규칙, 라벨, simplify 게이트 |
| [issue-body-template.md](issue-body-template.md) | 승인자용 이슈 본문 섹션 |
| [audit-schema.md](audit-schema.md) | 점수화된 audit JSON 형식 |

## 라벨

| 라벨 | 의미 |
|------|------|
| `tech-debt` | 하네스로 등록한 모든 이슈 |
| `tech-debt-pending` | 승인 대기 (`tech-debt-approved` 미부여) |
| `tech-debt-approved` | **승인 게이트** — 에이전트가 수정·PR 가능 |
| `tech-debt-in-progress` | 수정 진행 중 (선택) |

## 체크리스트

```
기술 부채 하네스:
- [ ] Phase 1: harness.sh audit (정적 도구 → raw-audit.json)
- [ ] Phase 2: 에이전트 enrichment → scored audit.json (impact/risk/effort, 필요 시 분할)
- [ ] Phase 3: validate-audit.py + prioritize.py + sync-registry.py
- [ ] Phase 4: 이슈 dry-run → 상위 항목 표 제시
- [ ] Phase 5: create-issue.py → tech-debt-pending 라벨
- [ ] STOP — 이슈에 tech-debt-approved 될 때까지 대기
- [ ] Phase 6: 라벨 확인; 브랜치 tech-debt/<이슈>-<slug>
- [ ] Phase 7: 수정 구현 (분할 시 sub_item 하나만)
- [ ] Phase 8: 테스트 실행 (반드시 통과)
- [ ] Phase 9: simplify 스킬 / harness-rules 단순화 게이트
- [ ] Phase 10: gh pr create (Fixes #N)
```

---

## Phase 1 — 정적 감사 (스크립트)

**대상 워크스페이스 루트**에서:

```bash
/path/to/tech-debt-harness/harness.sh audit
# 또는
python3 /path/to/tech-debt-harness/scripts/run-audit.py --workspace .
```

산출물: `docs/tech-debt/YYYY-MM-DD-raw-audit.json`

도구 (가능한 범위): ruff, pip-audit/pip outdated, npm audit, TODO 밀도, README/테스트 레이아웃.

---

## Phase 2 — 에이전트 enrichment (tech-debt 스킬)

`~/.claude/skills/tech-debt/SKILL.md` (또는 동등) 의 분류·공식:

`우선순위 = (영향 + 위험) × (6 - 공수)`

1. raw findings + Serena/코드 리뷰를 **점수화된** `docs/tech-debt/YYYY-MM-DD-audit.json` 으로 병합
2. `TD-001` … id, fingerprint 부여 (raw에 있으면 유지)
3. 항목별 impact/risk/effort 1–5 (한글 title/description 권장)
4. **분할 규칙:** `effort >= 4` 또는 `estimated_files > 10` 이면:
   - `sub_items[]` 로 작은 단위 추가, 또는
   - 우선순위 낮추고 보류 (자동 수정 안 함)
5. 승인자가 읽을 `business_justification` 을 한글로 작성

[audit-schema.md](audit-schema.md) 참고.

---

## Phase 3 — 기계 파이프라인

```bash
export AUDIT=docs/tech-debt/YYYY-MM-DD-audit.json
python3 .../validate-audit.py "$AUDIT"
python3 .../prioritize.py --audit "$AUDIT" --print-top
python3 .../sync-registry.py --workspace . --audit "$AUDIT"
```

`sync-registry.py` 는 open `tech-debt` 이슈와 fingerprint 가 겹치면 **스킵**, 해결된 항목은 audit 목록에서 **제거**.

sync 후 항목이 줄었으면 prioritize 재실행.

---

## Phase 4 — Dry-run (필수)

이슈 생성 전 표 제시:

| ID | 우선순위 | 분류 | 제목 | 자동수정? | 이슈 |
|----|----------|------|------|-----------|------|
| TD-001 | 40 | code_debt | … | 예 | (신규) |

상위 항목이 `auto_fix_eligible` 이 아니면 **이슈만 등록** — 같은 실행에서 PR 약속 금지.

---

## Phase 5 — 이슈 등록

```bash
DRY_RUN=1 /path/to/tech-debt-harness/harness.sh issue
# 사용자 확인 후 →
/path/to/tech-debt-harness/harness.sh issue
```

**STOP.** 이슈에 `tech-debt-approved` 가 없으면 수정 코드 작성 금지.

이슈 제목·본문은 **한글** (`[기술부채] …`).

---

## Phase 6 — 승인 확인 + 이슈 처리

```bash
ISSUE=<N> ./harness.sh check-approval
ISSUE=<N> ./harness.sh fix-start
./harness.sh fix-verify
./harness.sh fix-commit
ISSUE=<N> ./harness.sh fix-pr
```

상태 파일: `docs/tech-debt/.active-fix.json`

---

## Phase 7–8 — 수정 + 테스트

- 브랜치: `tech-debt/<이슈번호>-<짧은-slug>`
- 범위: **한 건** (분할 시 `sub_item` 하나)
- 프로젝트 테스트 명령을 green 될 때까지 실행 (`pytest`, `npm test` 등)
- 범위 확대 없이 테스트 통과 불가 시 **이슈에 코멘트만** — PR 없음

---

## Phase 9 — Simplify 게이트

1. `simplify` 스킬 탐색: `~/.cursor/skills/simplify/SKILL.md`, `~/.codex/`, `~/.claude/`
2. 있으면 → 변경 파일에 적용
3. 없으면 → [harness-rules.md](harness-rules.md) § 단순화 체크리스트

---

## Phase 10 — Pull request

```bash
gh pr create --title "fix(기술부채): <제목>" --body "$(cat <<'EOF'
## 기술 부채
Fixes #<이슈>

## 요약
...

## 검증
- [ ] 테스트 통과
- [ ] Simplify 게이트 통과

## 감사(audit)
- `docs/tech-debt/YYYY-MM-DD-audit.json` — TD-00N
EOF
)"
```

PR을 이슈에 링크. 머지로 이슈가 닫히면 다음 sync 에서 registry 에서 제외.

---

## 오류 처리

| 상황 | 조치 |
|------|------|
| sync 후 항목 없음 | "신규 부채 없음" 보고 후 종료 |
| 상위 항목 auto_fix 불가 | 이슈만; PR 없음 |
| 테스트 실패 | PR 없음; 이슈 코멘트 |
| 잘못된 레포 | `origin` 이상 시 중단 |
| gh 없음 | Phase 5 에서 중단 |

---

## 연동

- **tech-debt** (Anthropic) — Phase 2 점수 프레임워크
- **tasks-to-issues** — 유사한 dry-run·라벨 패턴; 아티팩트 체인은 다름
- **split-to-prs** — 수정 중 범위가 커질 때
