#!/usr/bin/env python3
"""QM/QFT/gauge observed-sector denominator source-role checks."""
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any
sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/qm-qft-observed-sector-source-role-audit.generated.md"
QM_ROUTES = [
    "R-OQ0057-LAB-GIE-BMV",
    "R-OQ0057-LAB-GRAVITON-COUNTING",
    "R-OQ0057-AMPLITUDES-BOOTSTRAP",
    "R-OQ0057-ASYMPTOTIC-SAFETY",
    "R-OQ0057-STRINGM-ATLAS",
]
QFT_REFS = ["REF-0710", "REF-0711"]
LORENTZ_CPT_SME_REFS = ["REF-0509", "REF-0715", "REF-0716", "REF-0717", "REF-0718"]
LORENTZ_CPT_SME_FORECAST_ID = "DF-0027-LORENTZ-CPT-SME-OBSERVED-SECTOR-REPLAY"
LORENTZ_CPT_SME_DELTA_ID = "ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE"
LORENTZ_CPT_SME_DECISION_ID = "DX-0020-LORENTZ-CPT-SME-OBSERVED-SECTOR-REPLAY"
FORECAST_ID = "DF-0025-QM-QFT-GAUGE-OBSERVED-SECTOR-REPLAY"
DELTA_ID = "ED-0031-QM-QFT-GAUGE-OBSERVED-SECTOR-PRESSURE"
DECISION_ID = "DX-0018-QM-QFT-GAUGE-OBSERVED-SECTOR-REPLAY"
EVIDENCE_UNITS = [
    "EU-0004-STRINGM-ATLAS-DUALITY-VACUUM",
    "EU-0005-AS-RG-TRUNCATION",
    "EU-0007-AMPLITUDES-BOOTSTRAP-CONSISTENCY",
    "EU-0008-LAB-GIE-MEDIATOR",
    "EU-0011-GRAVITON-COUNTING",
]
LEDGER_SPECS = [
    ("QUANTIZATION-MAP-LEDGER.json", "quantization_rows", "quantization_map_id"),
    ("GAUGE-SYMMETRY-LEDGER.json", "gauge_rows", "gauge_symmetry_id"),
    ("UNITARITY-CHECK-LEDGER.json", "unitarity_rows", "unitarity_check_id"),
    ("LORENTZ-COVARIANCE-LEDGER.json", "lorentz_covariance_rows", "lorentz_covariance_id"),
    ("MICROCAUSALITY-LOCALITY-LEDGER.json", "microcausality_locality_rows", "microcausality_locality_id"),
    ("LOCAL-QFT-RECOVERY-LEDGER.json", "local_qft_recovery_rows", "local_qft_recovery_id"),
    ("SCATTERING-OBSERVABLE-LEDGER.json", "scattering_observable_rows", "scattering_observable_id"),
]
LORENTZ_CPT_SME_LEDGER_SPECS = [
    ("LORENTZ-COVARIANCE-LEDGER.json", "lorentz_covariance_rows", "lorentz_covariance_id"),
    ("CPT-DISCRETE-SYMMETRY-LEDGER.json", "cpt_discrete_symmetry_rows", "cpt_discrete_symmetry_id"),
    ("MICROCAUSALITY-LOCALITY-LEDGER.json", "microcausality_locality_rows", "microcausality_locality_id"),
]
ALLOWED_JSON_FILES = {rel for rel, _, _ in LEDGER_SPECS} | {rel for rel, _, _ in LORENTZ_CPT_SME_LEDGER_SPECS} | {
    "OBSERVED-SECTOR-RECOVERY-LEDGER.json",
    "DISCRIMINATOR-FORECAST-LEDGER.json",
    "EMPIRICAL-DELTA-LEDGER.json",
    "DECISION-EXPERIMENT-LEDGER.json",
    "FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json",
    "CANDIDATE-ROUTE-STATE-LEDGER.json",
    # rev0347: evidence units may carry typed exclusion events naming these refs;
    # row-level acquired source_refs are checked separately above.
    "EVIDENCE-UNIT-LEDGER.json",
}
S_LEVEL = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5}
WRAPPER_TOKEN = "METADATA-PROVENANCE-WRAPPER"

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
    dedup: list[str] = []
    for rid in out:
        if rid not in dedup:
            dedup.append(rid)
    return dedup

