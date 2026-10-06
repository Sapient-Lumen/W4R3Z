#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md": [
        "authoritative manifest digest",
        "sha256(utf8(JCS(authoritative_manifest)))",
        "tree/collection digests may still exist as **supplementary summary evidence**",
    ],
    "adrs/ADR-0271-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md": [
        "authoritative manifest digest",
        "canonical serialized authoritative per-member manifest",
        "sha256(utf8(JCS(authoritative_manifest)))",
        "tree/collection digests may still appear as **supplementary summary evidence**",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep authoritative collection identity digest-bound to the canonical manifest",
        "authoritative manifest digest",
        "sha256(utf8(JCS(authoritative_manifest)))",
        "Aggregate tree/collection digests may still exist as **supplementary summary evidence**",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
        "authoritative manifest digest",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
        "authoritative manifest digest",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
        "authoritative manifest digest",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
        "digest-bound to the canonical explicit manifest",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
        "digest-bound to the canonical explicit manifest",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0271",
        "authoritative manifest digest",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_manifest_digest.py",
    ],
    "docs/99-llm-runbook.md": [
        "check_workstation_datatransfer_collection_manifest_digest.py",
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
    ],
    "docs/110-juicy-os-lessons.md": [
        "ADR-0271",
        "sha256(utf8(JCS(authoritative_manifest)))",
    ],
    "docs/00-index.md": [
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
        "check_workstation_datatransfer_collection_manifest_digest.py",
    ],
    "README.md": [
        "ADR-0271",
        "docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md",
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
        print("workstation data-transfer collection manifest-digest check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection manifest-digest check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
