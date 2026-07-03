#!/usr/bin/env python3
"""기술부채 수정 PR 생성."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _lib import active_fix_path, gh_issue_view, load_json, run_cmd, save_json, today_str


def render_pr_body(state: dict, audit_path: str | None) -> str:
    issue = state.get("issue")
    td_id = state.get("td_id") or "—"
    title = state.get("title", "").replace("[기술부채]", "").strip()
    audit_line = f"- `{audit_path}` — {td_id}" if audit_path else f"- 이슈 #{issue}"
    return f"""## 기술 부채

Fixes #{issue}

## 요약

{title}

## 검증

- [x] `harness.sh fix-verify` 테스트 통과
- [ ] Simplify 게이트 (스킬 또는 harness-rules 체크리스트)

## 감사(audit)

{audit_line}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="tech-debt 수정 PR 생성")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--issue", type=int, help="이슈 번호 (기본: .active-fix.json)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    state_path = active_fix_path(workspace)
    state = load_json(state_path) if state_path.is_file() else {}

    issue_num = args.issue or state.get("issue")
    if not issue_num:
        print("ISSUE 번호 또는 .active-fix.json 필요", file=sys.stderr)
        return 1

    if not state:
        issue = gh_issue_view(workspace, int(issue_num))
        if not issue:
            return 1
        state = {"issue": issue_num, "title": issue.get("title"), "branch": None}

    branch = state.get("branch")
    code, cur, _ = run_cmd(["git", "branch", "--show-current"], workspace)
    if branch and code == 0 and cur.strip() != branch:
        print(f"현재 브랜치가 {cur.strip()} 입니다. {branch} 에서 실행하세요.", file=sys.stderr)
        return 1

    code, out, _ = run_cmd(["git", "status", "--porcelain"], workspace)
    if out.strip():
        print("미커밋 변경이 있습니다. fix-commit 후 PR 생성하세요.", file=sys.stderr)
        return 1

    code, ahead, _ = run_cmd(["git", "rev-list", "--count", f"{state.get('base_branch', 'main')}..HEAD"], workspace)
    if code == 0 and ahead.strip() == "0":
        print("base 대비 커밋이 없습니다. fix-commit 후 PR 생성하세요.", file=sys.stderr)
        return 1

    title_short = state.get("title", f"이슈 {issue_num}").replace("[기술부채]", "").strip()[:80]
    pr_title = f"fix(기술부채): {title_short}"
    body = render_pr_body(state, state.get("audit_path"))

    if args.dry_run:
        print(json.dumps({"title": pr_title, "body": body}, ensure_ascii=False, indent=2))
        return 0

    if branch:
        code, _, err = run_cmd(["git", "push", "-u", "origin", branch], workspace, timeout=180)
        if code != 0:
            print(f"git push 실패: {err}", file=sys.stderr)
            return 1

    code, out, err = run_cmd(
        ["gh", "pr", "create", "--title", pr_title, "--body", body],
        workspace,
        timeout=120,
    )
    if code != 0:
        print(err or out, file=sys.stderr)
        return 1

    url = (out or "").strip()
    print(url)
    m = re.search(r"/pull/(\d+)", url)
    state["pr_url"] = url
    state["pr_number"] = int(m.group(1)) if m else None
    state["pr_created_at"] = today_str()
    save_json(state_path, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