def duplicate_refs(row: dict[str, Any]) -> list[str]:
    seen: set[str] = set(); dup: list[str] = []
    for ref in row.get("source_refs", []) or []:
        if ref in seen and ref not in dup:
            dup.append(ref)
        seen.add(ref)
    return dup

def contains_any_refs(obj: Any, refs: set[str]) -> bool:
    if isinstance(obj, dict):
        return any(contains_any_refs(v, refs) for v in obj.values())
    if isinstance(obj, list):
        return any(contains_any_refs(v, refs) for v in obj)
    return isinstance(obj, str) and obj in refs

def row_lookup(rows: list[dict[str, Any]], id_field: str, row_id: str) -> dict[str, Any] | None:
    for row in rows:
        if isinstance(row, dict) and row.get(id_field) == row_id:
            return row
    return None

def evaluate_qm_qft_observed_sector(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    ledger_summaries: list[dict[str, Any]] = []
    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    routes = {row.get("route_id"): row for row in route_rows if isinstance(row, dict) and isinstance(row.get("route_id"), str)}
    route_state = {rid: row.get("authority_state") for rid, row in routes.items()}
    add("route-count-unchanged", len(route_rows) == 13, f"route_rows={len(route_rows)}")

    osr_rows = load_json(root, "OBSERVED-SECTOR-RECOVERY-LEDGER.json").get("obligations", [])
    osr = row_lookup(osr_rows, "obligation_id", "OSR-QM-QFT")
    add("osr-qm-qft-present", isinstance(osr, dict), f"present={isinstance(osr, dict)}")
    if isinstance(osr, dict):
        add("osr-qm-qft-routes-exact", osr.get("route_ids_touching") == QM_ROUTES, f"routes={osr.get('route_ids_touching')}")
        missing = [ref for ref in QFT_REFS if ref not in osr.get("source_refs", [])]
        add("osr-qm-qft-current-refs-present", not missing, f"missing={missing}")
        add("osr-qm-qft-cap-S0", osr.get("observed_qm_qft_credit_cap") == "S0", f"cap={osr.get('observed_qm_qft_credit_cap')}")
        rule = str(osr.get("observed_qm_qft_credit_rule", "")).lower()
        add("osr-qm-qft-nonpromotion-rule", "not" in rule and ("promotion" in rule or "evidence" in rule), f"rule={osr.get('observed_qm_qft_credit_rule')}")

    eu_rows = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])
    acquired_hits: list[str] = []
    missing_handoffs: list[str] = []
    for row in eu_rows:
        if not isinstance(row, dict):
            continue
        eu_id = row.get("evidence_unit_id")
        refs = row.get("source_refs", []) or []
        bad = [ref for ref in QFT_REFS if ref in refs]
        if bad:
            acquired_hits.append(f"{eu_id}:{','.join(bad)}")
        if eu_id in EVIDENCE_UNITS and DELTA_ID not in (row.get("empirical_delta_ids", []) or []):
            missing_handoffs.append(eu_id)
    add("qft-refs-not-acquired-evidence", not acquired_hits, f"hits={acquired_hits}")
    add("evidence-units-reciprocate-delta", not missing_handoffs, f"missing={missing_handoffs}")

    forecast = row_lookup(load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", []), "forecast_id", FORECAST_ID)
    delta = row_lookup(load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", []), "delta_id", DELTA_ID)
    decision = row_lookup(load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", []), "experiment_id", DECISION_ID)
    for label, row in [("forecast", forecast), ("delta", delta), ("decision", decision)]:
        add(f"qm-qft-{label}-row-present", isinstance(row, dict), f"present={isinstance(row, dict)}")
        if not isinstance(row, dict):
            continue
        add(f"qm-qft-{label}-routes-exact", row.get("route_ids") == QM_ROUTES, f"routes={row.get('route_ids')}")
        missing = [ref for ref in QFT_REFS if ref not in row.get("source_refs", [])]
        add(f"qm-qft-{label}-refs-present", not missing, f"missing={missing}")
        add(f"qm-qft-{label}-source-refs-deduped", not duplicate_refs(row), f"duplicates={duplicate_refs(row)}")
        caps = row.get("route_authority_ceilings", {})
        add(f"qm-qft-{label}-route-caps-present", isinstance(caps, dict) and all(rid in caps for rid in QM_ROUTES), f"caps={caps}")
        if isinstance(caps, dict):
            for rid in QM_ROUTES:
                cap = caps.get(rid); state = route_state.get(rid)
                ok = cap in S_LEVEL and state in S_LEVEL and S_LEVEL[cap] <= S_LEVEL[state]
                add(f"qm-qft-{label}-current-cap-{rid}", ok, f"cap={cap}; state={state}")
        text = " ".join(str(v) for v in row.values() if isinstance(v, (str, int, float))).lower()
        add(f"qm-qft-{label}-nonpromotion-language", ("not" in text or "no route promotion" in text) and ("promotion" in text or "evidence" in text), f"text_has_nonpromotion={('not' in text or 'no route promotion' in text)}")
    if isinstance(decision, dict):
        add("qm-qft-decision-hooks-delta", DELTA_ID in (decision.get("empirical_delta_hooks", []) or []), f"hooks={decision.get('empirical_delta_hooks')}")
    if isinstance(delta, dict):
        add("qm-qft-delta-evidence-units-exact", set(delta.get("evidence_unit_ids", []) or []) == set(EVIDENCE_UNITS), f"evidence_unit_ids={delta.get('evidence_unit_ids')}")

    for rid in QM_ROUTES:
        row = routes.get(rid)
        add(f"qm-qft-route-present-{rid}", isinstance(row, dict), "present" if isinstance(row, dict) else "missing")
        if isinstance(row, dict):
            add(f"qm-qft-route-mirror-forecast-{rid}", FORECAST_ID in (row.get("forecast_ids", []) or []), f"forecast_ids={row.get('forecast_ids')}")
            add(f"qm-qft-route-mirror-delta-{rid}", DELTA_ID in (row.get("empirical_delta_ids", []) or []), f"empirical_delta_ids={row.get('empirical_delta_ids')}")
            add(f"qm-qft-route-mirror-decision-{rid}", DECISION_ID in (row.get("decision_experiment_ids", []) or []), f"decision_experiment_ids={row.get('decision_experiment_ids')}")

    route_control_rows = 0; wrapper_rows = 0
    for rel, collection, id_field in LEDGER_SPECS:
        rows = load_json(root, rel).get(collection, [])
        before = len(failures)
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_id = str(row.get(id_field, "<missing>"))
            routes_for_row = route_ids_for_row(row)
            refs = row.get("source_refs", []) or []
            present_new_refs = [ref for ref in QFT_REFS if ref in refs]
            if WRAPPER_TOKEN in row_id:
                wrapper_rows += 1
                add(f"qm-qft-wrapper-no-new-refs-{row_id}", not present_new_refs, f"present={present_new_refs}")
                add(f"qm-qft-wrapper-cap-S0-{row_id}", row.get("observed_qm_qft_credit_cap") == "S0", f"cap={row.get('observed_qm_qft_credit_cap')}")
                continue
            if any(rid in QM_ROUTES for rid in routes_for_row):
                route_control_rows += 1
                missing = [ref for ref in QFT_REFS if ref not in refs]
                add(f"qm-qft-route-control-new-refs-{row_id}", not missing, f"missing={missing}")
                add(f"qm-qft-route-control-deduped-{row_id}", not duplicate_refs(row), f"duplicates={duplicate_refs(row)}")
                add(f"qm-qft-route-control-role-{row_id}", row.get("observed_qm_qft_credit_role") == "observed-qm-qft-denominator-pressure", f"role={row.get('observed_qm_qft_credit_role')}")
                add(f"qm-qft-route-control-cap-S0-{row_id}", row.get("observed_qm_qft_credit_cap") == "S0", f"cap={row.get('observed_qm_qft_credit_cap')}")
                rule = str(row.get("observed_qm_qft_credit_rule", "")).lower()
                add(f"qm-qft-route-control-nonpromotion-{row_id}", "not" in rule and ("promotion" in rule or "evidence" in rule), f"rule={row.get('observed_qm_qft_credit_rule')}")
                caps = row.get("route_observed_qm_qft_credit_caps", {})
                for rid in [r for r in routes_for_row if r in QM_ROUTES]:
                    cap = caps.get(rid) if isinstance(caps, dict) else None
                    add(f"qm-qft-route-control-route-cap-{row_id}-{rid}", cap == "S0", f"cap={cap}")
        ledger_summaries.append({"ledger_file": rel, "rows": len(rows), "failures": len(failures) - before})

    # Lorentz/CPT/SME denominator pressure is part of the QM/QFT
    # observed-sector boundary, but it has a wider route footprint and a
    # narrower ledger footprint than constants/QED. Keep it here to avoid a
    # parallel policy file while still making the source role executable.
    all_routes = [row.get("route_id") for row in route_rows if isinstance(row, dict) and isinstance(row.get("route_id"), str)]
    route_specific_eus = [row.get("evidence_unit_id") for row in eu_rows if isinstance(row, dict) and row.get("evidence_unit_id") != "EU-0014-METADATA-PROVENANCE-WRAPPER"]
    acquired_lorentz_hits: list[str] = []
    missing_lorentz_handoffs: list[str] = []
    for row in eu_rows:
        if not isinstance(row, dict):
            continue
        eu_id = row.get("evidence_unit_id")
        bad = [ref for ref in LORENTZ_CPT_SME_REFS if ref in (row.get("source_refs", []) or [])]
        if bad:
            acquired_lorentz_hits.append(f"{eu_id}:{','.join(bad)}")
        if eu_id in route_specific_eus and LORENTZ_CPT_SME_DELTA_ID not in (row.get("empirical_delta_ids", []) or []):
            missing_lorentz_handoffs.append(str(eu_id))
    add("lorentz-cpt-sme-refs-not-acquired-evidence", not acquired_lorentz_hits, f"hits={acquired_lorentz_hits}")
    add("lorentz-cpt-sme-evidence-units-reciprocate-delta", not missing_lorentz_handoffs, f"missing={missing_lorentz_handoffs}")

    lorentz_forecast = row_lookup(load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", []), "forecast_id", LORENTZ_CPT_SME_FORECAST_ID)
    lorentz_delta = row_lookup(load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", []), "delta_id", LORENTZ_CPT_SME_DELTA_ID)
    lorentz_decision = row_lookup(load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", []), "experiment_id", LORENTZ_CPT_SME_DECISION_ID)
    for label, row in [("forecast", lorentz_forecast), ("delta", lorentz_delta), ("decision", lorentz_decision)]:
        add(f"lorentz-cpt-sme-{label}-row-present", isinstance(row, dict), f"present={isinstance(row, dict)}")
        if not isinstance(row, dict):
            continue
        add(f"lorentz-cpt-sme-{label}-routes-exact", row.get("route_ids") == all_routes, f"routes={row.get('route_ids')}")
        missing = [ref for ref in LORENTZ_CPT_SME_REFS if ref not in row.get("source_refs", [])]
        add(f"lorentz-cpt-sme-{label}-refs-present", not missing, f"missing={missing}")
        caps = row.get("route_authority_ceilings", {})
        add(f"lorentz-cpt-sme-{label}-caps-S0", isinstance(caps, dict) and set(caps) == set(all_routes) and all(value == "S0" for value in caps.values()), f"caps={caps}")
        text = " ".join(str(v) for v in row.values() if isinstance(v, (str, int, float))).lower()
        add(f"lorentz-cpt-sme-{label}-nonpromotion-language", "not" in text and ("promotion" in text or "evidence" in text or "support" in text), f"nonpromotion_present={'not' in text}")
    if isinstance(lorentz_decision, dict):
        add("lorentz-cpt-sme-decision-hooks-delta", LORENTZ_CPT_SME_DELTA_ID in (lorentz_decision.get("empirical_delta_hooks", []) or []), f"hooks={lorentz_decision.get('empirical_delta_hooks')}")
    if isinstance(lorentz_delta, dict):
        add("lorentz-cpt-sme-delta-evidence-units-exact", set(lorentz_delta.get("evidence_unit_ids", []) or []) == set(route_specific_eus), f"evidence_unit_ids={lorentz_delta.get('evidence_unit_ids')}")

    for rid in all_routes:
        row = routes.get(rid)
        if isinstance(row, dict):
            add(f"lorentz-cpt-sme-route-mirror-forecast-{rid}", LORENTZ_CPT_SME_FORECAST_ID in (row.get("forecast_ids", []) or []), f"forecast_ids={row.get('forecast_ids')}")
            add(f"lorentz-cpt-sme-route-mirror-delta-{rid}", LORENTZ_CPT_SME_DELTA_ID in (row.get("empirical_delta_ids", []) or []), f"empirical_delta_ids={row.get('empirical_delta_ids')}")
            add(f"lorentz-cpt-sme-route-mirror-decision-{rid}", LORENTZ_CPT_SME_DECISION_ID in (row.get("decision_experiment_ids", []) or []), f"decision_experiment_ids={row.get('decision_experiment_ids')}")

    lorentz_route_control_rows = 0
    lorentz_wrapper_rows = 0
    for rel, collection, id_field in LORENTZ_CPT_SME_LEDGER_SPECS:
        rows = load_json(root, rel).get(collection, [])
        before = len(failures)
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_id = str(row.get(id_field, "<missing>"))
            routes_for_row = route_ids_for_row(row)
            refs = row.get("source_refs", []) or []
            present = [ref for ref in LORENTZ_CPT_SME_REFS if ref in refs]
            if WRAPPER_TOKEN in row_id or not routes_for_row:
                lorentz_wrapper_rows += 1
                add(f"lorentz-cpt-sme-wrapper-no-new-refs-{row_id}", not present, f"present={present}")
                add(f"lorentz-cpt-sme-wrapper-cap-S0-{row_id}", row.get("lorentz_cpt_sme_credit_cap") == "S0", f"cap={row.get('lorentz_cpt_sme_credit_cap')}")
                continue
            lorentz_route_control_rows += 1
            missing = [ref for ref in LORENTZ_CPT_SME_REFS if ref not in refs]
            add(f"lorentz-cpt-sme-route-control-new-refs-{row_id}", not missing, f"missing={missing}")
            add(f"lorentz-cpt-sme-route-control-deduped-{row_id}", not duplicate_refs(row), f"duplicates={duplicate_refs(row)}")
            add(f"lorentz-cpt-sme-route-control-role-{row_id}", row.get("lorentz_cpt_sme_credit_role") == "observed-sector-symmetry-denominator-pressure", f"role={row.get('lorentz_cpt_sme_credit_role')}")
            add(f"lorentz-cpt-sme-route-control-cap-S0-{row_id}", row.get("lorentz_cpt_sme_credit_cap") == "S0", f"cap={row.get('lorentz_cpt_sme_credit_cap')}")
            rule = str(row.get("lorentz_cpt_sme_credit_rule", "")).lower()
            add(f"lorentz-cpt-sme-route-control-nonpromotion-{row_id}", "not" in rule and ("promotion" in rule or "evidence" in rule or "support" in rule), f"rule={row.get('lorentz_cpt_sme_credit_rule')}")
            caps = row.get("route_lorentz_cpt_sme_credit_caps", {})
            for rid in routes_for_row:
                cap = caps.get(rid) if isinstance(caps, dict) else None
                add(f"lorentz-cpt-sme-route-control-route-cap-{row_id}-{rid}", cap == "S0", f"cap={cap}")
        ledger_summaries.append({"ledger_file": rel, "rows": len(rows), "failures": len(failures) - before})

    misplaced: list[str] = []
    refset = set(QFT_REFS) | set(LORENTZ_CPT_SME_REFS)
    for path in sorted(root.glob("*.json")):
        if path.name in ALLOWED_JSON_FILES:
            continue
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        if contains_any_refs(obj, refset):
            misplaced.append(path.name)
    add("qft-refs-only-in-allowed-json-surfaces", not misplaced, f"misplaced={misplaced}")

    return {"audit_file": GENERATED_AUDIT, "current_refs": QFT_REFS, "qm_routes": QM_ROUTES, "route_control_rows": route_control_rows, "wrapper_rows": wrapper_rows, "lorentz_cpt_sme_refs": LORENTZ_CPT_SME_REFS, "lorentz_cpt_sme_route_control_rows": lorentz_route_control_rows, "lorentz_cpt_sme_wrapper_rows": lorentz_wrapper_rows, "ledger_summaries": ledger_summaries, "checks": checks, "failures": failures}

def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"

def write_qm_qft_observed_sector_audit(root: Path) -> None:
    result = evaluate_qm_qft_observed_sector(root)
    lines = [
        "# QM/QFT observed-sector source-role audit (generated)",
        "",
        "Generated from observed-sector, route-control, evidence-unit, forecast, empirical-delta, decision, and route-state ledgers. Do not edit directly; run `make index` after changing QM/QFT/gauge observed-sector pressure.",
        "",
        f"- Current QM/QFT denominator refs: {refs_text(result['current_refs'])}",
        f"- Lorentz/CPT/SME denominator refs: {refs_text(result['lorentz_cpt_sme_refs'])}",
        f"- QM/QFT routes checked: `{len(result['qm_routes'])}`",
        f"- QM/QFT route-control rows checked: `{result['route_control_rows']}`",
        f"- Metadata wrapper rows checked: `{result['wrapper_rows']}`",
        f"- Lorentz/CPT/SME route-control rows checked: `{result['lorentz_cpt_sme_route_control_rows']}`",
        f"- Lorentz/CPT/SME wrapper rows checked: `{result['lorentz_cpt_sme_wrapper_rows']}`",
        f"- QM/QFT observed-sector checks: `{len(result['checks'])}`",
        f"- QM/QFT observed-sector failures: `{len(result['failures'])}`",
        "",
        "## Ledger summary",
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
    lines += ["", "## Non-promotion rule", "", "Constants, precision lepton magnetic-moment refs, and Lorentz/CPT/SME refs are denominator/burden refs. They can force replay, caps, or rollback of ordinary QM/QFT/gauge, symmetry, locality, frame, antimatter, or dispersion wording; they do not supply acquired candidate-native evidence, promote any route, or close observed-sector recovery.", ""]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_qm_qft_observed_sector_audit(root)
    outcome = evaluate_qm_qft_observed_sector(root)
    if outcome["failures"]:
        print("QM/QFT OBSERVED SECTOR FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("QM/QFT OBSERVED SECTOR OK")
