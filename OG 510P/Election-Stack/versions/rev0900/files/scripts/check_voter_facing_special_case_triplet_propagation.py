#!/usr/bin/env python3
"""Reject doc-only drift for high-risk voter-facing special-case triplets."""

from __future__ import annotations

from pathlib import Path
import sys

from _shared.voter_surface_registry import load_surface_registry
from _shared.registry import split_semicolon

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CHECKLIST_HEADING = "## High-risk routing/control backstop"
REQUIRED_CHECKLIST_TOKENS = [
    "authoritative_help_uri",
    "authoritative_help_phone",
    "305",
    "307",
    "authoritative_office_name",
    "authoritative_office_scope",
    "official_secure_channel_note",
    "minimum_necessary_disclosure_note",
    "operability_now_note",
    "deadline_imminence_note",
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

        template_rel = row["template_path"]
        checklist_rel = row["checklist_path"]
        doc_id = row["doc_id"]

        try:
            template_text = _read(template_rel)
        except FileNotFoundError:
            errors.append(f"doc {doc_id}: missing template {template_rel}")
            continue

        try:
            checklist_text = _read(checklist_rel)
        except FileNotFoundError:
            errors.append(f"doc {doc_id}: missing checklist {checklist_rel}")
            continue

        if not ("authoritative_help_uri" in template_text or "authoritative_help_phone" in template_text):
            errors.append(
                f"doc {doc_id}: {template_rel} must carry `authoritative_help_uri` and/or `authoritative_help_phone`"
            )
        for token in [
            "authoritative_office_name",
            "authoritative_office_scope",
            "official_secure_channel_note",
            "minimum_necessary_disclosure_note",
            "operability_now_note",
            "deadline_imminence_note",
        ]:
            if token not in template_text:
                errors.append(f"doc {doc_id}: {template_rel} missing `{token}`")

        if REQUIRED_CHECKLIST_HEADING not in checklist_text:
            errors.append(
                f"doc {doc_id}: {checklist_rel} missing required heading {REQUIRED_CHECKLIST_HEADING!r}"
            )
        for token in REQUIRED_CHECKLIST_TOKENS:
            if token not in checklist_text:
                errors.append(f"doc {doc_id}: {checklist_rel} missing checklist token `{token}`")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 2

    print("PASS: special-case high-risk triplet propagation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
