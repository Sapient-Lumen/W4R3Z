#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md": ["normalized review path", "payload digest", "byte length", "not required first-cut manifest fields"],
    "adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md": ["smallest exact per-member field set", "normalized review path", "payload digest", "byte length"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["normalized review path", "exact member kind", "exact payload digest", "exact byte length", "Richer stat fidelity should come back only as a later explicit RFC decision"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "payload digest + byte length"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "payload digest + byte length"],
    "docs/410-desktop-viability-checklist.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "normalized review path"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "stat-light manifest floor"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "path/kind/payload identity"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0269", "advisory MIME type", "owner/mode/mtime/xattr fidelity"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_collection_manifest_field_floor.py"],
    "docs/99-llm-runbook.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "check_workstation_datatransfer_collection_manifest_field_floor.py"],
    "docs/110-juicy-os-lessons.md": ["ADR-0269", "path/kind/payload identity"],
    "docs/00-index.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "check_workstation_datatransfer_collection_manifest_field_floor.py"],
    "README.md": ["docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md", "stat-light manifest floor"],
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
        print("workstation data-transfer collection manifest-field-floor check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection manifest-field-floor check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
