#!/usr/bin/env python3
"""Guardrail for operator.session proof staying wired into incident/support bundles."""
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
    if "operator_sessions" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: operator_sessions")
    if "operator_session_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: operator_session_digests")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("operator_sessions") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.operator_sessions must be true")
    vals=(incident_example.get("includes") or {}).get("operator_session_digests") or []
    expected=digest("spec/examples/operator.session.json")
    if not vals:
        errors.append("spec/examples/incident.bundle.json missing includes.operator_session_digests")
    elif vals[0] != expected:
        errors.append("spec/examples/incident.bundle.json includes.operator_session_digests[0] must match computed digest of canonical operator.session example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    if ((bundle_plan_example.get("selection") or {}).get("include") or {}).get("operator_sessions") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.operator_sessions must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`operator.session` digest references","`includes.operator_session_digests`"],
        "docs/229-evidence-spine-overview.md":["`operator_session_digests`","operator access"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`operator_sessions` / `operator_session_digests`","operator-access-shaped incident"],
        "docs/311-operator-access-leases-and-ssh-certs.md":["official support handoff can now carry `operator_session_digests`","typed bundle contract"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["operator-session proof","which exact operator session participated","`operator_session_digests`"],
        "docs/627-incident-bundles-carry-support-session-proof-by-digest.md":["now decided separately in `docs/628-incident-bundles-carry-operator-session-proof-by-digest.md`"],
        "docs/628-incident-bundles-carry-operator-session-proof-by-digest.md":["`operator_sessions`","`operator_session_digests`","bastion dashboards"],
        "docs/98-archive-hygiene.md":["check_operator_session_bundle_contract.py","typed place for `operator.session` proof","bastion dashboards"],
        "docs/99-llm-runbook.md":["check_operator_session_bundle_contract.py","support handoff can carry `operator_session_digests`"],
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
    print("Operator-session bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
