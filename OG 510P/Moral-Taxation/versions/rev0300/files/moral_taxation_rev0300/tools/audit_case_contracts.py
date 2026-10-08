#!/usr/bin/env python3
import json, pathlib, re, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []
version = (root / "VERSION").read_text(encoding="utf-8").strip()

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
golden = json.loads((root / "docs/00-meta/golden-cases.json").read_text(encoding="utf-8"))
contracts_doc = json.loads((root / "docs/00-meta/case-contracts.json").read_text(encoding="utf-8"))
schema = json.loads((root / "docs/00-meta/case-contract-schema.json").read_text(encoding="utf-8"))
profiles_doc = json.loads((root / "docs/00-meta/remedy-profiles.json").read_text(encoding="utf-8"))
sources = json.loads((root / "SOURCES.json").read_text(encoding="utf-8")).get("sources", [])
source_ids = {s["id"] for s in sources}

if golden.get("revision") != version:
    errors.append("golden-cases.json revision must match VERSION")
if contracts_doc.get("revision") != version:
    errors.append("case-contracts.json revision must match VERSION")
if schema.get("revision") != version:
    errors.append("case-contract-schema.json revision must match VERSION")
if contracts_doc.get("case_count") != len(contracts_doc.get("contracts", [])):
    errors.append("case-contracts.json case_count must match contracts length")

route_by_id = {rec["id"]: rec for rec in cube.get("route_records", [])}
profile_by_id = {p["route_id"]: p for p in profiles_doc.get("profiles", [])}
axis_values = {a["id"]: set(a.get("values", [])) for a in cube.get("axes", [])}
required_fields = set(schema.get("required_contract_fields", []))
allowed_contract_types = set(schema.get("contract_types", []))
allowed_statuses = set(schema.get("status_values", []))

cases = golden.get("cases", [])
contracts = contracts_doc.get("contracts", [])
case_by_id = {c.get("case_id"): c for c in cases}
contract_by_id = {}
for con in contracts:
    cid = con.get("case_id")
    if cid in contract_by_id:
        errors.append(f"duplicate case contract for {cid}")
    contract_by_id[cid] = con
    missing = sorted(required_fields - set(con))
    if missing:
        errors.append(f"case contract {cid} missing fields {missing}")
    if con.get("contract_type") not in allowed_contract_types:
        errors.append(f"case contract {cid} unknown contract_type {con.get('contract_type')}")
    if con.get("status") not in allowed_statuses:
        errors.append(f"case contract {cid} unknown status {con.get('status')}")

missing_contracts = sorted(set(case_by_id) - set(contract_by_id))
extra_contracts = sorted(set(contract_by_id) - set(case_by_id))
if missing_contracts:
    errors.append(f"missing case contracts: {missing_contracts}")
if extra_contracts:
    errors.append(f"extra case contracts: {extra_contracts}")

for c in cases:
    cid = c.get("case_id")
    con = contract_by_id.get(cid)
    if not con:
        continue
    if con.get("number") != c.get("number"):
        errors.append(f"case contract {cid} number does not match golden case")
    if con.get("expected_route_ids") != c.get("expected_route_ids"):
        errors.append(f"case contract {cid} expected_route_ids drift from golden case")
    if con.get("expected_flags") != c.get("expected_flags"):
        errors.append(f"case contract {cid} expected_flags drift from golden case")
    if con.get("source_ids") != c.get("source_ids"):
        errors.append(f"case contract {cid} source_ids drift from golden case")
    if con.get("must_not_answer") != c.get("must_not_answer"):
        errors.append(f"case contract {cid} must_not_answer drift from golden case")
    if not con.get("must_not_answer"):
        errors.append(f"case contract {cid} must include at least one must_not_answer")
    if not con.get("expected_flags"):
        errors.append(f"case contract {cid} must include route-backed expected_flags")

    route_terms = set()
    expected_profiles = []
    expected_families = []
    for rid in con.get("expected_route_ids", []):
        rec = route_by_id.get(rid)
        if not rec:
            errors.append(f"case contract {cid} unknown expected route {rid}")
            continue
        if rid not in profile_by_id:
            errors.append(f"case contract {cid} route {rid} has no remedy profile")
        else:
            expected_profiles.append(rid)
            prof = profile_by_id[rid]
            text = " ".join(str(prof.get(k, "")) for k in ["incidence_problem", "default_move", "blocked_move", "escalation_trigger"])
            text += " " + " ".join(prof.get("required_guardrails", []))
            route_terms.update(re.findall(r"[a-z0-9_]+", text.lower()))
        fam = rec.get("family")
        if fam and fam not in expected_families:
            expected_families.append(fam)
        for vals in rec.get("axes", {}).values():
            route_terms.update(vals)
    if con.get("required_remedy_profiles") != expected_profiles:
        errors.append(f"case contract {cid} required_remedy_profiles must equal expected routes with profiles")
    if con.get("required_route_families") != expected_families:
        errors.append(f"case contract {cid} required_route_families is stale")

    raw_axes = con.get("required_axes", {})
    for axis, values in raw_axes.items():
        if axis not in axis_values:
            errors.append(f"case contract {cid} uses unknown raw axis {axis}")
            continue
        for value in values:
            if value not in axis_values[axis]:
                errors.append(f"case contract {cid} raw axis {axis} value {value!r} is outside cube vocabulary")
            route_terms.add(value)
    for flag in con.get("expected_flags", []):
        if flag not in route_terms:
            errors.append(f"case contract {cid} expected flag {flag!r} is not route-, remedy-, or axis-backed")
    for sid in con.get("source_ids", []):
        if sid not in source_ids:
            errors.append(f"case contract {cid} cites missing source {sid}")

case_nums = [c.get("number") for c in cases]
if case_nums != list(range(1, len(cases) + 1)):
    errors.append("golden case numbers must be continuous")
contract_nums = [c.get("number") for c in contracts]
if contract_nums != case_nums:
    errors.append("case contract numbers must track golden case numbers")

summary = cube.get("audit_summary", {})
if summary.get("case_contracts_required") is not True:
    errors.append("cube audit_summary must mark case_contracts_required=True")
if summary.get("case_contract_count") != len(contracts):
    errors.append("cube audit_summary case_contract_count is stale")
if summary.get("golden_case_count") != len(cases):
    errors.append("cube audit_summary golden_case_count is stale")
report_rel = cube.get("case_contract_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json case_contract_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    if f"Case contracts: {len(contracts)}" not in report:
        errors.append("case-contract audit report is stale")

if errors:
    raise SystemExit("\n".join(errors))
print("case contract audit ok")
