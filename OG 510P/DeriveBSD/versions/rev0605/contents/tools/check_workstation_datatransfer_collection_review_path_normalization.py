#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md": [
        "collection-relative UTF-8 text path normalized to Unicode NFC",
        "`/` is the only separator",
        "no leading slash",
        "no trailing slash",
        "fail closed",
    ],
    "adrs/ADR-0272-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md": [
        "collection-relative identity path",
        "Unicode NFC",
        "no `.` or `..` segments",
        "fail closed",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "normalized review paths stay collection-relative, clean slash-separated Unicode NFC text",
        "no leading/trailing slash",
        "no empty or dot segments",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
        "collection-relative clean slash-separated Unicode NFC review paths",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
        "collection-relative clean slash-separated Unicode NFC review paths",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
        "collection-relative clean slash-separated Unicode NFC review paths",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
        "collection-relative clean slash-separated Unicode NFC review paths",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
        "collection-relative clean slash-separated Unicode NFC",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0272",
        "collection-relative clean slash-separated Unicode NFC identity paths",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_review_path_normalization.py",
        "collection-review-path-normalization",
    ],
    "docs/99-llm-runbook.md": [
        "check_workstation_datatransfer_collection_review_path_normalization.py",
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90x) The first richer finite-collection handoff should canonicalize review paths before hashing them",
        "Unicode NFC",
        "APFS",
    ],
    "docs/32-curated-references.md": [
        "Unicode Standard Annex #15",
        "APFS FAQ",
    ],
    "docs/00-index.md": [
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
        "check_workstation_datatransfer_collection_review_path_normalization.py",
    ],
    "README.md": [
        "ADR-0272",
        "docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md",
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
        print("workstation data-transfer collection review-path-normalization check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection review-path-normalization check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
