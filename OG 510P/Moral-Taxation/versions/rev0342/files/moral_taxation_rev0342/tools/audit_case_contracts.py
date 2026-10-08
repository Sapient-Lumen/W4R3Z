#!/usr/bin/env python3
import collections, json, pathlib, re, subprocess, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []
version = (root / "VERSION").read_text(encoding="utf-8").strip()
CANDIDATE_LIMIT = 5
FACTS_ONLY_CANDIDATE_LIMIT = 8
RUNTIME_STATUS = "facts_and_axes_candidate_router_invoked"

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
route_count = len(route_by_id)
MIN_ROUTE_COVERAGE = route_count

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

# Runtime comparison: invoke the live deterministic candidate router and compare
# its returned candidates against the answer contracts. The combined pass uses
# written facts plus normalized case axes. The facts-only pass ignores axes and
# must still recover every expected route within a wider top-8 window.
runtime_results = []
router_path = root / "tools/route_case.py"
if not router_path.exists():
    errors.append("tools/route_case.py is required for runtime case comparison")
else:
    try:
        raw = subprocess.check_output(
            [
                sys.executable,
                str(router_path),
                str(root),
                "--all",
                "--candidate-limit",
                str(CANDIDATE_LIMIT),
                "--facts-only-candidate-limit",
                str(FACTS_ONLY_CANDIDATE_LIMIT),
                "--json",
            ],
            text=True,
        )
        runtime_payload = json.loads(raw)
        if runtime_payload.get("runtime_status") != RUNTIME_STATUS:
            errors.append("route_case.py returned stale runtime_status")
        if runtime_payload.get("candidate_limit") != CANDIDATE_LIMIT:
            errors.append("route_case.py returned stale candidate limit")
        if runtime_payload.get("facts_only_candidate_limit") != FACTS_ONLY_CANDIDATE_LIMIT:
            errors.append("route_case.py returned stale facts-only candidate limit")
        runtime_results = runtime_payload.get("results", [])
    except Exception as exc:
        errors.append(f"route_case.py failed: {exc}")
        runtime_results = []

runtime_by_id = {r.get("case_id"): r for r in runtime_results}
active_contracts = [c for c in contracts if c.get("status") == "active"]
expected_route_total = 0
expected_route_recall = 0
candidate_recall_cases = 0
topn_exact_cases = 0
primary_match_cases = 0
facts_only_expected_route_recall = 0
facts_only_candidate_recall_cases = 0
facts_only_primary_match_cases = 0
runtime_misses = []
facts_only_misses = []
for con in active_contracts:
    cid = con.get("case_id")
    result = runtime_by_id.get(cid)
    expected = set(con.get("expected_route_ids", []))
    expected_route_total += len(expected)
    if not result:
        runtime_misses.append({"case_id": cid, "missing": sorted(expected), "candidates": []})
        facts_only_misses.append({"case_id": cid, "missing": sorted(expected), "candidates": []})
        continue

    candidates = result.get("candidate_route_ids", [])
    candidate_set = set(candidates)
    recalled = expected & candidate_set
    expected_route_recall += len(recalled)
    if expected.issubset(candidate_set):
        candidate_recall_cases += 1
    else:
        runtime_misses.append({"case_id": cid, "missing": sorted(expected - candidate_set), "candidates": candidates})
    if set(candidates[:len(expected)]) == expected:
        topn_exact_cases += 1
    if result.get("primary_route_id") in expected:
        primary_match_cases += 1

    facts_only_candidates = result.get("facts_only_candidate_route_ids", [])
    facts_only_set = set(facts_only_candidates)
    facts_only_expected_route_recall += len(expected & facts_only_set)
    if expected.issubset(facts_only_set):
        facts_only_candidate_recall_cases += 1
    else:
        facts_only_misses.append({
            "case_id": cid,
            "missing": sorted(expected - facts_only_set),
            "candidates": facts_only_candidates,
        })
    if result.get("facts_only_primary_route_id") in expected:
        facts_only_primary_match_cases += 1

if runtime_misses:
    errors.append("runtime router missed expected route candidates: " + json.dumps(runtime_misses[:8], separators=(",", ":")))
if facts_only_misses:
    errors.append("facts-only router missed expected route candidates: " + json.dumps(facts_only_misses[:8], separators=(",", ":")))

