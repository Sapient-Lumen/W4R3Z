#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md": ["regular files", "explicit directories", "symlinks are not part of the first cut", "special filesystem objects are not part of the first cut"],
    "adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md": ["symlinks are not part of the first cut", "special filesystem objects are not part of the first cut", "fail closed"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["regular-file manifest entries", "explicit directory manifest entries", "unsupported member kinds must fail closed", "No symlink, device-node, FIFO, or socket member semantics are part of the first cut."],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md", "rejects symlinks and special files"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md", "regular-files-plus-explicit-directories only"],
    "docs/410-desktop-viability-checklist.md": ["docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md", "regular-files-plus-explicit-directories only"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md", "fail closed on symlink or special-file members"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md", "rejects symlinks and special files"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0268", "regular-files-plus-explicit-directories only", "symlink/special-file semantics"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_collection_member_kind_floor.py"],
    "docs/99-llm-runbook.md": ["docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md", "check_workstation_datatransfer_collection_member_kind_floor.py"],
    "docs/110-juicy-os-lessons.md": ["ADR-0268", "regular-files-plus-explicit-directories only"],
    "docs/00-index.md": ["docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md", "check_workstation_datatransfer_collection_member_kind_floor.py"],
    "README.md": ["ADR-0268", "docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md"],
}


def main() -> int:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        text = (ROOT / rel).read_text()
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing token {token!r}")
    if errors:
        print("workstation data-transfer collection member-kind floor check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection member-kind floor check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
