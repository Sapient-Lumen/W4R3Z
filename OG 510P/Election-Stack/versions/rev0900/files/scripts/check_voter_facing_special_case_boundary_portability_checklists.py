#!/usr/bin/env python3
"""Checklist boundary/portability backstop for high-risk voter-facing special-case surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry
from _shared.registry import split_semicolon

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST_HEADING = "## High-risk boundary/portability backstop"
DOC_SECTION_HEADING = "## Relationship to adjacent surfaces and non-overlap rules"
DOC_REF_RE = re.compile(r"(?:`|docs/)(\d{3})(?:`|\b)")
DATE_PATTERNS = ["last updated", "dated", "as-of", "as of", "publication date"]
NO_CROSS_PATTERNS = [
    "another state",
    "other state",
    "another county",
    "other county",
    "another jurisdiction",
    "other jurisdiction",
    "cross-jurisdiction",
    "not portable",
    "cross-facility",
    "another facility",
    "other facility",
]


def _read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise FileNotFoundError(rel)
    return p.read_text(encoding="utf-8")


def extract_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return "\n".join(lines[start:end]).strip()


def main() -> int:
    table = load_surface_registry()
    errors: list[str] = []

    for row in table.rows:
        if "special_case_high_risk" not in split_semicolon(row.get("control_tags", "")):
            continue

        doc_rel = row["doc_path"]
        checklist_rel = row["checklist_path"]
        doc_id = row["doc_id"]

        try:
            doc_text = _read(doc_rel)
        except FileNotFoundError:
            errors.append(f"doc {doc_id}: missing numbered doc {doc_rel}")
            continue
        try:
            checklist_text = _read(checklist_rel)
        except FileNotFoundError:
            errors.append(f"doc {doc_id}: missing checklist {checklist_rel}")
            continue

        doc_section = extract_section(doc_text, DOC_SECTION_HEADING)
        if not doc_section:
            errors.append(f"doc {doc_id}: {doc_rel} missing required non-overlap section")
            continue
        checklist_section = extract_section(checklist_text, CHECKLIST_HEADING)
        if not checklist_section:
            errors.append(f"doc {doc_id}: {checklist_rel} missing required heading {CHECKLIST_HEADING!r}")
            continue

        doc_refs = []
        for m in DOC_REF_RE.finditer(doc_section):
            ref = m.group(1)
            if ref != doc_id and ref not in doc_refs:
                doc_refs.append(ref)
        if len(doc_refs) < 2:
            errors.append(f"doc {doc_id}: {doc_rel} expected at least 2 adjacent-surface refs in non-overlap section")
            continue

        checklist_refs = []
        for m in DOC_REF_RE.finditer(checklist_section):
            ref = m.group(1)
            if ref != doc_id and ref not in checklist_refs:
                checklist_refs.append(ref)
        overlap = [ref for ref in checklist_refs if ref in doc_refs]
        if len(overlap) < 2:
            errors.append(
                f"doc {doc_id}: {checklist_rel} must echo at least 2 adjacent-surface refs from {doc_rel}; found overlap {overlap}"
            )

        lower = checklist_section.lower()
        for token in ["305", "307", "verify", "official"]:
            if token not in lower:
                errors.append(f"doc {doc_id}: {checklist_rel} missing boundary/portability token `{token}`")
        if not any(tok in lower for tok in DATE_PATTERNS):
            errors.append(f"doc {doc_id}: {checklist_rel} missing dated/last-updated preference in boundary/portability section")
        if not any(tok in lower for tok in NO_CROSS_PATTERNS):
            errors.append(f"doc {doc_id}: {checklist_rel} missing no-cross-jurisdiction/facility portability warning")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 2

    print("PASS: special-case high-risk checklist boundary/portability backstop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
