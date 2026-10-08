#!/usr/bin/env python3
"""Generate a grouped current-authority source burndown batch report.

This is a maintainer refactor helper, not a network refresher.  It turns the
near-term current-authority source queue into host/lane batches so maintainers
can review durable official sources before spending time on the platform/UI tail.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import tomllib
from collections import Counter, defaultdict
from pathlib import Path

from _shared.current_authority import (
    dominant_topic,
    host_of,
    is_current_authority,
    is_due_soon,
    is_pin_first_candidate,
    lane_for,
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
    "Grouped current-authority burndown batches are maintainer triage only. They do not refresh sources, "
    "prove current voter instructions, prove current law, or authorize live-pilot/legal reliance."
)


def load_rows() -> list[dict]:
    with LOCK.open("rb") as f:
        return tomllib.load(f).get("source", [])


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def action_for(lane: str, host: str, rows: list[dict]) -> str:
    if lane == "state_or_local_authority":
        return "Review jurisdiction pages/PDFs for currentness; pin durable PDFs first; never generalize one state page into national voter guidance."
    if host.endswith("eac.gov"):
        return "Review EAC pages in one official-source sweep; prefer PDFs/versioned resources when available and demote mutable landing pages to current-routing surfaces."
    if host.endswith(("cisa.gov", "get.gov")):
        return "Review CISA/get.gov pages as a cyber/official-domain sweep; pin PDFs where possible and keep HTML pages on bounded review windows."
    if host.endswith(("nist.gov", "csrc.nist.gov", "tsapps.nist.gov")):
        return "Prefer versioned NIST publications and pinned PDFs/HTML snapshots; keep draft/current landing pages separate from final standards."
    if host.endswith(("ada.gov", "justice.gov", "section508.gov")):
        return "Review accessibility/rights pages together; separate legal-rights guidance from implementation tutorials."
    if host.endswith(("vote.gov", "nass.org", "canivote.org")):
        return "Review voter-information routing pages as current pointers only; do not reuse them as jurisdiction-specific instructions."
    return "Review as current authority; pin durable bytes or demote to background/context where no stable artifact exists."


def summarize(rows: list[dict], release_date: dt.date, horizon_days: int) -> tuple[list[dict], dict]:
    due = [r for r in rows if is_due_soon(r, release_date, horizon_days) and is_current_authority(r)]
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for r in due:
        lane = lane_for(r)
        host = host_of(str(r.get("url") or ""))
        topic = dominant_topic(r)
        # Keep EAC/CISA/state pages batchable by host, but split very large hosts by topic.
        key = (lane, host, topic if host in {"eac.gov", "cisa.gov", "section508.gov", "vote.gov", "csrc.nist.gov", "tsapps.nist.gov"} else "mixed")
        grouped[key].append(r)

    table: list[dict] = []
    for i, ((lane, host, topic), items) in enumerate(sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0])), start=1):
        dates = sorted({str(r.get("review_by") or "") for r in items if r.get("review_by")})
        tags = Counter(t for r in items for t in tags_of(r))
        pin_first = sum(1 for r in items if is_pin_first_candidate(r))
        examples = sorted(items, key=lambda r: (str(r.get("review_by") or "9999-12-31"), str(r.get("id") or "")))[:12]
        table.append({
            "batch_id": f"CAB-{i:03d}",
            "lane": lane,
            "host": host,
            "topic": topic,
            "due_count": len(items),
            "pin_first_candidate_count": pin_first,
            "earliest_review_by": dates[0] if dates else "",
            "latest_review_by": dates[-1] if dates else "",
            "top_tags": "; ".join(f"{t}={c}" for t, c in tags.most_common(10)),
            "example_source_ids": "; ".join(str(r.get("id") or "") for r in examples),
            "recommended_action": action_for(lane, host, items),
            "boundary": BOUNDARY,
        })

    by_lane = Counter(lane_for(r) for r in due)
    by_host = Counter(host_of(str(r.get("url") or "")) for r in due)
    due_count = len(due)
    top10_count = sum(row["due_count"] for row in table[:10])
    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    summary = {
        "archive_version": version,
        "release_date": release_date.isoformat(),
        "horizon_days": horizon_days,
        "current_authority_due_count": due_count,
        "batch_count": len(table),
        "top_10_batches_cover_count": top10_count,
        "top_10_batches_cover_percent": round((top10_count / due_count * 100.0), 2) if due_count else 0.0,
        "lane_counts": dict(sorted(by_lane.items())),
        "top_hosts": by_host.most_common(20),
        "pin_first_candidate_count": sum(int(row["pin_first_candidate_count"]) for row in table),
        "boundary": BOUNDARY,
        "recommended_next_move": "Work current-authority batches before platform/UI batches; within each batch, pin durable PDFs/versioned artifacts first, then decide whether mutable HTML is a current-routing surface or should be demoted.",
    }
    return table, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=DEFAULT_RELEASE_DATE)
    ap.add_argument("--horizon-days", type=int, default=30)
    ap.add_argument("--csv", default=f"artifacts/reports/current-authority-burndown-batches-rev{VERSION_NUM}.csv")
    ap.add_argument("--json", default=f"artifacts/reports/current-authority-burndown-batches-rev{VERSION_NUM}.json")
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)
    table, summary = summarize(load_rows(), release_date, int(args.horizon_days))
    csv_path = ROOT / args.csv
    json_path = ROOT / args.json
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "batch_id", "lane", "host", "topic", "due_count", "pin_first_candidate_count",
            "earliest_review_by", "latest_review_by", "top_tags", "example_source_ids",
            "recommended_action", "boundary",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(table)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {display_path(csv_path)}")
    print(f"WROTE {display_path(json_path)}")
    print(f"current_authority_due={summary['current_authority_due_count']} batches={summary['batch_count']} top10_cover={summary['top_10_batches_cover_percent']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
