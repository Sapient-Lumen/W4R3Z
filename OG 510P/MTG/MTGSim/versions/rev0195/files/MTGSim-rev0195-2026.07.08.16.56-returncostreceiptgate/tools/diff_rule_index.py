#!/usr/bin/env python3
"""Diff two metadata-only rule indexes produced by extract_rule_index.py."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from typing import Any

# Reports should use the project/user timezone for readable revision artifacts.
os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()


def load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def by_id(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["rule_id"]: entry for entry in index.get("rules", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=pathlib.Path)
    parser.add_argument("new", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args()

    old = by_id(load(args.old))
    new = by_id(load(args.new))
    old_ids = set(old)
    new_ids = set(new)
    changed = sorted(rule_id for rule_id in old_ids & new_ids if old[rule_id].get("paragraph_sha256") != new[rule_id].get("paragraph_sha256"))
    report = {
        "schema": "mtgsim.rule_index_diff.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "old": str(args.old),
        "new": str(args.new),
        "summary": {
            "added": len(new_ids - old_ids),
            "removed": len(old_ids - new_ids),
            "changed": len(changed),
        },
        "added": sorted(new_ids - old_ids),
        "removed": sorted(old_ids - new_ids),
        "changed": changed,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"rule diff -> {args.out}")
    else:
        print(text)
    return 0 if not (new_ids - old_ids or old_ids - new_ids or changed) else 2


if __name__ == "__main__":
    raise SystemExit(main())
