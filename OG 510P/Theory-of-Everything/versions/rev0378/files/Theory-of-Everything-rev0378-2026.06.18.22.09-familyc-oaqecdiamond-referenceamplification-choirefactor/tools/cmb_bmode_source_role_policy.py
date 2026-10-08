#!/usr/bin/env python3
"""Check primordial tensor B-mode source-role pressure.

The B-mode lane has acquired SPT-3G public likelihood pressure and future
successor mission/runway pressure. This tool keeps them separated so forecasts,
mission status, and causal-source ambiguity cannot be spent as acquired tensor
evidence or Theory-of-Everything identity support.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

from source_role_event_utils import (
    duplicate_source_refs,
    find_ledger_row,
    missing_source_refs,
    present_source_refs,
    text_from_fields,
)

GENERATED_AUDIT = "docs/30-program/cmb-bmode-source-role-audit.generated.md"
ROUTE_ID = "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"
EVIDENCE_ID = "EU-0013-CMB-BMODE-PRIMORDIAL"
FORECAST_IDS = ["DF-0014-PRIMORDIAL-TENSOR-POST-CMBS4-REALIZATION", "DF-0020-PRIMORDIAL-TENSOR-SUCCESSOR-MANY-SOURCE-RUNWAY"]
DELTA_IDS = ["ED-0010-CMB-S4-PRIMORDIAL-TENSOR-FORECAST-CORRIDOR", "ED-0016-SPT3G-BMODE-BANDPOWER-LIKELIHOOD-PRESSURE", "ED-0026-CMB-BMODE-SUCCESSOR-MANY-SOURCE-PRESSURE"]
DECISION_ID = "DX-0005-CMB-PRIMORDIAL-TENSOR-BMODE"
ACQUIRED_SPT_REFS = ["REF-0640", "REF-0641", "REF-0642"]
STATUS_CLOSEOUT_REFS = ["REF-0633"]
SUCCESSOR_REFS = ["REF-0685", "REF-0686"]
AMBIGUITY_REFS = ["REF-0687"]
NEW_REFS = SUCCESSOR_REFS + AMBIGUITY_REFS

CONTROL_ROWS: list[tuple[str, str, str, str, list[str]]] = [
    ("MEASUREMENT-MODEL-LEDGER.json", "measurement_model_rows", "measurement_model_id", "MM-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
    ("SYSTEMATIC-UNCERTAINTY-LEDGER.json", "systematic_rows", "systematic_id", "SYS-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
    ("CALIBRATION-TRACEABILITY-LEDGER.json", "calibration_rows", "calibration_id", "CAL-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
    ("COSMOLOGICAL-BACKGROUND-LEDGER.json", "background_rows", "cosmological_background_id", "CBG-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
    ("THERMAL-HISTORY-LEDGER.json", "thermal_history_rows", "thermal_history_id", "THS-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
    ("GRAVITATIONAL-RADIATION-LEDGER.json", "radiation_rows", "gravitational_radiation_id", "GRR-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
    ("DATA-REDUCTION-LEDGER.json", "data_reduction_rows", "data_reduction_id", "DRC-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
    ("SUMMARY-STATISTIC-SUFFICIENCY-LEDGER.json", "summary_statistic_rows", "summary_statistic_sufficiency_id", "SSS-0013-PRIMORDIAL-TENSOR-BMODES", NEW_REFS),
]



def evaluate_cmb_bmode_source_role(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    route = find_ledger_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", ROUTE_ID)
    evidence = find_ledger_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID)
    decision = find_ledger_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID)

    add("route-present", route is not None, ROUTE_ID)
    if route:
        add("route-authority-remains-S2", route.get("authority_state") == "S2", f"authority_state={route.get('authority_state')}")
        add("route-ceiling-remains-S2", route.get("promotion_ceiling") == "S2", f"promotion_ceiling={route.get('promotion_ceiling')}")
        for fid in FORECAST_IDS:
            add(f"route-mirrors-forecast-{fid}", fid in route.get("forecast_ids", []), f"forecast_ids={route.get('forecast_ids')}")
        for did in DELTA_IDS:
            add(f"route-mirrors-delta-{did}", did in route.get("empirical_delta_ids", []), f"empirical_delta_ids={route.get('empirical_delta_ids')}")
        text = text_from_fields(route, ["residual_cap", "source_role_events", "rev0331_bmode_successor_source_role_note"])
        missing = [term for term in ["spt", "simons", "litebird", "causal-source", "not acquired", "no route"] if term not in text]
        add("route-source-role-language", not missing, f"missing_terms={missing}")

    for fid in FORECAST_IDS:
        row = find_ledger_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", fid)
        add(f"forecast-present-{fid}", row is not None, fid)
        if row:
            add(f"forecast-route-local-{fid}", row.get("route_id") == ROUTE_ID, f"route_id={row.get('route_id')}")
            add(f"forecast-credit-S2-{fid}", row.get("current_maximum_credit") == "S2", f"current_maximum_credit={row.get('current_maximum_credit')}")
            req = SUCCESSOR_REFS if fid.endswith("REALIZATION") else NEW_REFS
            miss = missing_source_refs(row, req)
            add(f"forecast-required-refs-{fid}", not miss, f"missing_refs={miss}")
            add(f"forecast-source-refs-deduped-{fid}", not duplicate_source_refs(row), f"duplicate_refs={duplicate_source_refs(row)}")
            record = text_from_fields(row, ["required_public_record", "non_promotion_warning", "positive_result_credit", "negative_result_credit"])
            missing = [term for term in ["successor", "forecast", "not", "promotion"] if term not in record]
            add(f"forecast-denominator-language-{fid}", not missing, f"missing_terms={missing}")

    for did in DELTA_IDS:
        row = find_ledger_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", did)
        add(f"delta-present-{did}", row is not None, did)
        if row:
            add(f"delta-route-local-{did}", row.get("route_ids") == [ROUTE_ID], f"route_ids={row.get('route_ids')}")
            add(f"delta-evidence-link-{did}", EVIDENCE_ID in (row.get("evidence_unit_ids") or []), f"evidence_unit_ids={row.get('evidence_unit_ids')}")
            add(f"delta-ceiling-S2-{did}", row.get("promotion_ceiling") == "S2", f"promotion_ceiling={row.get('promotion_ceiling')}")
            req = []
            if did.endswith("FORECAST-CORRIDOR"):
                req = SUCCESSOR_REFS
            elif did.endswith("LIKELIHOOD-PRESSURE"):
                req = ACQUIRED_SPT_REFS + AMBIGUITY_REFS
            else:
                req = NEW_REFS
            miss = missing_source_refs(row, req)
            add(f"delta-required-refs-{did}", not miss, f"missing_refs={miss}")
            add(f"delta-source-refs-deduped-{did}", not duplicate_source_refs(row), f"duplicate_refs={duplicate_source_refs(row)}")
            record = text_from_fields(row, ["record_delta", "candidate_native_effect", "state_effect", "residual_cap"])
            missing = [term for term in ["s2", "many", "source", "not"] if term not in record]
            add(f"delta-denominator-language-{did}", not missing, f"missing_terms={missing}")

    add("decision-present", decision is not None, DECISION_ID)
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"route_ids={decision.get('route_ids')}")
        for did in DELTA_IDS:
            add(f"decision-hooks-{did}", did in (decision.get("empirical_delta_hooks") or []), f"empirical_delta_hooks={decision.get('empirical_delta_hooks')}")
        miss = missing_source_refs(decision, ACQUIRED_SPT_REFS + NEW_REFS)
        add("decision-current-refs", not miss, f"missing_refs={miss}")
        add("decision-source-refs-deduped", not duplicate_source_refs(decision), f"duplicate_refs={duplicate_source_refs(decision)}")
        too_high = [item for item in decision.get("outcome_effects", []) if isinstance(item, dict) and item.get("promotion_ceiling") != "S2"]
        add("decision-outcomes-capped-S2", not too_high, f"too_high={too_high}")
        record = text_from_fields(decision, ["target_question", "public_record", "minimum_public_artifact", "non_promotion_clause", "outcome_effects"])
        missing = [term for term in ["successor", "causal", "foreground", "s2"] if term not in record]
        add("decision-denominator-language", not missing, f"missing_terms={missing}")

    add("evidence-present", evidence is not None, EVIDENCE_ID)
    if evidence:
        for did in DELTA_IDS:
            add(f"evidence-reciprocal-delta-{did}", did in (evidence.get("empirical_delta_ids") or []), f"empirical_delta_ids={evidence.get('empirical_delta_ids')}")
        forbidden_successor = present_source_refs(evidence, NEW_REFS)
        add("successor-refs-not-acquired-evidence", not forbidden_successor, f"forbidden_present={forbidden_successor}")
        forbidden_status = present_source_refs(evidence, STATUS_CLOSEOUT_REFS)
        add("closeout-status-refs-not-acquired-evidence", not forbidden_status, f"forbidden_present={forbidden_status}")
        status_refs = evidence.get("status_or_forecast_refs", []) if isinstance(evidence, dict) else []
        missing_status = [ref for ref in STATUS_CLOSEOUT_REFS if ref not in status_refs]
        add("closeout-status-refs-staged-outside-source-refs", not missing_status, f"missing_status_or_forecast_refs={missing_status}")
        miss = missing_source_refs(evidence, ACQUIRED_SPT_REFS)
        add("spt-refs-remain-acquired-evidence-pressure", not miss, f"missing_refs={miss}")
        add("evidence-credit-S2", evidence.get("maximum_credit") == "S2", f"maximum_credit={evidence.get('maximum_credit')}")
        record = text_from_fields(evidence, ["record_description", "credit_spend_rule"])
        missing = [term for term in ["successor", "closeout", "not", "acquired", "s2"] if term not in record]
        add("evidence-noncredit-language", not missing, f"missing_terms={missing}")

    control_results: list[dict[str, Any]] = []
    for rel, collection, id_field, row_id, refs in CONTROL_ROWS:
        row = find_ledger_row(root, rel, collection, id_field, row_id)
        miss = missing_source_refs(row, refs)
        dup = duplicate_source_refs(row)
        passed = row is not None and not miss and not dup
        control_results.append({"ledger_file": rel, "row_id": row_id, "required_refs": refs, "missing_refs": miss, "duplicate_refs": dup, "passed": passed})
        add(f"control-row-current-refs-{row_id}", row is not None and not miss, f"missing_refs={miss}")
        add(f"control-row-source-refs-deduped-{row_id}", not dup, f"duplicate_refs={dup}")

    return {"audit_file": GENERATED_AUDIT, "route_id": ROUTE_ID, "evidence_id": EVIDENCE_ID, "forecast_ids": FORECAST_IDS, "delta_ids": DELTA_IDS, "decision_id": DECISION_ID, "new_refs": NEW_REFS, "checks": checks, "control_results": control_results, "failures": failures}


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def write_cmb_bmode_source_role_audit(root: Path) -> None:
    result = evaluate_cmb_bmode_source_role(root)
    lines = [
        "# CMB B-mode source-role audit (generated)",
        "",
        "Generated from the primordial tensor B-mode route, forecast, empirical-delta, decision, evidence-unit, and control rows. Do not edit directly; run `make index` after changing B-mode pressure.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Evidence unit checked: `{result['evidence_id']}`",
        f"- New successor/ambiguity refs: {refs_text(result['new_refs'])}",
        f"- Closeout/status refs staged outside acquired evidence source refs: {refs_text(STATUS_CLOSEOUT_REFS)}",
        f"- CMB B-mode source-role checks: `{len(result['checks'])}`",
        f"- CMB B-mode source-role failures: `{len(result['failures'])}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` | {detail} |")
    lines += ["", "## Control-row source refs", "", "| Row | Required refs | Missing refs | Duplicate refs | Passed |", "|---|---|---|---|---:|"]
    for item in result["control_results"]:
        row = f"`{item['ledger_file']}:{item['row_id']}`"
        lines.append(f"| {row} | {refs_text(item['required_refs'])} | {refs_text(item['missing_refs'])} | {refs_text(item['duplicate_refs'])} | `{str(item['passed']).lower()}` |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    lines += ["", "## Non-promotion rule", "", "SPT-3G bandpowers/likelihoods are acquired S2 replay pressure; CMB-S4 closeout/status refs plus successor Simons Observatory and LiteBIRD refs plus causal-source constraints are route-local status/forecast/ambiguity pressure only. None of these rows identify inflation, quantum gravity, or a Theory-of-Everything candidate, and closeout/successor refs stay out of acquired evidence-unit `source_refs`.", ""]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_cmb_bmode_source_role_audit(root)
    outcome = evaluate_cmb_bmode_source_role(root)
    if outcome["failures"]:
        print("CMB BMODE SOURCE ROLE FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CMB BMODE SOURCE ROLE OK")
