#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "advisory MIME stays optional descriptive metadata and non-authoritative",
    ],
    "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md": [
        "advisory MIME stays **optional descriptive metadata**",
        "not authoritative reviewed identity",
        "later explicit RFC/ADR cut",
    ],
    "adrs/ADR-0280-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md": [
        "advisory MIME stays **optional descriptive metadata**",
        "not authoritative reviewed identity",
        "distinct later RFC/ADR cut",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep advisory MIME optional and non-authoritative",
        "Advisory MIME stays optional descriptive metadata and must not become authoritative reviewed identity",
        "Make advisory MIME mandatory for this lane",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "advisory MIME stays optional descriptive metadata rather than a mandatory reviewed field",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "advisory MIME stays optional descriptive metadata",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "advisory MIME stays optional descriptive metadata",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "advisory MIME stays optional descriptive metadata",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "advisory MIME remains descriptive and non-authoritative",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0280",
        "advisory MIME stays optional and non-authoritative",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_mime_posture.py",
        "collection-mime-posture",
    ],
    "docs/99-llm-runbook.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "check_workstation_datatransfer_collection_mime_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zf) Optional MIME hints should not become reviewed identity",
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
    ],
    "docs/00-index.md": [
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
        "advisory MIME now stays optional descriptive metadata",
    ],
    "README.md": [
        "ADR-0280",
        "docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection MIME posture check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection MIME posture check passed")
