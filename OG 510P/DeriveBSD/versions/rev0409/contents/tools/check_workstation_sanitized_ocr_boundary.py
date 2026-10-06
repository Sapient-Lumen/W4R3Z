#!/usr/bin/env python3
"""Guardrail for workstation OCR/searchable sanitized-derivative posture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md": [
        "flat visual derivative",
        "explicit secondary derivative",
        "inspection-shaped",
        "disposable-first",
        "ocr-inspection-derivative",
    ],
    "adrs/ADR-0245-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md": [
        "explicit secondary derivative",
        "flat visual derivative",
        "OCR/searchable derivatives remain inspection-shaped and disposable-first",
    ],
    "docs/267-sanitization-portal-and-disposable-sandboxes.md": [
        "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md",
        "flat visual derivative",
        "explicit secondary derivative",
    ],
    "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md": [
        "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md",
        "flat visual derivative",
        "OCR/searchable reconstruction",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md",
        "ocr-inspection-derivative",
    ],
    "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md": [
        "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md",
        "ocr-inspection-derivative",
        "not yet a baseline working-copy source",
    ],
    "docs/99-llm-runbook.md": [
        "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md",
        "check_workstation_sanitized_ocr_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_sanitized_ocr_boundary.py",
        "sanitized-ocr boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Searchable OCR on sanitized documents should stay explicit and secondary",
        "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md",
    ],
    "README.md": [
        "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md",
        "explicit secondary derivative",
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    plan = json.loads((ROOT / "spec" / "examples" / "content.ocr-inspection.plan.json").read_text(encoding="utf-8"))
    if ((plan.get("source") or {}).get("source_class")) != "sanitized-inspection-derivative":
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep source.source_class=sanitized-inspection-derivative")
    if ((plan.get("ocr") or {}).get("derivative_posture")) != "explicit-secondary-derivative":
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep ocr.derivative_posture=explicit-secondary-derivative")
    if ((plan.get("boundary") or {}).get("default_view_posture")) != "disposable-first":
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep boundary.default_view_posture=disposable-first")
    if ((plan.get("boundary") or {}).get("automatic_replacement")) != "forbidden":
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep boundary.automatic_replacement=forbidden")
    if ((plan.get("boundary") or {}).get("working_copy_allowed_by_default")) is not False:
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep boundary.working_copy_allowed_by_default=false")

    receipt = json.loads((ROOT / "spec" / "examples" / "content.ocr-inspection.receipt.json").read_text(encoding="utf-8"))
    if ((receipt.get("output") or {}).get("derivative_class")) != "ocr-inspection-derivative":
        errors.append("spec/examples/content.ocr-inspection.receipt.json must keep output.derivative_class=ocr-inspection-derivative")
    if ((receipt.get("lineage") or {}).get("relationship")) != "ocr-of-sanitized-inspection-derivative":
        errors.append("spec/examples/content.ocr-inspection.receipt.json must keep lineage.relationship=ocr-of-sanitized-inspection-derivative")
    if ((receipt.get("boundary") or {}).get("working_copy_allowed_by_default")) is not False:
        errors.append("spec/examples/content.ocr-inspection.receipt.json must keep boundary.working_copy_allowed_by_default=false")

    wc_plan_schema = json.loads((ROOT / "spec" / "content.working-copy.plan.schema.json").read_text(encoding="utf-8"))
    enum_values = (((wc_plan_schema.get("properties") or {}).get("source") or {}).get("properties") or {}).get("source_class", {}).get("enum", [])
    if "ocr-inspection-derivative" in enum_values:
        errors.append("spec/content.working-copy.plan.schema.json must not yet admit source.source_class=ocr-inspection-derivative")

    wc_receipt_schema = json.loads((ROOT / "spec" / "content.working-copy.receipt.schema.json").read_text(encoding="utf-8"))
    enum_values = (((wc_receipt_schema.get("properties") or {}).get("source") or {}).get("properties") or {}).get("source_class", {}).get("enum", [])
    if "ocr-inspection-derivative" in enum_values:
        errors.append("spec/content.working-copy.receipt.schema.json must not yet admit source.source_class=ocr-inspection-derivative")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation sanitized OCR boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
