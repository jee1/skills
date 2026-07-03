# 이슈 본문 템플릿 (경량)

`create-issue.py` 가 생성하는 GitHub 이슈 본문. 승인자는 전체 audit 없이 **무엇이**, **왜 지금**, **어떻게 검증**하는지 이해할 수 있어야 한다.

```markdown
<!-- tech-debt-fingerprint: {fingerprint} -->
<!-- tech-debt-id: {id} -->

## 요약

{1–3문장: 무엇이 문제인지}

## 왜 지금인가

- **분류:** `{category}` ({분류 한글명})
- **우선순위 점수:** {priority} = (영향 {impact} + 위험 {risk}) × (6 - 공수 {effort})
- **비즈니스 근거:** {팀에 왜 중요한지}

## 제안 수정안

{에이전트가 할 구체적 단계 — 파일, 접근, 테스트 계획}

## 근거

- {정적 도구 출력 또는 path:line}

## 영향 경로

- `{path}`

## 하위 항목 (분할 시)

- **{sub-title}** — {sub-description}

## 승인

자동 수정·PR 진행 시 라벨 `tech-debt-approved` 추가.
승인 후 `tech-debt-pending` 제거.

## 완료 조건

- [ ] CI에서 테스트 통과
- [ ] `simplify` 검토 완료
- [ ] PR에 `Fixes #이슈번호` 연결

## 추적

- 감사(audit): `docs/tech-debt/YYYY-MM-DD-audit.json`
```
