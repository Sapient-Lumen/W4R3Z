#!/usr/bin/env python3
"""Guardrail for fw.inventory.diff proof staying wired into incident/support bundles."""
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
    if "firmware_inventory_diff" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: firmware_inventory_diff")
    if "fw_inventory_diff_digest" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: fw_inventory_diff_digest")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("firmware_inventory_diff") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.firmware_inventory_diff must be true")
    val=(incident_example.get("includes") or {}).get("fw_inventory_diff_digest")
    expected=digest("spec/examples/fw.inventory.diff.json")
    if not val:
        errors.append("spec/examples/incident.bundle.json missing includes.fw_inventory_diff_digest")
    elif val != expected:
        errors.append("spec/examples/incident.bundle.json includes.fw_inventory_diff_digest must match computed digest of canonical fw.inventory.diff example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    if ((bundle_plan_example.get("selection") or {}).get("include") or {}).get("firmware_inventory_diff") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.firmware_inventory_diff must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["recent `fw.inventory.diff` digest references","`fw_inventory_diff_digest`"],
        "docs/229-evidence-spine-overview.md":["`fw_inventory_diff_digest`","firmware/platform drift"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`firmware_inventory_diff` / `fw_inventory_diff_digest`","firmware/platform-drift-shaped incident"],
        "docs/321-firmware-updates-and-uefi-variables-as-evidence.md":["official support handoff can now carry `fw_inventory_diff_digest`","reviewed firmware/platform drift proof"],
        "docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md":["`fw_inventory_diff_digest`","reviewed firmware/platform drift"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["firmware/platform drift proof","which exact `fw.inventory.diff` participated","`fw_inventory_diff_digest`"],
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md":["official support handoff now uses `fw_inventory_diff_digest`","screenshots or dashboard comparisons"],
        "docs/632-incident-bundles-carry-fw-inventory-diff-proof-by-digest.md":["`firmware_inventory_diff`","`fw_inventory_diff_digest`","screenshots, dashboards, or ticket prose"],
        "docs/98-archive-hygiene.md":["check_fw_inventory_diff_bundle_contract.py","typed place for `fw.inventory.diff` proof","screenshots or dashboard comparisons"],
        "docs/99-llm-runbook.md":["check_fw_inventory_diff_bundle_contract.py","support handoff can carry `fw_inventory_diff_digest`"],
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
    print("Firmware-inventory-diff bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