covered_route_ids = {
    rid
    for con in active_contracts
    for rid in con.get("expected_route_ids", [])
    if rid in route_by_id
}
coverage_percent = round(100 * len(covered_route_ids) / route_count, 1) if route_count else 0.0
if len(covered_route_ids) < MIN_ROUTE_COVERAGE:
    errors.append(
        f"case route coverage regressed below floor: {len(covered_route_ids)} < {MIN_ROUTE_COVERAGE}"
    )

family_totals = collections.Counter(rec.get("family") for rec in route_by_id.values())
family_covered = collections.Counter(route_by_id[rid].get("family") for rid in covered_route_ids)
family_coverage = {
    family: {"covered": family_covered[family], "total": family_totals[family]}
    for family in sorted(family_totals)
}
for family, counts in family_coverage.items():
    if counts["covered"] == 0:
        errors.append(f"case contracts leave route family {family} entirely uncovered")

route_axis_values = {axis: set() for axis in axis_values}
for rec in route_by_id.values():
    for axis, values in rec.get("axes", {}).items():
        route_axis_values.setdefault(axis, set()).update(values)
case_axis_values = {axis: set() for axis in axis_values}
for con in active_contracts:
    for axis, values in con.get("required_axes", {}).items():
        case_axis_values.setdefault(axis, set()).update(values)
case_only_axis_counts = {
    axis: len(case_axis_values.get(axis, set()) - route_axis_values.get(axis, set()))
    for axis in sorted(case_axis_values)
    if case_axis_values.get(axis, set()) - route_axis_values.get(axis, set())
}
case_only_axis_count = sum(case_only_axis_counts.values())

summary = cube.get("audit_summary", {})
expected_summary_pairs = {
    "case_contracts_required": True,
    "case_contract_count": len(contracts),
    "golden_case_count": len(cases),
    "case_route_coverage_count": len(covered_route_ids),
    "case_route_uncovered_count": route_count - len(covered_route_ids),
    "case_route_coverage_percent": coverage_percent,
    "case_route_coverage_floor": MIN_ROUTE_COVERAGE,
    "case_route_family_coverage": family_coverage,
    "case_runtime_status": RUNTIME_STATUS,
    "case_runtime_candidate_limit": CANDIDATE_LIMIT,
    "case_runtime_facts_only_candidate_limit": FACTS_ONLY_CANDIDATE_LIMIT,
    "case_runtime_case_count": len(active_contracts),
    "case_runtime_candidate_recall_case_count": candidate_recall_cases,
    "case_runtime_topn_exact_case_count": topn_exact_cases,
    "case_runtime_primary_match_case_count": primary_match_cases,
    "case_runtime_expected_route_recall_count": expected_route_recall,
    "case_runtime_expected_route_total": expected_route_total,
    "case_runtime_candidate_miss_count": len(runtime_misses),
    "case_runtime_facts_only_candidate_recall_case_count": facts_only_candidate_recall_cases,
    "case_runtime_facts_only_primary_match_case_count": facts_only_primary_match_cases,
    "case_runtime_facts_only_expected_route_recall_count": facts_only_expected_route_recall,
    "case_runtime_facts_only_candidate_miss_count": len(facts_only_misses),
    "case_only_axis_value_count": case_only_axis_count,
    "case_only_axis_value_counts": case_only_axis_counts,
}
for key, expected_value in expected_summary_pairs.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("case_contract_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json case_contract_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    if f"Case contracts: {len(contracts)}" not in report:
        errors.append("case-contract audit report is stale")
    if f"Route coverage: {len(covered_route_ids)}/{route_count} ({coverage_percent:.1f}%)" not in report:
        errors.append("case-contract audit report route coverage is stale")
    if f"Runtime status: {RUNTIME_STATUS}" not in report:
        errors.append("case-contract audit report must state the runtime boundary")
    if f"Runtime top-{CANDIDATE_LIMIT} route recall: {expected_route_recall}/{expected_route_total}" not in report:
        errors.append("case-contract audit report runtime recall is stale")
    if f"Facts-only top-{FACTS_ONLY_CANDIDATE_LIMIT} route recall: {facts_only_expected_route_recall}/{expected_route_total}" not in report:
        errors.append("case-contract audit report facts-only recall is stale")
    if f"Runtime top-N exact cases: {topn_exact_cases}/{len(active_contracts)}" not in report:
        errors.append("case-contract audit report top-N exact count is stale")
    if f"Case-only axis values: {case_only_axis_count}" not in report:
        errors.append("case-contract audit report case-only axis count is stale")

if errors:
    raise SystemExit("\n".join(errors))
print("case contract audit ok")
