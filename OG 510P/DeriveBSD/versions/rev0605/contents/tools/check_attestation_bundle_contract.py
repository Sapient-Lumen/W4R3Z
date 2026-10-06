#!/usr/bin/env python3
"""Guardrail for measured-posture proof staying wired into incident/support bundles."""
from __future__ import annotations
import json
from pathlib import Path

from cube_digest_lib import file_json_digest, load_json as load_json_strict
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return load_json_strict(ROOT, rel)

def digest(rel: str) -> str:
    return file_json_digest(ROOT, rel)

def main() -> int:
    errors=[]
    incident_schema=load_json("spec/incident.bundle.schema.json")
    include_knobs=((incident_schema.get("$defs") or {}).get("include_knobs") or {}).get("properties") or {}
    includes=(((incident_schema.get("properties") or {}).get("includes") or {}).get("properties") or {})
    for knob in ["boot_attestation","attestation_reference","attestation_receipts"]:
        if knob not in include_knobs:
            errors.append(f"spec/incident.bundle.schema.json missing include knob: {knob}")
    for field in ["boot_attestation_digest","attestation_reference_digest","attestation_receipt_digests"]:
        if field not in includes:
            errors.append(f"spec/incident.bundle.schema.json missing includes field: {field}")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    for knob in ["boot_attestation","attestation_reference","attestation_receipts"]:
        if scope_include.get(knob) is not True:
            errors.append(f"spec/examples/incident.bundle.json scope.include.{knob} must be true")
    includes_obj=incident_example.get("includes") or {}
    if includes_obj.get("boot_attestation_digest") != digest("spec/examples/boot.attestation.json"):
        errors.append("spec/examples/incident.bundle.json includes.boot_attestation_digest must match computed digest of canonical boot.attestation example")
    if includes_obj.get("attestation_reference_digest") != digest("spec/examples/attestation.reference.json"):
        errors.append("spec/examples/incident.bundle.json includes.attestation_reference_digest must match computed digest of canonical attestation.reference example")
    if includes_obj.get("attestation_receipt_digests") != [digest("spec/examples/attestation.receipt.json")]:
        errors.append("spec/examples/incident.bundle.json includes.attestation_receipt_digests must match computed digest of canonical attestation.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    bp_inc=((bundle_plan_example.get("selection") or {}).get("include") or {})
    for knob in ["boot_attestation","attestation_reference","attestation_receipts"]:
        if bp_inc.get(knob) is not True:
            errors.append(f"spec/examples/bundle.plan.json selection.include.{knob} must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`boot_attestation_digest`","`attestation_reference_digest`","`attestation_receipt_digests`","verifier dashboards, portal screenshots, or ticket prose"],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md":["official support handoff can now carry `boot_attestation_digest`","`attestation_reference_digest`","`attestation_receipt_digests`"],
        "docs/229-evidence-spine-overview.md":["Official support handoff can also carry `boot_attestation_digest`","`attestation_reference_digest`","`attestation_receipt_digests`"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`boot_attestation` / `boot_attestation_digest`","`attestation_reference` / `attestation_reference_digest`","`attestation_receipts` / `attestation_receipt_digests`"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["`boot_attestation_digest`","`attestation_reference_digest`","`attestation_receipt_digests`","verifier dashboards, portal screenshots, or ticket prose"],
        "docs/639-incident-bundles-carry-attestation-proof-by-digest.md":["`boot_attestation`","`attestation_reference`","`attestation_receipts`","`boot_attestation_digest`","`attestation_reference_digest`","`attestation_receipt_digests`","verifier dashboards, portal screenshots, or ticket prose"],
        "docs/98-archive-hygiene.md":["check_attestation_bundle_contract.py","typed attestation posture proof"],
        "docs/99-llm-runbook.md":["check_attestation_bundle_contract.py","support handoff can carry `boot_attestation_digest`"],
    }
    for rel, needles in doc_checks.items():
        text=(ROOT/rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Attestation bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
