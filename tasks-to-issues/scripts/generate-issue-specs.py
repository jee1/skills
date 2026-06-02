#!/usr/bin/env python3
"""Draft Issue Spec files from validated tasks.md + TDD."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

AC_ID = re.compile(r"\bAC-\d+\b", re.I)
TEST_ID = re.compile(r"\bT-\d+\b", re.I)
TASK_ID = re.compile(r"\bTK-\d{3}\b", re.I)
TASK_LINE = re.compile(r"^\s*-\s*\[\s*[ xX]\s*\]\s*(TK-\d{3}\b.*)$", re.M)
TK_LINE_START = re.compile(r"^\s*-\s*\[\s*[ xX]\s*\]\s*TK-\d{3}\b")
PHASE_AC = re.compile(r"^##\s+Phase\s+\d+:\s*(AC-\d+)\s*[—–-]\s*(.+)$", re.M | re.I)
MUST = re.compile(r"\bMust\b", re.I)


def _load_validate_tasks():
    vt_path = Path(__file__).resolve().parent.parent.parent / "tdd-to-tasks" / "scripts" / "validate-tasks.py"
    spec = importlib.util.spec_from_file_location("validate_tasks", vt_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _parse_ac_rows(tdd_body: str, vt) -> dict[str, dict[str, str]]:
    ch6 = vt._chapter_slice(tdd_body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    _, ac_sec = vt._subsection_content(ch6, r"###\s+인수\s*조건")
    rows: dict[str, dict[str, str]] = {}
    for line in ac_sec.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|\s*AC\s+ID\s*\|", line, re.I) or re.match(r"^\|\s*[-:]+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        m = AC_ID.search(cells[0])
        if not m:
            continue
        ac = m.group(0).upper().replace("ac-", "AC-")
        rows[ac] = {
            "prd": cells[1],
            "condition": cells[2],
            "priority": cells[3],
            "done": cells[4],
        }
    return rows


def _parse_tests_for_ac(tdd_body: str, vt, ac: str) -> list[dict[str, str]]:
    ch6 = vt._chapter_slice(tdd_body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    _, test_sec = vt._subsection_content(ch6, r"###\s+테스트")
    out: list[dict[str, str]] = []
    for line in test_sec.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|\s*Test\s+ID\s*\|", line, re.I) or re.match(r"^\|\s*[-:]+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        if ac not in cells[1].upper().replace("ac-", "AC-"):
            continue
        out.append(
            {
                "test_id": cells[0],
                "layer": cells[2],
                "scenario": cells[3],
                "fixture": cells[4],
                "ci_gate": cells[5],
            }
        )
    return out


def _phase_titles(tasks_body: str) -> dict[str, str]:
    titles: dict[str, str] = {}
    for m in PHASE_AC.finditer(tasks_body):
        ac = m.group(1).upper().replace("ac-", "AC-")
        titles[ac] = m.group(2).strip()
    return titles


def _tk_lines_for_ac(tasks_body: str, ac: str) -> list[str]:
    ac_u = ac.upper().replace("ac-", "AC-")
    phase_pattern = re.compile(
        rf"^##\s+Phase\s+\d+:\s*{re.escape(ac_u)}\s*[—–\-]",
        re.M | re.I,
    )
    match = phase_pattern.search(tasks_body)
    if not match:
        return []
    start = match.end()
    next_phase = re.search(r"^##\s+Phase\s+", tasks_body[start:], re.M)
    block = tasks_body[start : start + next_phase.start()] if next_phase else tasks_body[start:]
    lines: list[str] = []
    for m in TASK_LINE.finditer(block):
        lines.append(f"- [ ] {m.group(1).strip()}")
    return lines


def _deps_for_tks(tasks_body: str, tks: set[str]) -> list[str]:
    deps: list[str] = []
    for line in tasks_body.splitlines():
        m = re.match(r"^(TK-\d{3})\s+blockedBy\s+(TK-\d{3})\b", line.strip(), re.I)
        if m and m.group(1).upper() in tks:
            deps.append(line.strip())
    return deps


def _other_acs(all_acs: list[str], current: str) -> str:
    others = [a for a in all_acs if a != current]
    return ", ".join(others) if others else "(none)"


def _render_spec(
    *,
    feature: str,
    ac: str,
    short_title: str,
    row: dict[str, str],
    tests: list[dict[str, str]],
    tk_lines: list[str],
    deps: list[str],
    other_acs: str,
    tdd_source: str,
    tasks_source: str,
    generated_at: str,
) -> str:
    test_rows = "\n".join(
        f"| {t['test_id']} | {t['layer']} | {t['scenario']} | {t['fixture']} | {t['ci_gate']} |"
        for t in tests
    )
    if not test_rows:
        test_rows = "| T-? | — | _(fill from TDD)_ | — | — |"

    tk_block = "\n".join(tk_lines) if tk_lines else "- [ ] TK-??? [AC-n] _(from tasks.md)_"
    deps_block = "\n".join(deps) if deps else "(none)"
    done_lines = row["done"]
    if not done_lines.startswith("-"):
        done_lines = f"- {done_lines}"

    date_slug = generated_at
    plan_path = f"docs/superpowers/plans/{date_slug}-{feature}-{ac}-plan.md"

    return f"""---
