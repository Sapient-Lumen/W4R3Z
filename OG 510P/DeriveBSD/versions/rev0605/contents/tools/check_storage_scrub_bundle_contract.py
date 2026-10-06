#!/usr/bin/env python3
"""Guardrail for storage.scrub.receipt proof staying wired into incident/support bundles."""
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
    for knob in ("storage_pool_inventory", "storage_health_snapshot", "storage_scrub_receipts"):
        if knob not in include_knobs:
            errors.append(f"spec/incident.bundle.schema.json missing include knob: {knob}")
    for field in ("storage_pool_inventory_digest", "storage_health_snapshot_digest", "storage_scrub_receipt_digests"):
        if field not in includes:
            errors.append(f"spec/incident.bundle.schema.json missing includes field: {field}")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    for knob in ("storage_pool_inventory", "storage_health_snapshot", "storage_scrub_receipts"):
        if scope_include.get(knob) is not True:
            errors.append(f"spec/examples/incident.bundle.json scope.include.{knob} must be true")
    includes_obj=incident_example.get("includes") or {}
    if includes_obj.get("storage_pool_inventory_digest") != digest("spec/examples/storage.pool.inventory.json"):
        errors.append("spec/examples/incident.bundle.json includes.storage_pool_inventory_digest must match computed digest of canonical storage.pool.inventory example")
    if includes_obj.get("storage_health_snapshot_digest") != digest("spec/examples/storage.health.snapshot.json"):
        errors.append("spec/examples/incident.bundle.json includes.storage_health_snapshot_digest must match computed digest of canonical storage.health.snapshot example")
    val=includes_obj.get("storage_scrub_receipt_digests")
    expected=digest("spec/examples/storage.scrub.receipt.json")
    if not val:
        errors.append("spec/examples/incident.bundle.json missing includes.storage_scrub_receipt_digests")
    elif val != [expected]:
        errors.append("spec/examples/incident.bundle.json includes.storage_scrub_receipt_digests must match computed digest of canonical storage.scrub.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    bp_inc=((bundle_plan_example.get("selection") or {}).get("include") or {})
    for knob in ("storage_pool_inventory", "storage_health_snapshot", "storage_scrub_receipts"):
        if bp_inc.get(knob) is not True:
            errors.append(f"spec/examples/bundle.plan.json selection.include.{knob} must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`storage_scrub_receipt_digests`","official support handoff"],
        "docs/225-storage-health-and-scrubbing-as-evidence.md":["official support handoff can now carry `storage_scrub_receipt_digests`","`zpool status` transcripts"],
        "docs/229-evidence-spine-overview.md":["`storage_scrub_receipt_digests`","storage integrity / scrub outcomes"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`storage_scrub_receipts` / `storage_scrub_receipt_digests`","storage-integrity-shaped incident"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["storage integrity proof","which exact `storage.scrub.receipt` participated","`storage_scrub_receipt_digests`"],
        "docs/635-incident-bundles-carry-storage-scrub-proof-by-digest.md":["`storage_scrub_receipts`","`storage_scrub_receipt_digests`","`zpool status` transcripts, dashboard screenshots, or operator notes"],
        "docs/98-archive-hygiene.md":["check_storage_scrub_bundle_contract.py","typed place for `storage.scrub.receipt` proof"],
        "docs/99-llm-runbook.md":["check_storage_scrub_bundle_contract.py","support handoff can carry `storage_scrub_receipt_digests`"],
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
    print("Storage-scrub bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
