#!/usr/bin/env python3
"""Authority-hierarchy minimums for special-case voter-facing surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
CONTROL_TAG = "special_case_high_risk"
REQUIRED_HEADING = "## Authority hierarchy, official-routing precedence, and national-summary ceiling"
LOCAL_PATTERNS = [
    "local election office",
    "state or local",
    "state election",
    "county board",
    "registrar",
    "clerk",
    "election office",
]
GENERALIZED_PATTERNS = [
    "national",
    "generalized",
    "routing aids",
    "routing aid",
    "not substitutes",
    "not a substitute",
    "this archive",
]
PREFERENCE_PATTERNS = [
    "prefer the most current official",
    "most current official",
    "if a national",
    "if materials differ",
    "conflicts with",
    "differs",
]


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

    for p in sorted(DOCS_DIR.glob("*.md")):
        doc_id = numbered_doc_id(p)
        if doc_id not in doc_ids:
            continue
        seen_docs.add(doc_id)
        text = p.read_text(encoding="utf-8")
        section = extract_section(text)
        if section is None:
            errors.append(
                f"{p.relative_to(ROOT)}: missing required heading '{REQUIRED_HEADING}'"
            )
            continue

        lowered = section.lower()
        if "official" not in lowered or "controlling" not in lowered:
            errors.append(
                f"{p.relative_to(ROOT)}: authority-hierarchy section must say the current official source controls"
            )
        if not any(token in lowered for token in LOCAL_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: authority-hierarchy section must name the state/local election-office authority"
            )
        if not any(token in lowered for token in GENERALIZED_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: authority-hierarchy section must say national/generalized/archive summaries are routing aids or not substitutes"
            )
        if not any(token in lowered for token in PREFERENCE_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: authority-hierarchy section must say to prefer the most current official instruction when materials differ"
            )

    missing_docs = sorted(doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"missing special-case surface docs: {missing_docs}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: special-case voter-facing surface authority-hierarchy minimums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
