#!/usr/bin/env python3
"""Generate a compact source-review pressure report.

This is an audit/refactor helper, not a freshness verifier.  It prevents the
maintainer from treating hundreds of mutable source-review rows as one linear
queue by grouping them into action lanes.
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
    CURRENT_AUTHORITY_TAGS,
    PLATFORM_TAGS,
    STATE_HINT_TAGS,
    host_of,
    is_authority_host,
    parsed_url_parts,
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

ACCESSIBILITY_REFERENCE_TAGS = {"accessibility", "wcag", "wai", "aria", "section508", "section_508", "media_accessibility"}
LEGAL_TAGS = {"law", "us", "esi", "spoliation"}
CITATION_BACKFILL_TAGS = {"citation_backfill"}
DURABLE_STANDARD_TAGS = {"rfc", "ct", "dns", "dnssec", "ip", "examples", "e2e", "vvsg", "tuf", "c2pa"}
IMPLEMENTATION_HINT_TAGS = {"implementation_hint", "platform_watchlist", "accessibility_implementation_hint", "standard_watchlist"}

BOUNDARY = (
    "Source-review pressure reports prioritize maintainer attention. They do not "
    "refresh sources, prove current law, prove current voter instructions, or make "
    "a live-pilot release safe."
)


def is_accessibility_reference(tags: set[str], host: str, path: str) -> bool:
    """Return true for accessibility standards/pattern rows, not generic UI docs."""

    if host.endswith("w3.org") and ("/wai/" in path or path.startswith("/tr/wcag")):
        return True
    return bool(tags & ACCESSIBILITY_REFERENCE_TAGS)


def is_durable_standard_reference(tags: set[str], host: str, path: str) -> bool:
    if tags & DURABLE_STANDARD_TAGS:
        return True
    if host.endswith("w3.org") and path.startswith("/tr/"):
        return True
    if host.endswith(("oasis-open.org", "rfc-editor.org", "ietf.org")):
        return True
    return False


def classify(row: dict, release_date: dt.date) -> str:
    sha = str(row.get("sha256") or "").strip()
    if sha:
        return "pinned_not_due"
    rb = row.get("review_by")
    if not rb:
        return "unpinned_missing_review_by"
    try:
        review_by = dt.date.fromisoformat(str(rb))
    except Exception:
        return "unpinned_bad_review_by"
    if review_by < release_date:
        return "release_blocking_expired"
    if review_by > release_date + dt.timedelta(days=30):
        return "unpinned_due_later"
    tags = set(str(t) for t in (row.get("tags") or []))
    host, path = parsed_url_parts(str(row.get("url") or ""))
    authority_host = is_authority_host(host)
    if tags & STATE_HINT_TAGS:
        return "state_or_local_authority_due_30d"
    if authority_host or (tags & CURRENT_AUTHORITY_TAGS and not (tags & PLATFORM_TAGS)):
        return "current_authority_due_30d"
    if tags & LEGAL_TAGS or host.endswith("law.cornell.edu") or host.endswith("uscode.house.gov"):
        return "legal_reference_due_30d"
    if tags & IMPLEMENTATION_HINT_TAGS:
        return "implementation_hint_watchlist_due_30d"
    if is_accessibility_reference(tags, host, path):
        return "accessibility_reference_due_30d"
    if is_durable_standard_reference(tags, host, path):
        return "durable_standard_due_30d"
    if tags & CITATION_BACKFILL_TAGS:
        return "citation_backfill_due_30d"
    if tags & PLATFORM_TAGS and not authority_host:
        return "platform_ui_vendor_due_30d"
    return "other_due_30d"


def load_rows() -> list[dict]:
    with LOCK.open("rb") as f:
        return tomllib.load(f).get("source", [])


def display_path(path: Path) -> str:
    """Return a stable display path for both in-repo and external output files."""

    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def summarize(rows: list[dict], release_date: dt.date) -> tuple[list[dict], dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[classify(row, release_date)].append(row)

    recommended_action = {
        "release_blocking_expired": "Refresh, pin, demote, or remove before release.",
        "accessibility_reference_due_30d": "Review as a public-rights/accessibility lane, not as generic platform churn; prefer durable WCAG/DOJ anchors over scattered pattern pages.",
        "current_authority_due_30d": "Review first; these are the closest to current public election/cyber authority.",
        "state_or_local_authority_due_30d": "Review before any local adoption claim or voter-facing use.",
        "platform_ui_vendor_due_30d": "Do not review linearly; sample high-use surfaces, consolidate duplicate cue docs, and demote non-critical UI minutiae.",
        "citation_backfill_due_30d": "Prefer pinning durable byte artifacts or replacing with a stable canonical source.",
        "legal_reference_due_30d": "Review only with legal/current-authority caveat; do not rely as legal advice.",
        "durable_standard_due_30d": "Prefer pinned immutable versioned specs rather than recurring mutable landing-page review.",
        "implementation_hint_watchlist_due_30d": "Non-authority implementation/watchlist rows: review only when an active voter-facing or evidence-capture surface depends on the behavior.",
        "other_due_30d": "Triage manually after current-authority and platform sprawl lanes.",
        "unpinned_due_later": "No immediate action; keep in ordinary queue.",
        "unpinned_missing_review_by": "Hygiene blocker: add review_by or pin.",
        "unpinned_bad_review_by": "Hygiene blocker: fix malformed review_by.",
        "pinned_not_due": "No freshness review required unless the citation needs current interpretation.",
    }
    rows_out: list[dict] = []
    for lane in sorted(grouped.keys()):
        items = grouped[lane]
        hosts = Counter(host_of(str(r.get("url") or "")) for r in items)
        tags = Counter(t for r in items for t in (r.get("tags") or []))
        due_dates = sorted({str(r.get("review_by") or "") for r in items if r.get("review_by")})
        rows_out.append({
            "lane": lane,
            "count": len(items),
            "earliest_review_by": due_dates[0] if due_dates else "",
            "latest_review_by": due_dates[-1] if due_dates else "",
            "top_hosts": "; ".join(f"{h}={c}" for h, c in hosts.most_common(8) if h),
            "top_tags": "; ".join(f"{t}={c}" for t, c in tags.most_common(10)),
            "example_source_ids": "; ".join(str(r.get("id")) for r in items[:12]),
            "recommended_action": recommended_action.get(lane, "Triage manually."),
            "boundary": BOUNDARY,
        })

    due30 = sum(len(v) for k, v in grouped.items() if k.endswith("due_30d"))
    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    summary = {
        "archive_version": version,
        "release_date": release_date.isoformat(),
        "source_count": len(rows),
        "pinned_count": len(grouped.get("pinned_not_due", [])),
        "unexpired_due_within_30_days_count": due30,
        "expired_review_count": len(grouped.get("release_blocking_expired", [])),
        "platform_ui_vendor_due_30d_count": len(grouped.get("platform_ui_vendor_due_30d", [])),
        "accessibility_reference_due_30d_count": len(grouped.get("accessibility_reference_due_30d", [])),
        "current_authority_due_30d_count": len(grouped.get("current_authority_due_30d", [])),
        "state_or_local_authority_due_30d_count": len(grouped.get("state_or_local_authority_due_30d", [])),
        "implementation_hint_watchlist_due_30d_count": len(grouped.get("implementation_hint_watchlist_due_30d", [])),
        "boundary": BOUNDARY,
        "lanes": rows_out,
    }
    return rows_out, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=DEFAULT_RELEASE_DATE, help="YYYY-MM-DD release review date")
    ap.add_argument("--csv", default=f"artifacts/reports/source-review-pressure-rev{VERSION_NUM}.csv")
    ap.add_argument("--json", default=f"artifacts/reports/source-review-pressure-rev{VERSION_NUM}.json")
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)
    rows = load_rows()
    table, summary = summarize(rows, release_date)

    csv_path = ROOT / args.csv
    json_path = ROOT / args.json
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["lane", "count", "earliest_review_by", "latest_review_by", "top_hosts", "top_tags", "example_source_ids", "recommended_action", "boundary"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in table:
            w.writerow(row)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {display_path(csv_path)}")
    print(f"WROTE {display_path(json_path)}")
    print(f"expired={summary['expired_review_count']} due30={summary['unexpired_due_within_30_days_count']} platform_ui={summary['platform_ui_vendor_due_30d_count']} implementation_hint={summary['implementation_hint_watchlist_due_30d_count']} current_authority={summary['current_authority_due_30d_count']} state_local={summary['state_or_local_authority_due_30d_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
