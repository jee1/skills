#!/usr/bin/env python3
"""Mechanical validator for tdd-to-tasks output documents."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER_KEYS = frozenset(
    {"title", "feature", "mode", "tdd_source", "prd_source", "generated_at", "validation_passed"}
)

TASK_ID = re.compile(r"\bTK-\d{3}\b", re.I)
AC_ID = re.compile(r"\bAC-\d+\b", re.I)
TEST_ID = re.compile(r"\bT-\d+\b", re.I)
PROVES_TEST = re.compile(r"proves\s+(T-\d+)", re.I)
TASK_LINE_START = re.compile(r"^\s*-\s*\[\s*[ xX]\s*\]\s*TK-\d{3}\b", re.M)
FILE_PATH = re.compile(r"`[^`\n]+`")
RTM_HEADER = re.compile(r"^##\s+추적\s+매트릭스", re.M | re.I)
DEPS_HEADER = re.compile(r"^##\s+Dependencies\s*$", re.M | re.I)
PHASE_HEADER = re.compile(r"^##\s+Phase\s+", re.M | re.I)
BLOCKED_BY = re.compile(r"^(TK-\d{3})\s+blockedBy\s+(TK-\d{3})\b", re.M | re.I)
MUST_PRIORITY = re.compile(r"\bMust\b", re.I)
CI_GATE_YES = re.compile(r"\byes\b", re.I)


class ValidationError:
    def __init__(self, line: int, code: str, message: str) -> None:
        self.line = line
        self.code = code
        self.message = message

    def __str__(self) -> str:
        loc = f"line {self.line}" if self.line > 0 else "document"
        return f"{loc}: [{self.code}] {self.message}"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, list[ValidationError]]:
    errors: list[ValidationError] = []
    if not text.startswith("---"):
        errors.append(ValidationError(1, "frontmatter-missing", "Document must start with YAML frontmatter (---)"))
        return {}, text, errors

    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(ValidationError(1, "frontmatter-unclosed", "Frontmatter opening --- not closed"))
        return {}, text, errors

    block = match.group(1)
    body = text[match.end() :]
    meta: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"').strip("'")

    missing = REQUIRED_FRONTMATTER_KEYS - set(meta.keys())
    for key in sorted(missing):
        errors.append(ValidationError(1, "frontmatter-key", f"Missing frontmatter key: {key}"))

    mode = meta.get("mode", "")
    if mode not in ("brownfield", "greenfield"):
        errors.append(
            ValidationError(1, "frontmatter-mode", f"mode must be brownfield or greenfield, got: {mode!r}")
        )

    return meta, body, errors


def _line_number(text: str, index: int) -> int:
    return text[:index].count("\n") + 1


def _parse_ac_table(tdd_body: str) -> dict[str, str]:
    """Return AC ID -> priority string from Ch.6 인수조건 table."""
    ch6 = _chapter_slice(tdd_body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    _, ac_sec = _subsection_content(ch6, r"###\s+인수\s*조건")
    ac_priority: dict[str, str] = {}
    for line in ac_sec.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|\s*AC\s+ID\s*\|", line, re.I):
            continue
        if re.match(r"^\|\s*[-:]+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        ac_match = AC_ID.search(cells[0])
        if not ac_match:
            continue
        ac_id = ac_match.group(0).upper().replace("ac-", "AC-")
        priority = cells[3] if len(cells) > 3 else ""
        ac_priority[ac_id] = priority
    return ac_priority


def _parse_test_table(tdd_body: str) -> dict[str, bool]:
    """Return Test ID -> CI gate is yes."""
    ch6 = _chapter_slice(tdd_body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    _, test_sec = _subsection_content(ch6, r"###\s+테스트")
    ci_by_test: dict[str, bool] = {}
    for line in test_sec.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|\s*Test\s+ID\s*\|", line, re.I):
            continue
        if re.match(r"^\|\s*[-:]+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        test_match = TEST_ID.search(cells[0])
        if not test_match:
            continue
        test_id = test_match.group(0).upper().replace("t-", "T-")
        gate = cells[-1] if cells else ""
        ci_by_test[test_id] = bool(CI_GATE_YES.search(gate))
    return ci_by_test


def _chapter_slice(body: str, start_pattern: str, end_pattern: str | None) -> str:
    start = re.search(start_pattern, body, flags=re.M)
    if not start:
        return ""
    begin = start.start()
    if end_pattern:
        end = re.search(end_pattern, body[begin + 1 :], flags=re.M)
        if end:
            return body[begin : begin + 1 + end.start()]
    return body[begin:]


def _subsection_content(chapter: str, header_pattern: str) -> tuple[int, str]:
    match = re.search(header_pattern, chapter, re.M)
    if not match:
        return 0, ""
    line_num = chapter[: match.start()].count("\n") + 1
    start = match.end()
    next_header = re.search(r"^###\s+|^##\s+", chapter[start:], re.M)
    end = start + next_header.start() if next_header else len(chapter)
    return line_num, chapter[start:end].strip()


def check_structure(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not RTM_HEADER.search(body):
        errors.append(ValidationError(0, "rtm-missing", "Missing required section: ## 추적 매트릭스 (RTM)"))
    if not DEPS_HEADER.search(body):
        errors.append(ValidationError(0, "deps-missing", "Missing required section: ## Dependencies"))
    if not PHASE_HEADER.search(body):
        errors.append(ValidationError(0, "phase-missing", "Missing required section: ## Phase …"))
    task_count = sum(1 for line in body.splitlines() if TASK_LINE_START.match(line))
    if task_count < 2:
        errors.append(
            ValidationError(0, "tasks-thin", "Need ≥2 checklist tasks (- [ ] TK-nnn) under Phase sections")
        )
    return errors


def check_task_lines(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for line_num, line in enumerate(body.splitlines(), start=1):
        if not TASK_LINE_START.match(line):
            continue
        if not AC_ID.search(line):
            errors.append(
                ValidationError(
                    line_num,
                    "task-no-ac",
                    "Implementation task must include [AC-n] reference",
                )
            )
        lower = line.lower()
        if "test" not in lower and "migration" not in lower and "setup" not in lower:
            if not FILE_PATH.search(line):
                errors.append(
                    ValidationError(
                        line_num,
                        "no-file-path",
                        "Implement/wire task needs a file path in backticks",
                    )
                )
    return errors


def check_rtm(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    rtm_match = RTM_HEADER.search(body)
    if not rtm_match:
        return errors
    start = rtm_match.end()
    next_sec = re.search(r"^##\s+", body[start:], re.M)
    rtm_block = body[start : start + next_sec.start()] if next_sec else body[start:]
    data_rows = 0
    for line in rtm_block.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|\s*PRD\s*\|", line, re.I):
            continue
        if re.match(r"^\|\s*[-:]+\s*\|", line):
            continue
        if AC_ID.search(line):
            data_rows += 1
    if data_rows < 1:
        errors.append(ValidationError(_line_number(body, rtm_match.start()), "rtm-empty", "RTM table needs ≥1 AC row"))
    return errors


def check_dependencies(body: str, task_ids: set[str]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for match in BLOCKED_BY.finditer(body):
        left, right = match.group(1).upper(), match.group(2).upper()
        line_num = _line_number(body, match.start())
        if left not in task_ids:
            errors.append(ValidationError(line_num, "deps-unknown-task", f"blockedBy references unknown {left}"))
        if right not in task_ids:
            errors.append(ValidationError(line_num, "deps-unknown-blocker", f"blockedBy references unknown {right}"))
    return errors


def cross_check_tdd(tasks_body: str, tdd_text: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    _, tdd_body, _ = parse_frontmatter(tdd_text)
    ac_table = _parse_ac_table(tdd_body)
    test_ci = _parse_test_table(tdd_body)
    tdd_ac_ids = set(ac_table.keys())
    if not tdd_ac_ids:
        errors.append(ValidationError(0, "tdd-no-ac", "TDD Ch.6 ### 인수조건 has no parseable AC IDs"))
        return errors

    must_ac = {ac for ac, pri in ac_table.items() if MUST_PRIORITY.search(pri)}
    if not must_ac:
        must_ac = tdd_ac_ids

    task_ac_refs: set[str] = set()
    for line in tasks_body.splitlines():
        if not TASK_LINE_START.match(line):
            continue
        for ac in AC_ID.findall(line):
            task_ac_refs.add(ac.upper().replace("ac-", "AC-"))

    orphan_ac = task_ac_refs - tdd_ac_ids
    if orphan_ac:
        errors.append(
            ValidationError(
                0,
                "task-ac-orphan",
                f"Tasks reference unknown AC IDs: {', '.join(sorted(orphan_ac))}",
            )
        )

    untasked = must_ac - task_ac_refs
    if untasked:
        errors.append(
            ValidationError(
                0,
                "ac-untasked",
                f"Must AC needs ≥1 task with [AC-n]; missing: {', '.join(sorted(untasked))}",
            )
        )

    ci_tests = {tid for tid, yes in test_ci.items() if yes}
    proved_tests: set[str] = set()
    for line in tasks_body.splitlines():
        if not TASK_LINE_START.match(line):
            continue
        for match in PROVES_TEST.finditer(line):
            proved_tests.add(match.group(1).upper().replace("t-", "T-"))

    untested = ci_tests - proved_tests
    if untested:
        errors.append(
            ValidationError(
                0,
                "test-untasked",
                f"CI-gated tests need a task with 'proves T-n'; missing: {', '.join(sorted(untested))}",
            )
        )

    orphan_tests = proved_tests - set(test_ci.keys())
    if orphan_tests and test_ci:
        errors.append(
            ValidationError(
                0,
                "task-test-orphan",
                f"Tasks prove unknown Test IDs: {', '.join(sorted(orphan_tests))}",
            )
        )

    return errors


def validate(text: str, tdd_text: str | None = None) -> list[ValidationError]:
    errors: list[ValidationError] = []
    meta, body, fm_errors = parse_frontmatter(text)
    errors.extend(fm_errors)
    errors.extend(check_structure(body))
    errors.extend(check_rtm(body))
    errors.extend(check_task_lines(body))

    task_ids = {t.upper() for t in TASK_ID.findall(body)}
    errors.extend(check_dependencies(body, task_ids))

    if tdd_text:
        errors.extend(cross_check_tdd(body, tdd_text))

    tdd_src = meta.get("tdd_source", "")
    if tdd_src and tdd_src not in text:
        errors.append(
            ValidationError(0, "tdd-source-unlinked", f"Body should cite tdd_source path: {tdd_src}")
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate tdd-to-tasks output")
    parser.add_argument("tasks_file", type=Path, help="Path to tasks markdown file")
    parser.add_argument("--tdd", type=Path, help="Source TDD for cross-check")
    args = parser.parse_args()

    tasks_path = args.tasks_file
    if not tasks_path.is_file():
        print(f"File not found: {tasks_path}", file=sys.stderr)
        return 1

    text = tasks_path.read_text(encoding="utf-8")
    tdd_text = None
    if args.tdd:
        if not args.tdd.is_file():
            print(f"TDD file not found: {args.tdd}", file=sys.stderr)
            return 1
        tdd_text = args.tdd.read_text(encoding="utf-8")

    errors = validate(text, tdd_text)
    if not errors:
        print("OK")
        return 0

    for err in errors:
        print(err, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
