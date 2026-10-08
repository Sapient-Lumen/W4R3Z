#!/usr/bin/env python3
"""Lab GIE/BMV source-role and realization-pressure policy.

Current GIE/BMV literature is scientifically valuable but especially easy to
overcredit: protocol-relaxation, shielding/stability, noise bounds, and
classical/nonlocal comparator papers can sound like direct evidence.  This
policy keeps those sources route-local, decision-visible, and excluded from the
acquired evidence-unit source set until a direct public two-body run exists.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/lab-gie-bmv-source-role-audit.generated.md"
ROUTE_ID = "R-OQ0057-LAB-GIE-BMV"
FORECAST_ID = "DF-0023-LAB-GIE-PROTOCOL-NOISE-CLASSICAL-SPLIT"
DELTA_ID = "ED-0029-LAB-GIE-PROTOCOL-NOISE-CLASSICAL-SPLIT-PRESSURE"
DECISION_ID = "DX-0016-LAB-GIE-PROTOCOL-NOISE-CLASSICAL-SPLIT"
DIRECT_DECISION_ID = "DX-0001-DIRECT-GIE-BMV-ENTANGLEMENT"
EVIDENCE_ID = "EU-0008-LAB-GIE-MEDIATOR"
FRESH_REFS = ["REF-0695", "REF-0696", "REF-0697", "REF-0698"]
PRESSURE_REFS = ["REF-0209"] + FRESH_REFS
OLDER_INFERENCE_REFS = ["REF-0643", "REF-0644", "REF-0645", "REF-0646"]

REQUIRED_PLACEMENTS: list[tuple[str, str, str, str, list[str]]] = [
    ("DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", FORECAST_ID, PRESSURE_REFS),
    ("EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", DELTA_ID, PRESSURE_REFS),
    ("DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID, PRESSURE_REFS),
    ("DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DIRECT_DECISION_ID, PRESSURE_REFS),
    ("PUBLIC-RECORD-CARRIER-LEDGER.json", "carrier_rows", "carrier_id", "PRC-GIE-LAB-CUSTODY", PRESSURE_REFS),
    ("ACQUISITION-PROTOCOL-LEDGER.json", "protocol_rows", "protocol_id", "AP-GIE-LAB-CUSTODY-CHAIN", PRESSURE_REFS),
    ("MEASUREMENT-MODEL-LEDGER.json", "measurement_model_rows", "measurement_model_id", "MM-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("SYSTEMATIC-UNCERTAINTY-LEDGER.json", "systematic_rows", "systematic_id", "SYS-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("CALIBRATION-TRACEABILITY-LEDGER.json", "calibration_rows", "calibration_id", "CAL-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("DETECTOR-RESPONSE-LEDGER.json", "detector_response_rows", "detector_response_id", "DRESP-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("DECOHERENCE-POINTER-LEDGER.json", "decoherence_pointer_rows", "decoherence_pointer_id", "DECOH-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("STATE-PREPARATION-LEDGER.json", "state_preparation_rows", "state_preparation_id", "SPREP-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("INTERVENTION-PROTOCOL-LEDGER.json", "intervention_rows", "intervention_id", "IV-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("COUNTERFACTUAL-ROBUSTNESS-LEDGER.json", "counterfactual_rows", "counterfactual_id", "CF-0008-LAB-GIE-BMV", PRESSURE_REFS),
    ("EVIDENCE-SEVERITY-LEDGER.json", "severity_rows", "severity_id", "SV-0003-DIRECT-GIE-BMV-SEVERITY", PRESSURE_REFS),
]


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(root: Path, rel: str, collection: str, id_field: str, row_id: str) -> dict[str, Any] | None:
    rows = load_json(root, rel).get(collection, [])
    return next((row for row in rows if isinstance(row, dict) and row.get(id_field) == row_id), None)


def missing_refs(row: dict[str, Any] | None, refs: list[str]) -> list[str]:
    if not row:
        return refs[:]
    present = row.get("source_refs", [])
    return [ref for ref in refs if ref not in present]


def combined_text(row: dict[str, Any] | None, keys: list[str]) -> str:
    if not row:
        return ""
    parts: list[str] = []
    for key in keys:
        value = row.get(key, "")
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parts.extend(str(v) for v in item.values())
                else:
                    parts.append(str(item))
        elif isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
    return " ".join(parts).lower()


def evaluate_lab_gie_bmv_source_role(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    def add(label: str, passed: bool, detail: str) -> None:
        checks.append({"check": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    route = find_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", ROUTE_ID)
    forecast = find_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", FORECAST_ID)
    delta = find_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", DELTA_ID)
    decision = find_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID)
    direct_decision = find_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DIRECT_DECISION_ID)
    evidence = find_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID)

    add("route-present", route is not None, ROUTE_ID)
    if route:
        add("route-current-S2", route.get("authority_state") == "S2", f"authority_state={route.get('authority_state')}")
        add("route-ceiling-S3", route.get("promotion_ceiling") == "S3", f"promotion_ceiling={route.get('promotion_ceiling')}")
        add("route-mirrors-forecast", FORECAST_ID in route.get("forecast_ids", []), str(route.get("forecast_ids", [])))
        add("route-mirrors-delta", DELTA_ID in route.get("empirical_delta_ids", []), str(route.get("empirical_delta_ids", [])))
        add("route-mirrors-decision", DECISION_ID in route.get("decision_experiment_ids", []), str(route.get("decision_experiment_ids", [])))
        text = combined_text(route, ["stability_margin", "earliest_blocker", "residual_cap", "source_role_events", "rev0335_lab_gie_source_role_note"])
        for token in ["direct", "shield", "thermal", "classical", "conditional s3"]:
            add(f"route-names-{token}-denominator", token in text, text[:240])

    add("forecast-present", forecast is not None, FORECAST_ID)
    if forecast:
        add("forecast-route-local", forecast.get("route_id") == ROUTE_ID, f"route_id={forecast.get('route_id')}")
        add("forecast-current-credit-S2", forecast.get("current_maximum_credit") == "S2", f"current_maximum_credit={forecast.get('current_maximum_credit')}")
        add("forecast-carries-new-refs", not missing_refs(forecast, PRESSURE_REFS), f"missing={missing_refs(forecast, PRESSURE_REFS)}")
        text = combined_text(forecast, ["required_public_record", "positive_result_credit", "non_promotion_warning"])
        for token in ["constrained", "shield", "thermal", "classical", "not a direct"]:
            add(f"forecast-names-{token}", token in text, text[:240])

    add("delta-present", delta is not None, DELTA_ID)
    if delta:
        add("delta-route-local", delta.get("route_ids") == [ROUTE_ID], f"route_ids={delta.get('route_ids')}")
        add("delta-ceiling-S3", delta.get("promotion_ceiling") == "S3", f"promotion_ceiling={delta.get('promotion_ceiling')}")
        add("delta-carries-new-refs", not missing_refs(delta, PRESSURE_REFS), f"missing={missing_refs(delta, PRESSURE_REFS)}")
        add("delta-hooks-evidence-unit", EVIDENCE_ID in delta.get("evidence_unit_ids", []), str(delta.get("evidence_unit_ids", [])))
        text = combined_text(delta, ["record_delta", "state_effect", "residual_cap"])
        for token in ["no direct", "thermal", "classical", "excluded"]:
            add(f"delta-names-{token}", token in text, text[:240])

    add("decision-present", decision is not None, DECISION_ID)
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"route_ids={decision.get('route_ids')}")
        add("decision-hooks-delta", DELTA_ID in decision.get("empirical_delta_hooks", []), str(decision.get("empirical_delta_hooks", [])))
        add("decision-carries-new-refs", not missing_refs(decision, PRESSURE_REFS), f"missing={missing_refs(decision, PRESSURE_REFS)}")
        ceilings = [item.get("promotion_ceiling") for item in decision.get("outcome_effects", []) if isinstance(item, dict)]
        add("decision-ceilings-within-route-pocket", all(c in {"S0", "S1", "S2", "S3"} for c in ceilings), f"ceilings={ceilings}")
        add("decision-has-protocol-only-S2-outcome", any(item.get("outcome_class") == "protocol-only-pass" and item.get("promotion_ceiling") == "S2" for item in decision.get("outcome_effects", []) if isinstance(item, dict)), "protocol-only outcome must stay S2")

    add("direct-decision-present", direct_decision is not None, DIRECT_DECISION_ID)
    if direct_decision:
        add("direct-decision-hooks-new-delta", DELTA_ID in direct_decision.get("empirical_delta_hooks", []), str(direct_decision.get("empirical_delta_hooks", [])))
        add("direct-decision-carries-new-refs", not missing_refs(direct_decision, PRESSURE_REFS), f"missing={missing_refs(direct_decision, PRESSURE_REFS)}")

    add("evidence-unit-present", evidence is not None, EVIDENCE_ID)
    if evidence:
        add("evidence-unit-reciprocal-delta", DELTA_ID in evidence.get("empirical_delta_ids", []), str(evidence.get("empirical_delta_ids", [])))
        leaked = [ref for ref in FRESH_REFS if ref in evidence.get("source_refs", [])]
        add("new-refs-absent-from-evidence-unit", not leaked, f"leaked_refs={leaked}")
        add("evidence-unit-remains-S2", evidence.get("maximum_credit") == "S2", f"maximum_credit={evidence.get('maximum_credit')}")

    for rel, collection, id_field, row_id, refs in REQUIRED_PLACEMENTS:
        row = find_row(root, rel, collection, id_field, row_id)
        add(f"placement-row-present-{row_id}", row is not None, rel)
        if row:
            add(f"placement-refs-{row_id}", not missing_refs(row, refs), f"missing={missing_refs(row, refs)}")
            routes = []
            if isinstance(row.get("route_id"), str):
                routes.append(row["route_id"])
            routes.extend(rid for rid in row.get("route_ids", []) if isinstance(rid, str))
            if routes:
                add(f"placement-route-local-{row_id}", all(rid == ROUTE_ID for rid in routes), f"routes={routes}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": ROUTE_ID,
        "new_refs": FRESH_REFS,
        "pressure_refs": PRESSURE_REFS,
        "older_inference_refs": OLDER_INFERENCE_REFS,
        "checks": checks,
        "failures": failures,
        "placements_checked": len(REQUIRED_PLACEMENTS),
    }


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def write_lab_gie_bmv_source_role_audit(root: Path) -> None:
    result = evaluate_lab_gie_bmv_source_role(root)
    lines = [
        "# Lab GIE/BMV protocol-noise-classical source-role audit (generated)",
        "",
        "Generated from the lab GIE/BMV route, forecast, empirical-delta, decision, evidence-unit, carrier, protocol, and control ledgers. Do not edit directly; run `make index` after changing GIE/BMV source roles.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Fresh protocol/noise/classical-split refs excluded from evidence unit: {refs_text(result['new_refs'])}",
        f"- Pressure refs required on route-facing rows: {refs_text(result['pressure_refs'])}",
        f"- Older inference-split refs retained for context: {refs_text(result['older_inference_refs'])}",
        f"- Placement rows checked: `{result['placements_checked']}`",
        f"- Lab GIE/BMV source-role checks: `{len(result['checks'])}`",
        f"- Lab GIE/BMV source-role failures: `{len(result['failures'])}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        if len(detail) > 360:
            detail = detail[:357] + "..."
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` | {detail} |")
    lines += ["", "## Failure details", ""]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Constrained-dynamics feasibility, shielded-setup stability, thermal-noise bounds, and classical/nonlocal comparator debates are route-local pressure. They are excluded from acquired evidence-unit source refs and cannot move the lab GIE/BMV route above current S2 unless a future direct public record activates the route's already stated conditional S3 pocket.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_lab_gie_bmv_source_role_audit(root)
    outcome = evaluate_lab_gie_bmv_source_role(root)
    if outcome["failures"]:
        print("LAB GIE/BMV SOURCE-ROLE POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("LAB GIE/BMV SOURCE-ROLE POLICY OK")
