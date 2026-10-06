#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md": [
        "selected roots prefix-free",
        "overlap-free antichain",
        "no silent subsumption",
    ],
    "adrs/ADR-0275-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md": [
        "overlap-free antichain",
        "hidden local review memory",
        "fail closed",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep accepted selected roots overlap-free and non-subsuming",
        "overlap-free antichain",
        "must not silently",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
        "selected roots overlap-free",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
        "selected roots overlap-free",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
        "ancestor/descendant root overlap must fail closed",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
        "selected-root overlap-free",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
        "no silent subsumption",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0275",
        "selected roots overlap-free",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_selected_roots.py",
        "collection-selected-roots",
    ],
    "docs/99-llm-runbook.md": [
        "check_workstation_datatransfer_collection_selected_roots.py",
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90za) The first richer finite-collection handoff should keep selected roots overlap-free",
        "showDirectoryPicker",
        "ACTION_OPEN_DOCUMENT_TREE",
    ],
    "docs/32-curated-references.md": [
        "WICG File System Access / showDirectoryPicker",
        "Android shared-storage documents/files guide (`ACTION_OPEN_DOCUMENT_TREE` directory-tree access behavior)",
    ],
    "docs/00-index.md": [
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
        "check_workstation_datatransfer_collection_selected_roots.py",
    ],
    "README.md": [
        "ADR-0275",
        "docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md",
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
        print("workstation data-transfer collection selected-roots check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection selected-roots check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
