#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "adrs/ADR-0288-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md": [
        "ui.collection.handoff.grant",
        "ui.collection.handoff.manifest",
        "ui.collection.handoff.receipt",
        "first spec stack",
    ],
    "docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md": [
        "ui.collection.handoff.grant",
        "ui.collection.handoff.manifest",
        "ui.collection.handoff.receipt",
        "spec/ui.collection.handoff.grant.schema.json",
        "spec/ui.collection.handoff.manifest.schema.json",
        "spec/ui.collection.handoff.receipt.schema.json",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "ui.collection.handoff.grant",
        "ui.collection.handoff.manifest",
        "ui.collection.handoff.receipt",
        "docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md",
    ],
    "docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md": [
        "docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md",
        "ui.collection.handoff.grant",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_artifact_family_contract.py",
        "ui.collection.handoff.*",
    ],
    "docs/99-llm-runbook.md": [
        "docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md",
        "check_workstation_datatransfer_collection_artifact_family_contract.py",
    ],
    "docs/00-index.md": [
        "docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md",
        "ui.collection.handoff.grant",
    ],
    "docs/110-juicy-os-lessons.md": [
        "docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md",
        "ui.collection.handoff.manifest",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0288",
        "ui.collection.handoff.grant",
    ],
    "README.md": [
        "ADR-0288",
        "ui.collection.handoff.*",
    ],
}

SPEC_FILES = [
    "spec/ui.collection.handoff.grant.schema.json",
    "spec/ui.collection.handoff.manifest.schema.json",
    "spec/ui.collection.handoff.receipt.schema.json",
    "spec/examples/ui.collection.handoff.grant.json",
    "spec/examples/ui.collection.handoff.manifest.json",
    "spec/examples/ui.collection.handoff.receipt.json",
]

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

for rel in SPEC_FILES:
    if not (ROOT / rel).exists():
        errors.append(f"missing required artifact-family file: {rel}")

if errors:
    print("workstation data-transfer collection artifact-family contract check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection artifact-family contract check passed")
