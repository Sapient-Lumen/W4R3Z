#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "receiver-local stable result-root handle",
    ],
    "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "display-path snapshot remains descriptive rather than authoritative",
    ],
    "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md": [
        "receiver-local stable result-root handle",
        "authoritative local result locator",
        "display-path snapshot",
    ],
    "adrs/ADR-0283-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md": [
        "receiver-local stable result-root handle",
        "authoritative local result locator",
        "mutable path string",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep result-root locator handle-first and display-path snapshots advisory",
        "receiver-local stable result-root handle",
        "Make mutable path text the authoritative local result locator",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "receiver-local stable result-root handle",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "authoritative local result locator",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "receiver-local stable result-root handle",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "display-path snapshot",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "receiver-local stable result-root handle",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0283",
        "result-root locator posture",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_result_root_locator_posture.py",
        "collection-result-root-locator-posture",
    ],
    "docs/99-llm-runbook.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "check_workstation_datatransfer_collection_result_root_locator_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zi) Result-root evidence should be handle-first, not path-string folklore",
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
    ],
    "docs/00-index.md": [
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
        "receiver-local stable result-root handle",
    ],
    "README.md": [
        "ADR-0283",
        "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection result-root locator posture check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection result-root locator posture check passed")