title: "Issue Spec: {ac} — {short_title}"
feature: {feature}
ac_id: {ac}
priority: {row['priority']}
tdd_source: "{tdd_source}"
tasks_source: "{tasks_source}"
generated_at: {generated_at}
spec_ready: false
blocked_by: []
---

# Issue Spec: {ac} — {short_title}

## Acceptance

{row['condition']}

**PRD:** {row['prd']}

## Done when

{done_lines}

## Tests

| Test ID | Layer | Scenario | Fixture / Mock | CI gate |
|---------|-------|----------|----------------|---------|
{test_rows}

## Behavior (in scope)

- _(Summarize happy path + error branches for {ac} from TDD Ch.6 flow — edit before spec_ready)_

## Interfaces & code

- _(List components/paths from TDD Ch.5–6 and tasks.md backticks — edit before spec_ready)_

## Implementation tasks

{tk_block}

## Dependencies

```text
{deps_block}
```

## Out of scope

- {other_acs}
- Ch.7 items not required for this AC

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | {tdd_source} |
| Tasks | {tasks_source} |
| Plan | _(after writing-plans)_ `{plan_path}` |
| Tracker | _(after register)_ |
"""


def _render_foundation(
    *,
    feature: str,
    title: str,
    tk_lines: list[str],
    deps: list[str],
    ac_list: str,
    tdd_source: str,
    tasks_source: str,
    generated_at: str,
) -> str:
    tk_block = "\n".join(tk_lines) if tk_lines else "- [ ] TK-??? _(Setup/Foundation from tasks.md)_"
    deps_block = "\n".join(deps) if deps else "(none)"
    return f"""---
title: "Issue Spec: Foundation — {title}"
feature: {feature}
ac_id: none
priority: infra
tdd_source: "{tdd_source}"
tasks_source: "{tasks_source}"
generated_at: {generated_at}
spec_ready: false
blocked_by: []
---

# Issue Spec: Foundation — {title}

## Goal

Enable AC implementation phases (migrations, flags, fixtures).

## Done when

- All Setup + Foundation TK lines in tasks.md are complete
- AC phases unblocked per tasks.md Dependencies

## Implementation tasks

{tk_block}

## Dependencies

```text
{deps_block}
```

## Out of scope

- {ac_list} (per-AC issue specs)

## Open questions

- (none)

## Traceability

