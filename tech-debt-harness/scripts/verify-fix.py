#!/usr/bin/env python3
"""기술부채 수정 후 테스트 실행."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _lib import active_fix_path, detect_test_command, load_json, run_cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="tech-debt 수정 검증 (테스트)")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--cmd", help="테스트 명령 (공백 구분). 미지정 시 자동 탐지")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if args.cmd:
        test_cmd = args.cmd.split()
    else:
        test_cmd = detect_test_command(workspace)

    if not test_cmd:
        print("테스트 명령을 찾지 못했습니다. --cmd 로 지정하세요.", file=sys.stderr)
        return 1

    print(f"실행: {' '.join(test_cmd)}", file=sys.stderr)
    code, out, err = run_cmd(test_cmd, workspace, timeout=args.timeout)
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)

    state_path = active_fix_path(workspace)
    if state_path.is_file():
        state = load_json(state_path)
        state["last_verify"] = {"cmd": test_cmd, "exit_code": code}
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if code != 0:
        print(f"테스트 실패 (exit {code})", file=sys.stderr)
        return code
    print("✓ 테스트 통과", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
