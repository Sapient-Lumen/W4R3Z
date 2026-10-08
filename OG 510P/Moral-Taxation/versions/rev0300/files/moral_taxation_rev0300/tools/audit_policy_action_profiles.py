#!/usr/bin/env python3
import json, pathlib, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []
version = (root / "VERSION").read_text(encoding="utf-8").strip()

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
schema = json.loads((root / "docs/00-meta/policy-action-schema.json").read_text(encoding="utf-8"))
profiles_doc = json.loads((root / "docs/00-meta/policy-action-profiles.json").read_text(encoding="utf-8"))
remedy_doc = json.loads((root / "docs/00-meta/remedy-profiles.json").read_text(encoding="utf-8"))

if schema.get("revision") != version:
    errors.append("policy-action-schema.json revision must match VERSION")
if profiles_doc.get("revision") != version:
    errors.append("policy-action-profiles.json revision must match VERSION")
if profiles_doc.get("case_count") != len(profiles_doc.get("profiles", [])):
    errors.append("policy-action-profiles.json case_count must match profiles length")

route_by_id = {rec["id"]: rec for rec in cube.get("route_records", [])}
remedy_ids = {p["route_id"] for p in remedy_doc.get("profiles", [])}
allowed = set(schema.get("action_families", {}))
required = set(schema.get("required_profile_fields", []))
profile_by_id = {}

fee_like = {"fee", "user_fee", "service_charge", "license_fee", "monitoring_fee", "supervision_fee", "court_fee", "fee_cap", "line_item_cap", "quality_fee"}
tax_like = {"tax", "levy", "surcharge", "tariff", "border_adjustment", "gross_receipts_tax", "digital_ad_tax", "universal_service_fee", "wagering_tax", "excise_tax"}
no_go_like = {"no_go_rule", "siting_veto", "injunction"}

for prof in profiles_doc.get("profiles", []):
    rid = prof.get("route_id")
    if rid in profile_by_id:
        errors.append(f"duplicate policy-action profile for route {rid}")
    profile_by_id[rid] = prof
    missing = sorted(required - set(prof))
    if missing:
        errors.append(f"policy-action profile {rid} missing fields {missing}")
    if rid not in route_by_id:
        errors.append(f"policy-action profile {rid} has no cube route record")
        continue
    rec = route_by_id[rid]
    if prof.get("family") != rec.get("family"):
        errors.append(f"policy-action profile {rid} family does not match cube record")
    if prof.get("action_family") not in allowed:
        errors.append(f"policy-action profile {rid} unknown action_family {prof.get('action_family')}")
    if prof.get("remedy_profile_required") != rid or rid not in remedy_ids:
        errors.append(f"policy-action profile {rid} must require the matching remedy profile")
    if set(prof.get("source_currentness_refs", [])) != set(rec.get("source_currentness_refs", [])):
        errors.append(f"policy-action profile {rid} source_currentness_refs must mirror cube record")
    if not isinstance(prof.get("required_distinctions"), list) or len(prof.get("required_distinctions", [])) < 3:
        errors.append(f"policy-action profile {rid} needs at least three required_distinctions")
    if not prof.get("legitimate_use") or not prof.get("category_error_to_block"):
        errors.append(f"policy-action profile {rid} needs legitimate_use and category_error_to_block")
    instr = set(rec.get("axes", {}).get("instrument", []))
    if prof.get("action_family") == "user_fee_or_service_charge" and prof.get("benefit_nexus") not in {"cost_value_special_benefit", "explicit_statutory_fee_authority"}:
        errors.append(f"fee-primary policy-action profile {rid} needs a benefit_nexus")
    if instr & fee_like and prof.get("action_family") == "tax_revenue_or_rent_capture" and "fee" in str(prof.get("category_error_to_block", "")).lower() and "benefit" not in str(prof.get("required_distinctions", [])).lower():
        errors.append(f"mixed tax/fee policy-action profile {rid} must preserve fee benefit-nexus distinction")
    if instr & no_go_like and prof.get("action_family") not in {"prohibition_no_go_or_veto", "source_release_integrity", "classification_review_or_safe_harbor"}:
        errors.append(f"no-go-like route {rid} should not be classified as {prof.get('action_family')}")
    if rid == "instrument_choice_tax_fee_mandate_ban_public_option_compensation" and prof.get("action_family") != "classification_review_or_safe_harbor":
        errors.append("instrument-choice route must audit action categories rather than becoming tax or fee primary")

missing_profiles = sorted(set(route_by_id) - set(profile_by_id))
extra_profiles = sorted(set(profile_by_id) - set(route_by_id))
if missing_profiles:
    errors.append(f"missing policy-action profiles for cube route records: {missing_profiles}")
if extra_profiles:
    errors.append(f"extra policy-action profiles without cube records: {extra_profiles}")

summary = cube.get("audit_summary", {})
if summary.get("policy_action_profiles_required") is not True:
    errors.append("cube audit_summary must mark policy_action_profiles_required=True")
if summary.get("policy_action_profile_count") != len(route_by_id):
    errors.append("cube audit_summary policy_action_profile_count is stale")
counts = {}
for p in profiles_doc.get("profiles", []):
    counts[p.get("action_family")] = counts.get(p.get("action_family"), 0) + 1
if summary.get("policy_action_family_counts") != {k: counts[k] for k in sorted(counts)}:
    errors.append("cube audit_summary policy_action_family_counts is stale")
report_rel = cube.get("policy_action_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json policy_action_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    if f"Policy-action profiles: {len(route_by_id)}" not in report:
        errors.append("policy-action audit report is stale")

if errors:
    raise SystemExit("\n".join(errors))
print("policy-action profile audit ok")
