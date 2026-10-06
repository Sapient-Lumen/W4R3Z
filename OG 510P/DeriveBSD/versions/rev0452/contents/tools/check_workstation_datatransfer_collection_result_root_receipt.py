#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "pins the exact created fresh root",
    ],
    "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md": [
        "must pin the exact **created fresh destination root**",
        "pathless success prose or parent-only placement evidence is insufficient",
        "later rename/move/import/promote actions may mint their own receipts",
    ],
    "adrs/ADR-0281-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md": [
        "must pin the exact **created fresh destination root**",
        "parent-only success receipt is insufficient",
        "result root that was actually created",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep retrieve receipts exact on the created fresh destination root",
        "must pin the exact created fresh destination root",
        "Leave retrieve success pathless or parent-only in receipts",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "pin the exact created fresh root",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "exact created fresh root",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "exact created fresh root",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "pin the exact created fresh root",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "exact created fresh root",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0281",
        "exact created fresh root",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_result_root_receipt.py",
        "collection-result-root-receipt",
    ],
    "docs/99-llm-runbook.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "check_workstation_datatransfer_collection_result_root_receipt.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zg) Fresh-root retrieve should leave an exact result-root receipt",
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
    ],
    "docs/00-index.md": [
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
        "exact created fresh root",
    ],
    "README.md": [
        "ADR-0281",
        "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection result-root receipt check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection result-root receipt check passed")
