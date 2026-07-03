#!/usr/bin/env python3
"""승인된 기술부채 이슈 처리 시작: 라벨 갱신 + 작업 브랜치 생성."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from _lib import (
    APPROVED_LABEL,
    IN_PROGRESS_LABEL,
    PENDING_LABEL,
    active_fix_path,
    find_audit_item,
    gh_issue_view,
    git_default_branch,
    git_remote_origin,
    parse_issue_body_meta,
    run_cmd,
    save_json,
    slugify_branch,
    today_str,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="승인된 tech-debt 이슈 처리 시작 (브랜치·상태 파일)")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    issue_num = args.issue

    origin = git_remote_origin(workspace)
    if not origin:
        print("git remote origin 없음", file=sys.stderr)
        return 1

    issue = gh_issue_view(workspace, issue_num)
    if not issue:
        return 1

    labels = {lbl["name"] for lbl in issue.get("labels") or []}
    if APPROVED_LABEL not in labels:
        print(f"이슈 #{issue_num}에 {APPROVED_LABEL} 라벨이 없습니다. 승인 후 다시 실행하세요.", file=sys.stderr)
        return 2

    body = issue.get("body") or ""
    meta = parse_issue_body_meta(body)
    audit_path, audit_item = find_audit_item(workspace, meta.get("fingerprint"), meta.get("td_id"))
    if meta.get("audit_path"):
        candidate = workspace / meta["audit_path"]
        if candidate.is_file():
            audit_path = candidate

    title = issue.get("title", f"issue-{issue_num}")
    slug_source = ""
    if audit_item and audit_item.get("affected_paths"):
        slug_source = Path(str(audit_item["affected_paths"][0])).stem
    else:
        slug_source = title
    branch = f"tech-debt/{issue_num}-{slugify_branch(slug_source)}"
    base = git_default_branch(workspace)

    state = {
        "issue": issue_num,
        "issue_url": issue.get("url"),
        "title": title,
        "branch": branch,
        "base_branch": base,
        "td_id": meta.get("td_id") or (audit_item or {}).get("id"),
        "fingerprint": meta.get("fingerprint") or (audit_item or {}).get("fingerprint"),
        "audit_path": str(audit_path.relative_to(workspace)) if audit_path and audit_path.is_relative_to(workspace) else None,
        "auto_fix_eligible": bool((audit_item or {}).get("auto_fix_eligible")),
        "affected_paths": list((audit_item or {}).get("affected_paths") or []),
        "started_at": today_str(),
        "origin": origin,
    }

    if args.dry_run:
        print(json.dumps({"dry_run": True, **state}, ensure_ascii=False, indent=2))
        return 0

    code, out, err = run_cmd(["git", "status", "--porcelain"], workspace)
    if code != 0:
        print(err or out, file=sys.stderr)
        return 1
    if out.strip() and os.environ.get("ALLOW_DIRTY") != "1":
        print("작업 트리에 미커밋 변경이 있습니다. 커밋/스태시 후 재시도하거나 ALLOW_DIRTY=1", file=sys.stderr)
        return 1

    code, _, err = run_cmd(["git", "fetch", "origin", base], workspace, timeout=180)
    if code != 0:
        print(f"git fetch 실패: {err}", file=sys.stderr)
        return 1

    code, _, err = run_cmd(["git", "checkout", base], workspace)
    if code != 0:
        print(f"git checkout {base} 실패: {err}", file=sys.stderr)
        return 1

    code, _, err = run_cmd(["git", "pull", "--ff-only", "origin", base], workspace, timeout=180)
    if code != 0:
        print(f"git pull 실패: {err}", file=sys.stderr)
        return 1

    code, _, err = run_cmd(["git", "checkout", "-b", branch], workspace)
    if code != 0:
        code2, _, _ = run_cmd(["git", "checkout", branch], workspace)
        if code2 != 0:
            print(f"브랜치 생성/체크아웃 실패: {err}", file=sys.stderr)
            return 1

    label_cmd = [
        "gh",
        "issue",
        "edit",
        str(issue_num),
        "--add-label",
        IN_PROGRESS_LABEL,
    ]
    if PENDING_LABEL in labels:
        label_cmd.extend(["--remove-label", PENDING_LABEL])
    code, out, err = run_cmd(label_cmd, workspace)
    if code != 0:
        print(f"라벨 갱신 실패: {err or out}", file=sys.stderr)
        return 1

    save_json(active_fix_path(workspace), state)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    print(
        f"\n✓ 브랜치 {branch} — fix-start 가 검증 루프를 이어갑니다 (SKIP_VERIFY=1 이면 생략)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
