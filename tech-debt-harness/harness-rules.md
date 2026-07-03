# 기술 부채 하네스 규칙

## 안전 한도 (자동 수정 가능 여부)

| 가드 | 한도 |
|------|------|
| `estimated_files` | 자동 수정 시 ≤ 10 |
| `effort` 점수 | 자동 수정 시 ≤ 3 |
| `architecture_debt` | 대규모 리팩터는 사용자 명시 승인 전 이슈만 |
| API breaking | 별도 승인 없이 하네스 PR에서 금지 |

`prioritize.py` 가 위 규칙으로 `auto_fix_eligible` 을 설정한다. `false` 이면 PR 금지.

## 분할 규칙

부채 항목이 너무 클 때:

1. `sub_items[]` 에 각각 title, description, `estimated_files`, effort ≤ 3
2. **부모** 이슈로 전체를 설명하거나 **첫 sub_item만** 이슈로 등록
3. 첫 PR은 **가장 작은 sub_item** 중 우선순위 높은 것부터

분할 트리거 (하나라도 해당):

- `effort >= 4`
- `estimated_files > 10`
- 예상 변경 400 LOC 초과

## Fingerprint 중복 제거

`fingerprint = sha256(category|title|sorted_paths)[:16]`

이슈 본문에 포함:

```html
<!-- tech-debt-fingerprint: abc123 -->
```

`sync-registry.py` 가 open 이슈와 매칭. **중복 스킵**, 해결된 항목은 audit 에서 **제거**.

## 라벨 워크플로

```text
이슈 생성  → tech-debt, tech-debt-pending, tech-debt/<분류>
승인자     → tech-debt-approved 추가, tech-debt-pending 제거 (수동)
에이전트   → 선택: tech-debt-in-progress
PR 머지    → 이슈 닫힘 → registry status resolved
```

## 단순화 체크리스트 (simplify 스킬 대체)

변경 파일 전체에 적용:

- [ ] 한 번만 쓰는 추상화 추가 없음
- [ ] 중복 로직 도입 없음
- [ ] 이름이 주변 코드베이스와 일치
- [ ] 에러 처리가 프로젝트 관례에 맞음 (과하지 않음)
- [ ] stated fix 대비 diff 최소

PR에 기록: "Simplify 게이트: 통과 (스킬)" 또는 "Simplify 게이트: 통과 (체크리스트)".

## 테스트 요구사항

- 레포가 쓰는 **CI와 동일한 명령** 실행 (`.github/workflows`, `package.json`, `pyproject.toml` 참고)
- 테스트 실패 시 하네스 PR **차단**
- 테스트 skip/disable 로 green 만들기 금지

## 레포 안전

- `git remote get-url origin` 이 기대한 워크스페이스에서만 `gh issue create`
- dry-run 표에 origin URL 표시

## 이슈 처리 스크립트

승인(`tech-debt-approved`) 후:

```bash
ISSUE=<N> ./harness.sh fix-start    # 브랜치 + 검증 루프(통과까지)
./harness.sh fix-commit
ISSUE=<N> ./harness.sh fix-pr
```

- `fix-start`: base 브랜치 pull → `tech-debt/<N>-<slug>` 생성 → `tech-debt-in-progress`
- **검증**: 기본 `TEST_SCOPE=affected` — 이슈의 영향 경로만 (`vitest run <spec.ts>` 등). 전체는 `TEST_SCOPE=full`
- **루프**: 실패 시 수정 후 Enter로 재검증 (`FIX_UNTIL_PASS=1` 기본, `q` 중단)
- 코드 수정 자체는 스크립트 밖 (에이전트 또는 직접 편집)
- 상태: `docs/tech-debt/.active-fix.json`
