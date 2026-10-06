#!/usr/bin/env python3
"""Guardrail for keeping portable supplementary breakglass adapter/runtime evidence payload-anchored."""
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
        "payload-anchored",
        "exported passive artifact digest or accepted case-object proof",
        "receipt-only chain",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "payload-anchored",
        "portal archaeology",
        "accepted case-object proof",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    ex = load_json("spec/examples/incident.bundle.json")
    extra = ((ex.get("includes") or {}).get("extra") or [])
    if not any("artifactpayload" in item for item in extra):
        errors.append("spec/examples/incident.bundle.json includes.extra missing payload-anchor artifact digest example")

    doc_checks = {
        "adrs/ADR-0305-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md": [
            "payload identity anchor",
            "accepted case-object proof",
            "receipt-only chain",
        ],
        "docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md": [
            "payload-anchored",
            "receipt-only scrapbook space",
            "tools/check_breakglass_adapter_payload_anchor_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "payload-anchored too",
            "passive artifact digest or accepted case-object proof",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "payload-anchored instead of receipt-only",
            "portal archaeology",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "supplementary adapter/runtime exports must also stay payload-anchored",
            "passive artifact digest or accepted case-object proof",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "Keep the same portable story payload-anchored too",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "payload-anchored to at least one passive artifact digest or accepted case-object proof",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "payload-anchored too",
            "receipt-only transport archaeology",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0305",
            "payload-anchored to at least one passive artifact digest or accepted case-object proof",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_payload_anchor_boundary.py",
            "payload-anchored",
        ],
        "docs/99-llm-runbook.md": [
            "docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md",
            "tools/check_breakglass_adapter_payload_anchor_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md",
            "tools/check_breakglass_adapter_payload_anchor_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "receipt-only handling proof still needs a payload anchor",
            "docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md",
        ],
        "docs/32-curated-references.md": [
            "RFC 6920",
            "NIST SP 800-86",
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
    print("Breakglass adapter payload-anchor boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
