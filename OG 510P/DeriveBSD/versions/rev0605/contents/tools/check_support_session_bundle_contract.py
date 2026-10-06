#!/usr/bin/env python3
"""Guardrail for support.session proof staying wired into incident/support bundles."""
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
    if "support_sessions" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: support_sessions")
    if "support_session_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: support_session_digests")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("support_sessions") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.support_sessions must be true")
    vals=(incident_example.get("includes") or {}).get("support_session_digests") or []
    expected=digest("spec/examples/support.session.json")
    if not vals:
        errors.append("spec/examples/incident.bundle.json missing includes.support_session_digests")
    elif vals[0] != expected:
        errors.append("spec/examples/incident.bundle.json includes.support_session_digests[0] must match computed digest of canonical support.session example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    if ((bundle_plan_example.get("selection") or {}).get("include") or {}).get("support_sessions") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.support_sessions must be true")
    doc_checks={
        "docs/216-incident-snapshots-and-support-bundles.md":["`support.session` digest references","`includes.support_session_digests`"],
        "docs/229-evidence-spine-overview.md":["`support_session_digests`","remote assistance"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`support_sessions` / `support_session_digests`","remote-assistance-shaped incident"],
        "docs/291-remote-assistance-sessions-as-evidence.md":["official support handoff can now carry `support_session_digests`","typed bundle contract"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["support-session proof","which exact remote-assistance session participated","`support_session_digests`"],
        "docs/627-incident-bundles-carry-support-session-proof-by-digest.md":["`support_sessions`","`support_session_digests`","helper dashboards"],
        "docs/98-archive-hygiene.md":["check_support_session_bundle_contract.py","typed place for `support.session` proof","helper dashboards"],
        "docs/99-llm-runbook.md":["check_support_session_bundle_contract.py","support handoff can carry `support_session_digests`"],
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
    print("Support-session bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
