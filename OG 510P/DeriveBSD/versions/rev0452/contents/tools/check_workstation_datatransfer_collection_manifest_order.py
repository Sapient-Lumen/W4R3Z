#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md": ["strict ascending bytewise order of normalized review path", "locale-independent", "duplicate normalized review paths"],
    "adrs/ADR-0270-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md": ["canonicalized by normalized review path", "strict ascending bytewise order", "locale-independent", "duplicate normalized review paths"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["Keep authoritative manifest order canonical and duplicate-free", "strict ascending bytewise order of normalized review path", "locale-independent", "duplicate normalized review paths must fail closed"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md", "normalized review path"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md", "normalized review path"],
    "docs/410-desktop-viability-checklist.md": ["docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md", "duplicate normalized review paths"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md", "strict ascending bytewise order"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md", "strict ascending bytewise order"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0270", "duplicate normalized review paths fail closed"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_collection_manifest_order.py"],
    "docs/99-llm-runbook.md": ["docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md", "check_workstation_datatransfer_collection_manifest_order.py"],
    "docs/110-juicy-os-lessons.md": ["ADR-0270", "canonical review-path order"],
    "docs/00-index.md": ["docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md", "check_workstation_datatransfer_collection_manifest_order.py"],
    "README.md": ["ADR-0270", "docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md"],
}


def main() -> int:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        text = (ROOT / rel).read_text()
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing token {token!r}")
    if errors:
        print("workstation data-transfer collection manifest-order check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection manifest-order check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
