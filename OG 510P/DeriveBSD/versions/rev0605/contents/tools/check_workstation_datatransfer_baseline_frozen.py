#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md": ["frozen portable baseline", "complete enough to implement", "RFC-first"],
    "adrs/ADR-0261-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md": ["frozen portable baseline", "RFC-first", "not baseline"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md", "ordinary portable baseline", "RFC-first"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md", "ordinary portable baseline", "RFC-first"],
    "docs/410-desktop-viability-checklist.md": ["docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md", "frozen ordinary transfer baseline"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md", "RFC-first"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md", "ordinary portable lane"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0261", "frozen portable baseline", "RFC-first"],
    "docs/99-llm-runbook.md": ["docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md", "check_workstation_datatransfer_baseline_frozen.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_baseline_frozen.py"],
    "docs/110-juicy-os-lessons.md": ["Ordinary workstation transfer should freeze before richer lanes", "docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md"],
    "README.md": ["ADR-0261", "docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md"],
}

EXPECTED_PROPERTIES = [
    "kind",
    "grant_version",
    "lease_id",
    "subject",
    "offer_source_subject",
    "direction",
    "delivery_mode",
    "offer",
    "renewal_posture",
    "supersedes_grant_digest",
    "successor_scope_posture",
    "constraints",
    "effective_until",
    "issued_at",
    "signature",
]

EXAMPLE_PATHS = [
    "spec/examples/ui.datatransfer.grant.json",
    "spec/examples/ui.datatransfer.grant.retry.json",
]

errors = []

for rel, tokens in DOC_TOKENS.items():
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing file: {rel}")
        continue
    text = path.read_text()
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

schema = json.loads((ROOT / "spec/ui.datatransfer.grant.schema.json").read_text())
description = schema.get("description", "")
for token in ["ordinary workstation transfer baseline", "frozen", "RFC-first"]:
    if token not in description:
        errors.append(f"spec/ui.datatransfer.grant.schema.json: description missing {token!r}")

properties = list(schema.get("properties", {}).keys())
if properties != EXPECTED_PROPERTIES:
    errors.append(
        "spec/ui.datatransfer.grant.schema.json: top-level properties drifted: "
        f"expected {EXPECTED_PROPERTIES!r}, got {properties!r}"
    )

if schema.get("additionalProperties", True) is not False:
    errors.append("spec/ui.datatransfer.grant.schema.json: root additionalProperties must be false")

enum = schema.get("properties", {}).get("delivery_mode", {}).get("enum")
if enum != ["single-delivery", "multi-delivery"]:
    errors.append(
        "spec/ui.datatransfer.grant.schema.json: delivery_mode enum drifted: "
        f"got {enum!r}"
    )

allowed = set(EXPECTED_PROPERTIES)
for rel in EXAMPLE_PATHS:
    data = json.loads((ROOT / rel).read_text())
    extra = sorted(set(data.keys()) - allowed)
    if extra:
        errors.append(f"{rel}: found non-baseline top-level keys {extra!r}")

if errors:
    print("Workstation data-transfer baseline-frozen check FAILED", file=sys.stderr)
    for err in errors:
        print(f" - {err}", file=sys.stderr)
    sys.exit(1)

print("Workstation data-transfer baseline-frozen checks: OK")
