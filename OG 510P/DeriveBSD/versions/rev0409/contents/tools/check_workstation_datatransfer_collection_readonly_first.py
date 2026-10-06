#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md": ["read-only only", "write-enabled receive", "follow-on RFC/ADR decision"],
    "adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md": ["read-only only", "write-enabled receive", "follow-on RFC/ADR decision"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["read-only only", "No write-enabled receive exception is part of the first cut.", "follow-on RFC/ADR decision"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "read-only only"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "read-only only"],
    "docs/410-desktop-viability-checklist.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "read-only only"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "read-only only"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "read-only only"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0267", "read-only only", "write-enabled receive"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_collection_readonly_first.py"],
    "docs/99-llm-runbook.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "check_workstation_datatransfer_collection_readonly_first.py"],
    "docs/110-juicy-os-lessons.md": ["ADR-0267", "read-only only"],
    "docs/00-index.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "check_workstation_datatransfer_collection_readonly_first.py"],
    "README.md": ["docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md", "read-only only"],
}


def main() -> int:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        text = (ROOT / rel).read_text()
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing token {token!r}")
    if errors:
        print("workstation data-transfer collection readonly-first check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("workstation data-transfer collection readonly-first check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
