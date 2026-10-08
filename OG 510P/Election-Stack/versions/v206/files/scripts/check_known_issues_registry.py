#!/usr/bin/env python3
"""scripts/check_known_issues_registry.py

Drift firewall for the "known issues" registry.

Purpose:
- Provide a stable, low-bloat format for publishing a public-facing "known issues" list
  and patch/mitigation status.
- Prevent silent schema drift in the CSV format.

Validates:
- registry exists and has required headers
- issue_id uniqueness and basic format
- status is from a small allowed set
- refs (if present) point to real files in the repo
- first_reported (if present) is YYYY-MM-DD

Note: The registry may be empty (headers only).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _shared.registry import read_csv, require_headers, split_semicolon

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "known-issues.csv"

RE_ID = re.compile(r"^[A-Za-z0-9_-]+$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_STATUS = {
    "open",
    "mitigated",
    "fixed",
    "won_t_fix",
    "false_positive",
}


def main() -> int:
    if not REGISTRY.exists():
        print(f"ERROR: missing registry: {REGISTRY}", file=sys.stderr)
        return 2

    tbl = read_csv(REGISTRY)
    required_headers = {
        "issue_id",
        "status",
        "component",
        "summary",
        "first_reported",
        "public_notice_id",
        "fixed_in",
        "mitigation",
        "refs",
        "notes",
    }

    missing = require_headers(tbl, required_headers)
    if missing:
        print(f"ERROR: {REGISTRY} missing headers: {missing}", file=sys.stderr)
        return 2

    seen: set[str] = set()
    any_fail = False

    for i, r in enumerate(tbl.rows, start=2):

            iid = r.get("issue_id", "")
            if not iid or not RE_ID.match(iid):
                any_fail = True
                print(f"ERROR:{REGISTRY}:{i}: invalid issue_id '{iid}'", file=sys.stderr)
            if iid in seen:
                any_fail = True
                print(f"ERROR:{REGISTRY}:{i}: duplicate issue_id '{iid}'", file=sys.stderr)
            seen.add(iid)

            status = r.get("status", "")
            if status and status not in ALLOWED_STATUS:
                any_fail = True
                print(
                    f"ERROR:{REGISTRY}:{i}: invalid status '{status}' (allowed: {sorted(ALLOWED_STATUS)})",
                    file=sys.stderr,
                )

            first = r.get("first_reported", "")
            if first and not RE_DATE.match(first):
                any_fail = True
                print(f"ERROR:{REGISTRY}:{i}: first_reported must be YYYY-MM-DD, got '{first}'", file=sys.stderr)

            for p in split_semicolon(r.get("refs", "")):
                path = ROOT / p
                if not path.exists():
                    any_fail = True
                    print(f"ERROR:{REGISTRY}:{i}: missing refs path '{p}'", file=sys.stderr)

    if any_fail:
        return 2

    print("OK known-issues registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
