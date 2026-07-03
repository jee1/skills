"""Shared helpers for tech-debt harness scripts."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
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
