#!/usr/bin/env python3
"""Mechanical validator for prd-review output documents."""

from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_READINESS = frozenset({"ready", "needs-clarification", "blocked"})
VALID_PATHS = frozenset({"standard", "enhanced", "full"})
VALID_PHASE6 = frozenset({"A", "B", "C"})
FINDING_ID = re.compile(r"\b(AMB|CTR|CMP|TST|TRM|SCP)-\d+\b", re.I)
FR_ID = re.compile(r"\bFR-\d+\b", re.I)
OQ_ID = re.compile(r"\bOQ-\d+\b", re.I)
PRD_ANCHOR = re.compile(r"\[source:prd#[^\]]+\]", re.I)
COVERAGE_STATUS = re.compile(
    r"\|\s*[^|]+\s*\|\s*(Clear|Partial|Missing)\s*\|", re.I
)

REQUIRED_SECTIONS = [
    r"##\s+Executive\s+summary",
    r"##\s+Coverage\s+map",
    r"##\s+Findings",
    r"##\s+Pre-inventory\s+for\s+prd-to-tdd",
    r"##\s+Recommended\s+next\s+step",
]

FRONTMATTER_READINESS = re.compile(
    r"^readiness:\s*(ready|needs-clarification|blocked)\s*$", re.M | re.I
)
FRONTMATTER_FEATURE = re.compile(r"^feature:\s*.+\s*$", re.M)
FRONTMATTER_PRD = re.compile(r"^prd_source:\s*.+\s*$", re.M)
FRONTMATTER_DATE = re.compile(r"^reviewed_at:\s*\d{4}-\d{2}-\d{2}\s*$", re.M)
FRONTMATTER_PATH = re.compile(
    r"^prd_review_path:\s*(standard|enhanced|full)\s*$", re.M | re.I
)
FRONTMATTER_SCORE = re.compile(r"^complexity_score:\s*\d+\s*$", re.M)
FRONTMATTER_MODE = re.compile(r"^phase_6_mode:\s*([ABC])\s*$", re.M | re.I)
FRONTMATTER_DUAL = re.compile(r"^dual_brain_used:\s*(true|false)\s*$", re.M | re.I)

FINDINGS_TABLE_HEADER = re.compile(
    r"\|\s*severity\s*\|\s*prd-anchor\s*\|\s*ID\s*\|\s*issue\s*\|\s*suggested_fix\s*\|",
    re.I,
)

MIN_COVERAGE_ROWS = 8


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


def _path_mode_consistency(path: str, mode: str, dual: bool) -> list[str]:
    errors: list[str] = []
    path_l = path.lower()
    mode_u = mode.upper()
    if path_l == "standard" and mode_u != "A":
        errors.append(
            f"prd_review_path is 'standard' but phase_6_mode is '{mode_u}' (expected A)"
        )
    if path_l == "enhanced" and mode_u not in {"B"}:
        errors.append(
            f"prd_review_path is 'enhanced' but phase_6_mode is '{mode_u}' (expected B)"
        )
    if path_l == "full" and mode_u != "C":
        errors.append(
            f"prd_review_path is 'full' but phase_6_mode is '{mode_u}' (expected C)"
        )
    if path_l in {"enhanced", "full"} and not dual:
        errors.append(
            f"prd_review_path is '{path_l}' but dual_brain_used is false (expected true)"
        )
    if path_l == "standard" and dual:
        errors.append(
            "prd_review_path is 'standard' but dual_brain_used is true (expected false)"
        )
    return errors


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)

    if not fm.strip():
        errors.append("missing YAML frontmatter (--- ... ---)")
    else:
        if not FRONTMATTER_FEATURE.search(fm):
            errors.append("frontmatter: missing feature:")
        if not FRONTMATTER_PRD.search(fm):
            errors.append("frontmatter: missing prd_source:")
        if not FRONTMATTER_DATE.search(fm):
            errors.append("frontmatter: missing reviewed_at: YYYY-MM-DD")
        m = FRONTMATTER_READINESS.search(fm)
        if not m:
            errors.append(
                "frontmatter: missing readiness: (ready|needs-clarification|blocked)"
            )
        else:
            readiness = m.group(1).lower()
            ctr_ids = {
                x.upper()
                for x in FINDING_ID.findall(body)
                if x.upper().startswith("CTR")
            }
            if readiness == "ready" and ctr_ids:
                errors.append(
                    f"readiness is 'ready' but CTR findings exist: {sorted(ctr_ids)}"
                )
            crit = re.findall(r"^\|\s*Critical\s*\|", body, re.M | re.I)
            if readiness == "ready" and crit:
                errors.append(
                    "readiness is 'ready' but Critical severity rows exist in findings"
                )

        path_m = FRONTMATTER_PATH.search(fm)
        if not path_m:
            errors.append(
                "frontmatter: missing prd_review_path: (standard|enhanced|full)"
            )
        if not FRONTMATTER_SCORE.search(fm):
            errors.append("frontmatter: missing complexity_score: <integer>")
        mode_m = FRONTMATTER_MODE.search(fm)
        if not mode_m:
            errors.append("frontmatter: missing phase_6_mode: (A|B|C)")
        dual_m = FRONTMATTER_DUAL.search(fm)
        if not dual_m:
            errors.append("frontmatter: missing dual_brain_used: (true|false)")
        elif path_m and mode_m:
            dual = dual_m.group(1).lower() == "true"
            errors.extend(
                _path_mode_consistency(path_m.group(1), mode_m.group(1), dual)
            )

    for pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, body, re.I):
            errors.append(f"missing section matching /{pattern}/")

    if not FINDINGS_TABLE_HEADER.search(body):
        errors.append(
            "Findings section: missing table header severity|prd-anchor|ID|issue|suggested_fix"
        )

    coverage_rows = COVERAGE_STATUS.findall(body)
    if len(coverage_rows) < MIN_COVERAGE_ROWS:
        errors.append(
            f"Coverage map: expected at least {MIN_COVERAGE_ROWS} rows with "
            "Clear/Partial/Missing status"
        )

    fr_count = len(FR_ID.findall(body))
    if fr_count < 1:
        errors.append("Pre-inventory: expected at least one FR-n ID")

    anchors = PRD_ANCHOR.findall(body)
    if fr_count > 0 and len(anchors) < 1:
        errors.append(
            "expected at least one [source:prd#...] anchor in pre-inventory or findings"
        )

    if re.search(r"^##\s+Contradictions", body, re.M | re.I):
        if "CTR" not in body.upper() and "None identified" not in body:
            pass  # optional section

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate-prd-review.py <path-to-prd-review.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2
    errors = validate(path)
    if errors:
        print(f"FAIL: {path}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
