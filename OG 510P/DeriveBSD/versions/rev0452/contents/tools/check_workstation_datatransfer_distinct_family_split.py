#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md": ["distinct artifact families", "ui.datatransfer.grant", "ui.datatransfer.receipt"],
    "adrs/ADR-0262-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md": ["distinct artifact family", "ui.datatransfer.grant", "ui.datatransfer.receipt"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md", "distinct artifact family"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md", "distinct family"],
    "docs/410-desktop-viability-checklist.md": ["docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md", "distinct artifact families"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md", "distinct artifact family"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md", "distinct artifact family"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0262", "distinct artifact family"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_distinct_family_split.py"],
    "docs/99-llm-runbook.md": ["docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md", "check_workstation_datatransfer_distinct_family_split.py"],
    "docs/110-juicy-os-lessons.md": ["ADR-0262", "docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md"],
    "README.md": ["ADR-0262", "docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md"],
}

EXPECTED_SCHEMA_FILES = [
    "spec/ui.datatransfer.grant.schema.json",
    "spec/ui.datatransfer.receipt.schema.json",
]

EXPECTED_EXAMPLE_FILES = [
    "spec/examples/ui.datatransfer.grant.json",
    "spec/examples/ui.datatransfer.grant.ocr-inspection-text.json",
    "spec/examples/ui.datatransfer.grant.retry.json",
    "spec/examples/ui.datatransfer.receipt.json",
    "spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json",
]

EXPECTED_RECEIPT_PROPERTIES = [
    "kind",
    "receipt_version",
    "lease_id",
    "subject",
    "offer_source_subject",
    "direction",
    "offer_id",
    "summary",
    "grant_exhausted",
    "transferred_at",
    "signature",
    "grant_digest",
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

grant = json.loads((ROOT / "spec/ui.datatransfer.grant.schema.json").read_text())
receipt = json.loads((ROOT / "spec/ui.datatransfer.receipt.schema.json").read_text())

for path, obj in [
    ("spec/ui.datatransfer.grant.schema.json", grant),
    ("spec/ui.datatransfer.receipt.schema.json", receipt),
]:
    description = obj.get("description", "")
    for token in ["ordinary", "distinct artifact families"]:
        if token not in description:
            errors.append(f"{path}: description missing {token!r}")

if grant.get("properties", {}).get("kind", {}).get("const") != "ui-datatransfer-grant":
    errors.append("spec/ui.datatransfer.grant.schema.json: kind const drifted")
if receipt.get("properties", {}).get("kind", {}).get("const") != "ui-datatransfer-receipt":
    errors.append("spec/ui.datatransfer.receipt.schema.json: kind const drifted")

receipt_properties = list(receipt.get("properties", {}).keys())
if receipt_properties != EXPECTED_RECEIPT_PROPERTIES:
    errors.append(
        "spec/ui.datatransfer.receipt.schema.json: top-level properties drifted: "
        f"expected {EXPECTED_RECEIPT_PROPERTIES!r}, got {receipt_properties!r}"
    )

if receipt.get("additionalProperties", True) is not False:
    errors.append("spec/ui.datatransfer.receipt.schema.json: root additionalProperties must be false")

schema_files = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("spec/ui.datatransfer*.schema.json"))
if schema_files != EXPECTED_SCHEMA_FILES:
    errors.append(
        "ui.datatransfer schema family drifted: "
        f"expected {EXPECTED_SCHEMA_FILES!r}, got {schema_files!r}"
    )

example_files = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("spec/examples/ui.datatransfer*.json"))
if example_files != EXPECTED_EXAMPLE_FILES:
    errors.append(
        "ui.datatransfer example family drifted: "
        f"expected {EXPECTED_EXAMPLE_FILES!r}, got {example_files!r}"
    )

if errors:
    print("Workstation data-transfer distinct-family-split check FAILED", file=sys.stderr)
    for err in errors:
        print(f" - {err}", file=sys.stderr)
    sys.exit(1)

print("Workstation data-transfer distinct-family-split checks: OK")
