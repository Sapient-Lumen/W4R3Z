#!/usr/bin/env python3
"""Guardrail for time.sync proof staying wired into incident/support bundles."""
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
    for knob in ("time_source_inventory", "time_sync_snapshot", "time_sync_receipts"):
        if knob not in include_knobs:
            errors.append(f"spec/incident.bundle.schema.json missing include knob: {knob}")
    for field in ("time_source_inventory_digest", "time_sync_snapshot_digest", "time_sync_receipt_digests"):
        if field not in includes:
            errors.append(f"spec/incident.bundle.schema.json missing includes field: {field}")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    for knob in ("time_source_inventory", "time_sync_snapshot", "time_sync_receipts"):
        if scope_include.get(knob) is not True:
            errors.append(f"spec/examples/incident.bundle.json scope.include.{knob} must be true")
    includes_obj=incident_example.get("includes") or {}
    if includes_obj.get("time_source_inventory_digest") != digest("spec/examples/time.source.inventory.json"):
        errors.append("spec/examples/incident.bundle.json includes.time_source_inventory_digest must match computed digest of canonical time.source.inventory example")
    if includes_obj.get("time_sync_snapshot_digest") != digest("spec/examples/time.sync.snapshot.json"):
        errors.append("spec/examples/incident.bundle.json includes.time_sync_snapshot_digest must match computed digest of canonical time.sync.snapshot example")
    val=includes_obj.get("time_sync_receipt_digests")
    expected_receipt=digest("spec/examples/time.sync.receipt.json")
    if not val:
        errors.append("spec/examples/incident.bundle.json missing includes.time_sync_receipt_digests")
    elif val != [expected_receipt]:
        errors.append("spec/examples/incident.bundle.json includes.time_sync_receipt_digests must match computed digest of canonical time.sync.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    bp_inc=((bundle_plan_example.get("selection") or {}).get("include") or {})
    for knob in ("time_source_inventory", "time_sync_snapshot", "time_sync_receipts"):
        if bp_inc.get(knob) is not True:
            errors.append(f"spec/examples/bundle.plan.json selection.include.{knob} must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`time_sync_receipt_digests`","official support handoff"],
        "docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md":["official support handoff can now carry `time_sync_receipt_digests`","daemon logs or raw protocol transcripts"],
        "docs/229-evidence-spine-overview.md":["`time_sync_receipt_digests`","trustworthy-time action proof"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`time_source_inventory` / `time_source_inventory_digest`","`time_sync_receipts` / `time_sync_receipt_digests`"],
        "docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md":["support handoff can stay on `time_source_inventory_digest` + `time_sync_snapshot_digest` + `time_sync_receipt_digests`","`time-proof-bundle` stays a richer side-evidence lane"],
        "docs/308-time-monitors-and-lie-detection.md":["`time_sync_receipt_digests`","raw transcripts only inside stronger export paths"],
        "docs/468-trustworthy-time-posture-by-profile.md":["official support handoff can carry `time_sync_receipt_digests`","daemon logs or raw protocol transcripts"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["trustworthy-time action proof","which exact `time.sync.receipt` participated","`time_sync_receipt_digests`"],
        "docs/634-incident-bundles-carry-time-sync-proof-by-digest.md":["`time_sync_receipts`","`time_sync_receipt_digests`","daemon logs, monitor dashboards, or raw NTS/Roughtime transcripts"],
        "docs/98-archive-hygiene.md":["check_time_sync_bundle_contract.py","typed place for `time.sync.receipt` proof"],
        "docs/99-llm-runbook.md":["check_time_sync_bundle_contract.py","support handoff can carry `time_sync_receipt_digests`"],
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
    print("Time-sync bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
