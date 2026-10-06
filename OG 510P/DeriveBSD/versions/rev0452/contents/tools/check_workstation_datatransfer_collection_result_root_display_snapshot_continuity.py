#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "retrieve-frozen advisory display snapshot",
    ],
    "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md": [
        "retrieve-time snapshot",
        "retrieve-frozen",
        "later local rename/move/import/promote actions do **not** silently rewrite it in place",
        "successor observations",
    ],
    "adrs/ADR-0284-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md": [
        "retrieve-time snapshot",
        "retrieve-frozen",
        "later local rename/move/import/promote actions do **not** silently rewrite it in place",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep advisory display snapshots retrieve-frozen when present",
        "retrieve-time snapshot",
        "Rewrite the original advisory display snapshot after later local rename or move",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "retrieve-frozen advisory display snapshot",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "retrieve-frozen advisory display snapshot",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "retrieve-frozen advisory display snapshot",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "retrieve-frozen advisory display snapshot",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "retrieve-frozen advisory display snapshot",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0284",
        "display-snapshot continuity",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_result_root_display_snapshot_continuity.py",
        "collection-result-root-display-snapshot-continuity",
    ],
    "docs/99-llm-runbook.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "check_workstation_datatransfer_collection_result_root_display_snapshot_continuity.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zj) Advisory retrieve labels should stay retrieve-frozen, not become a moving current-location story",
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
    ],
    "docs/00-index.md": [
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
        "retrieve-frozen advisory display snapshot",
    ],
    "README.md": [
        "ADR-0284",
        "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection result-root display snapshot continuity check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection result-root display snapshot continuity check passed")
