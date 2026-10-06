#!/usr/bin/env python3
"""Guardrail for lease.snapshot authority context staying wired into incident/support bundles."""
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
    if "lease_snapshot" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: lease_snapshot")
    if "lease_snapshot_digest" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: lease_snapshot_digest")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("lease_snapshot") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.lease_snapshot must be true")
    includes_obj=incident_example.get("includes") or {}
    if includes_obj.get("lease_snapshot_digest") != digest("spec/examples/lease.snapshot.json"):
        errors.append("spec/examples/incident.bundle.json includes.lease_snapshot_digest must match computed digest of canonical lease.snapshot example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    bp_inc=((bundle_plan_example.get("selection") or {}).get("include") or {})
    if bp_inc.get("lease_snapshot") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.lease_snapshot must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`lease_snapshot_digest`","official support handoff","temporary-authority context"],
        "docs/229-evidence-spine-overview.md":["`lease_snapshot_digest`","what temporary authority was still live"],
        "docs/249-lease-registry-and-cross-lane-revocation.md":["official support handoff can now carry `lease_snapshot_digest`","bastion dashboards or operator memory"],
        "docs/252-lease-envelope-and-cross-lane-joins.md":["official support handoff can now carry `lease_snapshot_digest`","authority context"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`lease_snapshot` / `lease_snapshot_digest`","temporary-authority-shaped incident"],
        "docs/449-lease-issue-and-use-receipts.md":["official support handoff can now carry `lease_snapshot_digest`","what temporary authority was still live at capture time"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["temporary-authority context proof","what temporary authority was still live at capture time","`lease_snapshot_digest`"],
        "docs/636-incident-bundles-carry-lease-snapshot-authority-context-by-digest.md":["`lease_snapshot`","`lease_snapshot_digest`","bastion dashboards, control-plane screenshots, operator memory, or chat archaeology"],
        "docs/98-archive-hygiene.md":["check_lease_snapshot_bundle_contract.py","typed place for `lease.snapshot` authority context"],
        "docs/99-llm-runbook.md":["check_lease_snapshot_bundle_contract.py","support handoff can carry `lease_snapshot_digest`"],
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
    print("Lease-snapshot bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
