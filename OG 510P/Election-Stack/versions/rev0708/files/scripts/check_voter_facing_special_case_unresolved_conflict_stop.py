#!/usr/bin/env python3
"""Unresolved-conflict stop and no-synthesis discipline for special-case voter-facing surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
CONTROL_TAG = "special_case_high_risk"
REQUIRED_HEADING = "## Unresolved official conflict, no-synthesis, and office-confirmation rule"
CONFLICT_PATTERNS = [
    "conflict",
    "disagree",
    "inconsistent",
    "unresolved",
    "material gap",
]
NOSYNTH_PATTERNS = [
    "do not synthesize",
    "do not combine",
    "do not infer",
    "do not average",
    "no-synthesis",
]
STOP_PATTERNS = [
    "stop condition",
    "stop and",
    "before acting",
]
CONFIRM_PATTERNS = [
    "case-specific confirmation",
    "local election office",
    "county board",
    "registrar",
    "clerk",
    "office/help path",
    "`305`",
    "305",
]
RIGHTS_PATTERNS = [
    "`307`",
    "307",
    "rights/safety",
    "intimidation",
    "discrimination",
    "unsafe disclosure",
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
        if not any(token in lowered for token in CONFLICT_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: unresolved-conflict section must mention conflicting/disagreeing/incomplete official materials"
            )
        if not any(token in lowered for token in NOSYNTH_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: unresolved-conflict section must tell the reader not to synthesize/combine/infer a controlling answer"
            )
        if not any(token in lowered for token in STOP_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: unresolved-conflict section must say unresolved conflict is a stop condition before acting"
            )
        if not any(token in lowered for token in CONFIRM_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: unresolved-conflict section must route the reader to the authoritative office or `305` for case-specific confirmation"
            )
        if not any(token in lowered for token in RIGHTS_PATTERNS):
            errors.append(
                f"{p.relative_to(ROOT)}: unresolved-conflict section must preserve `307` as the rights/safety lane when needed"
            )

    missing_docs = sorted(doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"missing special-case surface docs: {missing_docs}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: special-case voter-facing surface unresolved-conflict stop minimums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
