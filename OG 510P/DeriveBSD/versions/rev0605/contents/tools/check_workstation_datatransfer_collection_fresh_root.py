#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md": [
        "fresh destination root",
        "no silent merge",
        "same bytes already there",
    ],
    "adrs/ADR-0276-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md": [
        "fresh destination root",
        "same-bytes reuse",
        "fail closed",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep retrieve fresh-rooted and no-silent-merge into existing tree",
        "fresh destination root",
        "must not silently",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
        "fresh-rooted retrieve",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
        "fresh destination root",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
        "silent merge into an existing tree",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
        "fresh-rooted retrieve",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
        "no silent merge into an existing tree",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0276",
        "fresh destination root",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_fresh_root.py",
        "collection-fresh-root",
    ],
    "docs/99-llm-runbook.md": [
        "check_workstation_datatransfer_collection_fresh_root.py",
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zb) The first richer finite-collection handoff should retrieve into a fresh root",
        "ACTION_CREATE_DOCUMENT cannot overwrite an existing file",
        "org.freedesktop.portal.FileTransfer.RetrieveFiles",
    ],
    "docs/32-curated-references.md": [
        "Android shared-storage documents/files guide (`ACTION_CREATE_DOCUMENT` cannot overwrite an existing file; same-name save appends a numeric suffix)",
        "XDG Desktop Portal: FileTransfer portal (brokered drag&drop/copy-paste export)",
    ],
    "docs/00-index.md": [
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
        "check_workstation_datatransfer_collection_fresh_root.py",
    ],
    "README.md": [
        "ADR-0276",
        "docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md",
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing token {token!r}")
    if errors:
        print("workstation data-transfer collection fresh-root check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection fresh-root check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
