#!/usr/bin/env python3
"""Classical-GR observed-sector source-role checks.

EHT, S-star, DESI gravity, equivalence-principle, fifth-force, quantum-free-fall,
and clock/redshift results are observed-sector denominators: they increase the
burden on routes that claim classical-GR/weak-field recovery, but they are not
candidate-native evidence, black-hole microstate evidence, dark-sector detection,
metric-theory proof, or ToE promotion.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/classical-gr-observed-sector-source-role-audit.generated.md"
CLASSICAL_GR_REFS = ["REF-0702", "REF-0703", "REF-0704", "REF-0705"]
EHT_REFS = ["REF-0702", "REF-0703"]
DESI_GR_REFS = ["REF-0704"]
S2_GR_REFS = ["REF-0705"]
EQUIVALENCE_WEAKFIELD_REFS = ["REF-0437", "REF-0725", "REF-0726", "REF-0727", "REF-0728"]
EQUIVALENCE_FORECAST_ID = "DF-0029-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-REPLAY"
EQUIVALENCE_DELTA_ID = "ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE"
EQUIVALENCE_DECISION_ID = "DX-0022-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-REPLAY"
OSR_CLASSICAL = "OSR-CLASSICAL-GR"
WRAPPER_TOKEN = "METADATA-PROVENANCE-WRAPPER"
FORECAST_ID = "DF-0024-CLASSICAL-GR-OBSERVED-SECTOR-REPLAY"
DELTA_ID = "ED-0030-CLASSICAL-GR-OBSERVED-SECTOR-PRESSURE"
DECISION_ID = "DX-0017-CLASSICAL-GR-OBSERVED-SECTOR-REPLAY"
S_LEVEL = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5}
LEDGER_REQUIREMENTS = [
    ("CLASSICAL-LIMIT-LEDGER.json", "classical_limit_rows", "classical_limit_id", CLASSICAL_GR_REFS),
    ("WEAK-FIELD-PPN-LEDGER.json", "weak_field_ppn_rows", "weak_field_ppn_id", S2_GR_REFS),
    ("HORIZON-STRUCTURE-LEDGER.json", "horizon_rows", "horizon_structure_id", EHT_REFS),
    ("COSMOLOGICAL-BACKGROUND-LEDGER.json", "background_rows", "cosmological_background_id", DESI_GR_REFS),
]
ALLOWED_JSON_REF_FILES = {
    "OBSERVED-SECTOR-RECOVERY-LEDGER.json",
    "CLASSICAL-LIMIT-LEDGER.json",
    "WEAK-FIELD-PPN-LEDGER.json",
    "HORIZON-STRUCTURE-LEDGER.json",
    "COSMOLOGICAL-BACKGROUND-LEDGER.json",
    "EQUIVALENCE-PRINCIPLE-LEDGER.json",
    "DISCRIMINATOR-FORECAST-LEDGER.json",
    "EMPIRICAL-DELTA-LEDGER.json",
    "DECISION-EXPERIMENT-LEDGER.json",
    "FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json",
    # rev0347: evidence units may carry typed exclusion events naming these refs;
    # row-level acquired source_refs are checked separately above.
    "EVIDENCE-UNIT-LEDGER.json",
    # rev0348: route heads carry typed route-local handoff events naming these refs;
    # promotion/candidate-support leakage is checked by source_role_events lint.
    "CANDIDATE-ROUTE-STATE-LEDGER.json",
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def route_ids_for_row(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key, val in row.items():
        if "route" not in key:
            continue
        if isinstance(val, str) and val.startswith("R-"):
            out.append(val)
        elif isinstance(val, list):
            out.extend(item for item in val if isinstance(item, str) and item.startswith("R-"))
        elif isinstance(val, dict):
            out.extend(item for item in val if isinstance(item, str) and item.startswith("R-"))
    dedup: list[str] = []
    for rid in out:
        if rid not in dedup:
            dedup.append(rid)
    return dedup


def row_by_id(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    for row in rows:
        if isinstance(row, dict) and row.get(key) == value:
            return row
    return None


def duplicate_refs(row: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    dup: list[str] = []
    for ref in row.get("source_refs", []) or []:
        if ref in seen and ref not in dup:
            dup.append(ref)
        seen.add(ref)
    return dup


def route_state_maps(root: Path) -> tuple[dict[str, str], dict[str, str], set[str]]:
    rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    states = {row["route_id"]: row.get("authority_state") for row in rows if isinstance(row, dict) and isinstance(row.get("route_id"), str)}
    ceilings = {row["route_id"]: row.get("promotion_ceiling") for row in rows if isinstance(row, dict) and isinstance(row.get("route_id"), str)}
    classical_routes = {
        row["route_id"]
        for row in rows
        if isinstance(row, dict)
        and isinstance(row.get("route_id"), str)
        and OSR_CLASSICAL in (row.get("observed_sector_obligations", []) or [])
    }
    return states, ceilings, classical_routes


def contains_any_ref(value: Any, refs: set[str]) -> bool:
    if isinstance(value, dict):
        return any(contains_any_ref(v, refs) for v in value.values())
    if isinstance(value, list):
        return any(contains_any_ref(v, refs) for v in value)
    return isinstance(value, str) and value in refs


def evaluate_classical_gr_observed_sector(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    ledger_summaries: list[dict[str, Any]] = []
    states, ceilings, classical_routes = route_state_maps(root)

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    add("classical-route-set-nonempty", bool(classical_routes), f"routes={sorted(classical_routes)}")

    osr_rows = load_json(root, "OBSERVED-SECTOR-RECOVERY-LEDGER.json").get("obligations", [])
    osr = row_by_id(osr_rows, "obligation_id", OSR_CLASSICAL)
    add("osr-classical-row-present", osr is not None, f"row_present={osr is not None}")
    if osr:
        osr_routes = set(osr.get("route_ids_touching", []) or [])
        add("osr-classical-route-set-matches-route-ledger", osr_routes == classical_routes, f"osr_routes={sorted(osr_routes)}; route_ledger={sorted(classical_routes)}")
        missing_refs = [ref for ref in CLASSICAL_GR_REFS if ref not in (osr.get("source_refs", []) or [])]
        add("osr-classical-current-refs-present", not missing_refs, f"missing_refs={missing_refs}")
        missing_ep_refs = [ref for ref in EQUIVALENCE_WEAKFIELD_REFS if ref not in (osr.get("source_refs", []) or [])]
        add("osr-equivalence-weakfield-refs-present", not missing_ep_refs, f"missing_refs={missing_ep_refs}")
        add("osr-classical-non-promotion-language", "not" in str(osr.get("residual_cap", "")).lower() or "not" in str(osr.get("current_archive_state", "")).lower(), f"residual_cap={osr.get('residual_cap')}")

    # Current classical-GR refs must not be spent as acquired evidence-unit support.
    evidence_hits: list[str] = []
    for row in load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", []):
        refs = row.get("source_refs", []) or []
        bad = [ref for ref in CLASSICAL_GR_REFS if ref in refs]
        if bad:
            evidence_hits.append(f"{row.get('evidence_unit_id')}:{','.join(bad)}")
    add("current-classical-gr-refs-not-acquired-evidence", not evidence_hits, f"hits={evidence_hits}")

    ep_evidence_hits: list[str] = []
    for row in load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", []):
        refs = row.get("source_refs", []) or []
        bad = [ref for ref in EQUIVALENCE_WEAKFIELD_REFS if ref in refs]
        if bad:
            ep_evidence_hits.append(f"{row.get('evidence_unit_id')}:{','.join(bad)}")
    add("equivalence-weakfield-refs-not-acquired-evidence", not ep_evidence_hits, f"hits={ep_evidence_hits}")

    total_route_rows_checked = 0
    wrapper_rows_checked = 0
    for ledger_file, collection, id_field, required_refs in LEDGER_REQUIREMENTS:
        rows = load_json(root, ledger_file).get(collection, [])
        before = len(failures)
        for row in rows:
            if not isinstance(row, dict):
                continue
            rid = row.get(id_field, "<missing>")
            row_routes = set(route_ids_for_row(row))
            refs = row.get("source_refs", []) or []
            present_current = [ref for ref in CLASSICAL_GR_REFS if ref in refs]
            dup = duplicate_refs(row)
            add(f"classical-gr-source-refs-deduped-{rid}", not dup, f"duplicate_refs={dup}")
            if WRAPPER_TOKEN in str(rid):
                wrapper_rows_checked += 1
                add(f"classical-gr-wrapper-no-current-refs-{rid}", not present_current, f"present_current_refs={present_current}")
                continue
            if row_routes & classical_routes:
                total_route_rows_checked += 1
                missing = [ref for ref in required_refs if ref not in refs]
                add(f"classical-gr-required-refs-present-{rid}", not missing, f"missing_refs={missing}; required={required_refs}")
                role = row.get("observed_classical_gr_credit_role")
                cap = row.get("observed_classical_gr_credit_cap")
                rule = row.get("observed_classical_gr_credit_rule")
                add(f"classical-gr-role-present-{rid}", role == "observed-classical-gr-denominator-pressure", f"role={role}")
                route_caps = row.get("route_observed_classical_gr_credit_caps", {})
                add(f"classical-gr-route-caps-present-{rid}", isinstance(route_caps, dict) and all(r in route_caps for r in row_routes & classical_routes), f"route_caps={route_caps}")
                add(f"classical-gr-rule-nonpromotion-{rid}", isinstance(rule, str) and ("not" in rule.lower() or "forbidden" in rule.lower()), f"rule={rule}")
                for route_id in sorted(row_routes & classical_routes):
                    cap_value = route_caps.get(route_id, cap)
                    ok = cap_value in S_LEVEL and states.get(route_id) in S_LEVEL and S_LEVEL[cap_value] <= S_LEVEL[states[route_id]]
                    add(f"classical-gr-current-cap-{rid}-{route_id}", ok, f"cap={cap_value}; route_state={states.get(route_id)}; route_ceiling={ceilings.get(route_id)}")
            else:
                add(f"classical-gr-nonclassical-row-no-current-refs-{rid}", not present_current, f"routes={sorted(row_routes)}; present_current_refs={present_current}")
        ledger_summaries.append({"ledger_file": ledger_file, "rows": len(rows), "failures": len(failures) - before})

    # Pressure rows must be route-facing and conservative.
    forecast = row_by_id(load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", []), "forecast_id", FORECAST_ID)
    delta = row_by_id(load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", []), "delta_id", DELTA_ID)
    decision = row_by_id(load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", []), "experiment_id", DECISION_ID)
    for name, row, id_value in [("forecast", forecast, FORECAST_ID), ("delta", delta, DELTA_ID), ("decision", decision, DECISION_ID)]:
        add(f"classical-gr-{name}-row-present", row is not None, f"id={id_value}")
        if not row:
            continue
        row_routes = set(route_ids_for_row(row))
        add(f"classical-gr-{name}-route-set", row_routes == classical_routes, f"row_routes={sorted(row_routes)}; classical_routes={sorted(classical_routes)}")
        missing = [ref for ref in CLASSICAL_GR_REFS if ref not in (row.get("source_refs", []) or [])]
        add(f"classical-gr-{name}-refs-present", not missing, f"missing_refs={missing}")
        ceilings_map = row.get("route_authority_ceilings")
        add(f"classical-gr-{name}-route-ceilings-present", isinstance(ceilings_map, dict) and set(ceilings_map) == classical_routes, f"route_authority_ceilings={ceilings_map}")
        if isinstance(ceilings_map, dict):
            for route_id, cap in ceilings_map.items():
                ok = cap in S_LEVEL and states.get(route_id) in S_LEVEL and S_LEVEL[cap] <= S_LEVEL[states[route_id]]
                add(f"classical-gr-{name}-current-state-cap-{route_id}", ok, f"cap={cap}; route_state={states.get(route_id)}")
        text = " ".join(str(row.get(k, "")) for k in ["non_promotion_warning", "residual_cap", "non_promotion_clause", "state_effect"])
        add(f"classical-gr-{name}-nonpromotion-language", "not" in text.lower() and ("promotion" in text.lower() or "candidate" in text.lower()), f"text={text[:180]}")

    if decision:
        hooks = decision.get("empirical_delta_hooks", []) or []
        add("classical-gr-decision-hooks-delta", DELTA_ID in hooks, f"hooks={hooks}")

    # Route-head mirrors must expose the new pressure rows for every classical-GR route.
    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    for row in route_rows:
        route_id = row.get("route_id") if isinstance(row, dict) else None
        if route_id not in classical_routes:
            continue
        add(f"classical-gr-route-mirror-forecast-{route_id}", FORECAST_ID in (row.get("forecast_ids", []) or []), f"forecast_ids={row.get('forecast_ids')}")
        add(f"classical-gr-route-mirror-delta-{route_id}", DELTA_ID in (row.get("empirical_delta_ids", []) or []), f"empirical_delta_ids={row.get('empirical_delta_ids')}")
        add(f"classical-gr-route-mirror-decision-{route_id}", DECISION_ID in (row.get("decision_experiment_ids", []) or []), f"decision_experiment_ids={row.get('decision_experiment_ids')}")


    # Equivalence-principle / fifth-force / weak-field denominator extension.
    all_routes = set(states)
    ep_route_rows_checked = 0
    ep_wrapper_rows_checked = 0
    ep_rows = load_json(root, "EQUIVALENCE-PRINCIPLE-LEDGER.json").get("equivalence_principle_rows", [])
    for row in ep_rows:
        if not isinstance(row, dict):
            continue
        rid = row.get("equivalence_principle_id", "<missing>")
        row_routes = set(route_ids_for_row(row))
        refs = row.get("source_refs", []) or []
        present_ep = [ref for ref in EQUIVALENCE_WEAKFIELD_REFS if ref in refs]
        dup = duplicate_refs(row)
        add(f"equivalence-weakfield-source-refs-deduped-{rid}", not dup, f"duplicate_refs={dup}")
        if WRAPPER_TOKEN in str(rid):
            ep_wrapper_rows_checked += 1
            add(f"equivalence-weakfield-wrapper-no-current-refs-{rid}", not present_ep, f"present_current_refs={present_ep}")
            continue
        ep_route_rows_checked += 1
        missing = [ref for ref in EQUIVALENCE_WEAKFIELD_REFS if ref not in refs]
        add(f"equivalence-weakfield-required-refs-present-{rid}", not missing, f"missing_refs={missing}")
        role = row.get("observed_equivalence_principle_credit_role")
        cap = row.get("observed_equivalence_principle_credit_cap")
        rule = row.get("observed_equivalence_principle_credit_rule")
        route_caps = row.get("route_observed_equivalence_principle_credit_caps", {})
        add(f"equivalence-weakfield-role-present-{rid}", role == "equivalence-fifth-force-weakfield-denominator-pressure", f"role={role}")
        add(f"equivalence-weakfield-cap-S0-{rid}", cap == "S0", f"cap={cap}")
        add(f"equivalence-weakfield-route-caps-S0-{rid}", isinstance(route_caps, dict) and all(route_caps.get(route) == "S0" for route in row_routes), f"route_caps={route_caps}")
        add(f"equivalence-weakfield-rule-nonpromotion-{rid}", isinstance(rule, str) and "not" in rule.lower() and ("promote" in rule.lower() or "candidate" in rule.lower() or "evidence" in rule.lower()), f"rule={rule}")

    eq_forecast = row_by_id(load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", []), "forecast_id", EQUIVALENCE_FORECAST_ID)
    eq_delta = row_by_id(load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", []), "delta_id", EQUIVALENCE_DELTA_ID)
    eq_decision = row_by_id(load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", []), "experiment_id", EQUIVALENCE_DECISION_ID)
    for name, row, id_value in [("forecast", eq_forecast, EQUIVALENCE_FORECAST_ID), ("delta", eq_delta, EQUIVALENCE_DELTA_ID), ("decision", eq_decision, EQUIVALENCE_DECISION_ID)]:
        add(f"equivalence-weakfield-{name}-row-present", row is not None, f"id={id_value}")
        if not row:
            continue
        row_routes = set(route_ids_for_row(row))
        add(f"equivalence-weakfield-{name}-all-route-set", row_routes == all_routes, f"row_routes={sorted(row_routes)}; all_routes={sorted(all_routes)}")
        missing = [ref for ref in EQUIVALENCE_WEAKFIELD_REFS if ref not in (row.get("source_refs", []) or [])]
        add(f"equivalence-weakfield-{name}-refs-present", not missing, f"missing_refs={missing}")
        ceilings_map = row.get("route_authority_ceilings")
        add(f"equivalence-weakfield-{name}-route-ceilings-S0", isinstance(ceilings_map, dict) and set(ceilings_map) == all_routes and all(v == "S0" for v in ceilings_map.values()), f"route_authority_ceilings={ceilings_map}")
        text = " ".join(str(row.get(k, "")) for k in ["non_promotion_warning", "residual_cap", "non_promotion_clause", "state_effect", "positive_result_credit"])
        add(f"equivalence-weakfield-{name}-nonpromotion-language", "not" in text.lower() and ("promotion" in text.lower() or "support" in text.lower() or "evidence" in text.lower()), f"text={text[:180]}")
    if eq_decision:
        hooks = eq_decision.get("empirical_delta_hooks", []) or []
        add("equivalence-weakfield-decision-hooks-delta", EQUIVALENCE_DELTA_ID in hooks, f"hooks={hooks}")

    eu_rows = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])
    missing_eu_delta = [row.get("evidence_unit_id") for row in eu_rows if isinstance(row, dict) and row.get("evidence_unit_id") != "EU-0014-METADATA-PROVENANCE-WRAPPER" and EQUIVALENCE_DELTA_ID not in (row.get("empirical_delta_ids", []) or [])]
    add("equivalence-weakfield-evidence-units-reciprocate-delta", not missing_eu_delta, f"missing={missing_eu_delta}")
    wrapper = row_by_id(eu_rows, "evidence_unit_id", "EU-0014-METADATA-PROVENANCE-WRAPPER")
    add("equivalence-weakfield-metadata-wrapper-lacks-delta-handle", isinstance(wrapper, dict) and EQUIVALENCE_DELTA_ID not in (wrapper.get("empirical_delta_ids", []) or []), f"empirical_delta_ids={wrapper.get('empirical_delta_ids') if isinstance(wrapper, dict) else None}")

    for row in route_rows:
        route_id = row.get("route_id") if isinstance(row, dict) else None
        if route_id not in all_routes:
            continue
        add(f"equivalence-weakfield-route-mirror-forecast-{route_id}", EQUIVALENCE_FORECAST_ID in (row.get("forecast_ids", []) or []), f"forecast_ids={row.get('forecast_ids')}")
        add(f"equivalence-weakfield-route-mirror-delta-{route_id}", EQUIVALENCE_DELTA_ID in (row.get("empirical_delta_ids", []) or []), f"empirical_delta_ids={row.get('empirical_delta_ids')}")
        add(f"equivalence-weakfield-route-mirror-decision-{route_id}", EQUIVALENCE_DECISION_ID in (row.get("decision_experiment_ids", []) or []), f"decision_experiment_ids={row.get('decision_experiment_ids')}")

    misplaced: list[str] = []
    ref_set = set(CLASSICAL_GR_REFS)
    for path in sorted(root.glob("*.json")):
        if path.name in ALLOWED_JSON_REF_FILES:
            continue
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        if contains_any_ref(obj, ref_set):
            misplaced.append(path.name)
    add("current-classical-gr-refs-only-in-classical-gr-ledgers", not misplaced, f"misplaced_files={misplaced}")

    ep_misplaced: list[str] = []
    ep_ref_set = set(EQUIVALENCE_WEAKFIELD_REFS)
    for path in sorted(root.glob("*.json")):
        if path.name in ALLOWED_JSON_REF_FILES:
            continue
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        if contains_any_ref(obj, ep_ref_set):
            ep_misplaced.append(path.name)
    add("equivalence-weakfield-refs-only-in-observed-gr-ledgers", not ep_misplaced, f"misplaced_files={ep_misplaced}")

    return {
        "audit_file": GENERATED_AUDIT,
        "classical_routes": sorted(classical_routes),
        "current_refs": CLASSICAL_GR_REFS,
        "ledger_summaries": ledger_summaries,
        "route_rows_checked": total_route_rows_checked,
        "wrapper_rows_checked": wrapper_rows_checked,
        "equivalence_weakfield_refs": EQUIVALENCE_WEAKFIELD_REFS,
        "equivalence_weakfield_route_rows_checked": ep_route_rows_checked,
        "equivalence_weakfield_wrapper_rows_checked": ep_wrapper_rows_checked,
        "checks": checks,
        "failures": failures,
    }


def write_classical_gr_observed_sector_audit(root: Path) -> None:
    result = evaluate_classical_gr_observed_sector(root)
    lines = [
        "# Classical-GR observed-sector source-role audit (generated)",
        "",
        "Generated from observed-sector, classical-limit, weak-field/PPN, horizon, cosmological-background, forecast, empirical-delta, decision, evidence-unit, and route-state ledgers. Do not edit directly; run `make index` after changing classical-GR observed-sector custody.",
        "",
        f"- Classical-GR routes checked: `{len(result['classical_routes'])}`",
        f"- Current classical-GR refs under audit: `{', '.join(result['current_refs'])}`",
        f"- Classical-GR route rows checked: `{result['route_rows_checked']}`",
        f"- Equivalence/fifth-force/weak-field refs under audit: `{', '.join(result['equivalence_weakfield_refs'])}`",
        f"- Equivalence/fifth-force/weak-field route rows checked: `{result['equivalence_weakfield_route_rows_checked']}`",
        f"- Wrapper rows checked for no current refs: `{result['wrapper_rows_checked']}`",
        f"- Equivalence wrapper rows checked for no current refs: `{result['equivalence_weakfield_wrapper_rows_checked']}`",
        f"- Classical-GR observed-sector checks: `{len(result['checks'])}`",
        f"- Classical-GR observed-sector failures: `{len(result['failures'])}`",
        "",
        "## Classical-GR route set",
        "",
        ", ".join(f"`{route}`" for route in result["classical_routes"]),
        "",
        "## Ledger summaries",
        "",
        "| Ledger | Rows | Failures |",
        "|---|---:|---:|",
    ]
    for item in result["ledger_summaries"]:
        lines.append(f"| `{item['ledger_file']}` | `{item['rows']}` | `{item['failures']}` |")
    lines += ["", "## Failure details", ""]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "EHT shadow/polarization, S-star precession, DESI growth/full-shape gravity, MICROSCOPE WEP, short-range inverse-square/fifth-force, atom-interferometer WEP, ACES/PHARAO clock/redshift, and torsion-balance constraints are public observed-sector denominators. They increase replay burden for routes claiming classical-GR, weak-field, metric, free-fall, fifth-force, or clock/redshift recovery, but they do not become acquired evidence-unit source credit, black-hole microstate evidence, dark-sector detection, candidate-native support, or route promotion.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_classical_gr_observed_sector_audit(root)
    outcome = evaluate_classical_gr_observed_sector(root)
    if outcome["failures"]:
        print("CLASSICAL GR OBSERVED-SECTOR POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CLASSICAL GR OBSERVED-SECTOR OK")
