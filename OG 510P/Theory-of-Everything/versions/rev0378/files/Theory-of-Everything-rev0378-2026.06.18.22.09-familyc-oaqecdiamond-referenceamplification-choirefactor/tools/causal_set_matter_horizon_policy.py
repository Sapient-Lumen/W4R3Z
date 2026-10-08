#!/usr/bin/env python3
"""Check causal-set matter-correlator, continuum, and horizon/entropy pressure.

The causal-set lane can use QSG, continuum-emergence, interacting-QFT
correlator/scattering, fuzzy-horizon, and horizon-molecule papers as route-local
pressure.  These sources must not become acquired evidence-unit source credit or
black-hole/continuum/matter-sector closure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/causal-set-matter-horizon-source-role-audit.generated.md"
ROUTE_ID = "R-OQ0057-CAUSAL-SET"
EVIDENCE_ID = "EU-0006-CAUSAL-SET-DYNAMICS"
FORECAST_IDS = [
    "DF-0008-CAUSAL-SET-MATTER-DYNAMICS",
    "DF-0018-CAUSAL-SET-CORRELATOR-HORIZON-ENTROPY-REPLAY",
]
DELTA_IDS = [
    "ED-0014-CAUSAL-SET-QSG-DYNAMICS-PRESSURE",
    "ED-0024-CAUSAL-SET-MATTER-CORRELATOR-HORIZON-ENTROPY-PRESSURE",
]
DECISION_ID = "DX-0010-CAUSAL-SET-MATTER-CONTINUUM-RECOVERY"
FRESH_CAUSAL_SET_REFS = ["REF-0169", "REF-0668", "REF-0669", "REF-0681", "REF-0682"]
MATTER_REFS = ["REF-0681"]
HORIZON_ENTROPY_REFS = ["REF-0669", "REF-0682"]
CONTINUUM_REFS = ["REF-0668"]

CONTROL_ROWS: list[tuple[str, str, str, str, list[str]]] = [
    ("ACQUISITION-PROTOCOL-LEDGER.json", "protocol_rows", "protocol_id", "AP-CAUSAL-SET-SIMULATION-REPLAY", FRESH_CAUSAL_SET_REFS),
    ("EVIDENCE-SEVERITY-LEDGER.json", "severity_rows", "severity_id", "SV-0009-CAUSAL-SET-DYNAMICS-SEVERITY", FRESH_CAUSAL_SET_REFS),
    ("CONTINUUM-EXTRAPOLATION-LEDGER.json", "continuum_extrapolation_rows", "continuum_extrapolation_id", "CEX-0006-CAUSAL-SET", ["REF-0668", "REF-0669"]),
    ("CORRELATION-FUNCTION-LEDGER.json", "correlation_function_rows", "correlation_function_id", "CFN-0006-CAUSAL-SET", ["REF-0681"]),
    ("HORIZON-STRUCTURE-LEDGER.json", "horizon_rows", "horizon_structure_id", "HZN-0006-CAUSAL-SET", ["REF-0669"]),
    ("BLACK-HOLE-THERMODYNAMICS-LEDGER.json", "thermodynamics_rows", "black_hole_thermodynamics_id", "BHT-0006-CAUSAL-SET", ["REF-0682"]),
]


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(root: Path, rel: str, collection: str, id_field: str, row_id: str) -> dict[str, Any] | None:
    rows = load_json(root, rel).get(collection, [])
    if not isinstance(rows, list):
        return None
    return next((row for row in rows if isinstance(row, dict) and row.get(id_field) == row_id), None)


def missing_refs(row: dict[str, Any] | None, refs: list[str]) -> list[str]:
    present = row.get("source_refs", []) if isinstance(row, dict) else []
    return [ref for ref in refs if ref not in present]


def present_refs(row: dict[str, Any] | None, refs: list[str]) -> list[str]:
    present = row.get("source_refs", []) if isinstance(row, dict) else []
    return [ref for ref in refs if ref in present]


def text_of(row: dict[str, Any] | None, keys: list[str]) -> str:
    if not isinstance(row, dict):
        return ""
    parts: list[str] = []
    for key in keys:
        val = row.get(key, "")
        if isinstance(val, str):
            parts.append(val)
        elif isinstance(val, list):
            parts.extend(str(item) for item in val)
        elif isinstance(val, dict):
            parts.extend(str(item) for item in val.values())
    return " ".join(parts).lower()


def evaluate_causal_set_matter_horizon(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    route = find_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", ROUTE_ID)
    evidence = find_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID)
    decision = find_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID)

    add("route-present", route is not None, ROUTE_ID)
    if route:
        add("route-authority-remains-S1", route.get("authority_state") == "S1", f"authority_state={route.get('authority_state')}")
        add("route-ceiling-remains-S2", route.get("promotion_ceiling") == "S2", f"promotion_ceiling={route.get('promotion_ceiling')}")
        for fid in FORECAST_IDS:
            add(f"route-mirrors-forecast-{fid}", fid in route.get("forecast_ids", []), f"forecast_ids={route.get('forecast_ids')}")
        for did in DELTA_IDS:
            add(f"route-mirrors-delta-{did}", did in route.get("empirical_delta_ids", []), f"empirical_delta_ids={route.get('empirical_delta_ids')}")
        text = text_of(route, ["earliest_blocker", "inverse_deficiency", "abstention_or_no_verdict_rule", "source_role_events", "rev0329_causal_set_pressure_note"])
        missing_terms = [term for term in ["matter", "correlator", "horizon", "entropy", "s1", "no route promotion"] if term not in text]
        add("route-denominator-language", not missing_terms, f"missing terms={missing_terms}")

    for fid in FORECAST_IDS:
        row = find_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", fid)
        add(f"forecast-present-{fid}", row is not None, fid)
        if row:
            add(f"forecast-route-local-{fid}", row.get("route_id") == ROUTE_ID, f"route_id={row.get('route_id')}")
            miss = missing_refs(row, FRESH_CAUSAL_SET_REFS)
            add(f"forecast-current-refs-{fid}", not miss, f"missing_refs={miss}")
            add(f"forecast-credit-capped-S1-{fid}", row.get("current_maximum_credit") == "S1", f"current_maximum_credit={row.get('current_maximum_credit')}")

    for did in DELTA_IDS:
        row = find_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", did)
        add(f"delta-present-{did}", row is not None, did)
        if row:
            add(f"delta-route-local-{did}", row.get("route_ids") == [ROUTE_ID], f"route_ids={row.get('route_ids')}")
            add(f"delta-evidence-link-{did}", EVIDENCE_ID in (row.get("evidence_unit_ids") or []), f"evidence_unit_ids={row.get('evidence_unit_ids')}")
            add(f"delta-ceiling-S1-{did}", row.get("promotion_ceiling") == "S1", f"promotion_ceiling={row.get('promotion_ceiling')}")
        if did == DELTA_IDS[0] and row:
            miss = missing_refs(row, FRESH_CAUSAL_SET_REFS)
            add("qsg-delta-current-refs", not miss, f"missing_refs={miss}")
        if did == DELTA_IDS[1] and row:
            miss = missing_refs(row, ["REF-0668", "REF-0669", "REF-0681", "REF-0682"])
            add("matter-horizon-delta-current-refs", not miss, f"missing_refs={miss}")
            text = text_of(row, ["record_delta", "candidate_native_effect", "residual_cap"])
            missing_terms = [term for term in ["correlator", "scattering", "horizon", "entropy", "many-to-one"] if term not in text]
            add("matter-horizon-delta-denominator-language", not missing_terms, f"missing_terms={missing_terms}")

    add("evidence-present", evidence is not None, EVIDENCE_ID)
    if evidence:
        for did in DELTA_IDS:
            add(f"evidence-reciprocal-delta-{did}", did in (evidence.get("empirical_delta_ids") or []), f"empirical_delta_ids={evidence.get('empirical_delta_ids')}")
        forbidden = present_refs(evidence, FRESH_CAUSAL_SET_REFS)
        add("fresh-refs-not-acquired-evidence", not forbidden, f"forbidden_present={forbidden}")
        text = text_of(evidence, ["record_description", "credit_spend_rule"])
        missing_terms = [term for term in ["pressure", "not", "acquired", "matter", "horizon"] if term not in text]
        add("evidence-noncredit-language", not missing_terms, f"missing_terms={missing_terms}")

    add("decision-present", decision is not None, DECISION_ID)
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"route_ids={decision.get('route_ids')}")
        for did in DELTA_IDS:
            add(f"decision-hooks-{did}", did in (decision.get("empirical_delta_hooks") or []), f"empirical_delta_hooks={decision.get('empirical_delta_hooks')}")
        too_high = [item for item in decision.get("outcome_effects", []) if isinstance(item, dict) and item.get("promotion_ceiling") not in {None, "S0", "S1", "S2"}]
        add("decision-outcomes-capped-S2", not too_high, f"too_high={too_high}")
        miss = missing_refs(decision, FRESH_CAUSAL_SET_REFS)
        add("decision-current-refs", not miss, f"missing_refs={miss}")

    control_results: list[dict[str, Any]] = []
    for rel, collection, id_field, row_id, refs in CONTROL_ROWS:
        row = find_row(root, rel, collection, id_field, row_id)
        miss = missing_refs(row, refs)
        passed = row is not None and not miss
        control_results.append({"ledger_file": rel, "row_id": row_id, "required_refs": refs, "missing_refs": miss, "passed": passed})
        add(f"control-row-current-refs-{row_id}", passed, f"missing_refs={miss}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": ROUTE_ID,
        "evidence_id": EVIDENCE_ID,
        "forecast_ids": FORECAST_IDS,
        "delta_ids": DELTA_IDS,
        "decision_id": DECISION_ID,
        "fresh_refs": FRESH_CAUSAL_SET_REFS,
        "checks": checks,
        "control_results": control_results,
        "failures": failures,
    }


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def write_causal_set_matter_horizon_audit(root: Path) -> None:
    result = evaluate_causal_set_matter_horizon(root)
    lines = [
        "# Causal-set matter/horizon source-role audit (generated)",
        "",
        "Generated from the causal-set route, forecast, empirical-delta, decision, evidence-unit, and route-control rows. Do not edit directly; run `make index` after changing causal-set matter or horizon pressure.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Evidence unit fenced from fresh source credit: `{result['evidence_id']}`",
        f"- Forecast rows: {refs_text(result['forecast_ids'])}",
        f"- Empirical-delta rows: {refs_text(result['delta_ids'])}",
        f"- Decision row: `{result['decision_id']}`",
        f"- Fresh causal-set pressure refs: {refs_text(result['fresh_refs'])}",
        f"- Causal-set matter/horizon checks: `{len(result['checks'])}`",
        f"- Causal-set matter/horizon failures: `{len(result['failures'])}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check.get("detail", "")).replace("|", "\\|")
        lines.append(f"| `{check.get('check')}` | `{str(check.get('passed')).lower()}` | {detail} |")
    lines += ["", "## Control rows", "", "| Ledger row | Required refs | Missing refs | Passed |", "|---|---|---|---:|"]
    for item in result["control_results"]:
        required = refs_text(item["required_refs"])
        missing = refs_text(item["missing_refs"])
        lines.append(f"| `{item['ledger_file']}:{item['row_id']}` | {required} | {missing} | `{str(item['passed']).lower()}` |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in result["failures"])
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Causal-set QSG, continuum-emergence, interacting-QFT correlator/scattering, fuzzy-horizon, and horizon-molecule sources are route-local pressure. They do not become acquired evidence-unit source credit, matter-sector completion, black-hole thermodynamic closure, or route promotion.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_causal_set_matter_horizon_audit(root)
    outcome = evaluate_causal_set_matter_horizon(root)
    if outcome["failures"]:
        print("CAUSAL-SET MATTER/HORIZON POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CAUSAL-SET MATTER/HORIZON POLICY OK")
