#!/usr/bin/env python3
"""Fail closed on state/local xrefs that look like live voter instructions.

rev0868 quarantined mutable state/local source rows as example/routing xrefs.
This checker keeps that boundary useful by rejecting two regressions:

1. quarantined state/local lockfile rows that lose the explicit
   "not current voter instruction" boundary or move back inside the 30-day
   source-review pressure window; and
2. markdown lines that cite unpinned state/local `xref:` IDs while describing
   the cited page as "current" without an explicit non-instruction boundary.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import tomllib
from pathlib import Path

from _shared.current_authority import lane_for, review_by_date, tags_of

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from release_context import release_date as archive_release_date
DEFAULT_RELEASE_DATE = archive_release_date(ROOT)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
XREF_RE = re.compile(r"xref:\s*`([^`]+)`")
CURRENT_RE = re.compile(r"\bcurrent\b", re.I)
BOUNDARY_RE = re.compile(r"not\s+current\s+voter\s+instruction", re.I)


def is_pinned(row: dict) -> bool:
    return bool(HEX64_RE.fullmatch(str(row.get("sha256") or "").strip()))


def load_rows() -> list[dict]:
    with LOCK.open("rb") as f:
        return tomllib.load(f).get("source", [])


def markdown_paths() -> list[Path]:
    roots = [ROOT / "docs", ROOT / "artifacts"]
    paths: list[Path] = []
    for root in roots:
        if root.exists():
            paths.extend(p for p in root.rglob("*.md") if p.is_file())
    return sorted(paths)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=os.environ.get("ELECTION_STACK_SOURCE_REVIEW_DATE", DEFAULT_RELEASE_DATE))
    ap.add_argument("--minimum-days", type=int, default=30)
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)
    minimum_review_by = release_date + dt.timedelta(days=int(args.minimum_days))

    rows = load_rows()
    by_id = {str(r.get("id") or ""): r for r in rows}
    state_local_unpinned = {
        sid: row for sid, row in by_id.items()
        if sid and not is_pinned(row) and lane_for(row) == "state_or_local_authority"
    }

    failures: list[str] = []
    quarantined = 0
    for sid, row in sorted(state_local_unpinned.items()):
        tags = tags_of(row)
        if "jurisdiction_quarantine" in tags:
            quarantined += 1
            note = str(row.get("note") or "")
            if not BOUNDARY_RE.search(note):
                failures.append(f"{sid}: quarantined row note is missing 'not current voter instruction' boundary")
            rb = review_by_date(row)
            if rb is None:
                failures.append(f"{sid}: quarantined row is missing parseable review_by")
            elif rb <= minimum_review_by:
                failures.append(
                    f"{sid}: quarantined row review_by={rb} is still inside "
                    f"{args.minimum_days}d pressure window ending {minimum_review_by}"
                )

    for path in markdown_paths():
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            cited = {m.group(1) for m in XREF_RE.finditer(line)} & set(state_local_unpinned)
            if not cited:
                continue
            if CURRENT_RE.search(line) and not BOUNDARY_RE.search(line):
                failures.append(
                    f"{rel}:{lineno}: state/local xref(s) {', '.join(sorted(cited))} use 'current' without a non-instruction boundary"
                )

    if failures:
        print(f"FAIL: state/local xref quarantine regression(s) found: {len(failures)}")
        for item in failures[:80]:
            print(f"- {item}")
        return 2
    print(
        f"PASS: state/local xref quarantine holds "
        f"({len(state_local_unpinned)} unpinned state/local rows, {quarantined} quarantined, "
        f"minimum_review_by_after={minimum_review_by})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
