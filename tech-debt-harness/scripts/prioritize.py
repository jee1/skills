#!/usr/bin/env python3
"""Mechanically score and rank tech-debt items; pick top-1 for issue creation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _lib import MAX_AUTO_FIX_EFFORT, MAX_AUTO_FIX_FILES, compute_priority, load_json, save_json


def enrich_and_rank(audit: dict) -> dict:
    items = audit.get("items") or []
    for item in items:
        impact = int(item.get("impact", 0))
        risk = int(item.get("risk", 0))
        effort = int(item.get("effort", 0))
        if impact < 1 or risk < 1 or effort < 1:
            raise ValueError(f"{item.get('id')}: impact/risk/effort must be 1-5")
        item["priority"] = compute_priority(impact, risk, effort)
        est_files = int(item.get("estimated_files", 1))
        effort_val = int(item.get("effort", 5))
        item["auto_fix_eligible"] = (
            est_files <= MAX_AUTO_FIX_FILES and effort_val <= MAX_AUTO_FIX_EFFORT and not item.get("sub_items")
        )
    ranked = sorted(items, key=lambda x: (-int(x["priority"]), x.get("id", "")))
    audit["items"] = ranked
    audit["top_item_id"] = ranked[0]["id"] if ranked else None
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank tech-debt audit items by priority formula")
    parser.add_argument("--audit", type=Path, required=True, help="Scored audit JSON path")
    parser.add_argument("--output", type=Path, help="Optional output path (default: overwrite --audit)")
    parser.add_argument("--print-top", action="store_true", help="Print top item id and priority")
    args = parser.parse_args()

    audit_path = args.audit.resolve()
    if not audit_path.exists():
        print(f"audit not found: {audit_path}", file=sys.stderr)
        return 1

    audit = load_json(audit_path)
    try:
        audit = enrich_and_rank(audit)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    out = args.output or audit_path
    save_json(out, audit)

    if args.print_top and audit.get("top_item_id"):
        top = audit["items"][0]
        print(f"{top['id']}\tpriority={top['priority']}\tauto_fix={top.get('auto_fix_eligible')}")
    elif args.print_top:
        print("no items", file=sys.stderr)
        return 1

    print(f"Ranked {len(audit.get('items', []))} item(s) → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
