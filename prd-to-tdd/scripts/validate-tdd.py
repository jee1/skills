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
CH1_TLDR = re.compile(r"^###\s+TL;DR", re.M)
CH1_GOALS = re.compile(r"^###\s+Goals\s*/\s*Non-Goals", re.M)
CH1_READER = re.compile(r"^###\s+이\s+문서\s+읽는\s+법", re.M)
CH1_TOC = re.compile(r"^###\s+목차", re.M)
CH4_SUMMARY = re.compile(r"^###\s+결정\s+요약", re.M)
CH6_SPEC_INDEX = re.compile(r"^###\s+스펙\s+인덱스", re.M)
SASIL_BLOCK = re.compile(r"^\s*>\s*\*\*사실:\*\*", re.M)
APPENDIX_A_ID = re.compile(r"^\|\s*(A-\d+)\s*\|", re.M)
MIN_HANNUINE_BULLETS = 3

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
            if not YOAK_PATTERN.search(content):
                errors.append(
                    ValidationError(
                        line_num,
                        "subsection-no-yoyak",
                        "Subsection must open with 요약: (see design-sections.md depth rubric)",
                    )
                )
            if len(content) < SUBSECTION_MIN_CHARS:
                errors.append(
                    ValidationError(
                        line_num,
                        "subsection-thin",
                        f"Subsection content too thin ({len(content)} chars, min {SUBSECTION_MIN_CHARS})",
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


def _count_hannuine_bullets(subsection: str) -> int:
    match = HANNUINE_HEADER.search(subsection)
    if not match:
        return 0
    after = subsection[match.end() :]
    count = 0
    for line in after.splitlines():
        stripped = line.strip()
        if stripped.startswith("#### ") or stripped.startswith("### ") or stripped.startswith("## "):
            break
        if re.match(r"^[-*]\s+", stripped):
            count += 1
    return count


def check_readability(body: str) -> list[ValidationError]:
    """Readability profile: navigation, diagrams, appendix citations."""
    errors: list[ValidationError] = []

    ch1 = _chapter_slice(body, r"^##\s+1\.\s+서문", r"^##\s+2\.\s+")
    if ch1:
        for pattern, code, label in (
            (CH1_TLDR, "ch1-tldr-missing", "### TL;DR"),
            (CH1_GOALS, "ch1-goals-missing", "### Goals / Non-Goals"),
            (CH1_READER, "ch1-reader-missing", "### 이 문서 읽는 법"),
            (CH1_TOC, "ch1-toc-missing", "### 목차"),
        ):
            if not pattern.search(ch1):
                errors.append(ValidationError(0, code, f"Ch.1 missing {label}"))

    ch4 = _chapter_slice(body, r"^##\s+4\.\s+", r"^##\s+5\.\s+")
    if ch4:
        if not CH4_SUMMARY.search(ch4):
            errors.append(ValidationError(0, "ch4-summary-missing", "Ch.4 missing ### 결정 요약"))
        else:
            _, summary_sec = _subsection_content(ch4, r"###\s+결정\s+요약")
            if _count_table_data_rows(summary_sec) < 1:
                errors.append(
                    ValidationError(0, "ch4-summary-empty", "### 결정 요약 needs ≥1 data row")
                )

    ch5 = _chapter_slice(body, r"^##\s+5\.\s+상위설계", r"^##\s+6\.\s+")
    if ch5:
        _, arch_sec = _subsection_content(ch5, r"###\s+아키텍처\s+개요")
        if arch_sec and not MERMAID_FENCE.search(arch_sec):
            errors.append(
                ValidationError(0, "ch5-mermaid-missing", "Ch.5 ### 아키텍처 개요 needs ```mermaid diagram")
            )
        for pattern, label in (
            (r"###\s+아키텍처\s+개요", "아키텍처 개요"),
            (r"###\s+구성요소\s+및\s+책임", "구성요소 및 책임"),
            (r"###\s+데이터\s+흐름", "데이터 흐름"),
        ):
            line_num, content = _subsection_content(ch5, pattern)
            if not content:
                continue
            bullets = _count_hannuine_bullets(content)
            if bullets < MIN_HANNUINE_BULLETS:
                errors.append(
                    ValidationError(
                        line_num,
                        "ch5-hannuine-missing",
                        f"Ch.5 ### {label} needs #### 한눈에 with ≥{MIN_HANNUINE_BULLETS} bullets (found {bullets})",
                    )
                )

    ch6 = _chapter_slice(body, r"^##\s+6\.\s+상세설계", r"^##\s+7\.\s+")
    if ch6:
        if not CH6_SPEC_INDEX.search(ch6):
            errors.append(ValidationError(0, "ch6-spec-index-missing", "Ch.6 missing ### 스펙 인덱스"))
        else:
            spec_pos = CH6_SPEC_INDEX.search(ch6)
            api_pos = re.search(r"^###\s+API\s+및\s+인터페이스", ch6, re.M)
            if spec_pos and api_pos and spec_pos.start() > api_pos.start():
                errors.append(
                    ValidationError(0, "ch6-spec-index-order", "### 스펙 인덱스 must appear before ### API 및 인터페이스")
                )
            _, spec_sec = _subsection_content(ch6, r"###\s+스펙\s+인덱스")
            if _count_table_data_rows(spec_sec) < 1:
                errors.append(
                    ValidationError(0, "ch6-spec-index-empty", "### 스펙 인덱스 needs ≥1 data row")
                )

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


def validate(path: Path, *, strict: bool = True, readability: bool = False) -> list[ValidationError]:
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
    if readability:
        errors.extend(check_readability(body))

    return errors


def main() -> int:
    args = sys.argv[1:]
    strict = True
    readability = False
    paths: list[str] = []
    for arg in args:
        if arg == "--lenient":
            strict = False
        elif arg == "--readability":
            readability = True
        elif arg.startswith("--"):
            print(f"Unknown flag: {arg}", file=sys.stderr)
            return 2
        else:
            paths.append(arg)
    if len(paths) != 1:
        print(
            f"Usage: {sys.argv[0]} [--lenient] [--readability] <path-to-tdd.md>",
            file=sys.stderr,
        )
        return 2

    path = Path(paths[0])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    errors = validate(path, strict=strict, readability=readability)
    if not errors:
        print(f"OK: {path}")
        return 0

    print(f"FAIL: {path} ({len(errors)} issue(s))", file=sys.stderr)
    for err in errors:
        print(str(err), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
