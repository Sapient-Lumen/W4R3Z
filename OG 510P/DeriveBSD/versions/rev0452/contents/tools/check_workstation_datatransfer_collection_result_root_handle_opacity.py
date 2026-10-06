#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md": [
        "opaque and non-path-shaped",
        "filesystem path, URI, sender-provided reviewed name, destination-label string",
        "bookmark ids, document ids, database keys, filesystem-handle adapters",
    ],
    "adrs/ADR-0285-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md": [
        "opaque and non-path-shaped",
        "filesystem path, URI, sender-provided reviewed name, destination-label string",
        "bookmark ids, document ids, database keys, filesystem-handle adapters",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep result-root handles opaque and non-path-shaped",
        "opaque and non-path-shaped",
        "Make the authoritative result-root handle a path string or URI",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0285",
        "result-root handle posture",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_result_root_handle_opacity.py",
        "collection-result-root-handle-opacity",
    ],
    "docs/99-llm-runbook.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "check_workstation_datatransfer_collection_result_root_handle_opacity.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zk) Handle-first only helps if the handle stays opaque and non-path-shaped",
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
    ],
    "docs/00-index.md": [
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
        "opaque and non-path-shaped",
    ],
    "README.md": [
        "ADR-0285",
        "docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection result-root handle opacity check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection result-root handle opacity check passed")
