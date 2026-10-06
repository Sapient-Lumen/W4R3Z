#!/usr/bin/env python3
"""Guardrail for uefi.var.set proof staying wired into incident/support bundles."""
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
    if "uefi_var_set_receipts" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: uefi_var_set_receipts")
    if "uefi_var_set_receipt_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: uefi_var_set_receipt_digests")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("uefi_var_set_receipts") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.uefi_var_set_receipts must be true")
    vals=(incident_example.get("includes") or {}).get("uefi_var_set_receipt_digests") or []
    expected=digest("spec/examples/uefi.var.set.receipt.json")
    if not vals:
        errors.append("spec/examples/incident.bundle.json missing includes.uefi_var_set_receipt_digests")
    elif vals[0] != expected:
        errors.append("spec/examples/incident.bundle.json includes.uefi_var_set_receipt_digests[0] must match computed digest of canonical uefi.var.set.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    if ((bundle_plan_example.get("selection") or {}).get("include") or {}).get("uefi_var_set_receipts") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.uefi_var_set_receipts must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`includes.uefi_var_set_receipt_digests`","raw efivar dumps","`uefi.var.set.receipt` digest references"],
        "docs/229-evidence-spine-overview.md":["`uefi_var_set_receipt_digests`","UEFI-variable mutation"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`uefi_var_set_receipts` / `uefi_var_set_receipt_digests`","BootOrder"],
        "docs/321-firmware-updates-and-uefi-variables-as-evidence.md":["official support handoff can now carry `uefi_var_set_receipt_digests`","typed bundle contract"],
        "docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md":["`uefi_var_set_receipt_digests`","official support handoff"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["`uefi_var_set_receipt_digests`","which exact `uefi.var.set.receipt` participated"],
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md":["official support handoff now uses `uefi_var_set_receipt_digests`","raw efivar"],
        "docs/630-incident-bundles-carry-uefi-var-set-proof-by-digest.md":["`uefi_var_set_receipts`","`uefi_var_set_receipt_digests`","raw efivar dumps"],
        "docs/98-archive-hygiene.md":["check_uefi_var_set_bundle_contract.py","raw efivar dumps"],
        "docs/99-llm-runbook.md":["check_uefi_var_set_bundle_contract.py","support handoff can carry `uefi_var_set_receipt_digests`"],
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
    print("UEFI-var-set bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
