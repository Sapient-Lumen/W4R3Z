#!/usr/bin/env python3
import json, pathlib, re, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
schema = json.loads((root / "docs/00-meta/cube-schema.json").read_text(encoding="utf-8"))
required_axes = set(schema["required_axes"])
axis_values = {a["id"]: set(a.get("values", [])) for a in cube.get("axes", [])}
record_ids = set()

for rec in cube.get("route_records", []):
    rid = rec.get("id", "")
    if rid in record_ids:
        errors.append(f"duplicate route id: {rid}")
    record_ids.add(rid)
    if not rec.get("family"):
        errors.append(f"route record {rid} missing family")
    axes = rec.get("axes", {})
    missing = sorted(required_axes - set(axes))
    extra = sorted(set(axes) - required_axes)
    if missing:
        errors.append(f"route record {rid} missing required axes: {missing}")
    if extra:
        errors.append(f"route record {rid} has axes outside schema: {extra}")
    for axis, values in axes.items():
        if not isinstance(values, list) or not values:
            errors.append(f"route record {rid} axis {axis} must be a non-empty list")
            continue
        for value in values:
            if value not in axis_values.get(axis, set()):
                errors.append(f"route record {rid} uses undeclared axis value {axis}={value}")
    if "ai_tax_advice" in axes.get("base", []) and "taxpayer_side_ai" not in rid:
        errors.append(f"route record {rid} has taxpayer-side-only base=ai_tax_advice")
    model_allowed = any(sub in rid for sub in ["taxpayer_side_ai", "model_assisted"])
    if not model_allowed:
        if "model_output" in axes.get("proof_posture", []):
            errors.append(f"route record {rid} has model-only proof_posture=model_output")
        if "model_output" in axes.get("evidence_state", []):
            errors.append(f"route record {rid} has model-only evidence_state=model_output")
    if "frontier_ai" in rid and "ai_tax_advice" in axes.get("base", []):
        errors.append(f"frontier AI route record {rid} should use frontier_ai_compute, not ai_tax_advice")
    if "model_assisted" in rid and "ai_tax_advice" in axes.get("base", []):
        errors.append(f"model-assisted administration route record {rid} should use model_assisted_administration, not ai_tax_advice")

summary = cube.get("audit_summary", {})
if summary.get("semantic_contamination_remaining"):
    errors.append(f"cube audit summary still reports semantic contamination: {summary.get('semantic_contamination_remaining')}")
if summary.get("record_count") != len(cube.get("route_records", [])):
    errors.append("cube audit summary record_count is stale")
if summary.get("source_currentness_claims_required") is not True:
    errors.append("cube audit summary must mark source_currentness_claims_required=True")
if summary.get("remedy_profiles_required") is not True:
    errors.append("cube audit summary must mark remedy_profiles_required=True")
if summary.get("case_contracts_required") is not True:
    errors.append("cube audit summary must mark case_contracts_required=True")
if summary.get("policy_action_profiles_required") is not True:
    errors.append("cube audit summary must mark policy_action_profiles_required=True")
if summary.get("case_contract_count") != len(json.loads((root / "docs/00-meta/case-contracts.json").read_text(encoding="utf-8")).get("contracts", [])):
    errors.append("cube audit summary case_contract_count is stale")
if summary.get("policy_action_profile_count") != len(json.loads((root / "docs/00-meta/policy-action-profiles.json").read_text(encoding="utf-8")).get("profiles", [])):
    errors.append("cube audit summary policy_action_profile_count is stale")

if summary.get("actor_accountability_profiles_required") is not True:
    errors.append("cube audit summary must mark actor_accountability_profiles_required=True")
if summary.get("actor_accountability_profile_count") != len(json.loads((root / "docs/00-meta/actor-accountability-profiles.json").read_text(encoding="utf-8")).get("profiles", [])):
    errors.append("cube audit summary actor_accountability_profile_count is stale")

if summary.get("remedy_profile_count") != len(cube.get("route_records", [])):
    errors.append("cube audit summary remedy_profile_count is stale")
if set(summary.get("missing_axis_counts_after_normalization", {}).keys()) != required_axes:
    errors.append("cube audit summary missing_axis_counts_after_normalization does not list every required axis")

if errors:
    raise SystemExit("\n".join(errors))
print("cube audit ok")
