#!/usr/bin/env python3
"""Guardrail for keeping supplementary breakglass adapter-side evidence receipt-first when exported."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    schema = load_json("spec/incident.bundle.schema.json")
    includes = ((schema.get("properties") or {}).get("includes") or {}).get("properties") or {}

    extra_desc = (includes.get("extra") or {}).get("description") or ""
    for needle in [
        "receipt-first",
        "`redaction.receipt` / `export.receipt` / `transport.receipt` evidence digests",
        "raw case attachment handles or ticket prose",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "receipt-first",
        "supplementary side evidence",
        "raw external handles",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    doc_checks = {
        "adrs/ADR-0302-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md": [
            "receipt-first",
            "redaction.receipt",
            "export.receipt",
            "transport.receipt",
            "raw ticket attachment ids",
        ],
        "docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md": [
            "receipt-first",
            "transport.acceptance.receipt",
            "raw attachment, portal object id, visible upload handle, or ticket prose",
            "tools/check_breakglass_adapter_export_receipt_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "receipt-first on typed `redaction.receipt` / `export.receipt` / `transport.receipt` evidence digests",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "receipt-first on typed redaction/export/transport receipts",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "supplementary adapter/runtime exports receipt-first on typed redaction/export/transport evidence",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "receipt-first on matching redaction/export/transport evidence digests",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "receipt-first on typed export/redaction/transport proof",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "receipt-first on typed redaction/export/transport proof",
        ],
        "docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md": [
            "receipt-first on typed export/redaction/transport receipts",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0302",
            "receipt-first on typed export/redaction/transport proof",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_export_receipt_boundary.py",
            "receipt-first when exported",
        ],
        "docs/99-llm-runbook.md": [
            "docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md",
            "tools/check_breakglass_adapter_export_receipt_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md",
            "tools/check_breakglass_adapter_export_receipt_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "receipt-first",
            "docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md",
        ],
        "docs/32-curated-references.md": [
            "Dell iDRAC virtual-console / virtual-media security guidance",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Breakglass adapter export receipt boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
