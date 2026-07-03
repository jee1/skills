#!/usr/bin/env python3
"""Check whether a tech-debt issue has the approval label."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _lib import APPROVED_LABEL, PENDING_LABEL, run_cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify tech-debt-approved label on issue")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--issue", type=int, required=True)
    args = parser.parse_args()

    code, out, err = run_cmd(
        ["gh", "issue", "view", str(args.issue), "--json", "number,title,labels,state"],
        args.workspace.resolve(),
    )
    if code != 0:
        print(err or out, file=sys.stderr)
        return 1

    data = json.loads(out)
    labels = {lbl["name"] for lbl in data.get("labels") or []}
    approved = APPROVED_LABEL in labels
    pending = PENDING_LABEL in labels

    print(
        json.dumps(
            {
                "issue": data.get("number"),
                "state": data.get("state"),
                "approved": approved,
                "pending": pending,
                "labels": sorted(labels),
            },
            ensure_ascii=False,
        )
    )
    return 0 if approved else 2


if __name__ == "__main__":
    raise SystemExit(main())
