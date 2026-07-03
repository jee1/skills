#!/usr/bin/env python3
"""Sync audit items with registry; skip open issues; drop resolved debts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from _lib import TECH_DEBT_LABEL, load_json, run_cmd, save_json, today_str


def _gh_issues(workspace: Path) -> list[dict[str, Any]]:
    code, out, err = run_cmd(
        [
            "gh",
            "issue",
            "list",
            "--label",
            TECH_DEBT_LABEL,
            "--state",
            "all",
            "--json",
            "number,title,state,labels,body",
            "--limit",
            "200",
        ],
        workspace,
    )
    if code != 0:
        print(f"gh issue list failed: {err or out}", file=sys.stderr)
        return []
    try:
        return json.loads(out or "[]")
    except json.JSONDecodeError:
        return []


def _fingerprint_from_body(body: str) -> str | None:
    m = re.search(r"<!--\s*tech-debt-fingerprint:\s*([a-f0-9]+)\s*-->", body or "", re.I)
    return m.group(1).lower() if m else None


def _load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "updated_at": today_str(), "items": {}}
    return load_json(path)


def sync(workspace: Path, audit_path: Path, registry_path: Path) -> dict[str, Any]:
    audit = load_json(audit_path)
    registry = _load_registry(registry_path)
    items_map: dict[str, Any] = registry.get("items") or {}

    open_fps: set[str] = set()
    for issue in _gh_issues(workspace):
        if issue.get("state") != "OPEN":
            fp = _fingerprint_from_body(issue.get("body") or "")
            if fp:
                items_map.setdefault(fp, {})["status"] = "resolved"
                items_map[fp]["resolved_issue"] = issue.get("number")
            continue
        fp = _fingerprint_from_body(issue.get("body") or "")
        if fp:
            open_fps.add(fp)
            items_map.setdefault(fp, {})["issue_number"] = issue.get("number")
            items_map[fp]["status"] = "open"

    filtered: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for item in audit.get("items") or []:
        fp = str(item.get("fingerprint", ""))
        reg = items_map.get(fp, {})
        if fp in open_fps or reg.get("status") == "open":
            skipped.append({"id": item.get("id"), "fingerprint": fp, "reason": "open issue exists"})
            continue
        if reg.get("status") == "resolved":
            continue
        filtered.append(item)

    audit["items"] = filtered
    audit["skipped_duplicates"] = skipped
    audit["synced_at"] = today_str()

    for item in filtered:
        fp = str(item.get("fingerprint", ""))
        items_map[fp] = {
            "id": item.get("id"),
            "title": item.get("title"),
            "status": "candidate",
            "last_seen": today_str(),
        }

    registry["items"] = items_map
    registry["updated_at"] = today_str()
    save_json(registry_path, registry)
    save_json(audit_path, audit)
    return {"kept": len(filtered), "skipped": len(skipped), "registry": str(registry_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dedupe audit against open tech-debt issues")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument(
        "--registry",
        type=Path,
        help="Registry JSON (default: <workspace>/docs/tech-debt/registry.json)",
    )
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    audit_path = args.audit.resolve()
    registry_path = args.registry or workspace / "docs" / "tech-debt" / "registry.json"

    if not audit_path.exists():
        print(f"audit not found: {audit_path}", file=sys.stderr)
        return 1

    result = sync(workspace, audit_path, registry_path)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
