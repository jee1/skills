#!/usr/bin/env python3
"""Mechanical validator for prd-to-tdd output documents."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# --- Configurable forbidden back-reference patterns ---
FORBIDDEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("back-ref-ko-앞서", re.compile(r"앞서")),
    ("back-ref-ko-위에서", re.compile(r"위에서")),
    ("back-ref-ko-아래에서", re.compile(r"아래에서")),
    ("back-ref-ko-후술", re.compile(r"후술")),
    ("back-ref-ko-나중에", re.compile(r"나중에\s+(설명|기술|언급)")),
    ("back-ref-ko-상기", re.compile(r"상기")),
    ("back-ref-ko-전술", re.compile(r"전술")),
    ("back-ref-en-as-mentioned", re.compile(r"\bas mentioned\b", re.I)),
    ("back-ref-en-see-above", re.compile(r"\bsee above\b", re.I)),
    ("back-ref-en-see-below", re.compile(r"\bsee below\b", re.I)),
    ("back-ref-en-later", re.compile(r"\b(later in this document|explained later)\b", re.I)),
    ("back-ref-en-previously", re.compile(r"\bpreviously mentioned\b", re.I)),
]

REQUIRED_FRONTMATTER_KEYS = frozenset(
    {"title", "feature", "mode", "prd_source", "generated_at", "validation_passed", "review_rounds"}
)

CHAPTER_HEADERS = {
    "brownfield": [
        r"##\s+1\.\s+서문",
        r"##\s+2\.\s+배경과\s+문제",
        r"##\s+3\.\s+현재\s+시스템",
        r"##\s+4\.\s+갭과\s+설계\s+전환",
        r"##\s+5\.\s+목표\s+설계와\s+마무리",
    ],
    "greenfield": [
        r"##\s+1\.\s+서문",
        r"##\s+2\.\s+배경과\s+문제",
        r"##\s+3\.\s+시작점",
        r"##\s+4\.\s+설계\s+결정",
        r"##\s+5\.\s+목표\s+설계와\s+마무리",
    ],
}

TIER1_KEYWORDS = re.compile(
    r"(결정|채택|선택|아키텍처|인증|보안|데이터베이스|datastore|JWT|OAuth)",
    re.I,
)

OFFICIAL_URL = re.compile(
    r"https?://[^\s\)>\"]+",
    re.I,
)

SOURCE_BLOCK = re.compile(r"^\s*>\s*\*\*(결정|사실|근거|코드):\*\*", re.M)

DECISION_BLOCK = re.compile(
    r">\s*\*\*결정:\*\*[^\n]*\n(?:>\s*\*\*근거:\*\*[^\n]*\n)?(?:>\s*\*\*코드:\*\*[^\n]*)?",
    re.M,
)


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


def check_chapters(body: str, mode: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if mode not in CHAPTER_HEADERS:
        return errors
    for pattern in CHAPTER_HEADERS[mode]:
        if not re.search(pattern, body):
            errors.append(
                ValidationError(0, "chapter-missing", f"Required chapter header not found: /{pattern}/")
            )
    return errors


def check_forbidden_phrases(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    lines = body.splitlines()
    for i, line in enumerate(lines, start=1):
        for code, pattern in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                errors.append(
                    ValidationError(i, code, f"Forbidden back-reference phrase: {line.strip()[:80]}")
                )
    return errors


def check_ch4_ch5_sources(body: str) -> list[ValidationError]:
    """Ch.4–5 should contain at least one source block if non-empty technical sections exist."""
    errors: list[ValidationError] = []
    parts = re.split(r"^##\s+5\.\s+", body, maxsplit=1, flags=re.M)
    tail = parts[0]
    ch4_match = re.search(r"^##\s+4\.\s+", tail, flags=re.M)
    if not ch4_match:
        return errors
    ch4_and_5 = tail[ch4_match.start() :]
    if len(ch4_and_5.strip()) < 100:
        return errors
    if not SOURCE_BLOCK.search(ch4_and_5):
        errors.append(
            ValidationError(
                0,
                "source-block-missing",
                "Chapters 4–5 appear to have content but no > **결정:** / **사실:** source blocks",
            )
        )
    return errors


def check_tier1_decisions(body: str, mode: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for match in DECISION_BLOCK.finditer(body):
        block = match.group(0)
        line_num = body[: match.start()].count("\n") + 1
        if not OFFICIAL_URL.search(block):
            errors.append(
                ValidationError(
                    line_num,
                    "tier1-no-official-url",
                    "Decision block missing official https URL in **근거:**",
                )
            )
        if mode == "brownfield":
            has_code = "**코드:**" in block and "Greenfield" not in block
            has_path = re.search(r"`[^`]+\.[a-zA-Z0-9]+:\d+", block)
            if has_code and not has_path:
                errors.append(
                    ValidationError(
                        line_num,
                        "tier1-code-ref",
                        "Brownfield decision block should include **코드:** path:line or explicit no-code reason",
                    )
                )
    return errors


def validate(path: Path) -> list[ValidationError]:
    text = path.read_text(encoding="utf-8")
    meta, body, errors = parse_frontmatter(text)
    mode = meta.get("mode", "")

    errors.extend(check_chapters(body, mode))
    errors.extend(check_forbidden_phrases(body))
    errors.extend(check_ch4_ch5_sources(body))
    errors.extend(check_tier1_decisions(body, mode))

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-tdd.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    errors = validate(path)
    if not errors:
        print(f"OK: {path}")
        return 0

    print(f"FAIL: {path} ({len(errors)} issue(s))", file=sys.stderr)
    for err in errors:
        print(str(err), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
