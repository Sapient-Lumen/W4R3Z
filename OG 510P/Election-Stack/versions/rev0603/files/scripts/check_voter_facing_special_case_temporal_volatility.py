#!/usr/bin/env python3
"""Temporal-volatility minimums for special-case voter-facing surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
CONTROL_TAG = "special_case_high_risk"
REQUIRED_HEADING = "## Temporal volatility, freshness, and no-cross-jurisdiction rules"
NO_CROSS_PATTERNS = [
    "do not infer",
    "another state",
    "other state",
    "another county",
    "other county",
    "another jurisdiction",
    "other jurisdiction",
    "cross-jurisdiction",
    "not portable",
]
DATE_PATTERNS = [
    "last updated",
    "dated",
    "as-of",
    "as of",
    "publication date",
    "check for updates",
]
JURISDICTION_PATTERNS = [
    "jurisdiction",
    "state",
    "county",
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
        if "verify" not in lowered or "official" not in lowered:
            errors.append(
                f"{p.relative_to(ROOT)}: temporal-volatility section must say to verify the current official source"
            )
        if not any(token in lowered for token in JURISDICTION_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: temporal-volatility section must say the rule is jurisdiction-specific"
            )
        if not any(token in lowered for token in DATE_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: temporal-volatility section must mention a dated/last-updated/as-of preference"
            )
        if not any(token in lowered for token in NO_CROSS_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: temporal-volatility section must forbid cross-jurisdiction inference/portability"
            )

    missing_docs = sorted(doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"missing special-case surface docs: {missing_docs}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: special-case voter-facing surface temporal-volatility minimums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
