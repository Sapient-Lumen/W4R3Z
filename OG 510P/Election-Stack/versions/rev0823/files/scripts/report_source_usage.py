#!/usr/bin/env python3
"""scripts/report_source_usage.py

Small maintainer helper: show how external source IDs are used across the repo.

This is intentionally non-blocking (exit 0) and does not fetch network resources.
Use it during reviews to keep the lockfile lean and to spot stale sources.

Usage:
  python3 scripts/report_source_usage.py
  python3 scripts/report_source_usage.py --json
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from _shared.md_scan import iter_markdown_files
from _shared.source_refs import iter_source_refs_in_line

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"


def parse_lock_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for m in re.finditer(r'(?m)^id\s*=\s*"([^"]+)"\s*$', text):
        ids.add(m.group(1).strip())
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(description="Report usage of external source IDs")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}", file=sys.stderr)
        return 2

    lock_text = LOCK.read_text(encoding="utf-8")
    lock_ids = parse_lock_ids(lock_text)

    files: list[Path] = iter_markdown_files(ROOT)

    uses = defaultdict(list)  # id -> [path:line]
    for p in files:
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, start=1):
            for ref in iter_source_refs_in_line(line, i):
                cid = ref.source_id
                uses[cid].append(f"{p.relative_to(ROOT)}:{i}")

    unused = sorted(lock_ids - set(uses.keys()))
    unknown = sorted(set(uses.keys()) - lock_ids)

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "lock_ids": sorted(lock_ids),
                    "usage": {k: v for k, v in sorted(uses.items())},
                    "unused_lock_ids": unused,
                    "unknown_citations": unknown,
                },
                indent=2,
            )
        )
        return 0

    print(f"Lockfile sources: {len(lock_ids)}")
    print(f"Cited sources:    {len(set(uses.keys()))}")
    print()

    if unknown:
        print("UNKNOWN CITATIONS (not in lockfile):")
        for cid in unknown:
            print(f"  - {cid} ({len(uses[cid])} refs)")
        print()

    if unused:
        print("UNUSED LOCKFILE IDS (not currently cited):")
        for cid in unused:
            print(f"  - {cid}")
        print()

    # Top used IDs (small)
    top = sorted(((cid, len(refs)) for cid, refs in uses.items() if cid in lock_ids), key=lambda x: (-x[1], x[0]))
    if top:
        print("TOP USED SOURCES:")
        for cid, n in top[:12]:
            print(f"  - {cid}: {n}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
