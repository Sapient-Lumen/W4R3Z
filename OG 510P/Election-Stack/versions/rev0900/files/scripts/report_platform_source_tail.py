#!/usr/bin/env python3
"""Report the platform/UI/vendor source-review tail.

This is an audit/refactor helper. It does not refresh sources. It identifies the
large near-term platform/vendor queue so maintainers can consolidate, sample, or
demote low-risk UI minutiae instead of reviewing hundreds of mutable pages one by
one.
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

BOUNDARY = (
    "Platform-tail reports are maintainer triage only. They do not refresh sources, "
    "prove current platform behavior, or authorize voter-facing use."
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


def action_for(host: str, tags: Counter) -> str:
    if host in {"developer.mozilla.org", "web.dev", "developer.chrome.com", "support.google.com", "learn.microsoft.com", "support.microsoft.com", "support.apple.com"}:
        return "Consolidate to one host-level UI-behavior note plus a small sampled watchlist; avoid doc-per-page refresh loops."
    if tags.get("wcag") or tags.get("wai") or tags.get("uswds"):
        return "Prefer durable pinned standards/guidance artifacts; do not treat every accessibility article as volatile platform UI."
    if tags.get("youtube") or tags.get("vimeo") or tags.get("video_players"):
        return "Keep only voter-facing media playback/accessibility invariants; demote vendor help minutiae to non-release-blocking watchlist."
    return "Group by host and product family; sample current high-risk voter-facing behavior before refreshing individual pages."


def summarize(rows: list[dict], release_date: dt.date, horizon_days: int) -> tuple[list[dict], dict]:
    due = [r for r in rows if is_due_platform(r, release_date, horizon_days)]
    by_host: dict[str, list[dict]] = defaultdict(list)
    for row in due:
        by_host[host_of(str(row.get("url") or ""))].append(row)

    table: list[dict] = []
    for host, items in sorted(by_host.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        tags = Counter(t for r in items for t in (r.get("tags") or []))
        dates = sorted({str(r.get("review_by") or "") for r in items if r.get("review_by")})
        table.append({
            "host": host,
            "due_count": len(items),
            "earliest_review_by": dates[0] if dates else "",
            "latest_review_by": dates[-1] if dates else "",
            "top_tags": "; ".join(f"{k}={v}" for k, v in tags.most_common(10)),
            "example_source_ids": "; ".join(str(r.get("id")) for r in items[:15]),
            "recommended_refactor_action": action_for(host, tags),
            "boundary": BOUNDARY,
        })

    host_counts = Counter(host_of(str(r.get("url") or "")) for r in due)
    tag_counts = Counter(t for r in due for t in (r.get("tags") or []))
    top10 = sum(c for _, c in host_counts.most_common(10))
    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    summary = {
        "archive_version": version,
        "release_date": release_date.isoformat(),
        "horizon_days": horizon_days,
        "platform_due_count": len(due),
        "distinct_platform_hosts": len(host_counts),
        "top_10_hosts_due_count": top10,
        "top_10_hosts_share": round(top10 / len(due), 4) if due else 0,
        "top_hosts": host_counts.most_common(20),
        "top_tags": tag_counts.most_common(30),
        "boundary": BOUNDARY,
        "recommended_next_move": "Treat the platform lane as a consolidation/sampling problem. Refresh current-authority rows first; for platform rows, collapse duplicate host/product pages into watchlists and router docs before spending maintainer hours on line-by-line review.",
    }
    return table, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=DEFAULT_RELEASE_DATE)
    ap.add_argument("--horizon-days", type=int, default=30)
    ap.add_argument("--csv", default=f"artifacts/reports/platform-source-tail-rev{VERSION_NUM}.csv")
    ap.add_argument("--json", default=f"artifacts/reports/platform-source-tail-rev{VERSION_NUM}.json")
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)
    rows = load_rows()
    table, summary = summarize(rows, release_date, int(args.horizon_days))

    csv_path = ROOT / args.csv
    json_path = ROOT / args.json
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["host", "due_count", "earliest_review_by", "latest_review_by", "top_tags", "example_source_ids", "recommended_refactor_action", "boundary"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in table:
            w.writerow(row)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {display_path(csv_path)}")
    print(f"WROTE {display_path(json_path)}")
    print(f"platform_due={summary['platform_due_count']} hosts={summary['distinct_platform_hosts']} top10_share={summary['top_10_hosts_share']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
