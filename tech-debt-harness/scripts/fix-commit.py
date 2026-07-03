#!/usr/bin/env python3
"""기술부채 수정 내용 커밋."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import active_fix_path, load_json, run_cmd, save_json


def main() -> int:
    parser = argparse.ArgumentParser(description="tech-debt 수정 커밋")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--message", help="커밋 메시지 (기본: fix(기술부채): ...)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    state_path = active_fix_path(workspace)
    state = load_json(state_path) if state_path.is_file() else {}
    issue = state.get("issue")
    title = state.get("title", "기술부채 수정")
    short = title.replace("[기술부채]", "").strip()[:72]
    message = args.message or f"fix(기술부채): {short}" + (f" (#{issue})" if issue else "")

    code, out, err = run_cmd(["git", "status", "--porcelain"], workspace)
    if code != 0:
        print(err or out, file=sys.stderr)
        return 1
    if not out.strip():
        print("커밋할 변경 없음", file=sys.stderr)
        return 1

    paths = state.get("affected_paths") or []
    add_cmd = ["git", "add", *paths] if paths else ["git", "add", "-A"]

    if args.dry_run:
        print(f"dry-run: {' '.join(add_cmd)} && git commit -m {message!r}")
        return 0

    code, _, err = run_cmd(add_cmd, workspace)
    if code != 0:
        print(f"git add 실패: {err}", file=sys.stderr)
        return 1

    code, out, err = run_cmd(["git", "commit", "-m", message], workspace)
    if code != 0:
        print(err or out, file=sys.stderr)
        return 1
    print(out.strip())
    if state_path.is_file():
        state["committed"] = True
        state["commit_message"] = message
        save_json(state_path, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
