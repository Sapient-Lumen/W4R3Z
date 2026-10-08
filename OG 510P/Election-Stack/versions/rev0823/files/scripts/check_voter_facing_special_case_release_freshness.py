#!/usr/bin/env python3
"""Check release-date freshness floor for high-risk voter-facing special-case docs."""

from __future__ import annotations

import re
import tomllib
from datetime import date
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
CHANGELOG = ROOT / "CHANGELOG.md"
CONTROL_TAG = "special_case_high_risk"
MIN_RECENT_OFFICIAL = 2
MAX_AGE_DAYS = 90
ANCHOR_RE = re.compile(r"\b(?:source|xref):\s*`([^`]+)`")
CHANGELOG_HEAD_RE = re.compile(r"^## v\d+ \((\d{4}-\d{2}-\d{2})\)", re.M)


def load_sources() -> dict[str, dict]:
    data = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    entries: list[dict] = []
    if "id" in data:
        entries.append({k: v for k, v in data.items() if k != "source"})
    entries.extend(data.get("source", []))
    out: dict[str, dict] = {}
    for e in entries:
        sid = e.get("id")
        if sid:
            out[str(sid)] = e
    return out


def parse_release_date() -> date:
    text = CHANGELOG.read_text(encoding="utf-8")
    m = CHANGELOG_HEAD_RE.search(text)
    if not m:
        raise SystemExit(f"ERROR: could not parse release date from {CHANGELOG}")
    return date.fromisoformat(m.group(1))


def main() -> int:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}")
        return 2
    if not CHANGELOG.exists():
        print(f"ERROR: missing changelog: {CHANGELOG}")
        return 2

    release_date = parse_release_date()
    table = load_surface_registry()
    special_ids = tagged_surface_doc_ids(table, CONTROL_TAG)
    sources = load_sources()

    rows: list[tuple[int, str]] = []
    for row in table.rows:
        if not any(row.values()):
            continue
        doc_id = int(row["doc_id"])
        if doc_id not in special_ids:
            continue
        rows.append((doc_id, row["doc_path"]))

    errors: list[str] = []
    for doc_id, rel in rows:
        p = ROOT / rel
        if not p.exists():
            errors.append(f"missing special-case surface doc {doc_id}: {rel}")
            continue

        ids = sorted(set(ANCHOR_RE.findall(p.read_text(encoding="utf-8"))))
        official_ids = [
            sid for sid in ids
            if "official_websites" in sources.get(sid, {}).get("tags", [])
        ]

        recent: list[str] = []
        bad_dates: list[str] = []
        for sid in official_ids:
            retrieved = str(sources.get(sid, {}).get("retrieved", "")).strip()
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", retrieved):
                bad_dates.append(sid)
                continue
            age = (release_date - date.fromisoformat(retrieved)).days
            if age < 0:
                errors.append(
                    f"{p.relative_to(ROOT)}: official source {sid} has retrieved={retrieved} after release date {release_date.isoformat()}"
                )
                continue
            if age <= MAX_AGE_DAYS:
                recent.append(sid)

        if len(recent) < MIN_RECENT_OFFICIAL:
            detail = (
                f"recent official anchors={', '.join(recent)}" if recent else "no recent official anchors"
            )
            if bad_dates:
                detail += f"; invalid_or_missing_retrieved={', '.join(bad_dates)}"
            errors.append(
                f"{p.relative_to(ROOT)}: expected at least {MIN_RECENT_OFFICIAL} official lock-backed anchors retrieved within {MAX_AGE_DAYS} days of release date {release_date.isoformat()}, found {len(recent)} ({detail})"
            )

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    doc_labels = ", ".join(str(doc_id) for doc_id, _ in rows)
    print(
        "PASS: special-case voter-facing release freshness floor "
        f"(docs {doc_labels} each have >= {MIN_RECENT_OFFICIAL} official anchors retrieved within {MAX_AGE_DAYS} days of release date {release_date.isoformat()})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
