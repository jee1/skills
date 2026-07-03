#!/usr/bin/env python3
"""이슈 등록 전 점수화 tech-debt audit JSON 검증."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import CATEGORIES, MAX_AUTO_FIX_EFFORT, MAX_AUTO_FIX_FILES, compute_priority, load_json


def validate_audit(data: dict) -> list[str]:
    errors: list[str] = []
    if not data.get("generated_at"):
        errors.append("generated_at 없음")
    items = data.get("items")
    if not items:
        errors.append("items 배열이 비어 있음")
        return errors

    ids: set[str] = set()
    for item in items:
        iid = item.get("id")
        if not iid:
            errors.append("id 없는 항목")
            continue
        if iid in ids:
            errors.append(f"중복 id: {iid}")
        ids.add(iid)

        cat = item.get("category")
        if cat not in CATEGORIES:
            errors.append(f"{iid}: 잘못된 category {cat}")

        for field in ("title", "description", "suggested_fix", "fingerprint"):
            if not item.get(field):
                errors.append(f"{iid}: {field} 없음")

        for score, label in (("impact", "영향"), ("risk", "위험"), ("effort", "공수")):
            val = item.get(score)
            if not isinstance(val, int) or not 1 <= val <= 5:
                errors.append(f"{iid}: {label}({score})는 1–5 정수")

        if all(isinstance(item.get(s), int) for s in ("impact", "risk", "effort")):
            expected = compute_priority(item["impact"], item["risk"], item["effort"])
            if item.get("priority") != expected:
                errors.append(f"{iid}: 우선순위 불일치 (입력 {item.get('priority')}, 기대 {expected})")

        est = int(item.get("estimated_files", 1))
        if est > MAX_AUTO_FIX_FILES and item.get("auto_fix_eligible"):
            errors.append(f"{iid}: estimated_files > {MAX_AUTO_FIX_FILES} 인데 auto_fix_eligible true")

        effort = int(item.get("effort", 5))
        if effort > MAX_AUTO_FIX_EFFORT and item.get("auto_fix_eligible"):
            errors.append(f"{iid}: effort > {MAX_AUTO_FIX_EFFORT} 인데 auto_fix_eligible true")

        if effort >= 4 and not item.get("sub_items") and est > 5:
            errors.append(f"{iid}: 공수/파일 수가 큰데 sub_items 없음 — 등록 전 분할 필요")

    if data.get("top_item_id") and data["top_item_id"] not in ids:
        errors.append("top_item_id가 items에 없음")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="tech-debt audit JSON 검증")
    parser.add_argument("audit", type=Path)
    args = parser.parse_args()
    path = args.audit.resolve()
    if not path.exists():
        print(f"파일 없음: {path}", file=sys.stderr)
        return 1
    data = load_json(path)
    errors = validate_audit(data)
    if errors:
        for err in errors:
            print(f"[오류] {err}", file=sys.stderr)
        return 1
    print(f"OK: 항목 {len(data.get('items', []))}건")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
