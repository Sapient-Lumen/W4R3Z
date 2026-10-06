#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md": ["manifest-first", "tree/collection digest", "explicit per-member manifest"],
    "adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md": ["manifest-first", "explicit per-member manifest", "supplementary summary evidence"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["explicit per-member manifest", "supplementary summary evidence", "tree-digest-only"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "manifest-first reviewed membership"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "explicit per-member manifest"],
    "docs/410-desktop-viability-checklist.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "manifest-first reviewed membership"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "per-member manifest"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "manifest-first reviewed membership"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0266", "manifest-first", "tree/collection digest"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_collection_manifest_posture.py"],
    "docs/99-llm-runbook.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "check_workstation_datatransfer_collection_manifest_posture.py"],
    "docs/110-juicy-os-lessons.md": ["ADR-0266", "explicit per-member manifest"],
    "docs/00-index.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "check_workstation_datatransfer_collection_manifest_posture.py"],
    "README.md": ["docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md", "manifest-first reviewed membership"],
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
        print("workstation data-transfer collection manifest posture check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection manifest posture check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
