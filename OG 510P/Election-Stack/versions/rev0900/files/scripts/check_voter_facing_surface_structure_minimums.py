#!/usr/bin/env python3
"""Check standard section structure for promoted voter-facing family-tail docs and any newer high-risk rows below that tail."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
UPPER_BAND_START = 335
CONTROL_TAG = "special_case_high_risk"
SPECIAL_LOWER_BAND_CUTOFF = 323

DYNAMIC_PAYLOAD_RE = re.compile(r"^## What belongs in the public .+ payload$", re.M)
REQUIRED_HEADINGS = [
    "## Why this exists (bounded)",
    "## Minimal claim-set",
    "## Canonical digest artifacts",
    "## Relationship to adjacent surfaces and non-overlap rules",
    "## Safe fallback and escalation boundaries",
    "## Temporal volatility, freshness, and no-cross-jurisdiction rules",
    "## Accessibility, language, and next-step clarity",
    "## Verification questions for captures and audits",
    "## Minimal artifacts in this archive",
]
SOURCE_HEADING_RE = re.compile(
    r"^## Sources \((?:authoritative public examples|official route examples; not current voter instruction)\)$",
    re.M,
)


def main() -> int:
    table = load_surface_registry()
    special_ids = tagged_surface_doc_ids(table, CONTROL_TAG)
    extra_ids = {doc_id for doc_id in special_ids if doc_id < SPECIAL_LOWER_BAND_CUTOFF}
    rows = []
    for row in table.rows:
        if not any(row.values()):
            continue
        doc_id = int(row["doc_id"])
        if doc_id < UPPER_BAND_START and doc_id not in extra_ids:
            continue
        rows.append((doc_id, row["doc_path"]))

    errors: list[str] = []
    for doc_id, rel in rows:
        p = ROOT / rel
        if not p.exists():
            errors.append(f"missing voter-facing family-tail doc {doc_id}: {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            if heading not in text:
                errors.append(f"{p.relative_to(ROOT)}: missing required section heading: {heading}")
        if not SOURCE_HEADING_RE.search(text):
            errors.append(
                f"{p.relative_to(ROOT)}: missing required Sources heading: "
                "authoritative public examples or official route examples; not current voter instruction"
            )
        if not DYNAMIC_PAYLOAD_RE.search(text):
            errors.append(
                f"{p.relative_to(ROOT)}: missing dynamic payload section heading matching '## What belongs in the public ... payload'"
            )

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    doc_labels = ", ".join(str(doc_id) for doc_id, _ in rows)
    print(
        "PASS: voter-facing structure minimums "
        f"(registry-selected docs {doc_labels} carry the standard bounded-surface sections)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
