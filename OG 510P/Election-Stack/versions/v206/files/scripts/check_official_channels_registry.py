#!/usr/bin/env python3
"""scripts/check_official_channels_registry.py

Drift firewall for the official communications channels registry.

Why this exists:
- Track A assumes adversaries can forge screenshots and "official" statements.
- Verifiers need a canonical list of where a jurisdiction *claims* to publish official updates.
- Operators need a bounded, auditable surface that can be mirrored and monitored.

This check enforces a small, stable CSV schema and basic hygiene.

Validates:
- registry exists and has required headers
- channel_id uniqueness + basic format
- channel_type from a small allowed set
- url is either empty, a http(s) URL, or a mailto: URL
- last_verified (if present) matches YYYY-MM-DD

Note: The registry is a template; placeholder values are allowed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _shared.registry import read_csv, require_headers

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "official-channels.csv"

RE_ID = re.compile(r"^[a-z0-9_]+$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_TYPES = {
    "website",
    "status_page",
    "press_release",
    "social",
    "email",
    "sms",
    "rss",
    "other",
}


def main() -> int:
    if not REGISTRY.exists():
        print(f"ERROR: missing registry: {REGISTRY}", file=sys.stderr)
        return 2

    tbl = read_csv(REGISTRY)
    required_headers = {
        "channel_id",
        "channel_type",
        "identifier",
        "url",
        "owner_org",
        "verification_method",
        "commitment_hint",
        "last_verified",
        "notes",
    }
    missing = require_headers(tbl, required_headers)
    if missing:
        print(f"ERROR: {REGISTRY} missing headers: {missing}", file=sys.stderr)
        return 2

    seen: set[str] = set()
    any_fail = False

    for i, r in enumerate(tbl.rows, start=2):

        cid = r.get("channel_id", "")
        if not cid or not RE_ID.match(cid):
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: invalid channel_id '{cid}'", file=sys.stderr)
        if cid in seen:
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: duplicate channel_id '{cid}'", file=sys.stderr)
        seen.add(cid)

        ctype = r.get("channel_type", "")
        if ctype and ctype not in ALLOWED_TYPES:
            any_fail = True
            print(
                f"ERROR:{REGISTRY}:{i}: invalid channel_type '{ctype}' (allowed: {sorted(ALLOWED_TYPES)})",
                file=sys.stderr,
            )

        url = r.get("url", "")
        if url and not (url.startswith("https://") or url.startswith("http://") or url.startswith("mailto:")):
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: url must be http(s) or mailto, got '{url}'", file=sys.stderr)

        last = r.get("last_verified", "")
        if last and not RE_DATE.match(last):
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: last_verified must be YYYY-MM-DD, got '{last}'", file=sys.stderr)

    if any_fail:
        return 2

    print("OK official-channels registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
