#!/usr/bin/env python3
"""Reject stale or impossible high-risk payload verification timestamps."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from _shared.registry import split_semicolon
from _shared.voter_surface_registry import load_surface_registry

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
CHANGELOG_HEAD_RE = re.compile(r"^## v\d+ \((\d{4}-\d{2}-\d{2})\)", re.M)


def parse_release_date() -> date:
    text = CHANGELOG.read_text(encoding="utf-8")
    m = CHANGELOG_HEAD_RE.search(text)
    if not m:
        raise SystemExit(f"ERROR: could not parse release date from {CHANGELOG}")
    return date.fromisoformat(m.group(1))


def parse_timestamp(raw: str) -> datetime:
    value = raw.strip()
    if "T" not in value:
        raise ValueError("timestamp must include time component")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def main() -> int:
    release_date = parse_release_date()
    table = load_surface_registry()
    errors: list[str] = []

    for row in table.rows:
        if "special_case_high_risk" not in split_semicolon(row.get("control_tags", "")):
            continue

        doc_id = row["doc_id"]
        template_rel = row["template_path"]
        template_path = ROOT / template_rel
        if not template_path.exists():
            errors.append(f"doc {doc_id}: missing template {template_rel}")
            continue

        try:
            payload = json.loads(template_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"doc {doc_id}: invalid JSON in {template_rel}: {exc}")
            continue

        raw_ts = payload.get("last_verified_at")
        if not isinstance(raw_ts, str) or not raw_ts.strip():
            errors.append(f"doc {doc_id}: {template_rel} missing non-empty `last_verified_at`")
            continue

        try:
            verified_at = parse_timestamp(raw_ts)
        except ValueError as exc:
            errors.append(f"doc {doc_id}: {template_rel} has invalid `last_verified_at` {raw_ts!r}: {exc}")
            continue

        window = payload.get("source_review_window_days")
        if not isinstance(window, int) or window <= 0:
            errors.append(f"doc {doc_id}: {template_rel} must set positive integer `source_review_window_days`")
            continue

        verified_date = verified_at.date()
        if verified_date > release_date:
            errors.append(
                f"doc {doc_id}: {template_rel} has `last_verified_at` {verified_at.isoformat().replace('+00:00', 'Z')} after release date {release_date.isoformat()}"
            )
            continue

        age_days = (release_date - verified_date).days
        if age_days > window:
            errors.append(
                f"doc {doc_id}: {template_rel} has `last_verified_at` {verified_at.isoformat().replace('+00:00', 'Z')} which is {age_days} days older than release date {release_date.isoformat()} and outside declared `source_review_window_days`={window}"
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    print(
        "PASS: special-case high-risk payload review-window coherence "
        f"(all tagged payload templates keep parseable nonfuture `last_verified_at` inside their declared review window relative to release date {release_date.isoformat()})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
