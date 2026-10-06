#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "chooser hint or destination prompt authoritative",
    ],
    "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md": [
        "receiver-local advisory UI state",
        "not authoritative reviewed state",
        "sender-directed destination parent",
    ],
    "adrs/ADR-0282-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md": [
        "receiver-local advisory UI state",
        "not authoritative reviewed state",
        "sender-directed destination parent",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep placement hints advisory and receiver-local, not reviewed authority",
        "parent chooser, destination label, suggested folder, or save-into prompt",
        "Make parent chooser or sender-suggested destination placement authoritative",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "placement-authority seam",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "parent chooser or destination label",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "receiver-local advisory UI state",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "receiver-local advisory UI state",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "not authoritative reviewed state",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0282",
        "placement hints stay advisory and receiver-local",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_placement_hint_posture.py",
        "collection-placement-hint-posture",
    ],
    "docs/99-llm-runbook.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "check_workstation_datatransfer_collection_placement_hint_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zh) Receiver placement hints should stay local advisory state",
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
    ],
    "docs/00-index.md": [
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
        "receiver-local advisory UI state",
    ],
    "README.md": [
        "ADR-0282",
        "docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection placement-hint posture check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection placement-hint posture check passed")
