#!/usr/bin/env python3
"""scripts/check_election_milestones_registry.py

Drift firewall for the election milestones registry.

Why this exists:
- Track A treats institutional milestones (canvass/certification/recount) as a legitimacy surface.
- Verifiers/monitors need a small, canonical vocabulary so milestone notices are comparable.
- Operators need a bounded set of IDs that can be mirrored and parity-checked.

Validates:
- registry exists and has required headers
- milestone_id uniqueness + basic format
- category from a small allowed set
- stable is either yes/no (or empty for template rows)

Note: The registry is a template; placeholder values are allowed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _shared.registry import read_csv, require_headers

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "election-milestones.csv"

RE_ID = re.compile(r"^[a-z0-9_]+$")

ALLOWED_CATEGORIES = {
    "process",
    "outcome",
    "remedy",
    "other",
}

ALLOWED_STABLE = {"", "yes", "no"}


def main() -> int:
    if not REGISTRY.exists():
        print(f"ERROR: missing registry: {REGISTRY}", file=sys.stderr)
        return 2

    tbl = read_csv(REGISTRY)
    required_headers = {"milestone_id", "category", "stable", "description", "notes"}
    missing = require_headers(tbl, required_headers)
    if missing:
        print(f"ERROR: {REGISTRY} missing headers: {missing}", file=sys.stderr)
        return 2

    seen: set[str] = set()
    any_fail = False

    for i, r in enumerate(tbl.rows, start=2):
        mid = r.get("milestone_id", "")
        if not mid or not RE_ID.match(mid):
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: invalid milestone_id '{mid}'", file=sys.stderr)
        if mid in seen:
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: duplicate milestone_id '{mid}'", file=sys.stderr)
        seen.add(mid)

        cat = r.get("category", "")
        if cat and cat not in ALLOWED_CATEGORIES:
            any_fail = True
            print(
                f"ERROR:{REGISTRY}:{i}: invalid category '{cat}' (allowed: {sorted(ALLOWED_CATEGORIES)})",
                file=sys.stderr,
            )

        stable = r.get("stable", "")
        if stable not in ALLOWED_STABLE:
            any_fail = True
            print(
                f"ERROR:{REGISTRY}:{i}: stable must be yes/no/empty, got '{stable}'",
                file=sys.stderr,
            )

    if any_fail:
        return 2

    print("OK election-milestones registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
