#!/usr/bin/env python3
"""Reject releases that accidentally bloat the archive.

This is a size-discipline tripwire, not a performance benchmark.

Defaults:
- max single file: 1 MiB
- max total tracked bytes: 5 MiB

The limits are intentionally conservative for this spec pack.
Override with flags if you have a justified reason, and record it as an ADR.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
}

# These should be empty in releases, but we exclude them from size accounting so local
# operator caches cannot trip the budget.
EXCLUDE_PREFIXES = {
    "evidence/cache/",
    # Local release zips / build outputs.
    "dist/",
}


def should_skip(p: Path) -> bool:
    rel = p.relative_to(ROOT).as_posix()
    if any(rel.startswith(pref) for pref in EXCLUDE_PREFIXES):
        return True
    parts = rel.split("/")
    return any(part in EXCLUDE_DIRS for part in parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-file-bytes", type=int, default=1_048_576)
    ap.add_argument("--max-total-bytes", type=int, default=5_242_880)  # 5 MiB
    args = ap.parse_args()

    total = 0
    worst = (Path("."), 0)
    offenders = []

    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if should_skip(p):
            continue
        sz = p.stat().st_size
        total += sz
        if sz > worst[1]:
            worst = (p, sz)
        if sz > args.max_file_bytes:
            offenders.append((p, sz))

    if offenders:
        print("ERROR: file(s) exceed max-file-bytes", file=sys.stderr)
        for p, sz in sorted(offenders, key=lambda x: x[1], reverse=True):
            rel = p.relative_to(ROOT)
            print(f"  {rel} {sz} bytes", file=sys.stderr)
        return 2

    if total > args.max_total_bytes:
        rel = worst[0].relative_to(ROOT)
        print(
            f"ERROR: total bytes {total} exceed max-total-bytes {args.max_total_bytes}. "
            f"Largest file: {rel} ({worst[1]} bytes)",
            file=sys.stderr,
        )
        return 2

    print(f"PASS: size budget (total={total} bytes; max_file={worst[0].relative_to(ROOT)}:{worst[1]} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
