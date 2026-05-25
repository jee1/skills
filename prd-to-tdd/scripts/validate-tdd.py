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
        r"##\s+5\.\s+상위설계",
        r"##\s+6\.\s+상세설계",
        r"##\s+7\.\s+마무리",
    ],
    "greenfield": [
        r"##\s+1\.\s+서문",
        r"##\s+2\.\s+배경과\s+문제",
        r"##\s+3\.\s+시작점",
        r"##\s+4\.\s+설계\s+결정",
        r"##\s+5\.\s+상위설계",
        r"##\s+6\.\s+상세설계",
        r"##\s+7\.\s+마무리",
    ],
}

CH5_SUBSECTIONS = [
    r"###\s+아키텍처\s+개요",
    r"###\s+구성요소\s+및\s+책임",
    r"###\s+데이터\s+흐름",
]

CH6_SUBSECTIONS = [
    r"###\s+API\s+및\s+인터페이스",
    r"###\s+데이터\s+모델",
    r"###\s+핵심\s+처리\s+흐름",
]

CH7_SUBSECTIONS = [
    r"###\s+롤아웃·일정",
    r"###\s+롤아웃\s+및\s+일정",
    r"###\s+리스크",
    r"###\s+열린\s+질문",
]

TIER1_KEYWORDS = re.compile(
    r"(결정|채택|선택|아키텍처|인증|보안|데이터베이스|datastore|JWT|OAuth)",
    re.I,
)

OFFICIAL_URL = re.compile(
    r"https?://[^\s\)>\"]+",
    re.I,
)

SOURCE_BLOCK = re.compile(r"^\s*>\s*\*\*(결정|사실|근거|코드|갈림|대안|권장|상태):\*\*", re.M)

REF_TAG = re.compile(r"\[ref:(A-\d+)\]", re.I)
APPENDIX_A_HEADER = re.compile(r"^##\s+부록\s+A", re.M)
APPENDIX_B_HEADER = re.compile(r"^##\s+부록\s+B", re.M)
MERMAID_FENCE = re.compile(r"```mermaid[\s\S]*?```", re.M)
HANNUINE_HEADER = re.compile(r"^####\s+한눈에", re.M)
CH1_GOALS = re.compile(r"^###\s+Goals\s*/\s*Non-Goals", re.M)
CH1_READER = re.compile(r"^###\s+이\s+문서\s+읽는\s+법", re.M)
CH1_TOC = re.compile(r"^###\s+목차", re.M)
CH4_SUMMARY = re.compile(r"^###\s+결정\s+요약", re.M)
SASIL_BLOCK = re.compile(r"^\s*>\s*\*\*사실:\*\*", re.M)
APPENDIX_A_ID = re.compile(r"^\|\s*(A-\d+)\s*\|", re.M)

MIN_CH234_SENTENCES = 8
MIN_CH1_OPENING_SENTENCES = 3
MIN_DOC_SENTENCES = 40
MIN_CH5_LEAD_SENTENCES = 2
MIN_CH6_LEAD_SENTENCES = 1

FORBIDDEN_META_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("meta-yoyak", re.compile(r"^요약\s*:", re.M)),
    ("meta-hannuine", re.compile(r"^####\s+한눈에", re.M)),
    ("meta-tldr", re.compile(r"^###\s+TL;DR", re.M)),
    ("meta-6h-en", re.compile(r"^(Who|What|When|Where|Why|How)\s*:", re.M | re.I)),
    ("meta-6h-ko", re.compile(r"^(누가|무엇|언제|어디|왜|어떻게)\s*:", re.M)),
]

BRIDGE_KEYWORDS = re.compile(
    r"때문|따라|현재|PRD|미구현|갭|요구|because|therefore|requires?",
    re.I,
)

# --- Strict depth profile (default) ---
SUBSECTION_MIN_CHARS = 120
MIN_CH5_COMPONENTS = 2
MIN_DATA_FLOW_STEPS = 3
MIN_API_TABLE_DATA_ROWS = 3
MIN_ENTITY_FIELD_ROWS = 3
MIN_ERROR_BRANCH_LINES = 2

YOAK_PATTERN = re.compile(r"요약\s*:")
COMPONENT_BULLET = re.compile(r"^[-*]\s+\*\*([^*]+)\*\*", re.M)
COMPONENT_TABLE = re.compile(r"\|\s*\*\*([^*]+)\*\*")
COMPONENT_LABEL = re.compile(r"\((신규|기존)\)")
NUMBERED_STEP = re.compile(r"^\s*\d+\.", re.M)
ERROR_BRANCH = re.compile(
    r"오류|에러|실패|retry|재시|rollback|보상|4\d{2}|5\d{2}|error|fail",
    re.I,
)

