#!/usr/bin/env python3
"""Reject drift where high-risk freshness/current-state/conflict controls live only in docs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from _shared.registry import split_semicolon
from _shared.voter_surface_registry import load_surface_registry

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CHECKLIST_HEADING = "## High-risk freshness/current-state/conflict backstop"
REQUIRED_TEMPLATE_TOKENS = [
    "last_verified_at",
    "source_review_window_days",
    "latest_notice_uri",
    "current_official_controls_note",
    "superseding_notice_note",
    "unresolved_conflict_stop_note",
]
REQUIRED_CHECKLIST_TOKENS = [
    "last_verified_at",
    "source_review_window_days",
    "latest_notice_uri",
    "current_official_controls_note",
    "superseding_notice_note",
    "unresolved_conflict_stop_note",
    "305",
    "307",
]


def _read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise FileNotFoundError(rel)
    return p.read_text(encoding="utf-8")


def main() -> int:
    table = load_surface_registry()
    errors: list[str] = []

    for row in table.rows:
        if "special_case_high_risk" not in split_semicolon(row.get("control_tags", "")):
            continue

        doc_id = row["doc_id"]
        template_rel = row["template_path"]
        checklist_rel = row["checklist_path"]

        try:
            template_text = _read(template_rel)
            payload = json.loads(template_text)
        except FileNotFoundError:
            errors.append(f"doc {doc_id}: missing template {template_rel}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"doc {doc_id}: invalid JSON in {template_rel}: {exc}")
            continue

        try:
            checklist_text = _read(checklist_rel)
        except FileNotFoundError:
            errors.append(f"doc {doc_id}: missing checklist {checklist_rel}")
            continue

        for token in REQUIRED_TEMPLATE_TOKENS:
            if token not in template_text:
                errors.append(f"doc {doc_id}: {template_rel} missing `{token}`")

        if payload.get("source_review_window_days") != 90:
            errors.append(
                f"doc {doc_id}: {template_rel} must set `source_review_window_days` to 90 for the current high-risk release-freshness floor"
            )
        for token in ["last_verified_at", "latest_notice_uri", "current_official_controls_note", "superseding_notice_note", "unresolved_conflict_stop_note"]:
            value = payload.get(token)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"doc {doc_id}: {template_rel} must populate `{token}` with non-empty text")

        if REQUIRED_CHECKLIST_HEADING not in checklist_text:
            errors.append(
                f"doc {doc_id}: {checklist_rel} missing required heading {REQUIRED_CHECKLIST_HEADING!r}"
            )
        for token in REQUIRED_CHECKLIST_TOKENS:
            if token not in checklist_text:
                errors.append(f"doc {doc_id}: {checklist_rel} missing checklist token `{token}`")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    print("PASS: special-case high-risk freshness/current-state/conflict propagation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
