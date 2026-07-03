#!/usr/bin/env python3
"""Mechanical validator for per-AC Issue Spec documents."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER_KEYS = frozenset(
    {
        "title",
        "feature",
        "ac_id",
        "priority",
        "tdd_source",
        "tasks_source",
        "generated_at",
        "spec_ready",
    }
)

AC_ID = re.compile(r"\bAC-\d+\b", re.I)
TEST_ID = re.compile(r"\bT-\d+\b", re.I)
TASK_ID = re.compile(r"\bTK-\d{3}\b", re.I)
TK_LINE = re.compile(r"^\s*-\s*\[\s*[ xX]\s*\]\s*TK-\d{3}\b", re.M)
GWT = re.compile(r"\bGiven\b.+\bWhen\b.+\bThen\b", re.I | re.S)
NONE_OPEN = re.compile(r"^\s*[-*]?\s*\(?none\)?\s*$|^\s*[-*]?\s*없음\s*$", re.I | re.M)

SECTION_ALIASES: dict[str, list[str]] = {
    "acceptance": [r"^##\s+Acceptance\s*$", r"^##\s+인수\s*조건\s*$"],
    "done_when": [r"^##\s+Done\s+when\s*$", r"^##\s+완료\s*판정\s*$"],
    "tests": [r"^##\s+Tests\s*$", r"^##\s+테스트\s*$"],
    "behavior": [r"^##\s+Behavior", r"^##\s+동작"],
    "interfaces": [r"^##\s+Interfaces", r"^##\s+인터페이스"],
    "impl_tasks": [r"^##\s+Implementation\s+tasks", r"^##\s+구현\s+태스크"],
    "out_of_scope": [r"^##\s+Out\s+of\s+scope", r"^##\s+범위\s*외"],
    "open_questions": [r"^##\s+Open\s+questions", r"^##\s+열린\s+질문"],
    "traceability": [r"^##\s+Traceability", r"^##\s+추적"],
}


class ValidationError:
    def __init__(self, line: int, code: str, message: str) -> None:
        self.line = line
        self.code = code
        self.message = message

    def __str__(self) -> str:
        loc = f"line {self.line}" if self.line > 0 else "document"
        return f"{loc}: [{self.code}] {self.message}"


def _load_validate_tasks():
    vt_path = Path(__file__).resolve().parent.parent.parent / "tdd-to-tasks" / "scripts" / "validate-tasks.py"
    spec = importlib.util.spec_from_file_location("validate_tasks", vt_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load validate-tasks.py from {vt_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"').strip("'")

    missing = REQUIRED_FRONTMATTER_KEYS - set(meta.keys())
    for key in sorted(missing):
        errors.append(ValidationError(1, "frontmatter-key", f"Missing frontmatter key: {key}"))

    priority = meta.get("priority", "")
    if priority not in ("Must", "Should", "infra"):
        errors.append(
            ValidationError(1, "frontmatter-priority", f"priority must be Must, Should, or infra, got: {priority!r}")
        )

    spec_ready = meta.get("spec_ready", "").lower()
    if spec_ready not in ("true", "false"):
        errors.append(ValidationError(1, "frontmatter-spec-ready", "spec_ready must be true or false"))

    ac_id = meta.get("ac_id", "")
    if priority != "infra" and not AC_ID.fullmatch(ac_id):
        errors.append(ValidationError(1, "frontmatter-ac-id", f"ac_id must be AC-n (e.g. AC-1), got: {ac_id!r}"))

    return meta, body, errors


def _line_number(text: str, index: int) -> int:
    return text[:index].count("\n") + 1


def _find_section(body: str, aliases: list[str]) -> tuple[int, str]:
    for pattern in aliases:
        match = re.search(pattern, body, re.M | re.I)
        if match:
            start = match.end()
            next_header = re.search(r"^##\s+", body[start:], re.M)
            end = start + next_header.start() if next_header else len(body)
            line_num = body[: match.start()].count("\n") + 1
            return line_num, body[start:end].strip()
    return 0, ""


def check_sections(body: str, is_infra: bool) -> list[ValidationError]:
    errors: list[ValidationError] = []
    required = ["done_when", "impl_tasks", "out_of_scope", "open_questions", "traceability"]
    if not is_infra:
        required = ["acceptance", "tests", "behavior", "interfaces", *required]
    else:
        required = ["done_when", "impl_tasks", "out_of_scope", "open_questions", "traceability"]

    for key in required:
        line_num, content = _find_section(body, SECTION_ALIASES[key])
        if not line_num:
            errors.append(ValidationError(0, "section-missing", f"Missing required section: {key}"))
            continue
        if len(content) < 8:
            errors.append(ValidationError(line_num, "section-empty", f"Section too short: {key}"))
    return errors


def check_acceptance(body: str, is_infra: bool) -> list[ValidationError]:
    if is_infra:
        return []
    errors: list[ValidationError] = []
    line_num, section = _find_section(body, SECTION_ALIASES["acceptance"])
    if not section:
        return errors
    if not GWT.search(section):
        errors.append(
            ValidationError(
                line_num,
                "acceptance-not-verifiable",
                "Acceptance should include Given … When … Then … (from TDD 인수조건)",
            )
        )
    return errors


def check_impl_tasks(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    line_num, section = _find_section(body, SECTION_ALIASES["impl_tasks"])
    if not section:
        return errors
    tk_lines = [ln for ln in section.splitlines() if TK_LINE.match(ln)]
    if len(tk_lines) < 1:
        errors.append(ValidationError(line_num, "impl-tasks-empty", "Need ≥1 `- [ ] TK-nnn` under Implementation tasks"))
    return errors


def check_tests_table(body: str, is_infra: bool) -> list[ValidationError]:
    if is_infra:
        return []
    errors: list[ValidationError] = []
    line_num, section = _find_section(body, SECTION_ALIASES["tests"])
    if not section:
        return errors
    rows = 0
    for line in section.splitlines():
        if line.strip().startswith("|") and TEST_ID.search(line) and not re.match(r"^\|\s*[-:]+\s*\|", line):
            if not re.match(r"^\|\s*Test\s+ID\s*\|", line, re.I):
                rows += 1
    if rows < 1:
        errors.append(ValidationError(line_num, "tests-empty", "Tests table needs ≥1 Test ID row"))
    return errors


def check_interfaces(body: str, is_infra: bool) -> list[ValidationError]:
    if is_infra:
        return []
    errors: list[ValidationError] = []
    line_num, section = _find_section(body, SECTION_ALIASES["interfaces"])
    if not section:
        return errors
    if not re.search(r"`[^`\n]+`", section):
        errors.append(ValidationError(line_num, "interfaces-no-path", "Interfaces section needs ≥1 path in backticks"))
    return errors


def check_open_questions(body: str, spec_ready: bool) -> list[ValidationError]:
    errors: list[ValidationError] = []
    line_num, section = _find_section(body, SECTION_ALIASES["open_questions"])
    if not section:
        return errors
    bullets = [ln.strip() for ln in section.splitlines() if ln.strip().startswith("-")]
    if not bullets:
        errors.append(ValidationError(line_num, "open-questions-empty", "Open questions needs at least one bullet"))
        return errors
    if spec_ready:
        for bullet in bullets:
            if NONE_OPEN.match(bullet):
                continue
            errors.append(
                ValidationError(
                    line_num,
                    "open-questions-blocking",
                    "spec_ready:true requires Open questions to be (none) / 없음 only",
                )
            )
            break
    return errors


def check_traceability(meta: dict[str, str], body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for key in ("tdd_source", "tasks_source"):
        path = meta.get(key, "")
        if path and path not in body and path not in meta.get("title", ""):
            errors.append(ValidationError(0, "traceability-path", f"Body or Traceability should cite {key}: {path}"))
    return errors


def _tasks_for_ac(tasks_body: str, ac_id: str) -> set[str]:
    """TK IDs listed under the Phase section for this AC (not Setup/Foundation tags)."""
    ac_upper = ac_id.upper().replace("ac-", "AC-")
    phase_pattern = re.compile(
        rf"^##\s+Phase\s+\d+:\s*{re.escape(ac_upper)}\s*[—–\-]",
        re.M | re.I,
    )
    match = phase_pattern.search(tasks_body)
    if not match:
        return set()
    start = match.end()
    next_phase = re.search(r"^##\s+Phase\s+", tasks_body[start:], re.M)
    block = tasks_body[start : start + next_phase.start()] if next_phase else tasks_body[start:]
    found: set[str] = set()
    for line in block.splitlines():
        if TK_LINE.match(line):
            for tk in TASK_ID.findall(line):
                found.add(tk.upper())
    return found


def cross_check(
    meta: dict[str, str],
    spec_body: str,
    tdd_text: str | None,
    tasks_text: str | None,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    is_infra = meta.get("priority") == "infra"
    ac_id = meta.get("ac_id", "")
    if is_infra or not tdd_text:
        return errors

    vt = _load_validate_tasks()
    _, tdd_body, _ = vt.parse_frontmatter(tdd_text)
    ac_table = vt._parse_ac_table(tdd_body)
    test_ci = vt._parse_test_table(tdd_body)

    ac_upper = ac_id.upper().replace("ac-", "AC-")
    if ac_upper not in ac_table:
        errors.append(ValidationError(0, "ac-unknown", f"ac_id {ac_upper} not found in TDD acceptance criteria"))
        return errors

    _, acc_sec = _find_section(spec_body, SECTION_ALIASES["acceptance"])
    _, tests_sec = _find_section(spec_body, SECTION_ALIASES["tests"])
    spec_tests = {t.upper().replace("t-", "T-") for t in TEST_ID.findall(tests_sec)}

    tdd_tests_for_ac: set[str] = set()
    design_ch = vt._design_chapter_slice(tdd_body)
    _, test_sec = vt._subsection_content(design_ch, r"###\s+(?:테스트|Tests)")
    for line in test_sec.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if ac_upper in cells[1].upper().replace("ac-", "AC-"):
            tm = TEST_ID.search(cells[0])
            if tm:
                tdd_tests_for_ac.add(tm.group(0).upper().replace("t-", "T-"))

    if tdd_tests_for_ac and not spec_tests:
        errors.append(
            ValidationError(0, "tests-missing-from-tdd", f"TDD lists tests for {ac_upper}: {sorted(tdd_tests_for_ac)}")
        )
    missing_tests = tdd_tests_for_ac - spec_tests
    if missing_tests:
        errors.append(
            ValidationError(
                0,
                "tests-incomplete",
                f"Tests table missing TDD test IDs for {ac_upper}: {', '.join(sorted(missing_tests))}",
            )
        )

    if tasks_text:
        _, tasks_body, _ = vt.parse_frontmatter(tasks_text)
        expected_tk = _tasks_for_ac(tasks_body, ac_upper)
        _, impl_sec = _find_section(spec_body, SECTION_ALIASES["impl_tasks"])
        spec_tk = {t.upper() for t in TASK_ID.findall(impl_sec)}
        if expected_tk and not spec_tk:
            errors.append(ValidationError(0, "tk-missing", f"Implementation tasks should list TK for {ac_upper}"))
        orphan = spec_tk - expected_tk
        if orphan and expected_tk:
            errors.append(
                ValidationError(
                    0,
                    "tk-orphan",
                    f"Spec lists TK not tied to {ac_upper} in tasks.md: {', '.join(sorted(orphan))}",
                )
            )
        missing_tk = expected_tk - spec_tk
        if missing_tk:
            errors.append(
                ValidationError(
                    0,
                    "tk-incomplete",
                    f"Spec missing TK from tasks.md for {ac_upper}: {', '.join(sorted(missing_tk))}",
                )
            )

    return errors


def validate(
    text: str,
    tdd_text: str | None = None,
    tasks_text: str | None = None,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    meta, body, fm_errors = parse_frontmatter(text)
    errors.extend(fm_errors)
    is_infra = meta.get("priority") == "infra"
    spec_ready = meta.get("spec_ready", "").lower() == "true"

    errors.extend(check_sections(body, is_infra))
    errors.extend(check_acceptance(body, is_infra))
    errors.extend(check_impl_tasks(body))
    errors.extend(check_tests_table(body, is_infra))
    errors.extend(check_interfaces(body, is_infra))
    errors.extend(check_open_questions(body, spec_ready))
    errors.extend(check_traceability(meta, body))
    errors.extend(cross_check(meta, body, tdd_text, tasks_text))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Issue Spec markdown")
    parser.add_argument("spec_file", type=Path, help="Path to issue spec file")
    parser.add_argument("--tdd", type=Path, help="Source TDD for cross-check")
    parser.add_argument("--tasks", type=Path, help="Source tasks.md for cross-check")
    args = parser.parse_args()

    spec_path = args.spec_file
    if not spec_path.is_file():
        print(f"File not found: {spec_path}", file=sys.stderr)
        return 1

    text = spec_path.read_text(encoding="utf-8")
    tdd_text = args.tdd.read_text(encoding="utf-8") if args.tdd and args.tdd.is_file() else None
    tasks_text = args.tasks.read_text(encoding="utf-8") if args.tasks and args.tasks.is_file() else None

    if args.tdd and not args.tdd.is_file():
        print(f"TDD file not found: {args.tdd}", file=sys.stderr)
        return 1
    if args.tasks and not args.tasks.is_file():
        print(f"Tasks file not found: {args.tasks}", file=sys.stderr)
        return 1

    errors = validate(text, tdd_text, tasks_text)
    if not errors:
        print("OK")
        return 0

    for err in errors:
        print(err, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
