#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "aimed first at **B/C/D** practical file-handoff pressure",
    ],
    "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md": [
        "supported profile scope is **B/C/D**",
        "**A / fleet_host** does **not** treat this lane as a baseline supported workflow",
        "distinct later RFC/ADR lane",
    ],
    "adrs/ADR-0277-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md": [
        "supported profile scope is **B/C/D**, not **A**",
        "not a fleet-host baseline",
        "distinct later RFC/ADR lane",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep the lane profiled to B/C/D and out of fleet-host baseline",
        "supported for **B/C/D**, not **A**",
        "distinct later RFC/ADR lane",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "B/C/D-only richer lane",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "explicitly out of fleet-host baseline",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "keep A on rollout/support/import-export lanes instead",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "out of fleet-host baseline",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "A should stay on artifacted rollout/support/import/export lanes",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0277",
        "B/C/D-only richer lane",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_profile_scope.py",
        "collection-profile-scope",
    ],
    "docs/99-llm-runbook.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "check_workstation_datatransfer_collection_profile_scope.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zc) The first richer finite-collection handoff should stay out of fleet hosts",
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
    ],
    "docs/00-index.md": [
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
        "becoming a fleet-host baseline",
    ],
    "README.md": [
        "ADR-0277",
        "docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection profile-scope check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection profile-scope check passed")
