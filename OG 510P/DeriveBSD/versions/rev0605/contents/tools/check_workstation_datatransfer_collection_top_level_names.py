#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md": [
        "top-level reviewed names as explicit reviewed state",
        "explicit reviewed aliases or fail closed",
        "must not silently",
    ],
    "adrs/ADR-0273-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md": [
        "top-level reviewed names are **reviewed state**",
        "synthetic common wrapper root",
        "fail closed",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep top-level reviewed names explicit and collision-safe",
        "must not silently inject a synthetic wrapper root",
        "explicit reviewed alias",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
        "no silent auto-rename or wrapper-root repair",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
        "no silent auto-rename or wrapper-root repair",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
        "no silent auto-rename or wrapper-root repair",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
        "reviewed top-level names",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
        "wrapper-root repair",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0273",
        "silent auto-rename or wrapper-root repair",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_top_level_names.py",
        "collection-top-level-names",
    ],
    "docs/99-llm-runbook.md": [
        "check_workstation_datatransfer_collection_top_level_names.py",
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90y) The first richer finite-collection handoff should keep top-level names explicit",
        "synthetic wrapper root",
        "GNU tar",
    ],
    "docs/32-curated-references.md": [
        "POSIX ar utility",
        "GNU tar manual: multiple members with the same name",
    ],
    "docs/00-index.md": [
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
        "check_workstation_datatransfer_collection_top_level_names.py",
    ],
    "README.md": [
        "ADR-0273",
        "docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md",
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
        print("workstation data-transfer collection top-level-names check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection top-level-names check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
