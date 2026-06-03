#!/usr/bin/env python3
"""Mechanical validator for prd-review output documents."""

from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_READINESS = frozenset({"ready", "needs-clarification", "blocked"})
VALID_SEVERITY = frozenset({"critical", "high", "medium", "low"})
FINDING_ID = re.compile(r"\b(AMB|CTR|CMP|TST|TRM|SCP)-\d+\b", re.I)
FR_ID = re.compile(r"\bFR-\d+\b", re.I)
OQ_ID = re.compile(r"\bOQ-\d+\b", re.I)
PRD_ANCHOR = re.compile(r"\[source:prd#[^\]]+\]", re.I)

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

FINDINGS_TABLE_HEADER = re.compile(
    r"\|\s*severity\s*\|\s*prd-anchor\s*\|\s*ID\s*\|\s*issue\s*\|\s*suggested_fix\s*\|",
    re.I,
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


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
            if readiness == "ready":
                ctr_ids = {x.upper() for x in FINDING_ID.findall(body) if x.upper().startswith("CTR")}
                if ctr_ids:
                    errors.append(
                        f"readiness is 'ready' but CTR findings exist: {sorted(ctr_ids)}"
                    )
                crit = re.findall(
                    r"^\|\s*Critical\s*\|", body, re.M | re.I
                )
                if crit:
                    errors.append(
                        "readiness is 'ready' but Critical severity rows exist in findings"
                    )

    for pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, body, re.I):
            errors.append(f"missing section matching /{pattern}/")

    if not FINDINGS_TABLE_HEADER.search(body):
        errors.append("Findings section: missing table header severity|prd-anchor|ID|issue|suggested_fix")

    fr_count = len(FR_ID.findall(body))
    if fr_count < 1:
        errors.append("Pre-inventory: expected at least one FR-n ID")

    anchors = PRD_ANCHOR.findall(body)
    if fr_count > 0 and len(anchors) < 1:
        errors.append("expected at least one [source:prd#...] anchor in pre-inventory or findings")

    if re.search(r"^##\s+Contradictions", body, re.M | re.I):
        if not FINDING_ID.search(body) or "CTR" not in body.upper():
            pass  # section may say "None identified"

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