DECISION_BLOCK = re.compile(
    r">\s*\*\*결정:\*\*[^\n]*\n(?:>\s*\*\*근거:\*\*[^\n]*\n)?(?:>\s*\*\*코드:\*\*[^\n]*)?",
    re.M,
)

FORK_BLOCK = re.compile(
    r">\s*\*\*갈림:\*\*[^\n]*\n"
    r"(?:>\s*\*\*[^\n]*\n)*?",
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


def _strip_structural_content(text: str) -> str:
    """Remove tables, blockquotes, fences, headings for prose metrics."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith("|"):
            continue
        if stripped.startswith(">"):
            continue
        if re.match(r"^#{1,6}\s", stripped):
            continue
        lines.append(line)
    return "\n".join(lines)


def _split_sentences(text: str) -> list[str]:
    prose = _strip_structural_content(text).strip()
    if not prose:
        return []
    parts = re.split(r"(?<=[.!?。])\s+|\n\n+", prose)
    return [p.strip() for p in parts if len(p.strip()) >= 8]


def _count_sentences(text: str) -> int:
    return len(_split_sentences(text))


def _prose_char_count(text: str) -> int:
    return len(_strip_structural_content(text).strip())


def _significant_tokens(sentence: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[\w가-힣]{3,}", sentence)}


def _chapter_bridge_ok(prev_chapter: str, next_chapter: str) -> bool:
    prev_sents = _split_sentences(prev_chapter)
    next_sents = _split_sentences(next_chapter)
    if not prev_sents or not next_sents:
        return False
    last, first = prev_sents[-1], next_sents[0]
    if _significant_tokens(last) & _significant_tokens(first):
        return True
    return bool(BRIDGE_KEYWORDS.search(first))


def _lead_prose_lines(subsection: str) -> str:
    """Text before first table, fence, numbered step, or component bullet."""
    collected: list[str] = []
    for line in subsection.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") or stripped.startswith("```"):
            break
        if re.match(r"^\d+\.", stripped):
            break
        if COMPONENT_BULLET.match(stripped):
            break
        if stripped.startswith("#### ") or stripped.startswith("### "):
            continue
        collected.append(line)
    return "\n".join(collected)


def _count_table_data_rows(text: str) -> int:
    table_lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return 0
    data_rows = 0
    for index, line in enumerate(table_lines):
        if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
            continue
        if index == 0:
            continue
        data_rows += 1
    return data_rows


def _extract_component_names(text: str) -> list[str]:
    names: list[str] = []
    for pattern in (COMPONENT_BULLET, COMPONENT_TABLE):
        names.extend(pattern.findall(text))
    seen: set[str] = set()
    ordered: list[str] = []
    for name in names:
        clean = name.strip()
        if clean and clean not in seen:
            seen.add(clean)
            ordered.append(clean)
    return ordered


def check_design_depth(body: str, mode: str) -> list[ValidationError]:
    """Strict profile: minimum content depth for Ch.5–6 subsections."""
    errors: list[ValidationError] = []
    ch5 = _chapter_slice(body, r"^##\s+5\.\s+상위설계", r"^##\s+6\.\s+")
    ch6 = _chapter_slice(body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    if not ch5 or not ch6:
        return errors

    ch5_checks = [
        (r"###\s+아키텍처\s+개요", "ch5-architecture"),
        (r"###\s+구성요소\s+및\s+책임", "ch5-components"),
        (r"###\s+데이터\s+흐름", "ch5-data-flow"),
    ]
    ch6_checks = [
        (r"###\s+API\s+및\s+인터페이스", "ch6-api"),
        (r"###\s+데이터\s+모델", "ch6-data-model"),
        (r"###\s+핵심\s+처리\s+흐름", "ch6-flow"),
    ]

    for chapter, checks in ((ch5, ch5_checks), (ch6, ch6_checks)):
        for pattern, _label in checks:
            line_num, content = _subsection_content(chapter, pattern)
            if not content:
                continue
            prose_len = _prose_char_count(content)
            if prose_len < SUBSECTION_MIN_CHARS:
                errors.append(
                    ValidationError(
                        line_num,
                        "subsection-thin",
                        f"Subsection prose too thin ({prose_len} chars, min {SUBSECTION_MIN_CHARS})",
                    )
                )

    comp_line, components_sec = _subsection_content(ch5, r"###\s+구성요소\s+및\s+책임")
    component_names = _extract_component_names(components_sec)
    if len(component_names) < MIN_CH5_COMPONENTS:
        errors.append(
            ValidationError(
                comp_line,
                "ch5-insufficient-components",
                f"Ch.5 ### 구성요소 needs ≥{MIN_CH5_COMPONENTS} named components (**Name** bullets or table)",
            )
        )

    if mode == "brownfield" and component_names:
        for line in components_sec.splitlines():
            if not COMPONENT_BULLET.match(line.strip()):
                continue
            if not COMPONENT_LABEL.search(line):
                bullet_line = comp_line + components_sec[: components_sec.find(line)].count("\n")
                errors.append(
                    ValidationError(
                        bullet_line,
                        "brownfield-component-label",
                        f"Brownfield component missing (신규) or (기존) label: {line.strip()[:60]}",
                    )
                )

    flow_line, flow_sec = _subsection_content(ch5, r"###\s+데이터\s+흐름")
    step_count = len(NUMBERED_STEP.findall(flow_sec))
    if step_count < MIN_DATA_FLOW_STEPS:
        errors.append(
            ValidationError(
                flow_line,
                "ch5-data-flow-steps",
                f"Ch.5 ### 데이터 흐름 needs ≥{MIN_DATA_FLOW_STEPS} numbered steps (1. 2. 3.)",
            )
        )

    api_line, api_sec = _subsection_content(ch6, r"###\s+API\s+및\s+인터페이스")
    api_rows = _count_table_data_rows(api_sec)
    if api_rows < MIN_API_TABLE_DATA_ROWS:
        errors.append(
            ValidationError(
                api_line,
                "ch6-api-no-table",
                f"Ch.6 ### API needs markdown table with ≥{MIN_API_TABLE_DATA_ROWS} data rows",
            )
        )

    model_line, model_sec = _subsection_content(ch6, r"###\s+데이터\s+모델")
    model_rows = _count_table_data_rows(model_sec)
    field_lines = len(
        [line for line in model_sec.splitlines() if re.search(r":\s*\w+|^\|\s*\w", line.strip())]
    )
    if model_rows < MIN_ENTITY_FIELD_ROWS and field_lines < MIN_ENTITY_FIELD_ROWS:
        errors.append(
            ValidationError(
                model_line,
                "ch6-data-model-thin",
                f"Ch.6 ### 데이터 모델 needs entity table (≥{MIN_ENTITY_FIELD_ROWS} field rows)",
            )
        )

    proc_line, proc_sec = _subsection_content(ch6, r"###\s+핵심\s+처리\s+흐름")
    error_lines = [line for line in proc_sec.splitlines() if ERROR_BRANCH.search(line)]
    if len(error_lines) < MIN_ERROR_BRANCH_LINES:
        errors.append(
            ValidationError(
                proc_line,
                "ch6-flow-no-errors",
                f"Ch.6 ### 핵심 처리 흐름 needs ≥{MIN_ERROR_BRANCH_LINES} error/retry branches",
            )
        )

    if component_names:
        for name in component_names:
            if name not in ch6:
                errors.append(
                    ValidationError(
                        comp_line,
                        "ch5-ch6-component-drift",
                        f"Ch.5 component **{name}** must be referenced in Ch.6 상세설계",
                    )
                )

    return errors


def check_design_subsections(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    ch5 = _chapter_slice(body, r"^##\s+5\.\s+상위설계", r"^##\s+6\.\s+")
    ch6 = _chapter_slice(body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    ch7 = _chapter_slice(body, r"^##\s+7\.\s+마무리", None)

    for pattern in CH5_SUBSECTIONS:
        if ch5 and not re.search(pattern, ch5):
            errors.append(
                ValidationError(0, "ch5-subsection-missing", f"Ch.5 missing required subsection: /{pattern}/")
            )
    for pattern in CH6_SUBSECTIONS:
        if ch6 and not re.search(pattern, ch6):
            errors.append(
                ValidationError(0, "ch6-subsection-missing", f"Ch.6 missing required subsection: /{pattern}/")
            )

    if ch7:
        if not re.search(r"###\s+열린\s+질문", ch7):
            errors.append(ValidationError(0, "ch7-open-questions", "Ch.7 missing ### 열린 질문"))
        if not (re.search(r"###\s+롤아웃·일정", ch7) or re.search(r"###\s+롤아웃\s+및\s+일정", ch7)):
            errors.append(ValidationError(0, "ch7-rollout", "Ch.7 missing ### 롤아웃·일정"))
        if not re.search(r"###\s+리스크", ch7):
            errors.append(ValidationError(0, "ch7-risks", "Ch.7 missing ### 리스크"))
    return errors


def check_ch4_ch6_sources(body: str) -> list[ValidationError]:
    """Ch.4 should contain Tier-1 source blocks when it has substance."""
    errors: list[ValidationError] = []
    ch4 = _chapter_slice(body, r"^##\s+4\.\s+", r"^##\s+5\.\s+")

    if len(ch4.strip()) >= 80 and not SOURCE_BLOCK.search(ch4):
        errors.append(
            ValidationError(
                0,
                "source-block-missing",
                "Ch.4 has content but no > **결정:** / **갈림:** source blocks",
            )
        )
    return errors


def _fork_block_slice(body: str, start: int) -> str:
    """Return consecutive blockquote lines starting at **갈림:**."""
    lines = body[start:].splitlines()
    collected: list[str] = []
    for line in lines:
        if line.startswith(">") or (not collected):
            if line.startswith(">"):
                collected.append(line)
            elif not collected:
                continue
            else:
                break
        else:
            break
    return "\n".join(collected)


def check_fork_blocks(body: str, mode: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for match in re.finditer(r"^\s*>\s*\*\*갈림:\*\*", body, re.M):
        line_num = body[: match.start()].count("\n") + 1
        block = _fork_block_slice(body, match.start())
        required = ("**대안:**", "**권장:**", "**근거:**", "**상태:**")
        for token in required:
            if token not in block:
                errors.append(
                    ValidationError(
                        line_num,
                        "fork-block-incomplete",
                        f"Fork block missing {token}",
                    )
                )
        if "**근거:**" in block and not OFFICIAL_URL.search(block):
            errors.append(
                ValidationError(
                    line_num,
                    "fork-no-official-url",
                    "Fork block **근거:** missing official https URL for recommended option",
                )
            )
        if "**상태:**" in block:
            if "권장(미확정)" not in block and "확정" not in block:
                errors.append(
                    ValidationError(
                        line_num,
                        "fork-status-invalid",
                        "**상태:** must be 권장(미확정) or 확정",
                    )
                )
        if mode == "brownfield" and "**코드:**" in block and "Greenfield" not in block:
            if not re.search(r"`[^`]+\.[a-zA-Z0-9]+:\d+", block):
                errors.append(
                    ValidationError(
                        line_num,
                        "fork-code-ref",
                        "Brownfield fork block should include **코드:** path:line when applicable",
                    )
                )
    return errors


def check_pending_open_questions(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if "권장(미확정)" not in body:
        return errors
    ch7_match = re.search(r"^##\s+7\.\s+마무리", body, flags=re.M)
    if not ch7_match:
        return errors
    ch7 = body[ch7_match.start() :]
    if "열린 질문" not in ch7 and "최종 선택" not in ch7:
        errors.append(
            ValidationError(
                0,
                "pending-fork-no-open-question",
                "Ch.4 has 권장(미확정) but Ch.7 lacks 열린 질문 / 최종 선택 item",
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


def _body_before_appendices(body: str) -> str:
    match = APPENDIX_A_HEADER.search(body)
    if match:
        return body[: match.start()]
    return body


def _appendix_slice(body: str, header_pattern: re.Pattern[str]) -> str:
    match = header_pattern.search(body)
    if not match:
        return ""
    begin = match.start()
    next_appendix = re.search(r"^##\s+부록\s+", body[begin + 1 :], re.M)
    if next_appendix:
        return body[begin : begin + 1 + next_appendix.start()]
    return body[begin:]


def _appendix_citation_checks(body: str, ch4: str, ch5: str, ch6: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for label, chunk in (("5", ch5), ("6", ch6)):
        if chunk and SASIL_BLOCK.search(chunk):
            errors.append(
                ValidationError(
                    0,
                    "ch56-sasil-forbidden",
                    f"Ch.{label} must not use > **사실:** blockquotes; use [ref:A-n] + Appendix A",
                )
            )

    if not APPENDIX_A_HEADER.search(body):
        errors.append(ValidationError(0, "appendix-a-missing", "Missing ## 부록 A. 출처·코드 위치"))
    else:
        appendix_a = _appendix_slice(body, APPENDIX_A_HEADER)
        appendix_ids = {m.group(1).upper() for m in APPENDIX_A_ID.finditer(appendix_a)}
        main_body = _body_before_appendices(body)
        for ref in {m.group(1).upper() for m in REF_TAG.finditer(main_body)}:
            if ref not in appendix_ids:
                errors.append(
                    ValidationError(
                        0,
                        "appendix-a-unresolved-ref",
                        f"[ref:{ref}] in body has no matching row in Appendix A",
                    )
                )

    ch4_has_blockquote = bool(re.search(r"^\s*>\s*\*\*(결정|갈림):\*\*", ch4, re.M)) if ch4 else False
    if ch4_has_blockquote and not APPENDIX_B_HEADER.search(body):
        errors.append(
            ValidationError(0, "appendix-b-missing", "Ch.4 has blockquotes but ## 부록 B is missing")
        )
    return errors


def check_narrative(body: str) -> list[ValidationError]:
    """Narrative profile: story prose, bridges, anti-labels, appendices."""
    errors: list[ValidationError] = []

    ch1 = _chapter_slice(body, r"^##\s+1\.\s+서문", r"^##\s+2\.\s+")
    ch2 = _chapter_slice(body, r"^##\s+2\.\s+", r"^##\s+3\.\s+")
    ch3 = _chapter_slice(body, r"^##\s+3\.\s+", r"^##\s+4\.\s+")
    ch4 = _chapter_slice(body, r"^##\s+4\.\s+", r"^##\s+5\.\s+")
    ch5 = _chapter_slice(body, r"^##\s+5\.\s+상위설계", r"^##\s+6\.\s+")
    ch6 = _chapter_slice(body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    ch234567 = _body_before_appendices(body)
    bridge_body = ch234567
    for code, pattern in FORBIDDEN_META_PATTERNS:
        if pattern.search(bridge_body):
            errors.append(
                ValidationError(0, code, f"Forbidden meta-label in Ch.2–7: {code}")
            )

    if ch1:
        first_sub = re.search(r"^###\s+", ch1, re.M)
        opening = ch1[: first_sub.start()] if first_sub else ch1
        opening = re.sub(r"^#\s+.*\n", "", opening, count=1, flags=re.M)
        if _count_sentences(opening) < MIN_CH1_OPENING_SENTENCES:
            errors.append(
                ValidationError(
                    0,
                    "ch1-opening-thin",
                    f"Ch.1 needs ≥{MIN_CH1_OPENING_SENTENCES} opening sentences before first ### (no TL;DR section)",
                )
            )
        for pattern, code, label in (
            (CH1_GOALS, "ch1-goals-missing", "### Goals / Non-Goals"),
            (CH1_READER, "ch1-reader-missing", "### 이 문서 읽는 법"),
            (CH1_TOC, "ch1-toc-missing", "### 목차"),
        ):
            if not pattern.search(ch1):
                errors.append(ValidationError(0, code, f"Ch.1 missing {label}"))

    for num, chapter, code in (
        (2, ch2, "ch2-min-sentences"),
        (3, ch3, "ch3-min-sentences"),
        (4, ch4, "ch4-min-sentences"),
    ):
        count = _count_sentences(chapter)
        if chapter and count < MIN_CH234_SENTENCES:
            errors.append(
                ValidationError(
                    0,
                    code,
                    f"Ch.{num} needs ≥{MIN_CH234_SENTENCES} prose sentences (found {count})",
                )
            )

    if ch2 and ch3 and not _chapter_bridge_ok(ch2, ch3):
        errors.append(ValidationError(0, "ch-bridge-2-3", "Weak narrative bridge between Ch.2 and Ch.3"))
    if ch3 and ch4 and not _chapter_bridge_ok(ch3, ch4):
        errors.append(ValidationError(0, "ch-bridge-3-4", "Weak narrative bridge between Ch.3 and Ch.4"))
    if ch4 and ch5 and not _chapter_bridge_ok(ch4, ch5):
        errors.append(ValidationError(0, "ch-bridge-4-5", "Weak narrative bridge between Ch.4 and Ch.5"))

    if ch4:
        if not CH4_SUMMARY.search(ch4):
            errors.append(ValidationError(0, "ch4-summary-missing", "Ch.4 missing ### 결정 요약"))
        else:
            _, summary_sec = _subsection_content(ch4, r"###\s+결정\s+요약")
            if _count_table_data_rows(summary_sec) < 1:
                errors.append(
                    ValidationError(0, "ch4-summary-empty", "### 결정 요약 needs ≥1 data row")
                )

    if ch5:
        _, arch_sec = _subsection_content(ch5, r"###\s+아키텍처\s+개요")
        if arch_sec and not MERMAID_FENCE.search(arch_sec):
            errors.append(
                ValidationError(0, "ch5-mermaid-missing", "Ch.5 ### 아키텍처 개요 needs ```mermaid diagram")
            )
        for pattern, label, min_lead in (
            (r"###\s+아키텍처\s+개요", "아키텍처 개요", MIN_CH5_LEAD_SENTENCES),
            (r"###\s+구성요소\s+및\s+책임", "구성요소 및 책임", MIN_CH5_LEAD_SENTENCES),
            (r"###\s+데이터\s+흐름", "데이터 흐름", MIN_CH5_LEAD_SENTENCES),
        ):
            line_num, content = _subsection_content(ch5, pattern)
            if not content:
                continue
            lead_count = _count_sentences(_lead_prose_lines(content))
            if lead_count < min_lead:
                errors.append(
                    ValidationError(
                        line_num,
                        "ch5-lead-prose-thin",
                        f"Ch.5 ### {label} needs ≥{min_lead} lead sentences before structure (found {lead_count})",
                    )
                )

    if ch6:
        for pattern, label in (
            (r"###\s+API\s+및\s+인터페이스", "API 및 인터페이스"),
            (r"###\s+데이터\s+모델", "데이터 모델"),
            (r"###\s+핵심\s+처리\s+흐름", "핵심 처리 흐름"),
        ):
            line_num, content = _subsection_content(ch6, pattern)
            if not content:
                continue
            lead_count = _count_sentences(_lead_prose_lines(content))
            if lead_count < MIN_CH6_LEAD_SENTENCES:
                errors.append(
                    ValidationError(
                        line_num,
                        "ch6-lead-prose-thin",
                        f"Ch.6 ### {label} needs ≥{MIN_CH6_LEAD_SENTENCES} lead sentence before tables (found {lead_count})",
                    )
                )

    doc_sentences = _count_sentences(_body_before_appendices(body))
    if doc_sentences < MIN_DOC_SENTENCES:
        errors.append(
            ValidationError(
                0,
                "doc-min-sentences",
                f"Document needs ≥{MIN_DOC_SENTENCES} prose sentences (found {doc_sentences})",
            )
        )

    errors.extend(_appendix_citation_checks(body, ch4, ch5, ch6))
    return errors


def check_readability(body: str) -> list[ValidationError]:
    """Deprecated alias — use check_narrative."""
    return check_narrative(body)


def validate(path: Path, *, strict: bool = True, narrative: bool = False, readability: bool = False) -> list[ValidationError]:
    if readability and not narrative:
        print("Warning: --readability is deprecated; use --narrative", file=sys.stderr)
        narrative = True
    text = path.read_text(encoding="utf-8")
    meta, body, errors = parse_frontmatter(text)
    mode = meta.get("mode", "")

    errors.extend(check_chapters(body, mode))
    errors.extend(check_forbidden_phrases(body))
    errors.extend(check_design_subsections(body))
    errors.extend(check_ch4_ch6_sources(body))
    errors.extend(check_fork_blocks(body, mode))
    errors.extend(check_tier1_decisions(body, mode))
    errors.extend(check_pending_open_questions(body))
    if strict:
        errors.extend(check_design_depth(body, mode))
    if narrative:
        errors.extend(check_narrative(body))

    return errors


def main() -> int:
    args = sys.argv[1:]
    strict = True
    narrative = False
    paths: list[str] = []
    for arg in args:
        if arg == "--lenient":
            strict = False
        elif arg in ("--readability", "--narrative"):
            narrative = True
        elif arg.startswith("--"):
            print(f"Unknown flag: {arg}", file=sys.stderr)
            return 2
        else:
            paths.append(arg)
    if len(paths) != 1:
        print(
            f"Usage: {sys.argv[0]} [--lenient] [--narrative] <path-to-tdd.md>",
            file=sys.stderr,
        )
        return 2

    path = Path(paths[0])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    readability = "--readability" in args
    errors = validate(path, strict=strict, narrative=narrative, readability=readability)
    if not errors:
        print(f"OK: {path}")
        return 0

    print(f"FAIL: {path} ({len(errors)} issue(s))", file=sys.stderr)
    for err in errors:
        print(str(err), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
