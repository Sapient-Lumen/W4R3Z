#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "bounded deterministic path-compression",
    ],
    "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md": [
        "trusted review UIs may visually path-compress deterministic ancestor-only directory runs",
        "authoritative manifest remains **fully explicit and ancestor-closed**",
        "later explicit RFC/ADR cut",
    ],
    "adrs/ADR-0279-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md": [
        "authoritative manifest remains fully explicit and ancestor-closed",
        "trusted review UIs **may** visually path-compress **deterministic ancestor-only directory runs**",
        "later explicit RFC/ADR cut",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep authoritative manifest explicit while allowing bounded path-compressed review presentation",
        "may visually path-compress deterministic ancestor-only directory runs",
        "must be able to reveal the full explicit rows",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "deterministic path-compression for ancestor-only directory runs",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "bounded path-compression of deterministic ancestor-only directory runs",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "path-compress deterministic ancestor-only directory runs",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "bounded path-compression of deterministic ancestor-only directory runs",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "collapsed display never replaces the explicit manifest",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0279",
        "bounded path-compression of deterministic ancestor-only runs",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_review_ui_path_compression.py",
        "collection-review-ui-path-compression",
    ],
    "docs/99-llm-runbook.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "check_workstation_datatransfer_collection_review_ui_path_compression.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90ze) Explicit reviewed trees may still deserve bounded path compression",
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
    ],
    "docs/00-index.md": [
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
        "ancestor-only directory runs",
    ],
    "README.md": [
        "ADR-0279",
        "docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection review-ui-path-compression check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection review-ui-path-compression check passed")
