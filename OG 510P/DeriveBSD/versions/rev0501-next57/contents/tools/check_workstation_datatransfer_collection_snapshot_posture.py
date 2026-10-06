#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md": ["snapshot-shaped", "not a live tree grant"],
    "adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md": ["snapshot-shaped", "not part of the first cut"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["finite reviewed directory snapshot semantics", "not live outward traversal of a source tree"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "snapshot-shaped reviewed membership"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "snapshot membership"],
    "docs/410-desktop-viability-checklist.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "reviewed finite snapshot membership"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "reviewed snapshot membership"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "snapshot-shaped reviewed membership"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0265", "snapshot membership"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_collection_snapshot_posture.py"],
    "docs/99-llm-runbook.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "check_workstation_datatransfer_collection_snapshot_posture.py"],
    "docs/110-juicy-os-lessons.md": ["ADR-0265", "snapshot-shaped reviewed membership"],
    "docs/00-index.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "check_workstation_datatransfer_collection_snapshot_posture.py"],
    "README.md": ["docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md", "snapshot-shaped reviewed membership"],
}


def main() -> int:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        path = ROOT / rel
        text = path.read_text()
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing token {token!r}")
    if errors:
        print("workstation data-transfer collection snapshot posture check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection snapshot posture check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
