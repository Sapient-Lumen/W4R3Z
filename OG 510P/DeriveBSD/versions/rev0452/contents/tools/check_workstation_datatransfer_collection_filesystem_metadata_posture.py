#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md": [
        "owner/group fidelity is **out of this lane entirely**",
        "mode-bit fidelity is **out of this lane entirely**",
        "mtime / last-modified fidelity is **out of this lane entirely**",
        "xattr / ACL / capability / other extended filesystem-metadata fidelity is **out of this lane entirely**",
    ],
    "adrs/ADR-0286-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md": [
        "owner/group fidelity is **out of this lane entirely**",
        "mode-bit fidelity is **out of this lane entirely**",
        "mtime / last-modified fidelity is **out of this lane entirely**",
        "xattr / ACL / capability / other extended filesystem-metadata fidelity is **out of this lane entirely**",
        "receiver-local realization detail",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep owner/mode/mtime/xattr fidelity out of this lane entirely",
        "receiver-local realization detail",
        "Standardize owner/mode/mtime/xattr fidelity later inside this same lane",
    ],
    "docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "stays out of this reviewed handoff lane entirely",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "filesystem-preserving archive format",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "filesystem-preserving archive format",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "filesystem-preserving archive format",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "filesystem-preservation policy",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "host-stat preservation story",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0286",
        "filesystem-metadata fidelity stay out of this lane entirely",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_filesystem_metadata_posture.py",
        "collection-filesystem-metadata-posture",
    ],
    "docs/99-llm-runbook.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "check_workstation_datatransfer_collection_filesystem_metadata_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zl) Reviewed selected-set handoff should not quietly become a filesystem-preserving archive format",
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
    ],
    "docs/00-index.md": [
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
        "filesystem-preserving archive format",
    ],
    "README.md": [
        "ADR-0286",
        "docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection filesystem-metadata posture check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection filesystem-metadata posture check passed")
