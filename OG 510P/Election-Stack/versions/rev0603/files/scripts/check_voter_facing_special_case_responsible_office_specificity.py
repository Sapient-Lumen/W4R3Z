#!/usr/bin/env python3
"""Responsible-office specificity floor for special-case voter-facing surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
CONTROL_TAG = "special_case_high_risk"
REQUIRED_HEADING = "## Responsible office specificity and jurisdiction-match floor"
OFFICE_PATTERNS = [
    "county board",
    "registrar",
    "clerk",
    "city/township",
    "tribal election office",
    "state elections division",
    "responsible official office",
    "office role",
]
JURISDICTION_PATTERNS = [
    "actual jurisdiction",
    "election scope",
    "jurisdiction and election scope",
    "neighboring county",
    "state-level summary",
    "generalized national explainer",
    "same office controls every voter",
]
ORDINARY_HELP_PATTERNS = ["`305`", "305", "ordinary-help lane", "ordinary help"]
RIGHTS_PATTERNS = ["`307`", "307", "rights/safety", "intimidation", "discrimination", "wrongful denial", "unsafe disclosure"]
FIELD_PATTERNS = ["`authoritative_office_name`", "`authoritative_office_scope`", "authoritative_office_name", "authoritative_office_scope"]


def numbered_doc_id(path: Path) -> int | None:
    m = re.match(r"^(\d{1,3})[-_].*\.md$", path.name)
    if not m:
        return None
    return int(m.group(1))


def extract_section(text: str) -> str | None:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == REQUIRED_HEADING:
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
    try:
        doc_ids = tagged_surface_doc_ids(load_surface_registry(), CONTROL_TAG)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    errors: list[str] = []
    seen_docs: set[int] = set()

    office_patterns = [t.lower() for t in OFFICE_PATTERNS]
    jurisdiction_patterns = [t.lower() for t in JURISDICTION_PATTERNS]
    ordinary_help_patterns = [t.lower() for t in ORDINARY_HELP_PATTERNS]
    rights_patterns = [t.lower() for t in RIGHTS_PATTERNS]

    for p in sorted(DOCS_DIR.glob("*.md")):
        doc_id = numbered_doc_id(p)
        if doc_id not in doc_ids:
            continue
        seen_docs.add(doc_id)
        text = p.read_text(encoding="utf-8")
        section = extract_section(text)
        if section is None:
            errors.append(f"{p.relative_to(ROOT)}: missing required heading '{REQUIRED_HEADING}'")
            continue

        lowered = section.lower()
        if not any(token in lowered for token in office_patterns):
            errors.append(f"{p.relative_to(ROOT)}: responsible-office section must identify the governing office kind/role")
        if not any(token in lowered for token in jurisdiction_patterns):
            errors.append(f"{p.relative_to(ROOT)}: responsible-office section must say the office must match the voter's jurisdiction/election scope")
        if not any(token in lowered for token in ordinary_help_patterns):
            errors.append(f"{p.relative_to(ROOT)}: responsible-office section must preserve `305` as the ordinary-help lane")
        if not any(token in lowered for token in rights_patterns):
            errors.append(f"{p.relative_to(ROOT)}: responsible-office section must preserve `307` or rights/safety escalation")
        if not all(token in text for token in ["authoritative_office_name", "authoritative_office_scope"]):
            errors.append(f"{p.relative_to(ROOT)}: doc must carry `authoritative_office_name` and `authoritative_office_scope` in the artifact skeleton or control section")

    missing_docs = sorted(doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"missing special-case surface docs: {missing_docs}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: special-case voter-facing surface responsible-office specificity minimums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
