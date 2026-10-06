#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md": [
        "authoritative manifest ancestor-closed",
        "every proper parent path",
        "not silently synthesize missing parent directories",
    ],
    "adrs/ADR-0274-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md": [
        "authoritative manifest is **ancestor-closed**",
        "every proper parent path",
        "not silently synthesize missing parent directories",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep manifest ancestry explicit and ancestor-closed",
        "every proper parent path",
        "must not silently synthesize missing parent directories",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
        "authoritative manifest ancestor-closed",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
        "authoritative manifest ancestor-closed",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
        "parent directories explicit reviewed structural state",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
        "ancestor-closed",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
        "implicit parent synthesis",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0274",
        "ancestor-only directory rows",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_ancestor_closure.py",
        "collection-ancestor-closure",
    ],
    "docs/99-llm-runbook.md": [
        "check_workstation_datatransfer_collection_ancestor_closure.py",
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90z) The first richer finite-collection handoff should make parent directories explicit",
        "Restoring Intermediate Directories",
        "ZIP files created by distutils will now include entries for directories",
    ],
    "docs/32-curated-references.md": [
        "GNU tar manual: Restoring Intermediate Directories",
        "Python changelog: ZIP files created by distutils will now include entries for directories",
    ],
    "docs/00-index.md": [
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
        "check_workstation_datatransfer_collection_ancestor_closure.py",
    ],
    "README.md": [
        "ADR-0274",
        "docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md",
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
        print("workstation data-transfer collection ancestor-closure check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection ancestor-closure check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
