#!/usr/bin/env python3
"""Report the near-term current-authority source-review queue.

This is the companion to the platform-tail report. It keeps maintainers from
burning time on mutable platform support pages before the smaller but riskier
set of election/cyber/current-authority references is reviewed, pinned, or
explicitly demoted.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import re
import tomllib
from collections import Counter, defaultdict
from pathlib import Path

from _shared.current_authority import (
    host_of,
    is_current_authority,
    is_due_soon,
    is_expired,
    is_pin_first_candidate,
    lane_for,
    review_status,
    tags_of,
)

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
VERSION_FILE = ROOT / "VERSION"
VERSION_NUM = VERSION_FILE.read_text(encoding="utf-8").strip().removeprefix("v").zfill(4)
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from release_context import release_date as archive_release_date
DEFAULT_RELEASE_DATE = archive_release_date(ROOT)

BOUNDARY = (
    "Current-authority source queue reports are maintainer triage only. They do not refresh sources, "
    "prove current voter instructions, prove current law, or authorize live-pilot or legal reliance."
)


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_rows() -> list[dict]:
    with LOCK.open("rb") as f:
        return tomllib.load(f).get("source", [])


def suggested_action(row: dict) -> str:
    url = str(row.get("url") or "")
    host = host_of(url)
    note = str(row.get("note") or "").lower()
    if str(row.get("pin_exemption") or "").strip():
        return "Re-check the blocked/exempt route; pin bytes if accessible, otherwise keep the exemption explicit and do not promote as fresh voter instruction."
    if is_pin_first_candidate(row):
        return "Attempt byte pin first; if the content has moved, update URL and note rather than extending review_by blindly."
    if host.endswith(("eac.gov", "cisa.gov", "nist.gov", "csrc.nist.gov", "tsapps.nist.gov", "justice.gov", "vote.gov")):
        return "Review current page and prefer a versioned/pinned canonical artifact when available; cite landing pages only as current-routing surfaces."
    if "re-reviewed" in note:
        return "Verify that the re-review note still reflects a current authoritative route; replace with pinned/source-specific artifact where possible."
    return "Review for currentness, pin if durable bytes exist, or demote if only background context."


def summarize(rows: list[dict], release_date: dt.date, horizon_days: int) -> tuple[list[dict], dict]:
    attention = [
        r for r in rows
        if is_current_authority(r) and (is_expired(r, release_date) or is_due_soon(r, release_date, horizon_days))
    ]
    by_lane: dict[str, list[dict]] = defaultdict(list)
    for row in attention:
        by_lane[lane_for(row)].append(row)

    table: list[dict] = []
    for lane, items in sorted(by_lane.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        hosts = Counter(host_of(str(r.get("url") or "")) for r in items)
        tags = Counter(t for r in items for t in tags_of(r))
        statuses = Counter(review_status(r, release_date, horizon_days) for r in items)
        dates = sorted({str(r.get("review_by") or "") for r in items if r.get("review_by")})
        examples = sorted(items, key=lambda r: (str(r.get("review_by") or "9999-12-31"), str(r.get("id") or "")))[:20]
        table.append({
            "lane": lane,
            "due_count": len(items),
            "expired_count": statuses.get("expired", 0),
            "due_soon_count": statuses.get("due_soon", 0),
            "earliest_review_by": dates[0] if dates else "",
            "latest_review_by": dates[-1] if dates else "",
            "top_hosts": "; ".join(f"{h}={c}" for h, c in hosts.most_common(8) if h),
            "top_tags": "; ".join(f"{t}={c}" for t, c in tags.most_common(12)),
            "status_counts": "; ".join(f"{s}={c}" for s, c in statuses.most_common()),
            "example_source_ids": "; ".join(str(r.get("id") or "") for r in examples),
            "recommended_action": suggested_action(examples[0]) if examples else "Review for currentness.",
            "boundary": BOUNDARY,
        })

    expired_count = sum(1 for r in attention if is_expired(r, release_date))
    due_soon_count = sum(1 for r in attention if is_due_soon(r, release_date, horizon_days))
    by_host = Counter(host_of(str(r.get("url") or "")) for r in attention)
    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    summary = {
        "archive_version": version,
        "release_date": release_date.isoformat(),
        "horizon_days": horizon_days,
        "current_authority_due_count": len(attention),
        "current_authority_expired_count": expired_count,
        "current_authority_due_soon_count": due_soon_count,
        "lane_counts": {lane: len(items) for lane, items in sorted(by_lane.items())},
        "top_hosts": by_host.most_common(25),
        "rows": table,
        "boundary": BOUNDARY,
        "recommended_next_move": "Review current-authority rows before platform/UI rows. Pin durable bytes when possible; do not extend review_by dates without a currentness note or demotion decision.",
    }
    return table, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=DEFAULT_RELEASE_DATE)
    ap.add_argument("--horizon-days", type=int, default=30)
    ap.add_argument("--csv", default=f"artifacts/reports/current-authority-source-queue-rev{VERSION_NUM}.csv")
    ap.add_argument("--json", default=f"artifacts/reports/current-authority-source-queue-rev{VERSION_NUM}.json")
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)
    table, summary = summarize(load_rows(), release_date, int(args.horizon_days))
    csv_path = ROOT / args.csv
    json_path = ROOT / args.json
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["lane", "due_count", "expired_count", "due_soon_count", "earliest_review_by", "latest_review_by", "top_hosts", "top_tags", "status_counts", "example_source_ids", "recommended_action", "boundary"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in table:
            w.writerow(row)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {display_path(csv_path)}")
    print(f"WROTE {display_path(json_path)}")
    print(f"current_authority_due={summary['current_authority_due_count']} expired={summary['current_authority_expired_count']} due_soon={summary['current_authority_due_soon_count']} lanes={len(summary['lane_counts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
