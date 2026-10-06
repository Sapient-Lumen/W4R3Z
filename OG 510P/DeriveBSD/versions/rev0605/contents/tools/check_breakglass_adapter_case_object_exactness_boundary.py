#!/usr/bin/env python3
"""Guardrail for keeping supplementary breakglass accepted case-object proof object-exact."""
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
        "accepted case-object proof",
        "object-exact",
        "accepted remote attachment/object/message-part identity",
        "parent ticket/case/thread/container ids may travel as context but not as the sole payload anchor",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "accepted case-object proof",
        "object-exact rather than case-exact",
        "accepted remote attachment/object/message-part identity",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    ex = load_json("spec/examples/incident.bundle.json")
    extra = ((ex.get("includes") or {}).get("extra") or [])
    if not any("acceptedcaseobjectproofexactobject" in item for item in extra):
        errors.append("spec/examples/incident.bundle.json includes.extra missing object-exact accepted case-object proof example")

    doc_checks = {
        "adrs/ADR-0306-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md": [
            "object-exact",
            "parent case/ticket/thread id",
            "exact remote attachment/object/message-part identity",
        ],
        "docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md": [
            "object-exact",
            "Parent case ids are context, not payload identity",
            "tools/check_breakglass_adapter_case_object_exactness_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "accepted case-object proof, keep it object-exact",
            "accepted remote attachment/object/message-part identity",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "accepted case-object proof, keep it object-exact too",
            "parent case/ticket/thread/container id",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "payload anchor uses accepted case-object proof, keep it object-exact",
            "accepted remote attachment/object/message-part identity",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "accepted-case-object lane, keep it object-exact too",
            "parent case/ticket/container",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "accepted-case-object payload anchor must stay object-exact",
            "accepted remote attachment/object/message-part identity",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "accepted case-object proof, keep it object-exact too",
            "surrounding case/ticket/thread/container",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0306",
            "accepted-case-object payload anchor",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_case_object_exactness_boundary.py",
            "accepted case-object proof object-exact",
        ],
        "docs/99-llm-runbook.md": [
            "docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md",
            "tools/check_breakglass_adapter_case_object_exactness_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md",
            "tools/check_breakglass_adapter_case_object_exactness_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "accepted case-object proof should stay object-exact",
            "docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md",
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
    print("Breakglass accepted case-object exactness boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
