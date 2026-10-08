#!/usr/bin/env python3
"""Fail if unpinned current-authority sources are expired or due inside the near-term release cliff.

This is narrower than the full source lockfile checker. It catches election/cyber/
accessibility/current-authority rows whose review windows already expired or are about to expire,
without forcing maintainers to linearly review the much larger platform/UI tail.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import tomllib
from pathlib import Path

from _shared.current_authority import is_current_authority, is_due_soon, is_expired

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from release_context import release_date as archive_release_date
DEFAULT_RELEASE_DATE = archive_release_date(ROOT)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"


def load_rows() -> list[dict]:
    with LOCK.open("rb") as f:
        return tomllib.load(f).get("source", [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=os.environ.get("ELECTION_STACK_SOURCE_REVIEW_DATE", DEFAULT_RELEASE_DATE))
    ap.add_argument("--horizon-days", type=int, default=30)
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)
    horizon = int(args.horizon_days)
    current_authority = [r for r in load_rows() if is_current_authority(r)]

    expired = [r for r in current_authority if is_expired(r, release_date)]
    due = [r for r in current_authority if is_due_soon(r, release_date, horizon)]
    if expired or due:
        if expired:
            print(f"ERROR: {len(expired)} unpinned current-authority source review window(s) expired before {release_date}")
            for r in sorted(expired, key=lambda r: (str(r.get('review_by') or ''), str(r.get('id') or '')))[:40]:
                print(f"- expired {r.get('id')} review_by={r.get('review_by')} url={r.get('url')}")
        if due:
            print(f"ERROR: {len(due)} unpinned current-authority source review window(s) due by {release_date + dt.timedelta(days=horizon)}")
            for r in sorted(due, key=lambda r: (str(r.get('review_by') or ''), str(r.get('id') or '')))[:40]:
                print(f"- due {r.get('id')} review_by={r.get('review_by')} url={r.get('url')}")
        return 2
    print(f"PASS: no unpinned current-authority source review windows expired before or due by {release_date + dt.timedelta(days=horizon)} (review date {release_date}, horizon {horizon}d)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
