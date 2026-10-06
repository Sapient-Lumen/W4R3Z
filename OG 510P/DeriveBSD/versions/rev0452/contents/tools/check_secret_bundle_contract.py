#!/usr/bin/env python3
"""Guardrail for secret-snapshot/secret-receipt proof staying wired into incident/support bundles."""
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
    for knob in ["secret_snapshot","secret_receipts"]:
        if knob not in include_knobs:
            errors.append(f"spec/incident.bundle.schema.json missing include knob: {knob}")
    for field in ["secret_snapshot_digest","secret_receipt_digests"]:
        if field not in includes:
            errors.append(f"spec/incident.bundle.schema.json missing includes field: {field}")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("secret_snapshot") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.secret_snapshot must be true")
    if scope_include.get("secret_receipts") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.secret_receipts must be true")
    includes_obj=incident_example.get("includes") or {}
    if includes_obj.get("secret_snapshot_digest") != digest("spec/examples/secret.snapshot.json"):
        errors.append("spec/examples/incident.bundle.json includes.secret_snapshot_digest must match computed digest of canonical secret.snapshot example")
    if includes_obj.get("secret_receipt_digests") != [digest("spec/examples/secret.receipt.json")]:
        errors.append("spec/examples/incident.bundle.json includes.secret_receipt_digests must match computed digest of canonical secret.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    bp_inc=((bundle_plan_example.get("selection") or {}).get("include") or {})
    if bp_inc.get("secret_snapshot") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.secret_snapshot must be true")
    if bp_inc.get("secret_receipts") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.secret_receipts must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`secret_snapshot_digest`","`secret_receipt_digests`","provider dashboards, screenshots, or ticket prose"],
        "docs/223-secrets-and-key-management-as-evidence.md":["official support handoff can now carry `secret_snapshot_digest` + `secret_receipt_digests`","metadata-only"],
        "docs/229-evidence-spine-overview.md":["Official support handoff can also carry `secret_snapshot_digest` + `secret_receipt_digests`","safe current secret posture"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`secret_snapshot` / `secret_snapshot_digest`","`secret_receipts` / `secret_receipt_digests`"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["secret-state/action proof","`secret_snapshot_digest`","`secret_receipt_digests`"],
        "docs/637-incident-bundles-carry-secret-state-and-action-proof-by-digest.md":["`secret_snapshot_digest`","`secret_receipt_digests`","provider dashboards, ticket notes, or screenshots"],
        "docs/98-archive-hygiene.md":["check_secret_bundle_contract.py","typed secret-state/action proof"],
        "docs/99-llm-runbook.md":["check_secret_bundle_contract.py","support handoff can carry `secret_snapshot_digest` + `secret_receipt_digests`"],
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
    print("Secret bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
