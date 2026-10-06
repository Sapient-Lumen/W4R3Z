#!/usr/bin/env python3
"""Guardrail for fw.update proof staying wired into incident/support bundles."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def digest(rel: str) -> str:
    return "sha256:" + hashlib.sha256(jcs_bytes(load_json(rel))).hexdigest()

def main() -> int:
    errors=[]
    incident_schema=load_json("spec/incident.bundle.schema.json")
    include_knobs=((incident_schema.get("$defs") or {}).get("include_knobs") or {}).get("properties") or {}
    includes=(((incident_schema.get("properties") or {}).get("includes") or {}).get("properties") or {})
    if "firmware_update_receipts" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: firmware_update_receipts")
    if "fw_update_receipt_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: fw_update_receipt_digests")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("firmware_update_receipts") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.firmware_update_receipts must be true")
    vals=(incident_example.get("includes") or {}).get("fw_update_receipt_digests") or []
    expected=digest("spec/examples/fw.update.receipt.json")
    if not vals:
        errors.append("spec/examples/incident.bundle.json missing includes.fw_update_receipt_digests")
    elif vals[0] != expected:
        errors.append("spec/examples/incident.bundle.json includes.fw_update_receipt_digests[0] must match computed digest of canonical fw.update.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    if ((bundle_plan_example.get("selection") or {}).get("include") or {}).get("firmware_update_receipts") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.firmware_update_receipts must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["recent `fw-update-receipt` digest references","`includes.fw_update_receipt_digests`"],
        "docs/229-evidence-spine-overview.md":["`fw_update_receipt_digests`","firmware-update"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`firmware_update_receipts` / `fw_update_receipt_digests`","firmware-update-shaped incident"],
        "docs/321-firmware-updates-and-uefi-variables-as-evidence.md":["official support handoff can now carry `fw_update_receipt_digests`","typed bundle contract"],
        "docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md":["`fw_update_receipt_digests`","official support handoff"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["firmware-update proof","which exact `fw.update.receipt` participated","`fw_update_receipt_digests`"],
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md":["official support handoff now uses `fw_update_receipt_digests`","updater dashboards"],
        "docs/631-incident-bundles-carry-fw-update-proof-by-digest.md":["`firmware_update_receipts`","`fw_update_receipt_digests`","updater dashboards"],
        "docs/98-archive-hygiene.md":["check_fw_update_bundle_contract.py","typed place for `fw.update.receipt` proof","updater dashboards"],
        "docs/99-llm-runbook.md":["check_fw_update_bundle_contract.py","support handoff can carry `fw_update_receipt_digests`"],
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
    print("Firmware-update bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
