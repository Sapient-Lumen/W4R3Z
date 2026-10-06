#!/usr/bin/env python3
"""Guardrail for workstation OCR/searchable sanitized-derivative ambient-index posture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md": [
        "ambient host/global indexes",
        "local viewer search may remain available",
        "detached text sidecars are not emitted by default",
        "docs/293-attribute-indexed-metadata-and-live-queries.md",
    ],
    "adrs/ADR-0246-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md": [
        "Ambient host/global indexing is forbidden by default",
        "Detached text sidecars are not emitted by default",
        "Local search may stay inside the inspection lane",
    ],
    "docs/267-sanitization-portal-and-disposable-sandboxes.md": [
        "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md",
        "ambient host/global indexing",
    ],
    "docs/293-attribute-indexed-metadata-and-live-queries.md": [
        "full-text body text from foreign-derived inspection artifacts is not a blessed baseline metadata class",
        "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md",
        "ambient/global host indexing by default",
    ],
    "docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md": [
        "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md",
        "ambient host/global indexing",
    ],
    "docs/99-llm-runbook.md": [
        "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md",
        "check_workstation_sanitized_ocr_index_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_sanitized_ocr_index_boundary.py",
        "sanitized-ocr ambient-index boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Searchable sanitized inspection should not silently become ambient host search state",
        "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md",
    ],
    "README.md": [
        "docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md",
        "ambient host/global indexing",
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
    boundary = plan.get("boundary") or {}
    if boundary.get("local_viewer_search") != "allowed":
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep boundary.local_viewer_search=allowed")
    if boundary.get("ambient_host_indexing") != "forbidden":
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep boundary.ambient_host_indexing=forbidden")
    if boundary.get("detached_text_sidecar_by_default") is not False:
        errors.append("spec/examples/content.ocr-inspection.plan.json must keep boundary.detached_text_sidecar_by_default=false")

    receipt = json.loads((ROOT / "spec" / "examples" / "content.ocr-inspection.receipt.json").read_text(encoding="utf-8"))
    boundary = receipt.get("boundary") or {}
    if boundary.get("local_viewer_search") != "allowed":
        errors.append("spec/examples/content.ocr-inspection.receipt.json must keep boundary.local_viewer_search=allowed")
    if boundary.get("ambient_host_indexing") != "forbidden":
        errors.append("spec/examples/content.ocr-inspection.receipt.json must keep boundary.ambient_host_indexing=forbidden")
    if boundary.get("detached_text_sidecar_by_default") is not False:
        errors.append("spec/examples/content.ocr-inspection.receipt.json must keep boundary.detached_text_sidecar_by_default=false")

    for rel in ["spec/content.ocr-inspection.plan.schema.json", "spec/content.ocr-inspection.receipt.schema.json"]:
        schema = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        boundary = ((schema.get("properties") or {}).get("boundary") or {})
        required = boundary.get("required") or []
        props = boundary.get("properties") or {}
        for name in ["local_viewer_search", "ambient_host_indexing", "detached_text_sidecar_by_default"]:
            if name not in required:
                errors.append(f"{rel} must require boundary.{name}")
        if (props.get("local_viewer_search") or {}).get("const") != "allowed":
            errors.append(f"{rel} must keep boundary.local_viewer_search=allowed")
        if (props.get("ambient_host_indexing") or {}).get("const") != "forbidden":
            errors.append(f"{rel} must keep boundary.ambient_host_indexing=forbidden")
        if (props.get("detached_text_sidecar_by_default") or {}).get("const") is not False:
            errors.append(f"{rel} must keep boundary.detached_text_sidecar_by_default=false")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation sanitized OCR ambient-index boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
