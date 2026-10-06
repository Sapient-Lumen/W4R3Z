#!/usr/bin/env python3
"""Guardrail for the workstation cross-domain data-transfer floor."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "ambient shared clipboard",
        "single-delivery by default",
        "cross-domain drag&drop is not baseline",
        "delivery_mode",
        "grant was exhausted",
    ],
    "adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md": [
        "ambient shared clipboard",
        "single-delivery by default",
        "ui.datatransfer.grant",
        "ui.datatransfer.receipt",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/538-workstation-cross-domain-datatransfer-floor.md",
        "no ambient shared clipboard",
        "delivery_mode",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "no ambient shared cross-domain sync",
        "typed receipts",
        "docs/538-workstation-cross-domain-datatransfer-floor.md",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "clipboard/file-transfer broker UX",
        "no ambient shared clipboard",
        "docs/538-workstation-cross-domain-datatransfer-floor.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0128",
        "no ambient shared cross-domain clipboard",
        "cross-domain drag&drop as a baseline requirement",
    ],
    "docs/99-llm-runbook.md": [
        "docs/538-workstation-cross-domain-datatransfer-floor.md",
        "check_workstation_datatransfer_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_boundary.py",
        "no-ambient-shared-clipboard",
    ],
    "docs/110-juicy-os-lessons.md": [
        "inter-qube clipboard clears on delivery",
        "docs/538-workstation-cross-domain-datatransfer-floor.md",
    ],
    "spec/ui.datatransfer.grant.schema.json": [
        '"delivery_mode"',
        '"single-delivery"',
        '"multi-delivery"',
    ],
    "spec/ui.datatransfer.receipt.schema.json": [
        '"grant_exhausted"',
    ],
    "spec/examples/ui.datatransfer.grant.json": [
        '"delivery_mode": "single-delivery"',
    ],
    "spec/examples/ui.datatransfer.receipt.json": [
        '"grant_exhausted": true',
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation data-transfer boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
