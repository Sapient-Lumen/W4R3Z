#!/usr/bin/env python3
"""Guardrail for restore apply proof staying wired into incident/support bundles."""
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
    if "restore_receipts" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: restore_receipts")
    if "restore_receipt_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: restore_receipt_digests")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("restore_receipts") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.restore_receipts must be true")
    vals=(incident_example.get("includes") or {}).get("restore_receipt_digests") or []
    expected=digest("spec/examples/restore.receipt.json")
    if not vals:
        errors.append("spec/examples/incident.bundle.json missing includes.restore_receipt_digests")
    elif vals[0] != expected:
        errors.append("spec/examples/incident.bundle.json includes.restore_receipt_digests[0] must match computed digest of canonical restore.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    if ((bundle_plan_example.get("selection") or {}).get("include") or {}).get("restore_receipts") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.restore_receipts must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["recent `restore.receipt` digests","`includes.restore_receipt_digests`"],
        "docs/229-evidence-spine-overview.md":["`restore_receipt_digests`","docs/626-incident-bundles-carry-restore-apply-proof-by-digest.md"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`restore_receipts` / `restore_receipt_digests`","recovery-shaped incident"],
        "docs/316-backups-and-restores-as-derived-operations.md":["official support bundles may carry `restore_receipt_digests`","official support handoff"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["restore apply proof","which exact restore apply participated","`restore_receipt_digests`"],
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md":["`restore_receipt_digests`","docs/626-incident-bundles-carry-restore-apply-proof-by-digest.md"],
        "docs/626-incident-bundles-carry-restore-apply-proof-by-digest.md":["`restore_receipts`","`restore_receipt_digests`","backend-specific restore-job logs"],
        "docs/98-archive-hygiene.md":["check_restore_bundle_contract.py","typed place for `restore.receipt` proof","operator memory"],
        "docs/99-llm-runbook.md":["check_restore_bundle_contract.py","support handoff can carry `restore_receipt_digests`"],
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
    print("Restore bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
