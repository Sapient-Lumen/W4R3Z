#!/usr/bin/env python3
"""scripts/check_public_notice_type_coherence.py

Drift firewall: keep PublicNotice.notice_type enum coherent with PublicNoticeFeed entry metadata.

Rationale:
- PublicNoticeFeed entries optionally copy notice_type to aid sorting/rendering.
- If the feed enum cannot represent a valid PublicNotice type, schemas diverge and
  operators are forced into lossy or invalid feeds.

Policy:
- PublicNoticeFeed.entries[].notice_type.enum MUST be a superset of PublicNotice.notice_type.enum.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise SystemExit(f"Not a JSON object: {path}")
    return obj


def _get_enum(schema: dict, path: str) -> list[str]:
    cur = schema
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise SystemExit(f"Missing schema path: {path}")
        cur = cur[part]
    if not isinstance(cur, list) or not all(isinstance(x, str) for x in cur):
        raise SystemExit(f"Enum at {path} is not a list[str]")
    return cur


def main() -> int:
    pn = _load(ROOT / "schemas" / "PublicNotice.json")
    pnf = _load(ROOT / "schemas" / "PublicNoticeFeed.json")

    pn_enum = _get_enum(pn, "properties.notice_type.enum")
    pnf_enum = _get_enum(
        pnf,
        "properties.entries.items.properties.notice_type.enum",
    )

    missing = [t for t in pn_enum if t not in pnf_enum]
    if missing:
        print("FAIL PublicNoticeFeed schema missing PublicNotice notice_type values:")
        for t in missing:
            print(f"- {t}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
