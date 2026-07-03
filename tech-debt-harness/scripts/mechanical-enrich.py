#!/usr/bin/env python3
"""raw-audit.json → 규칙 기반 점수화 audit.json (에이전트 enrichment 대체/보조)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _lib import compute_priority, load_json, next_debt_id, save_json, today_str

SKIP_PATH_PARTS = frozenset({".next", "node_modules", "vendor-chunks", ".git", "dist", "build", ".venv", "venv"})
SKIP_PATH_PATTERNS = (
    re.compile(r"docs/_work/"),
    re.compile(r"debt-markers", re.I),
)


def _skip_reason(paths: list[str]) -> str | None:
    for rel in paths:
        parts = Path(rel).parts
        if any(part in SKIP_PATH_PARTS for part in parts):
            return "빌드·벤더 산출물 경로"
        for pat in SKIP_PATH_PATTERNS:
            if pat.search(rel):
                return "리뷰/부채 마커 문서(의도적 TODO)"
    return None


def _is_test_path(path: str) -> bool:
    low = path.lower()
    return any(x in low for x in ("__tests__", "/tests/", ".spec.", ".test.", "_test."))


def _score_finding(finding: dict) -> tuple[int, int, int, str]:
    """Return impact, risk, effort, business_justification."""
    source = str(finding.get("source", ""))
    category = str(finding.get("category", "code_debt"))
    paths = finding.get("affected_paths") or []

    if category == "dependency_debt" or source in {"pip-audit", "npm-audit"}:
        return 4, 5, 2, "알려진 취약점·구버전 의존성은 보안·운영 리스크로 직결됩니다."
    if category == "test_debt" or source == "test-layout":
        return 4, 4, 3, "테스트 공백은 회귀가 프로덕션까지 전파될 수 있습니다."
    if category == "documentation_debt" or source == "readme-scan":
        return 2, 2, 1, "온보딩·운영 문서 부재는 팀 생산성을 떨어뜨립니다."
    if source == "ruff":
        return 3, 2, 2, "린트 위반 누적은 리뷰 비용과 버그 가능성을 높입니다."
    if source == "todo-scan":
        if paths and all(p.endswith(".md") for p in paths):
            return 2, 2, 2, "문서 내 미완료 마커는 계획 추적을 어렵게 합니다."
        if paths and _is_test_path(paths[0]):
            return 3, 3, 2, "테스트의 TODO는 미완성 검증·GREEN 단계 지연을 의미합니다."
        return 4, 3, 3, "소스의 TODO/FIXME 누적은 기능·리팩터링 미완료 신호입니다."
    return 3, 3, 3, "정적 감사에서 식별된 기술 부채입니다."


def _suggested_fix(finding: dict) -> str:
    source = str(finding.get("source", ""))
    if source in {"pip-audit", "npm-audit"}:
        return "의존성을 권장 버전으로 올리고 전체 테스트·감사를 재실행합니다."
    if source == "ruff":
        return "`ruff check --fix` 적용 후 남은 항목을 수동 수정합니다."
    if source == "todo-scan":
        return "TODO를 이슈/작업으로 전환하거나 코드에서 제거·구현 완료합니다."
    if source == "test-layout":
        return "핵심 모듈에 단위·통합 테스트 골격을 추가합니다."
    return finding.get("description", "원인을 좁힌 뒤 최소 범위로 수정합니다.")


def mechanical_enrich(raw: dict) -> dict:
    workspace = str(raw.get("workspace", ""))
    findings = raw.get("findings") or []
    items: list[dict] = []
    skipped: list[str] = []

    for finding in findings:
        paths = list(finding.get("affected_paths") or [])
        reason = _skip_reason(paths)
        if reason:
            title = str(finding.get("title", ""))[:60]
            skipped.append(f"{title} ({reason})")
            continue

        impact, risk, effort, justification = _score_finding(finding)
        est_files = max(1, len(paths)) if paths else 1
        item_id = next_debt_id([i["id"] for i in items])
        priority = compute_priority(impact, risk, effort)
        items.append(
            {
                "id": item_id,
                "fingerprint": finding.get("fingerprint", ""),
                "category": finding.get("category", "code_debt"),
                "title": str(finding.get("title", "")).replace("에 TODO/FIXME 과다", " — TODO/FIXME 정리 필요"),
                "description": finding.get("description", ""),
                "evidence": list(finding.get("evidence") or [])[:5],
                "impact": impact,
                "risk": risk,
                "effort": effort,
                "priority": priority,
                "business_justification": justification,
                "suggested_fix": _suggested_fix(finding),
                "affected_paths": paths,
                "estimated_files": est_files,
                "splittable": effort >= 4 or est_files > 10,
                "sub_items": [],
                "auto_fix_eligible": est_files <= 10 and effort <= 3,
                "enrichment": "mechanical",
            }
        )

    ranked = sorted(items, key=lambda x: (-x["priority"], x["id"]))
    top_id = ranked[0]["id"] if ranked else None
    generated = raw.get("generated_at") or today_str()
    source_raw = raw.get("source_raw")
    if not source_raw and workspace:
        source_raw = f"docs/tech-debt/{generated}-raw-audit.json"

    return {
        "generated_at": generated,
        "workspace": workspace,
        "source_raw": source_raw,
        "enrichment_mode": "mechanical",
        "skipped_findings": skipped,
        "items": ranked,
        "top_item_id": top_id,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="raw audit → 규칙 기반 점수화 audit.json")
    parser.add_argument("--raw", type=Path, required=True, help="raw-audit.json 경로")
    parser.add_argument("--output", type=Path, help="출력 audit.json (기본: 같은 날짜 audit.json)")
    parser.add_argument("--force", action="store_true", help="기존 audit.json 덮어쓰기")
    args = parser.parse_args()

    raw_path = args.raw.resolve()
    if not raw_path.exists():
        print(f"raw audit 없음: {raw_path}", file=sys.stderr)
        return 1

    raw = load_json(raw_path)
    out_path = args.output
    if not out_path:
        stem = raw_path.name.replace("-raw-audit.json", "-audit.json")
        out_path = raw_path.parent / stem
    out_path = out_path.resolve()

    if out_path.exists() and not args.force:
        print(f"이미 존재: {out_path} (덮어쓰려면 --force)", file=sys.stderr)
        return 1

    audit = mechanical_enrich(raw)
    if not audit["items"]:
        print("등록 가능한 항목 없음 (전부 필터됨). 에이전트 enrichment 또는 raw 감사 범위 조정 필요.", file=sys.stderr)
        if audit.get("skipped_findings"):
            for line in audit["skipped_findings"][:10]:
                print(f"  스킵: {line}", file=sys.stderr)
        return 1

    save_json(out_path, audit)
    print(f"규칙 기반 enrichment {len(audit['items'])}건 → {out_path}")
    if audit.get("skipped_findings"):
        print(f"스킵 {len(audit['skipped_findings'])}건 (빌드 산출물·의도적 마커 등)")
    if audit.get("top_item_id"):
        top = audit["items"][0]
        print(f"상위: {top['id']} priority={top['priority']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
