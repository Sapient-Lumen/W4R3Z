#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md": ["single-retrieve by default", "auto-stop after the first successful retrieve"],
    "adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md": ["single-retrieve by default", "auto-stops after the first successful retrieve"],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": ["single-retrieve by default", "auto-stop after the first successful retrieve", "no repeated-retrieve posture in the first cut"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "single-retrieve by default"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "auto-stop after the first successful retrieve"],
    "docs/410-desktop-viability-checklist.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "single-retrieve-by-default"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "auto-stopping"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "single-retrieve-by-default"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0264", "single-retrieve by default", "auto-stop after the first successful retrieve"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_finite_collection_autostop.py"],
    "docs/99-llm-runbook.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "check_workstation_datatransfer_finite_collection_autostop.py"],
    "docs/110-juicy-os-lessons.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "single-retrieve by default"],
    "docs/00-index.md": ["docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md", "check_workstation_datatransfer_finite_collection_autostop.py"],
    "README.md": ["ADR-0264", "docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md"],
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
    print("Workstation data-transfer finite-collection-autostop check FAILED", file=sys.stderr)
    for err in errors:
        print(f" - {err}", file=sys.stderr)
    sys.exit(1)

print("Workstation data-transfer finite-collection-autostop checks: OK")
