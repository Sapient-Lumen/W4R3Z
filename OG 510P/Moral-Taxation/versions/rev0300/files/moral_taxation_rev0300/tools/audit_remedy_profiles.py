#!/usr/bin/env python3
import json, pathlib, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []

version = (root / "VERSION").read_text(encoding="utf-8").strip()
cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
schema = json.loads((root / "docs/00-meta/remedy-schema.json").read_text(encoding="utf-8"))
profiles_doc = json.loads((root / "docs/00-meta/remedy-profiles.json").read_text(encoding="utf-8"))

if schema.get("revision") != version:
    errors.append("remedy-schema.json revision must match VERSION")
if profiles_doc.get("revision") != version:
    errors.append("remedy-profiles.json revision must match VERSION")
if profiles_doc.get("case_count") != len(profiles_doc.get("profiles", [])):
    errors.append("remedy-profiles.json case_count must match profiles length")

allowed_families = set(schema.get("remedy_families", {}))
required_fields = set(schema.get("required_profile_fields", []))
allowed_statuses = set(schema.get("proceeds_integrity_statuses", []))
route_by_id = {rec["id"]: rec for rec in cube.get("route_records", [])}
profile_by_id = {}

for p in profiles_doc.get("profiles", []):
    rid = p.get("route_id")
    if rid in profile_by_id:
        errors.append(f"duplicate remedy profile for route {rid}")
    profile_by_id[rid] = p
    missing = sorted(required_fields - set(p))
    if missing:
        errors.append(f"remedy profile {rid} missing fields {missing}")
    if rid not in route_by_id:
        errors.append(f"remedy profile {rid} has no cube route record")
        continue
    rec = route_by_id[rid]
    if p.get("family") != rec.get("family"):
        errors.append(f"remedy profile {rid} family does not match cube record")
    if p.get("remedy_family") not in allowed_families:
        errors.append(f"remedy profile {rid} uses unknown remedy_family {p.get('remedy_family')}")
    if not p.get("default_move") or not p.get("blocked_move") or p.get("default_move") == p.get("blocked_move"):
        errors.append(f"remedy profile {rid} must have distinct default_move and blocked_move")
    if not isinstance(p.get("required_guardrails"), list) or len(p.get("required_guardrails", [])) < 2:
        errors.append(f"remedy profile {rid} needs at least two guardrails")
    if not p.get("escalation_trigger"):
        errors.append(f"remedy profile {rid} needs an escalation_trigger")
    proc = p.get("proceeds_integrity", {})
    if proc.get("status") not in allowed_statuses:
        errors.append(f"remedy profile {rid} has invalid proceeds_integrity status {proc.get('status')}")
    if rec.get("proceeds_claims"):
        if proc.get("status") != "explicit_claims":
            errors.append(f"remedy profile {rid} must expose explicit proceeds_claims")
        if len(proc.get("claims", [])) != len(rec.get("proceeds_claims", [])):
            errors.append(f"remedy profile {rid} proceeds claim count does not match cube record")
    if set(p.get("source_currentness_refs", [])) != set(rec.get("source_currentness_refs", [])):
        errors.append(f"remedy profile {rid} source_currentness_refs must match cube record")
    if rec.get("source_currentness_refs") and "source_currentness" not in p.get("review_linkage", []):
        errors.append(f"remedy profile {rid} must link remedy review to source_currentness")
    remedy_types = set(rec.get("axes", {}).get("remedy_type", []))
    if "not_remedy_specific" not in remedy_types and p.get("remedy_family") == "general_design_review":
        errors.append(f"remedy profile {rid} cannot stay general_design_review when remedy_type is specific")
    severity = set(rec.get("axes", {}).get("severity", []))
    if severity & {"high", "critical"} and p.get("proceeds_integrity", {}).get("status") == "axis_only" and p.get("remedy_family") == "general_design_review":
        errors.append(f"high-severity remedy profile {rid} needs more than axis-only proceeds and general review")

missing_profiles = sorted(set(route_by_id) - set(profile_by_id))
extra_profiles = sorted(set(profile_by_id) - set(route_by_id))
if missing_profiles:
    errors.append(f"missing remedy profiles for cube route records: {missing_profiles}")
if extra_profiles:
    errors.append(f"extra remedy profiles without cube records: {extra_profiles}")

summary = cube.get("audit_summary", {})
if summary.get("remedy_profile_count") != len(route_by_id):
    errors.append("cube audit_summary remedy_profile_count is stale")
if summary.get("remedy_profiles_required") is not True:
    errors.append("cube audit_summary must mark remedy_profiles_required=True")
family_counts = {}
for p in profiles_doc.get("profiles", []):
    family_counts[p.get("remedy_family")] = family_counts.get(p.get("remedy_family"), 0) + 1
if summary.get("remedy_family_counts") != {k: family_counts[k] for k in sorted(family_counts)}:
    errors.append("cube audit_summary remedy_family_counts is stale")

if errors:
    raise SystemExit("\n".join(errors))
print("remedy profile audit ok")
