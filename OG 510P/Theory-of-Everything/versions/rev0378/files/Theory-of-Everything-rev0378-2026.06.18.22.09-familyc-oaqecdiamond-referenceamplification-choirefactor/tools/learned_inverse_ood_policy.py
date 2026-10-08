#!/usr/bin/env python3
"""Route-local OOD / simulator-inheritance checks for the learned-inverse lane.

Learning an inverse map can be useful benchmark pressure without being evidence
for bulk ontology.  The risky failure mode is spending finite-window, simulator-
conditioned, architecture-dependent reconstruction successes as if they were
route promotion.  This audit keeps current learned-inverse papers as route-local
S2 pressure and requires public OOD, abstention, cutoff/window, baseline, and
uncertainty/coverage denominators.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/learned-inverse-ood-audit.generated.md"
ROUTE_ID = "R-OQ0057-FAMILYC-LEARNED-INVERSE"
FORECAST_ID = "DF-0012-FAMILYC-LEARNED-INVERSE-OOD-PUBLIC-HOLDOUT"
DELTA_ID = "ED-0012-FAMILYC-LEARNED-INVERSE-OOD-CUTOFF-PRESSURE"
DECISION_ID = "DX-0014-FAMILYC-LEARNED-INVERSE-OOD-ABSTENTION"
EVIDENCE_ID = "EU-0002-FAMILYC-LEARNED-INVERSE-BENCHMARK"
REQUIRED_REFS = ["REF-0131", "REF-0143", "REF-0670", "REF-0671", "REF-0672"]
CONDITION_REF_REQUIREMENTS: dict[tuple[str, str, str, str], list[str]] = {
    ("PREDICTIVE-GENERALIZATION-LEDGER.json", "generalization_rows", "generalization_id", "GEN-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0670", "REF-0671", "REF-0672"],
    ("SURROGATE-EMULATOR-LEDGER.json", "surrogate_emulator_rows", "surrogate_emulator_id", "SUR-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0131", "REF-0143", "REF-0670", "REF-0671"],
    ("SIM-TO-REAL-TRANSFER-LEDGER.json", "sim_to_real_transfer_rows", "sim_to_real_transfer_id", "SRT-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0131", "REF-0143", "REF-0672"],
    ("EVALUATION-PROTOCOL-LEDGER.json", "evaluation_protocol_rows", "evaluation_protocol_id", "EVP-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0670", "REF-0671", "REF-0672"],
    ("BENCHMARK-SUITE-LEDGER.json", "benchmark_suite_rows", "benchmark_suite_id", "BMS-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0670", "REF-0671"],
    ("BENCHMARK-METRIC-LEDGER.json", "benchmark_metric_rows", "benchmark_metric_id", "BMT-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0671", "REF-0672"],
    ("UNCERTAINTY-INTERVAL-LEDGER.json", "uncertainty_interval_rows", "uncertainty_interval_id", "UIN-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0672"],
    ("COVERAGE-CALIBRATION-LEDGER.json", "coverage_calibration_rows", "coverage_calibration_id", "CCG-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0672"],
    ("NUMERICAL-STABILITY-LEDGER.json", "stability_rows", "numerical_stability_id", "NST-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0670", "REF-0671"],
    ("MODEL-CAPACITY-LEDGER.json", "capacity_rows", "model_capacity_id", "CAP-0002-FAMILYC-LEARNED-INVERSE"): ["REF-0670", "REF-0671"],
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((row for row in rows if isinstance(row, dict) and row.get(key) == value), None)


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def _combined_text(row: dict[str, Any], keys: list[str]) -> str:
    parts: list[str] = []
    for key in keys:
        value = row.get(key, "")
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
    return " ".join(parts).lower()


def evaluate_learned_inverse_ood(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    route_ledger = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json")
    forecast_ledger = load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json")
    delta_ledger = load_json(root, "EMPIRICAL-DELTA-LEDGER.json")
    decision_ledger = load_json(root, "DECISION-EXPERIMENT-LEDGER.json")
    evidence_ledger = load_json(root, "EVIDENCE-UNIT-LEDGER.json")

    route = find_row(route_ledger.get("route_rows", []), "route_id", ROUTE_ID)
    forecast = find_row(forecast_ledger.get("forecast_rows", []), "forecast_id", FORECAST_ID)
    delta = find_row(delta_ledger.get("empirical_deltas", []), "delta_id", DELTA_ID)
    decision = find_row(decision_ledger.get("decision_experiments", []), "experiment_id", DECISION_ID)
    evidence = find_row(evidence_ledger.get("evidence_units", []), "evidence_unit_id", EVIDENCE_ID)

    def add(label: str, passed: bool, detail: str) -> None:
        checks.append({"check": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    add("route-present", route is not None, f"route `{ROUTE_ID}` must exist")
    if route:
        add("route-current-state-capped", route.get("authority_state") == "S2", f"current authority is `{route.get('authority_state')}`; expected `S2`")
        add("route-promotion-ceiling-capped", route.get("promotion_ceiling") == "S2", f"promotion ceiling is `{route.get('promotion_ceiling')}`; expected `S2`")
        combined = _combined_text(route, ["record_process", "inverse_deficiency", "stability_margin", "residual_cap", "abstention_rule", "earliest_blocker"])
        required_terms = ["finite-frequency", "cutoff", "training", "ood", "abstention", "coverage", "simulator", "baseline", "seed"]
        missing_terms = [term for term in required_terms if term not in combined]
        add("route-names-ood-denominators", not missing_terms, f"route text missing terms {missing_terms}")

    add("forecast-present", forecast is not None, f"forecast `{FORECAST_ID}` must exist")
    if forecast:
        add("forecast-route-local", forecast.get("route_id") == ROUTE_ID, f"forecast route is `{forecast.get('route_id')}`")
        add("forecast-credit-capped", forecast.get("current_maximum_credit") == "S2", f"forecast current maximum is `{forecast.get('current_maximum_credit')}`; expected `S2`")
        missing = [ref for ref in REQUIRED_REFS if ref not in forecast.get("source_refs", [])]
        add("forecast-current-refs", not missing, f"missing refs {missing}; present {forecast.get('source_refs', [])}")
        record = _combined_text(forecast, ["forecast_artifact", "required_public_record", "minimum_public_artifact", "non_promotion_warning"])
        required_terms = ["finite", "frequency", "cutoff", "held-out", "ood", "baseline", "seed", "uncertainty", "coverage", "abstention", "replay"]
        missing_terms = [term for term in required_terms if term not in record]
        add("forecast-public-denominators", not missing_terms, f"forecast text missing terms {missing_terms}")
        add("forecast-non-promotion", "not" in record and ("promotion" in record or "ontology" in record or "identity" in record), "forecast must explicitly block promotion/ontology/identity spending")

    add("delta-present", delta is not None, f"delta `{DELTA_ID}` must exist")
    if delta:
        add("delta-route-local", delta.get("route_ids") == [ROUTE_ID], f"delta route_ids are `{delta.get('route_ids')}`")
        add("delta-credit-capped", delta.get("promotion_ceiling") == "S2", f"delta promotion ceiling is `{delta.get('promotion_ceiling')}`; expected `S2`")
        missing = [ref for ref in REQUIRED_REFS if ref not in delta.get("source_refs", [])]
        add("delta-current-refs", not missing, f"missing refs {missing}; present {delta.get('source_refs', [])}")
        combined = _combined_text(delta, ["record_delta", "candidate_native_effect", "residual_cap", "notes"])
        required_terms = ["finite-frequency", "cutoff", "architecture", "training", "pinn", "multi-regime", "simulator", "baseline", "ood", "abstention", "uncertainty", "coverage"]
        missing_terms = [term for term in required_terms if term not in combined]
        add("delta-hard-denominators", not missing_terms, f"delta text missing terms {missing_terms}")

    add("decision-present", decision is not None, f"decision experiment `{DECISION_ID}` must exist")
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"decision route_ids are `{decision.get('route_ids')}`")
        missing_refs = [ref for ref in REQUIRED_REFS if ref not in decision.get("source_refs", [])]
        add("decision-current-refs", not missing_refs, f"missing refs {missing_refs}; present {decision.get('source_refs', [])}")
        add("decision-hooks-delta", DELTA_ID in decision.get("empirical_delta_hooks", []), f"decision hooks {decision.get('empirical_delta_hooks', [])}")
        record = _combined_text(decision, ["target_question", "public_record", "minimum_public_artifact", "decision_rule", "positive_outcome", "negative_outcome", "promotion_cap", "outcome_effects", "non_promotion_clause"])
        required_terms = ["finite", "frequency", "cutoff", "ood", "abstention", "baseline", "seed", "coverage", "uncertainty", "simulator"]
        missing_terms = [term for term in required_terms if term not in record]
        add("decision-public-artifact-denominators", not missing_terms, f"decision artifact missing terms {missing_terms}")
        add("decision-non-promotion", "s2" in record and ("s1" in record or "demotion" in record or "promotion" in record), "decision must bound positive and negative outcome authority")

    add("evidence-present", evidence is not None, f"evidence unit `{EVIDENCE_ID}` must exist")
    if evidence:
        present_forbidden = [ref for ref in REQUIRED_REFS if ref in evidence.get("source_refs", [])]
        add("fresh-refs-not-acquired-evidence", not present_forbidden, f"fresh refs incorrectly present on acquired evidence unit: {present_forbidden}")
        add("evidence-credit-capped", evidence.get("maximum_credit") == "S2", f"evidence maximum credit is `{evidence.get('maximum_credit')}`; expected `S2`")
        add("evidence-names-current-delta-handoff", DELTA_ID in evidence.get("empirical_delta_ids", []), f"evidence empirical_delta_ids {evidence.get('empirical_delta_ids', [])}")

    for (rel, collection, key, row_id), refs in CONDITION_REF_REQUIREMENTS.items():
        data = load_json(root, rel)
        row = find_row(data.get(collection, []), key, row_id)
        add(f"condition-row-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row is not None:
            missing = [ref for ref in refs if ref not in row.get("source_refs", [])]
            add(f"condition-row-refs-{row_id}", not missing, f"missing refs {missing}; present {row.get('source_refs', [])}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": ROUTE_ID,
        "forecast_id": FORECAST_ID,
        "delta_id": DELTA_ID,
        "decision_id": DECISION_ID,
        "evidence_id": EVIDENCE_ID,
        "required_refs": REQUIRED_REFS,
        "condition_requirements": CONDITION_REF_REQUIREMENTS,
        "checks": checks,
        "failures": failures,
    }


def write_learned_inverse_ood_audit(root: Path) -> None:
    result = evaluate_learned_inverse_ood(root)
    lines = [
        "# Learned-inverse OOD / simulator-inheritance audit (generated)",
        "",
        "Generated from the learned-inverse route, forecast, empirical-delta, decision-experiment, evidence-unit, and ML/control ledgers. Do not edit directly; run `make index` after changing learned-inverse OOD custody.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Required current refs: {refs_text(result['required_refs'])}",
        f"- Learned-inverse OOD checks: `{len(result['checks'])}`",
        f"- Learned-inverse OOD failures: `{len(result['failures'])}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` | {detail} |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Current learned-inverse / holographic-ML papers can strengthen only route-local finite-window, cutoff, OOD, baseline, uncertainty/coverage, and simulator-inheritance pressure. They may be exposed through forecast, decision, and empirical-delta handoff rows, but the fresh refs must not become acquired evidence-unit support or a route promotion beyond S2.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_learned_inverse_ood_audit(root)
    outcome = evaluate_learned_inverse_ood(root)
    if outcome["failures"]:
        print("LEARNED INVERSE OOD POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("LEARNED INVERSE OOD POLICY OK")
