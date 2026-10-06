#!/usr/bin/env python3
"""Guardrail for keeping supplementary breakglass adapter/runtime receipt chains authority-anchored."""
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
        "authority-anchored to the same bundle's `breakglass_receipt_digests`",
        "receipt chain does not prove emergency authority on its own",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "orphan portable stories",
        "same bundle or handoff",
        "matching `breakglass.receipt` digest",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    doc_checks = {
        "adrs/ADR-0303-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md": [
            "authority-anchored",
            "breakglass_receipt_digests",
            "do not self-authenticate emergency authority",
        ],
        "docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md": [
            "authority-anchored",
            "extra[] is not enough on its own",
            "tools/check_breakglass_adapter_anchor_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "do not let that supplementary receipt chain float by itself",
            "same bundle/handoff",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "Do not let that supplementary receipt chain travel alone",
            "keep at least one exact `breakglass_receipt_digests` join",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "supplementary adapter/runtime exports must also stay authority-anchored",
            "orphan receipt chains",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "Do not let those supplementary receipt chains float without the governing authority record",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "authority-anchored to at least one exact `breakglass.receipt` digest",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "authority anchor",
            "transport history alone",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0303",
            "authority-anchored to exact `breakglass_receipt_digests`",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_anchor_boundary.py",
            "authority-anchored",
        ],
        "docs/99-llm-runbook.md": [
            "docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md",
            "tools/check_breakglass_adapter_anchor_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md",
            "tools/check_breakglass_adapter_anchor_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "authority-anchored",
            "docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md",
        ],
        "docs/32-curated-references.md": [
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
    print("Breakglass adapter anchor boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
