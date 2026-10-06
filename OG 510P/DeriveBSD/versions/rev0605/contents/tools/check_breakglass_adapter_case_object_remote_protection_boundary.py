#!/usr/bin/env python3
"""Guardrail for keeping breakglass accepted case-object proof remote-protection-shaped when visible."""
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
        "protection/retention/hold posture",
        "remote-protection-shaped",
        "durable evidence by implication",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "protection/retention/hold posture",
        "remote-protection-shaped",
        "durable evidence by implication",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    ex = load_json("spec/examples/incident.bundle.json")
    extra = ((ex.get("includes") or {}).get("extra") or [])
    if not any("acceptedcaseobjectproofexactobjectvalidatorpinnedremoteprotection" in item for item in extra):
        errors.append("spec/examples/incident.bundle.json includes.extra missing remote-protection-shaped accepted case-object proof example")

    doc_checks = {
        "adrs/ADR-0308-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md": [
            "remote-protection-shaped when visible",
            "overwrite/delete-resistance posture",
            "remote locator continuity still remains future work",
        ],
        "docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md": [
            "remote-protection-shaped when visible",
            "quietly treat any accepted portal object as durable evidence by implication",
            "tools/check_breakglass_adapter_case_object_remote_protection_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "keep it remote-protection-shaped too when visible",
            "docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "remote-protection-shaped too when visible",
            "durable evidence by implication",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "remote-protection-shaped too when visible",
            "durable evidence by implication",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "remote-protection-shaped when visible too",
            "accepted object posture",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "remote-protection-shaped when visible",
            "durable evidence by implication",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "remote-protection-shaped too when visible",
            "durable evidence by implication",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0308",
            "remote-locator continuity",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_case_object_remote_protection_boundary.py",
            "remote-protection-shaped when visible",
        ],
        "docs/99-llm-runbook.md": [
            "docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md",
            "tools/check_breakglass_adapter_case_object_remote_protection_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md",
            "tools/check_breakglass_adapter_case_object_remote_protection_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "accepted case-object anchors should keep visible remote protection posture",
            "docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md",
        ],
        "docs/32-curated-references.md": [
            "Google Cloud Storage Object Retention Lock",
            "Azure immutable blob version immutability / legal hold",
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
    print("Breakglass accepted case-object remote-protection continuity boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
