#!/usr/bin/env python3
"""대상 워크스페이스에서 정적 분석을 실행하고 raw findings JSON을 출력한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _lib import detect_project_kinds, make_fingerprint, next_debt_id, run_cmd, today_str

FINDING = dict[str, object]


def _add(
    findings: list[FINDING],
    *,
    category: str,
    title: str,
    description: str,
    evidence: list[str],
    affected_paths: list[str],
    source: str,
) -> None:
    findings.append(
        {
            "category": category,
            "title": title,
            "description": description,
            "evidence": evidence,
            "affected_paths": affected_paths,
            "source": source,
            "fingerprint": make_fingerprint(category, title, affected_paths),
        }
    )


def _scan_todos(workspace: Path) -> list[FINDING]:
    findings: list[FINDING] = []
    pattern = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.I)
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "venv", "dist", "build"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".js", ".ts", ".tsx", ".go", ".rs", ".md", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = [line.strip() for line in text.splitlines() if pattern.search(line)]
        if len(hits) < 5:
            continue
        rel = str(path.relative_to(workspace))
        _add(
            findings,
            category="code_debt",
            title=f"{rel}에 TODO/FIXME 과다",
            description=f"TODO/FIXME 마커 {len(hits)}개 — 미뤄진 작업이 누적됨.",
            evidence=hits[:5],
            affected_paths=[rel],
            source="todo-scan",
        )
    return findings


def _run_ruff(workspace: Path) -> list[FINDING]:
    findings: list[FINDING] = []
    code, out, err = run_cmd(["ruff", "check", ".", "--output-format", "json"], workspace)
    if code == 127:
        return findings
    raw = out or err
    if not raw.strip():
        return findings
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        if code != 0 and raw.strip():
            _add(
                findings,
                category="code_debt",
                title="Ruff 린트 위반",
                description="전체 출력: `ruff check .` 실행.",
                evidence=raw.splitlines()[:10],
                affected_paths=[],
                source="ruff",
            )
        return findings
    by_file: dict[str, int] = {}
    for item in data:
        filename = str(item.get("filename", ""))
        by_file[filename] = by_file.get(filename, 0) + 1
    for filename, count in sorted(by_file.items(), key=lambda x: -x[1])[:5]:
        rel = filename
        try:
            rel = str(Path(filename).relative_to(workspace))
        except ValueError:
            pass
        _add(
            findings,
            category="code_debt",
            title=f"{rel} Ruff 린트 위반",
            description=f"이 파일에서 ruff 위반 {count}건.",
            evidence=[f"ruff: {count} issues"],
            affected_paths=[rel],
            source="ruff",
        )
    return findings


def _run_pip_audit(workspace: Path) -> list[FINDING]:
    findings: list[FINDING] = []
    req = workspace / "requirements.txt"
    if not req.exists():
        return findings
    code, out, err = run_cmd(["pip-audit", "-r", str(req), "--format", "json"], workspace)
    if code == 127:
        code, out, err = run_cmd(["pip", "list", "--outdated", "--format", "json"], workspace)
        if code != 0:
            return findings
        try:
            pkgs = json.loads(out or "[]")
        except json.JSONDecodeError:
            return findings
        for pkg in pkgs[:10]:
            name = pkg.get("name", "unknown")
            _add(
                findings,
                category="dependency_debt",
                title=f"구버전 Python 패키지: {name}",
                description=f"현재 {pkg.get('version')} → 최신 {pkg.get('latest_version')}",
                evidence=[json.dumps(pkg, ensure_ascii=False)],
                affected_paths=["requirements.txt"],
                source="pip-list-outdated",
            )
        return findings
    try:
        data = json.loads(out or "{}")
    except json.JSONDecodeError:
        return findings
    vulns = data.get("dependencies", data) if isinstance(data, dict) else data
    if isinstance(vulns, list):
        for dep in vulns[:15]:
            name = dep.get("name", "unknown")
            _add(
                findings,
                category="dependency_debt",
                title=f"취약 의존성: {name}",
                description="pip-audit이 알려진 취약점을 보고함.",
                evidence=[json.dumps(dep, ensure_ascii=False)[:500]],
                affected_paths=["requirements.txt"],
                source="pip-audit",
            )
    return findings


def _run_npm_audit(workspace: Path) -> list[FINDING]:
    findings: list[FINDING] = []
    if not (workspace / "package.json").exists():
        return findings
    code, out, err = run_cmd(["npm", "audit", "--json"], workspace, timeout=180)
    if code == 127:
        return findings
    try:
        data = json.loads(out or err or "{}")
    except json.JSONDecodeError:
        return findings
    advisories = data.get("vulnerabilities") or {}
    for name, info in list(advisories.items())[:15]:
        severity = info.get("severity", "unknown")
        _add(
            findings,
            category="dependency_debt",
            title=f"npm audit: {name} ({severity})",
            description=str(info.get("via", info))[:300],
            evidence=[f"severity={severity}"],
            affected_paths=["package.json"],
            source="npm-audit",
        )
    return findings


def _scan_missing_readme(workspace: Path) -> list[FINDING]:
    findings: list[FINDING] = []
    if not (workspace / "README.md").exists():
        _add(
            findings,
            category="documentation_debt",
            title="루트 README.md 없음",
            description="저장소 루트에 README가 없어 온보딩·사용법이 문서화되지 않음.",
            evidence=["README.md 없음"],
            affected_paths=[],
            source="doc-scan",
        )
    return findings


def _scan_test_layout(workspace: Path, kinds: set[str]) -> list[FINDING]:
    findings: list[FINDING] = []
    if "python" not in kinds:
        return findings
    has_tests = any(workspace.rglob("test_*.py")) or any(workspace.rglob("tests"))
    has_py = any(workspace.rglob("*.py"))
    if has_py and not has_tests:
        _add(
            findings,
            category="test_debt",
            title="테스트 파일 없는 Python 프로젝트",
            description="test_*.py 또는 tests/ 디렉터리가 없음.",
            evidence=["테스트 없음"],
            affected_paths=[],
            source="test-scan",
        )
    return findings


def collect_raw_findings(workspace: Path) -> list[FINDING]:
    kinds = detect_project_kinds(workspace)
    findings: list[FINDING] = []
    findings.extend(_scan_missing_readme(workspace))
    findings.extend(_scan_test_layout(workspace, kinds))
    findings.extend(_scan_todos(workspace))
    if "python" in kinds:
        findings.extend(_run_ruff(workspace))
        findings.extend(_run_pip_audit(workspace))
    if "node" in kinds:
        findings.extend(_run_npm_audit(workspace))
    # dedupe by fingerprint
    seen: set[str] = set()
    unique: list[FINDING] = []
    for item in findings:
        fp = str(item["fingerprint"])
        if fp in seen:
            continue
        seen.add(fp)
        unique.append(item)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="현재 워크스페이스 정적 기술 부채 감사")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="대상 레포 루트")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write raw findings JSON (default: docs/tech-debt/<date>-raw-audit.json)",
    )
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"워크스페이스 없음: {workspace}", file=sys.stderr)
        return 1

    findings = collect_raw_findings(workspace)
    out_path = args.output or workspace / "docs" / "tech-debt" / f"{today_str()}-raw-audit.json"
    payload = {
        "generated_at": today_str(),
        "workspace": str(workspace),
        "finding_count": len(findings),
        "findings": findings,
        "next_id_hint": next_debt_id([]),
        "agent_note": (
            "에이전트가 impact/risk/effort/suggested_fix 를 채운 점수화 audit로 enrichment 한 뒤 "
            "prioritize.py 실행. tech-debt-harness/SKILL.md Phase 2 참고. title/description 등은 한글 권장."
        ),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"raw finding {len(findings)}건 → {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
