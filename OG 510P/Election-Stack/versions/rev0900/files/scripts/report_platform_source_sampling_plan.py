#!/usr/bin/env python3
"""Generate a bounded sampling plan for the platform/UI/vendor source-review tail.

The goal is operational: when hundreds of mutable platform help pages are due,
reviewing every row linearly is likely to fail. This report selects a small,
host-balanced sample for maintainer attention while preserving the no-claim
boundary that current voter-facing authority must be reviewed separately.
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
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
VERSION_FILE = ROOT / "VERSION"
VERSION_NUM = VERSION_FILE.read_text(encoding="utf-8").strip().removeprefix("v").zfill(4)
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from release_context import release_date as archive_release_date
DEFAULT_RELEASE_DATE = archive_release_date(ROOT)

PLATFORM_TAGS = {
    "adobe", "android", "apple", "browser", "chrome", "css", "design",
    "digital_gov", "drive", "forms", "google", "gsa", "html", "mdn",
    "microsoft", "mobile", "notifications", "onedrive", "powerpoint",
    "safari", "search", "search_central", "sharepoint", "slides", "teams",
    "uswds", "video_players", "vimeo", "w3c", "wai", "wcag", "web_dev",
    "workspace", "youtube", "mozilla", "firefox", "slack", "open_graph",
    "link_previews", "social_share", "metadata", "unfurls",
}
ACCESSIBILITY_REFERENCE_TAGS = {"accessibility", "wcag", "wai", "aria", "section508", "media_accessibility"}

PRIORITY_BUCKETS = [
    ("accessibility/forms", {"accessibility", "wcag", "wai", "aria", "forms", "keyboard", "focus"}),
    ("media/playback", {"video_players", "youtube", "vimeo", "captions", "transcripts", "live_events"}),
    ("account/auth/domain", {"developer_identity", "search_console", "dns", "domains", "permissions", "account", "ownership"}),
    ("browser/mobile/runtime", {"browser", "browser_behavior", "mobile", "android", "safari", "chrome", "service_worker", "notifications"}),
    ("platform-ai/search", {"ai_controls", "copilot", "search", "search_central", "generative_answers"}),
]

BOUNDARY = (
    "Sampling plans are maintainer triage only. They do not refresh sources, prove current platform behavior, "
    "or authorize voter-facing reliance. Current election-authority rows remain first-priority review items."
)


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def is_accessibility_reference(row: dict) -> bool:
    url = str(row.get("url") or "")
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.lower()
    tags = {str(t) for t in (row.get("tags") or [])}
    if host.endswith("w3.org") and ("/wai/" in path or path.startswith("/tr/wcag")):
        return True
    return bool(tags & ACCESSIBILITY_REFERENCE_TAGS)


def load_rows() -> list[dict]:
    with LOCK.open("rb") as f:
        return tomllib.load(f).get("source", [])


def is_due_platform(row: dict, release_date: dt.date, horizon_days: int) -> bool:
    if str(row.get("sha256") or "").strip():
        return False
    tags = {str(t) for t in (row.get("tags") or [])}
    if not (tags & PLATFORM_TAGS):
        return False
    if is_accessibility_reference(row):
        return False
    rb = row.get("review_by")
    if not rb:
        return False
    try:
        review_by = dt.date.fromisoformat(str(rb))
    except Exception:
        return False
    return release_date <= review_by <= release_date + dt.timedelta(days=horizon_days)


def bucket_for(tags: set[str]) -> str:
    for label, bucket_tags in PRIORITY_BUCKETS:
        if tags & bucket_tags:
            return label
    return "other-platform-ui"


def row_priority(row: dict) -> tuple:
    tags = {str(t) for t in (row.get("tags") or [])}
    bucket_index = next((i for i, (_, btags) in enumerate(PRIORITY_BUCKETS) if tags & btags), len(PRIORITY_BUCKETS))
    review_by = str(row.get("review_by") or "9999-12-31")
    return (bucket_index, review_by, str(row.get("id") or ""))


def choose_samples(items: list[dict], per_host: int) -> list[tuple[dict, str]]:
    by_bucket: dict[str, list[dict]] = defaultdict(list)
    for row in sorted(items, key=row_priority):
        tags = {str(t) for t in (row.get("tags") or [])}
        by_bucket[bucket_for(tags)].append(row)

    chosen: list[tuple[dict, str]] = []
    used_ids: set[str] = set()
    # First pass: one representative from each high-value bucket.
    for label, _ in PRIORITY_BUCKETS:
        if len(chosen) >= per_host:
            break
        bucket = by_bucket.get(label) or []
        for row in bucket:
            sid = str(row.get("id") or "")
            if sid not in used_ids:
                chosen.append((row, label))
                used_ids.add(sid)
                break
    # Second pass: earliest due remaining rows.
    for row in sorted(items, key=row_priority):
        if len(chosen) >= per_host:
            break
        sid = str(row.get("id") or "")
        if sid in used_ids:
            continue
        tags = {str(t) for t in (row.get("tags") or [])}
        chosen.append((row, bucket_for(tags)))
        used_ids.add(sid)
    return chosen


def build_plan(rows: list[dict], release_date: dt.date, horizon_days: int, per_host: int) -> tuple[list[dict], dict]:
    due = [r for r in rows if is_due_platform(r, release_date, horizon_days)]
    by_host: dict[str, list[dict]] = defaultdict(list)
    for row in due:
        by_host[host_of(str(row.get("url") or ""))].append(row)

    sample_rows: list[dict] = []
    host_summary = []
    for host, items in sorted(by_host.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        chosen = choose_samples(items, per_host)
        tags = Counter(t for r in items for t in (r.get("tags") or []))
        host_summary.append({"host": host, "due_count": len(items), "sample_count": len(chosen), "top_tags": tags.most_common(8)})
        for row, bucket in chosen:
            sample_rows.append({
                "host": host,
                "sample_bucket": bucket,
                "source_id": str(row.get("id") or ""),
                "review_by": str(row.get("review_by") or ""),
                "tags": "; ".join(str(t) for t in (row.get("tags") or [])),
                "url_host_only": host,
                "recommended_review_question": review_question(bucket),
                "boundary": BOUNDARY,
            })

    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    summary = {
        "archive_version": version,
        "release_date": release_date.isoformat(),
        "horizon_days": horizon_days,
        "platform_due_count": len(due),
        "distinct_platform_hosts": len(by_host),
        "sample_count": len(sample_rows),
        "per_host_cap": per_host,
        "linear_review_avoided_count": max(0, len(due) - len(sample_rows)),
        "sample_share_of_due": round(len(sample_rows) / len(due), 4) if due else 0,
        "host_summary": host_summary,
        "boundary": BOUNDARY,
        "recommended_next_move": "Review current-authority rows first. For platform/UI/vendor rows, use this bounded sample to decide whether a host/product family changed materially; then refresh only rows needed by active voter-facing surfaces.",
    }
    return sample_rows, summary


def review_question(bucket: str) -> str:
    if bucket == "accessibility/forms":
        return "Did the platform alter voter-facing form, focus, caption, transcript, or accessibility behavior that the cube treats as an invariant?"
    if bucket == "media/playback":
        return "Did media playback, captions, transcripts, live-event restrictions, or embedding defaults change enough to affect official communications evidence?"
    if bucket == "account/auth/domain":
        return "Did ownership, account, domain, permission, or verification flows change enough to affect official-channel custody assumptions?"
    if bucket == "browser/mobile/runtime":
        return "Did browser/mobile/runtime behavior change enough to affect capture, caching, notification, or embedded-web evidence?"
    if bucket == "platform-ai/search":
        return "Did AI/search surfaces change enough to affect voter-information routing, summaries, or non-authoritative wrapper boundaries?"
    return "Did this host/product family change in a way that affects active voter-facing or evidence-capture assumptions?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=DEFAULT_RELEASE_DATE)
    ap.add_argument("--horizon-days", type=int, default=30)
    ap.add_argument("--per-host", type=int, default=3)
    ap.add_argument("--csv", default=f"artifacts/reports/platform-source-sampling-plan-rev{VERSION_NUM}.csv")
    ap.add_argument("--json", default=f"artifacts/reports/platform-source-sampling-plan-rev{VERSION_NUM}.json")
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)
    rows, summary = build_plan(load_rows(), release_date, int(args.horizon_days), max(1, int(args.per_host)))
    csv_path = ROOT / args.csv
    json_path = ROOT / args.json
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["host", "sample_bucket", "source_id", "review_by", "tags", "url_host_only", "recommended_review_question", "boundary"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {display_path(csv_path)}")
    print(f"WROTE {display_path(json_path)}")
    print(f"platform_due={summary['platform_due_count']} sample={summary['sample_count']} avoided={summary['linear_review_avoided_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
