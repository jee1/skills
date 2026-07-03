#!/usr/bin/env python3
"""기술부채 수정 검증 (테스트) — 영향 경로 스코프·통과할 때까지 재시도."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from _lib import active_fix_path, load_json, resolve_test_command, run_cmd, save_json


def run_verify_once(workspace: Path, test_cmd: list[str], timeout: int) -> tuple[int, str, str]:
    print(f"실행: {' '.join(test_cmd)}", file=sys.stderr)
    code, out, err = run_cmd(test_cmd, workspace, timeout=timeout)
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    return code, out, err


def main() -> int:
    parser = argparse.ArgumentParser(description="tech-debt 수정 검증 (테스트)")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--cmd", help="테스트 명령 (공백 구분)")
    parser.add_argument(
        "--scope",
        choices=("affected", "full"),
        default=os.environ.get("TEST_SCOPE", "affected"),
        help="affected=영향 경로만 (기본), full=레포 전체 테스트",
    )
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument(
        "--until-pass",
        action="store_true",
        default=os.environ.get("FIX_UNTIL_PASS", "0") == "1",
        help="통과할 때까지 재시도 (대화형). fix-start 에서 기본 켜짐",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=int(os.environ.get("MAX_VERIFY_ATTEMPTS", "0")),
        help="0=무제한(대화형), 양수면 N회 후 종료",
    )
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    state_path = active_fix_path(workspace)
    state = load_json(state_path) if state_path.is_file() else {}
    affected = list(state.get("affected_paths") or [])

    test_cmd = resolve_test_command(
        workspace,
        affected_paths=affected,
        scope=args.scope,
        explicit_cmd=args.cmd,
    )
    if not test_cmd:
        print("테스트 명령을 찾지 못했습니다. TEST_CMD=... 또는 --cmd 로 지정하세요.", file=sys.stderr)
        return 1

    if args.scope == "affected" and affected and test_cmd:
        print(f"스코프: 영향 경로 {len(affected)}개", file=sys.stderr)
    elif args.scope == "full":
        print("스코프: 레포 전체", file=sys.stderr)

    interactive = args.until_pass and sys.stdin.isatty()
    if args.until_pass and not sys.stdin.isatty():
        print("비대화형 환경 — until-pass 는 1회만 실행합니다.", file=sys.stderr)
        args.until_pass = False

    attempt = 0
    while True:
        attempt += 1
        if args.until_pass:
            print(f"\n═══ 검증 시도 {attempt} ═══", file=sys.stderr)

        code, _, _ = run_verify_once(workspace, test_cmd, args.timeout)

        if state_path.is_file():
            state = load_json(state_path)
            state["last_verify"] = {
                "cmd": test_cmd,
                "scope": args.scope,
                "exit_code": code,
                "attempt": attempt,
            }
            if code == 0:
                state["verify_passed"] = True
            save_json(state_path, state)

        if code == 0:
            print("✓ 테스트 통과", file=sys.stderr)
            return 0

        print(f"테스트 실패 (exit {code})", file=sys.stderr)

        if not args.until_pass:
            return code if code != 0 else 1

        if args.max_attempts and attempt >= args.max_attempts:
            print(f"최대 시도 {args.max_attempts}회 도달 — 중단", file=sys.stderr)
            return code

        try:
            answer = input("\n코드 수정 후 Enter → 재검증  |  q → 중단: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n중단", file=sys.stderr)
            return code
        if answer in {"q", "quit", "exit"}:
            return code


if __name__ == "__main__":
    raise SystemExit(main())
