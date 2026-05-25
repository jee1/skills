import importlib.util
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "validate_tdd", Path(__file__).with_name("validate-tdd.py")
)
assert _SPEC and _SPEC.loader
v = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(v)


FRONTMATTER = """---
title: "TDD: test"
feature: test
mode: brownfield
prd_source: "x"
generated_at: 2026-05-25
validation_passed: false
review_rounds: 0
---

# Test — Technical Design Document
"""

MINIMAL_READABLE_BODY = """
## 1. 서문
### TL;DR
One. Two. Three.
### Goals / Non-Goals
**Goals:** a b c
**Non-Goals:** x y
### 이 문서 읽는 법
| PM | x | 2 |
| Dev | y | 5 |
| Audit | z | 3 |
### 목차
1. a
## 2. 배경과 문제
요약: scope
## 3. 현재 시스템
요약: as-is xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
## 4. 갭과 설계 전환
### 결정 요약
| # | 주제 | 선택 | 상태 | 상세 |
|---|------|------|------|------|
| 1 | t | c | 확정 | x |
> **결정:** adopt X.
> **근거:** https://example.com/docs
> **코드:** `src/a.ts:1`
## 5. 상위설계
### 아키텍처 개요
요약: layers xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```mermaid
flowchart LR
  A --> B
```
#### 한눈에
- a
- b
- c
### 구성요소 및 책임
요약: comps xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- **Foo** (기존): does foo
- **Bar** (신규): does bar
#### 한눈에
- a
- b
- c
### 데이터 흐름
요약: flow xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
1. step
2. step
3. step
#### 한눈에
- a
- b
- c
## 6. 상세설계
### 스펙 인덱스
| Endpoint / Interface | Entity | Error codes |
|----------------------|--------|-------------|
| POST /x | orders | 404 |
### API 및 인터페이스
요약: api xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
| Field | Type | Required | Note |
| a | b | yes | c |
| d | e | yes | f |
| g | h | yes | i |
| Code | HTTP | When | Client action | Retry? |
| E1 | 404 | miss | fix | no |
| E2 | 409 | dup | show | no |
| E3 | 502 | pg | retry | yes |
See [ref:A-1].
### 데이터 모델
요약: model xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
| Field | Type | Nullable | Constraint | Notes |
| id | uuid | no | PK | |
| status | enum | no | | |
| at | ts | yes | | |
### 핵심 처리 흐름
요약: proc xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
**Happy path:** Foo then Bar
**Errors:**
- timeout 502 retry
- inventory fail 500 rollback
## 7. 마무리
### 롤아웃·일정
phase 1
### 리스크
| R | I | M |
| a | b | c |
### 열린 질문
- none
## 부록 A. 출처·코드 위치
| ID | 주장 | PRD | Code | External URL |
|----|------|-----|------|--------------|
| A-1 | claim | prd | `src/a.ts:1` | |
## 부록 B. Ch.4 결정 전문
> **결정:** adopt X.
> **근거:** https://example.com/docs
> **코드:** `src/a.ts:1`
"""


class TestStrictSourcePolicy(unittest.TestCase):
    def test_ch5_subsection_without_sasil_block_passes_strict(self):
        doc = FRONTMATTER + MINIMAL_READABLE_BODY
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=True)
            codes = [e.code for e in errors]
            self.assertNotIn("subsection-source-missing", codes)
            self.assertNotIn("source-block-missing", codes, [str(e) for e in errors if e.code == "source-block-missing"])
        finally:
            path.unlink()


class TestReadabilityProfile(unittest.TestCase):
    def test_readability_checks_pass(self):
        doc = FRONTMATTER + MINIMAL_READABLE_BODY
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(doc)
            path = Path(f.name)
        try:
            errors = v.validate(path, strict=True, readability=True)
            self.assertEqual(errors, [], [str(e) for e in errors])
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
