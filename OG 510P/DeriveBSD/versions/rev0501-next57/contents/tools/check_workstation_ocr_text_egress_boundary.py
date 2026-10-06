#!/usr/bin/env python3
"""Guardrail for workstation OCR-derived text egress posture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": [
        "explicit `ui.datatransfer` act",
        "`text/plain;charset=utf-8`",
        "single-delivery",
        "content_source",
    ],
    "adrs/ADR-0247-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": [
        "Plain text is the boring baseline payload",
        "Single-delivery remains the ordinary posture",
        "Transfers may preserve OCR source lineage",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
        "content_source",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
        "plain-text",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
        "OCR-derived text egress",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
        "content_source",
    ],
    "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md": [
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
        "plain-text single-delivery data-transfer",
    ],
    "docs/99-llm-runbook.md": [
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
        "check_workstation_ocr_text_egress_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_ocr_text_egress_boundary.py",
        "OCR text-egress boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Searchable OCR should not silently become ambient clipboard/export state",
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
    ],
    "README.md": [
        "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md",
        "plain-text single-delivery",
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    for rel in ["spec/content.ocr-inspection.plan.schema.json", "spec/content.ocr-inspection.receipt.schema.json"]:
        schema = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        boundary = ((schema.get("properties") or {}).get("boundary") or {})
        required = boundary.get("required") or []
        props = boundary.get("properties") or {}
        for name in ["text_egress_default", "clipboard_mime_default", "rich_text_transfer_by_default"]:
            if name not in required:
                errors.append(f"{rel} must require boundary.{name}")
        if (props.get("text_egress_default") or {}).get("const") != "explicit-datatransfer-only":
            errors.append(f"{rel} must keep boundary.text_egress_default=explicit-datatransfer-only")
        if (props.get("clipboard_mime_default") or {}).get("const") != "text/plain;charset=utf-8":
            errors.append(f"{rel} must keep boundary.clipboard_mime_default=text/plain;charset=utf-8")
        if (props.get("rich_text_transfer_by_default") or {}).get("const") is not False:
            errors.append(f"{rel} must keep boundary.rich_text_transfer_by_default=false")

    for rel in ["spec/examples/content.ocr-inspection.plan.json", "spec/examples/content.ocr-inspection.receipt.json"]:
        example = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        boundary = example.get("boundary") or {}
        if boundary.get("text_egress_default") != "explicit-datatransfer-only":
            errors.append(f"{rel} must keep boundary.text_egress_default=explicit-datatransfer-only")
        if boundary.get("clipboard_mime_default") != "text/plain;charset=utf-8":
            errors.append(f"{rel} must keep boundary.clipboard_mime_default=text/plain;charset=utf-8")
        if boundary.get("rich_text_transfer_by_default") is not False:
            errors.append(f"{rel} must keep boundary.rich_text_transfer_by_default=false")

    for rel, field in [("spec/ui.datatransfer.grant.schema.json", "offer"), ("spec/ui.datatransfer.receipt.schema.json", "summary")]:
        schema = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        props = (((schema.get("properties") or {}).get(field) or {}).get("properties") or {})
        content_source = props.get("content_source") or {}
        required = content_source.get("required") or []
        for name in ["artifact_kind", "artifact_digest", "source_class"]:
            if name not in required:
                errors.append(f"{rel} must keep {field}.content_source requiring {name}")

    grant = json.loads((ROOT / "spec/examples/ui.datatransfer.grant.ocr-inspection-text.json").read_text(encoding="utf-8"))
    if grant.get("delivery_mode") != "single-delivery":
        errors.append("spec/examples/ui.datatransfer.grant.ocr-inspection-text.json must keep delivery_mode=single-delivery")
    if ((grant.get("offer") or {}).get("mime_types") or [None])[0] != "text/plain;charset=utf-8":
        errors.append("spec/examples/ui.datatransfer.grant.ocr-inspection-text.json must keep plain-text MIME")
    if (((grant.get("offer") or {}).get("content_source") or {}).get("source_class")) != "ocr-inspection-derivative":
        errors.append("spec/examples/ui.datatransfer.grant.ocr-inspection-text.json must keep content_source.source_class=ocr-inspection-derivative")

    receipt = json.loads((ROOT / "spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json").read_text(encoding="utf-8"))
    if ((receipt.get("summary") or {}).get("mime_type")) != "text/plain;charset=utf-8":
        errors.append("spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json must keep plain-text MIME")
    if (((receipt.get("summary") or {}).get("content_source") or {}).get("source_class")) != "ocr-inspection-derivative":
        errors.append("spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json must keep content_source.source_class=ocr-inspection-derivative")
    if receipt.get("grant_exhausted") is not True:
        errors.append("spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json must keep grant_exhausted=true")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation OCR text-egress boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
