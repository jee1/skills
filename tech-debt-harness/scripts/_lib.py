"""Shared helpers for tech-debt harness scripts."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

TECH_DEBT_LABEL = "tech-debt"
PENDING_LABEL = "tech-debt-pending"
APPROVED_LABEL = "tech-debt-approved"
IN_PROGRESS_LABEL = "tech-debt-in-progress"

CATEGORIES = frozenset(
    {
        "code_debt",
        "architecture_debt",
        "test_debt",
        "dependency_debt",
        "documentation_debt",
        "infrastructure_debt",
    }
)

MAX_AUTO_FIX_FILES = 10
MAX_AUTO_FIX_EFFORT = 3

CATEGORY_KO = {
    "code_debt": "코드 부채",
    "architecture_debt": "아키텍처 부채",
    "test_debt": "테스트 부채",
    "dependency_debt": "의존성 부채",
    "documentation_debt": "문서 부채",
    "infrastructure_debt": "인프라 부채",
}


@dataclass
class DebtItem:
    id: str
    fingerprint: str
    category: str
    title: str
    description: str
    evidence: list[str] = field(default_factory=list)
    impact: int = 0
    risk: int = 0
    effort: int = 0
    priority: int = 0
    suggested_fix: str = ""
    affected_paths: list[str] = field(default_factory=list)
    estimated_files: int = 1
    splittable: bool = False
    sub_items: list[dict[str, Any]] = field(default_factory=list)
    issue_number: int | None = None
    status: str = "open"  # open | resolved | skipped

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_priority(impact: int, risk: int, effort: int) -> int:
    impact = max(1, min(5, impact))
    risk = max(1, min(5, risk))
    effort = max(1, min(5, effort))
    return (impact + risk) * (6 - effort)


def make_fingerprint(category: str, title: str, affected_paths: list[str]) -> str:
    payload = "|".join([category.strip().lower(), title.strip().lower(), *sorted(affected_paths)])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def next_debt_id(existing: list[str]) -> str:
    nums = []
    for item_id in existing:
        m = re.match(r"TD-(\d+)$", item_id, re.I)
        if m:
            nums.append(int(m.group(1)))
    n = max(nums, default=0) + 1
    return f"TD-{n:03d}"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return 127, "", str(exc)


def detect_project_kinds(workspace: Path) -> set[str]:
    kinds: set[str] = set()
    if (workspace / "pyproject.toml").exists() or (workspace / "requirements.txt").exists():
        kinds.add("python")
    if (workspace / "package.json").exists():
        kinds.add("node")
    if (workspace / "go.mod").exists():
        kinds.add("go")
    if (workspace / "Cargo.toml").exists():
        kinds.add("rust")
    return kinds or {"generic"}


def git_remote_origin(workspace: Path) -> str | None:
    code, out, _ = run_cmd(["git", "remote", "get-url", "origin"], workspace)
    if code != 0:
        return None
    return out.strip() or None


def today_str() -> str:
    return date.today().isoformat()


ACTIVE_FIX_FILE = ".active-fix.json"


def active_fix_path(workspace: Path) -> Path:
    return workspace / "docs" / "tech-debt" / ACTIVE_FIX_FILE


def slugify_branch(text: str, max_len: int = 48) -> str:
    text = re.sub(r"^\[기술부채\]\s*", "", text, flags=re.I)
    text = re.sub(r"[^a-zA-Z0-9가-힣]+", "-", text).strip("-").lower()
    if not text:
        return "fix"
    # ASCII slug for branch names — take last meaningful segment if path-like
    parts = [p for p in text.split("-") if p]
    if len(parts) > 4:
        parts = parts[-4:]
    slug = "-".join(parts)
    return slug[:max_len].rstrip("-")


def parse_issue_body_meta(body: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for key, pattern in (
        ("fingerprint", r"tech-debt-fingerprint:\s*([a-f0-9]+)"),
        ("td_id", r"tech-debt-id:\s*(TD-\d+)"),
    ):
        m = re.search(pattern, body, re.I)
        if m:
            meta[key] = m.group(1)
    audit_m = re.search(r"감사\(audit\):\s*`([^`]+)`", body)
    if audit_m:
        meta["audit_path"] = audit_m.group(1)
    return meta


def gh_issue_view(workspace: Path, issue: int) -> dict[str, Any] | None:
    code, out, err = run_cmd(
        ["gh", "issue", "view", str(issue), "--json", "number,title,body,labels,state,url"],
        workspace,
    )
    if code != 0:
        print(err or out, file=sys.stderr)
        return None
    return json.loads(out)


def git_default_branch(workspace: Path) -> str:
    code, out, _ = run_cmd(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], workspace)
    if code == 0 and out.strip():
        ref = out.strip().split("/")[-1]
        if ref:
            return ref
    code, out, _ = run_cmd(["gh", "repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"], workspace)
    if code == 0 and out.strip():
        return out.strip()
    return "main"


def detect_scoped_test_command(workspace: Path, affected_paths: list[str]) -> list[str] | None:
    """영향 경로만 검증 — 전체 npm test / monorepo build 회피."""
    if not affected_paths:
        return None

    vitest_suffixes = (".spec.ts", ".spec.tsx", ".test.ts", ".test.tsx")
    vitest_files = [p for p in affected_paths if p.endswith(vitest_suffixes)]
    if vitest_files:
        pkg = workspace / "package.json"
        if pkg.exists():
            try:
                raw = pkg.read_text(encoding="utf-8")
                if "vitest" in raw:
                    return ["npx", "vitest", "run", *vitest_files, "--run"]
            except OSError:
                pass

    jest_suffixes = (".spec.js", ".test.js", ".spec.jsx", ".test.jsx")
    jest_files = [p for p in affected_paths if p.endswith(jest_suffixes)]
    if jest_files:
        pkg = workspace / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                scripts = data.get("scripts") or {}
                if "test" in scripts:
                    return ["npx", "jest", *jest_files]
            except (json.JSONDecodeError, OSError):
                pass

    pytest_files = [
        p
        for p in affected_paths
        if p.endswith(".py") and ("test" in p.lower() or "/tests/" in p.replace("\\", "/"))
    ]
    if pytest_files:
        return ["python3", "-m", "pytest", "-q", *pytest_files]

    return None


def resolve_test_command(
    workspace: Path,
    *,
    affected_paths: list[str] | None = None,
    scope: str = "affected",
    explicit_cmd: str | None = None,
) -> list[str] | None:
    if explicit_cmd:
        return explicit_cmd.split()
    paths = affected_paths or []
    if scope != "full" and paths:
        scoped = detect_scoped_test_command(workspace, paths)
        if scoped:
            return scoped
    return detect_test_command(workspace)


def detect_test_command(workspace: Path) -> list[str] | None:
    candidates: list[list[str]] = []
    if (workspace / "scripts" / "run-tests.sh").is_file():
        candidates.append(["bash", "scripts/run-tests.sh"])
    pkg = workspace / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            scripts = data.get("scripts") or {}
            if "test" in scripts and scripts["test"] and "no test" not in scripts["test"].lower():
                candidates.append(["npm", "test"])
        except json.JSONDecodeError:
            pass
    if (workspace / "pyproject.toml").exists() or (workspace / "pytest.ini").exists():
        candidates.append(["python3", "-m", "pytest", "-q"])
    makefile = workspace / "Makefile"
    if makefile.exists() and re.search(r"^test:", makefile.read_text(encoding="utf-8", errors="replace"), re.M):
        candidates.append(["make", "test"])
    return candidates[0] if candidates else None


def find_audit_item(workspace: Path, fingerprint: str | None, td_id: str | None) -> tuple[Path | None, dict[str, Any] | None]:
    debt_dir = workspace / "docs" / "tech-debt"
    if not debt_dir.is_dir():
        return None, None
    audit_files = sorted(debt_dir.glob("*-audit.json"), reverse=True)
    for path in audit_files:
        if path.name.endswith("-raw-audit.json"):
            continue
        try:
            audit = load_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        for item in audit.get("items") or []:
            if fingerprint and item.get("fingerprint") == fingerprint:
                return path, item
            if td_id and item.get("id") == td_id:
                return path, item
    return None, None
