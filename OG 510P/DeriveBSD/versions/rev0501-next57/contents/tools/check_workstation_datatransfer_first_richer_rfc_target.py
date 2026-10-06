#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md": ["reviewed finite collection handoff", "RFC-0194", "read-only only in the first cut"],
    "adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md": ["reviewed finite collection handoff", "B/C/D", "read-only by default"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["Status: draft", "finite selected set", "persistent document-tree authority", "read-only only"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md", "finite collection handoff"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md", "finite collection handoff"],
    "docs/410-desktop-viability-checklist.md": ["docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md", "read-only in the first cut"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md", "finite collection handoff"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md", "no persistent directory authority"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0263", "finite collection handoff", "RFC-0194"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_first_richer_rfc_target.py"],
    "docs/99-llm-runbook.md": ["docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md", "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md", "check_workstation_datatransfer_first_richer_rfc_target.py"],
    "docs/110-juicy-os-lessons.md": ["finite collection handoff", "docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md"],
    "docs/00-index.md": ["docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md", "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md"],
    "README.md": ["ADR-0263", "docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md"],
}

errors = []

for rel, tokens in DOC_TOKENS.items():
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing file: {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("Workstation data-transfer first-richer-RFC-target check FAILED", file=sys.stderr)
    for err in errors:
        print(f" - {err}", file=sys.stderr)
    sys.exit(1)

print("Workstation data-transfer first-richer-RFC-target checks: OK")
