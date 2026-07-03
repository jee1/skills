# 점수화 audit JSON 스키마

경로: `docs/tech-debt/YYYY-MM-DD-audit.json`

`title`, `description`, `business_justification`, `suggested_fix` 는 **한글** 권장.

```json
{
  "generated_at": "2026-07-03",
  "workspace": "/abs/path/to/repo",
  "source_raw": "docs/tech-debt/2026-07-03-raw-audit.json",
  "items": [
    {
      "id": "TD-001",
      "fingerprint": "a1b2c3d4e5f67890",
      "category": "dependency_debt",
      "title": "짧은 제목 (한글)",
      "description": "무엇이 문제인지",
      "evidence": ["pip-audit: ..."],
      "impact": 3,
      "risk": 4,
      "effort": 2,
      "priority": 28,
      "business_justification": "운영 의존성 보안 노출",
      "suggested_fix": "X를 Y로 올리고 pytest 실행",
      "affected_paths": ["requirements.txt"],
      "estimated_files": 2,
      "splittable": false,
      "sub_items": [],
      "auto_fix_eligible": true
    }
  ],
  "top_item_id": "TD-001"
}
```

## 분류 (category 키는 영문 유지)

| 키 | 한글 |
|----|------|
| `code_debt` | 코드 부채 |
| `architecture_debt` | 아키텍처 부채 |
| `test_debt` | 테스트 부채 |
| `dependency_debt` | 의존성 부채 |
| `documentation_debt` | 문서 부채 |
| `infrastructure_debt` | 인프라 부채 |

## 우선순위

`prioritize.py` 계산:

`priority = (impact + risk) * (6 - effort)`

validate 전에 에이전트가 `priority` 를 넣을 수 있음; validator 가 일치 여부 검사.

## 레지스트리

`docs/tech-debt/registry.json` — `sync-registry.py` 가 갱신:

```json
{
  "version": 1,
  "updated_at": "2026-07-03",
  "items": {
    "a1b2c3d4e5f67890": {
      "id": "TD-001",
      "title": "...",
      "status": "open",
      "issue_number": 42,
      "last_seen": "2026-07-03"
    }
  }
}
```

status: `candidate` | `open` | `resolved`
