#!/usr/bin/env python3
"""Guardrail for event-seal proof staying wired into incident/support bundles."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(rel: str) -> str:
    return "sha256:" + hashlib.sha256(jcs_bytes(load_json(rel))).hexdigest()


def main() -> int:
    errors: list[str] = []

    incident_schema = load_json("spec/incident.bundle.schema.json")
    include_knobs = ((incident_schema.get("$defs") or {}).get("include_knobs") or {}).get("properties") or {}
    includes = (((incident_schema.get("properties") or {}).get("includes") or {}).get("properties") or {})

    if "event_seal_receipts" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: event_seal_receipts")
    if "event_segments" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: event_segments")
    if "event_seal_receipt_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: event_seal_receipt_digests")
    if "event_segments" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: event_segments")

    bundle_plan_schema = load_json("spec/bundle.plan.schema.json")
    include_ref = ((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")

    incident_example = load_json("spec/examples/incident.bundle.json")
    scope_include = ((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("event_segments") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.event_segments must be true")
    if scope_include.get("event_seal_receipts") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.event_seal_receipts must be true")

    ex_includes = incident_example.get("includes") or {}
    vals = ex_includes.get("event_seal_receipt_digests") or []
    expected = digest("spec/examples/event.seal.receipt.json")
    if not vals:
        errors.append("spec/examples/incident.bundle.json missing includes.event_seal_receipt_digests")
    elif vals[0] != expected:
        errors.append("spec/examples/incident.bundle.json includes.event_seal_receipt_digests[0] must match computed digest of canonical event-seal receipt example")

    bundle_plan_example = load_json("spec/examples/bundle.plan.json")
    bp_include = ((bundle_plan_example.get("selection") or {}).get("include") or {})
    if bp_include.get("event_seal_receipts") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.event_seal_receipts must be true")

    doc_checks = {
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "recent `event.seal.receipt` digests",
            "`includes.event_seal_receipt_digests`",
        ],
        "docs/229-evidence-spine-overview.md": [
            "`event_seal_receipt_digests`",
            "docs/625-incident-bundles-carry-event-seal-proof-by-digest.md",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "`event_seal_receipts` / `event_seal_receipt_digests`",
            "bounded event-window handoff",
        ],
        "docs/424-forward-secure-event-log-sealing.md": [
            "`event_seal_receipt_digests`",
            "docs/625-incident-bundles-carry-event-seal-proof-by-digest.md",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "event-seal receipt digests when continuity proof matters",
            "`event_seal_receipt_digests`",
        ],
        "docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md": [
            "docs/625-incident-bundles-carry-event-seal-proof-by-digest.md",
        ],
        "docs/625-incident-bundles-carry-event-seal-proof-by-digest.md": [
            "`event_seal_receipts`",
            "`event_seal_receipt_digests`",
            "verifier-private output",
        ],
        "docs/98-archive-hygiene.md": [
            "check_event_seal_bundle_contract.py",
            "event segments while hand-waving seal proof",
        ],
        "docs/99-llm-runbook.md": [
            "check_event_seal_bundle_contract.py",
            "support handoff can carry `event_seal_receipt_digests`",
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

    print("Event-seal bundle contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
