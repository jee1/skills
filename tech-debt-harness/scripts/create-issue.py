#!/usr/bin/env python3
"""기술 부채 항목에 대한 GitHub 이슈를 생성한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _lib import (
    APPROVED_LABEL,
    CATEGORY_KO,
    IN_PROGRESS_LABEL,
    PENDING_LABEL,
    TECH_DEBT_LABEL,
    git_remote_origin,
    load_json,
    run_cmd,
    today_str,
)

CATEGORY_LABELS = {
    "code_debt": "tech-debt/code",
    "architecture_debt": "tech-debt/architecture",
    "test_debt": "tech-debt/test",
    "dependency_debt": "tech-debt/dependency",
    "documentation_debt": "tech-debt/docs",
    "infrastructure_debt": "tech-debt/infra",
}


def render_issue_body(item: dict, audit_path: Path) -> str:
    fp = item.get("fingerprint", "")
    evidence = item.get("evidence") or []
    paths = item.get("affected_paths") or []
    sub_items = item.get("sub_items") or []
    category = str(item.get("category", ""))
    category_label = CATEGORY_KO.get(category, category)
    lines = [
        f"<!-- tech-debt-fingerprint: {fp} -->",
        f"<!-- tech-debt-id: {item.get('id')} -->",
        "",
        "## 요약",
        "",
        str(item.get("description", "")),
        "",
        "## 왜 지금인가",
        "",
        f"- **분류:** `{category}` ({category_label})",
        f"- **우선순위 점수:** {item.get('priority')} = (영향 {item.get('impact')} + 위험 {item.get('risk')}) × (6 - 공수 {item.get('effort')})",
        f"- **비즈니스 근거:** {item.get('business_justification', item.get('suggested_fix', '제안 수정안 참고.'))}",
        "",
        "## 제안 수정안",
        "",
        str(item.get("suggested_fix", "(에이전트가 보완)")),
        "",
        "## 근거",
        "",
    ]
    for ev in evidence[:10]:
        lines.append(f"- {ev}")
    if paths:
        lines.extend(["", "## 영향 경로", ""])
        for p in paths:
            lines.append(f"- `{p}`")
    if sub_items:
        lines.extend(["", "## 하위 항목 (작은 PR로 분할)", ""])
        for sub in sub_items:
            lines.append(f"- **{sub.get('title')}** — {sub.get('description', '')}")
    lines.extend(
        [
            "",
            "## 승인",
            "",
            f"자동 수정·PR 진행이 가능할 때 라벨 `{APPROVED_LABEL}` 을 추가하세요.",
            f"승인 후 `{PENDING_LABEL}` 라벨은 제거하세요.",
            "",
            "## 완료 조건",
            "",
            "- [ ] CI에서 테스트 통과",
            "- [ ] `simplify` 검토 완료 (불필요한 복잡도 없음)",
            "- [ ] PR에 `Fixes #이슈번호` 연결",
            "",
            "## 추적",
            "",
            f"- 감사(audit): `{audit_path}`",
            f"- 생성일: {today_str()}",
        ]
    )
    return "\n".join(lines)


def ensure_labels(workspace: Path, labels: list[str]) -> None:
    label_descriptions = {
        TECH_DEBT_LABEL: "기술 부채 하네스 이슈",
        PENDING_LABEL: "승인 대기 (tech-debt-approved 필요)",
        APPROVED_LABEL: "수정·PR 승인됨",
        IN_PROGRESS_LABEL: "수정 진행 중",
    }
    for label in labels:
        desc = label_descriptions.get(label, "기술 부채")
        run_cmd(
            ["gh", "label", "create", label, "--color", "ededed", "--description", desc, "--force"],
            workspace,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="우선순위 1위 기술 부채를 GitHub 이슈로 등록")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--item-id", help="부채 ID (기본: audit의 top_item_id)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    audit_path = args.audit.resolve()
    if not audit_path.exists():
        print(f"audit 파일 없음: {audit_path}", file=sys.stderr)
        return 1

    origin = git_remote_origin(workspace)
    if not origin and not args.dry_run:
        print("경고: git remote origin 없음", file=sys.stderr)

    audit = load_json(audit_path)
    target_id = args.item_id or audit.get("top_item_id")
    if not target_id:
        print("audit에 top_item_id 없음", file=sys.stderr)
        return 1

    item = next((i for i in audit.get("items") or [] if i.get("id") == target_id), None)
    if not item:
        print(f"항목 없음: {target_id}", file=sys.stderr)
        return 1

    title = f"[기술부채] {item.get('title', target_id)}"
    body = render_issue_body(item, audit_path.relative_to(workspace) if audit_path.is_relative_to(workspace) else audit_path)

    labels = [TECH_DEBT_LABEL, PENDING_LABEL, CATEGORY_LABELS.get(str(item.get("category")), "tech-debt/code")]

    if args.dry_run:
        print(
            "※ DRY RUN — GitHub에 이슈를 만들지 않았습니다. 실제 등록은 --dry-run 없이 실행하세요.\n",
            file=sys.stderr,
        )
        print(json.dumps({"title": title, "labels": labels, "body_preview": body[:500]}, ensure_ascii=False, indent=2))
        print(
            f"\n실제 등록 예:\n  AUDIT={audit_path} python3 .../create-issue.py --workspace {workspace} --audit {audit_path}",
            file=sys.stderr,
        )
        return 0

    ensure_labels(workspace, [TECH_DEBT_LABEL, PENDING_LABEL, APPROVED_LABEL, IN_PROGRESS_LABEL, *CATEGORY_LABELS.values()])

    code, out, err = run_cmd(
        ["gh", "issue", "create", "--title", title, "--body", body, "--label", ",".join(labels)],
        workspace,
    )
    if code != 0:
        print(err or out, file=sys.stderr)
        return 1

    m = re.search(r"/issues/(\d+)", out or "")
    issue_num = int(m.group(1)) if m else None
    print(out.strip())
    if issue_num:
        item["issue_number"] = issue_num
        audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