| Link | Path |
|------|------|
| TDD | {tdd_source} |
| Tasks | {tasks_source} |
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate draft Issue Spec files")
    parser.add_argument("tasks_file", type=Path)
    parser.add_argument("--tdd", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/issues"))
    parser.add_argument("--include-should", action="store_true", help="Also generate Should-priority AC specs")
    parser.add_argument("--foundation", action="store_true", help="Also generate foundation-spec.md")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.tasks_file.is_file():
        print(f"Tasks not found: {args.tasks_file}", file=sys.stderr)
        return 1
    if not args.tdd.is_file():
        print(f"TDD not found: {args.tdd}", file=sys.stderr)
        return 1

    vt = _load_validate_tasks()
    tasks_text = args.tasks_file.read_text(encoding="utf-8")
    tdd_text = args.tdd.read_text(encoding="utf-8")
    tasks_meta, tasks_body, _ = vt.parse_frontmatter(tasks_text)
    _, tdd_body, _ = vt.parse_frontmatter(tdd_text)

    feature = tasks_meta.get("feature") or "feature"
    tdd_source = tasks_meta.get("tdd_source", str(args.tdd))
    tasks_source = str(args.tasks_file)
    generated_at = tasks_meta.get("generated_at", "YYYY-MM-DD")

    ac_rows = _parse_ac_rows(tdd_body, vt)
    phase_titles = _phase_titles(tasks_body)
    all_ac_ids = sorted(ac_rows.keys(), key=lambda x: int(re.search(r"\d+", x).group()) if re.search(r"\d+", x) else 0)

    out_dir = args.output_dir
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    for ac, row in sorted(ac_rows.items()):
        if MUST.search(row["priority"]):
            pass
        elif args.include_should:
            pass
        else:
            continue

        short = phase_titles.get(ac, row["condition"][:60])
        tks = {t.upper() for t in TASK_ID.findall("\n".join(_tk_lines_for_ac(tasks_body, ac)))}
        content = _render_spec(
            feature=feature,
            ac=ac,
            short_title=short,
            row=row,
            tests=_parse_tests_for_ac(tdd_body, vt, ac),
            tk_lines=_tk_lines_for_ac(tasks_body, ac),
            deps=_deps_for_tks(tasks_body, tks),
            other_acs=_other_acs(all_ac_ids, ac),
            tdd_source=tdd_source,
            tasks_source=tasks_source,
            generated_at=generated_at,
        )
        path = out_dir / f"{generated_at}-{feature}-{ac}-spec.md"
        if args.dry_run:
            print(f"would write: {path}")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"wrote: {path}")
        written.append(path)

    if args.foundation:
        foundation_tks: list[str] = []
        phase_headers = list(re.finditer(r"^##\s+Phase\s+.+$", tasks_body, re.M))
        for idx, header in enumerate(phase_headers):
            title = header.group(0)
            if re.search(r"AC-\d+", title, re.I):
                continue
            start = header.end()
            end = phase_headers[idx + 1].start() if idx + 1 < len(phase_headers) else len(tasks_body)
            block = tasks_body[start:end]
            for m in TASK_LINE.finditer(block):
                foundation_tks.append(f"- [ ] {m.group(1).strip()}")
        f_tk_set = {t.upper() for t in TASK_ID.findall("\n".join(foundation_tks))}
        f_content = _render_foundation(
            feature=feature,
            title=tasks_meta.get("title", feature).replace("Tasks:", "").strip(),
            tk_lines=foundation_tks,
            deps=_deps_for_tks(tasks_body, f_tk_set),
            ac_list=", ".join(all_ac_ids),
            tdd_source=tdd_source,
            tasks_source=tasks_source,
            generated_at=generated_at,
        )
        f_path = out_dir / f"{generated_at}-{feature}-foundation-spec.md"
        if args.dry_run:
            print(f"would write: {f_path}")
        else:
            f_path.write_text(f_content, encoding="utf-8")
            print(f"wrote: {f_path}")
        written.append(f_path)

    if not written:
        print("No specs generated (no Must AC rows?)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
