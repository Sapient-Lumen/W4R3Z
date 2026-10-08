#!/usr/bin/env python3
"""Revision helper for rev0196.

This archive revision adds one Resilio comparison document and four interface specs
about discovery basis, pairwise route truth, least-widening connectivity repair,
and disclosure-changing route toggles.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_DOCS = [
    "406-resilio-discovery-basis-route-eligibility-and-observer-delta-evaluation.md",
    "407-reachability-basis-page-discovery-lane-publication-audience-and-route-class-interface-spec.md",
    "408-peer-route-page-discovery-source-directness-relay-fallback-and-path-proof-interface-spec.md",
    "409-connectivity-repair-page-tracker-lan-predefined-host-and-listener-ladder-interface-spec.md",
    "410-exposure-widening-review-page-discovery-change-observer-delta-and-cache-clearance-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_DOCS if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing expected rev0196 docs: {missing}")
    print("rev0196 archive looks structurally complete.")
