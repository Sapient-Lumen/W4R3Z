#!/usr/bin/env python3
"""Route-local Lorentzian-observable checks for the asymptotic-safety lane.

Asymptotic-safety fixed-point and truncation results are valuable constraint
signals, but the risky failure mode is spending them as if they already supplied
Lorentzian public observables, scattering boundedness, black-hole sector
closure, or topology/swampland consistency.  This audit keeps the fresh AS
literature as route-local S2 pressure and out of acquired evidence credit.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/asymptotic-safety-lorentzian-observable-audit.generated.md"
ROUTE_ID = "R-OQ0057-ASYMPTOTIC-SAFETY"
FORECAST_ID = "DF-0007-AS-REGULATOR-PORTABILITY"
DELTA_ID = "ED-0013-AS-AMPLITUDE-REGULATOR-PORTABILITY-PRESSURE"
DECISION_ID = "DX-0009-AS-REGULATOR-PORTABILITY-EXTRACTION"
EVIDENCE_ID = "EU-0005-AS-RG-TRUNCATION"
REQUIRED_REFS = ["REF-0166", "REF-0658", "REF-0659", "REF-0481"]
CONDITION_REF_REQUIREMENTS = {
    ("RENORMALIZATION-FLOW-LEDGER.json", "flow_rows", "renormalization_flow_id", "RGF-0005-ASYMPTOTIC-SAFETY"): ["REF-0166", "REF-0658"],
    ("REGULARIZATION-SCHEME-LEDGER.json", "regularization_rows", "regularization_scheme_id", "REG-0005-ASYMPTOTIC-SAFETY"): ["REF-0166", "REF-0658"],
    ("SCATTERING-OBSERVABLE-LEDGER.json", "scattering_observable_rows", "scattering_observable_id", "SCAT-0005-ASYMPTOTIC-SAFETY"): ["REF-0166", "REF-0658"],
    ("ASYMPTOTIC-STATE-LEDGER.json", "asymptotic_state_rows", "asymptotic_state_id", "ASYM-0005-ASYMPTOTIC-SAFETY"): ["REF-0166"],
    ("INFRARED-DRESSING-LEDGER.json", "infrared_dressing_rows", "infrared_dressing_id", "IRD-0005-ASYMPTOTIC-SAFETY"): ["REF-0166"],
    ("UNITARITY-CHECK-LEDGER.json", "unitarity_rows", "unitarity_check_id", "UNI-0005-ASYMPTOTIC-SAFETY"): ["REF-0166", "REF-0481"],
    ("CAUSALITY-CONE-LEDGER.json", "causality_rows", "causality_cone_id", "CAU-0005-ASYMPTOTIC-SAFETY"): ["REF-0481"],
    ("STABILITY-POSITIVITY-LEDGER.json", "stability_rows", "stability_positivity_id", "STB-0005-ASYMPTOTIC-SAFETY"): ["REF-0166", "REF-0481"],
    ("HORIZON-STRUCTURE-LEDGER.json", "horizon_rows", "horizon_structure_id", "HZN-0005-ASYMPTOTIC-SAFETY"): ["REF-0659", "REF-0481"],
    ("BLACK-HOLE-THERMODYNAMICS-LEDGER.json", "thermodynamics_rows", "black_hole_thermodynamics_id", "BHT-0005-ASYMPTOTIC-SAFETY"): ["REF-0659", "REF-0481"],
    ("SPACETIME-TOPOLOGY-LEDGER.json", "topology_rows", "spacetime_topology_id", "TOP-0005-ASYMPTOTIC-SAFETY"): ["REF-0481"],
    ("LORENTZ-COVARIANCE-LEDGER.json", "lorentz_covariance_rows", "lorentz_covariance_id", "LCV-0005-ASYMPTOTIC-SAFETY"): ["REF-0166", "REF-0658"],
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((row for row in rows if isinstance(row, dict) and row.get(key) == value), None)


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def evaluate_asymptotic_safety_observable(root: Path) -> dict[str, Any]:
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

    def add_check(label: str, passed: bool, detail: str) -> None:
        checks.append({"check": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    add_check("route-present", route is not None, f"route `{ROUTE_ID}` must exist")
    if route:
        add_check("route-current-state-capped", route.get("authority_state") == "S2", f"current authority is `{route.get('authority_state')}`; expected `S2`")
        add_check("route-promotion-ceiling-capped", route.get("promotion_ceiling") == "S2", f"promotion ceiling is `{route.get('promotion_ceiling')}`; expected `S2`")
        combined = " ".join([route.get("inverse_deficiency", ""), route.get("stability_margin", ""), route.get("residual_cap", ""), route.get("earliest_blocker", "")]).lower()
        missing_terms = [term for term in ["lorentzian", "scattering", "momentum", "black-hole", "topology", "swampland"] if term not in combined]
        add_check("route-names-observable-debt", not missing_terms, f"route text missing terms {missing_terms}")

    add_check("forecast-present", forecast is not None, f"forecast `{FORECAST_ID}` must exist")
    if forecast:
        add_check("forecast-route-local", forecast.get("route_id") == ROUTE_ID, f"forecast route is `{forecast.get('route_id')}`")
        add_check("forecast-credit-capped", forecast.get("current_maximum_credit") == "S2", f"forecast current maximum is `{forecast.get('current_maximum_credit')}`; expected `S2`")
        missing = [ref for ref in REQUIRED_REFS if ref not in forecast.get("source_refs", [])]
        add_check("forecast-current-refs", not missing, f"missing refs {missing}; present {forecast.get('source_refs', [])}")
        public_record = forecast.get("required_public_record", "").lower()
        required_terms = ["lorentzian", "scattering", "momentum", "form-factor", "ir", "derivative", "glob", "black-hole", "topology", "swampland"]
        missing_terms = [term for term in required_terms if term not in public_record]
        add_check("forecast-replay-denominators", not missing_terms, f"required_public_record missing terms {missing_terms}")
        warning = forecast.get("non_promotion_warning", "").lower()
        add_check("forecast-non-promotion", ("not" in warning or "cannot" in warning) and ("identity" in warning or "closure" in warning), "forecast must explicitly block closure/identity spending")

    add_check("delta-present", delta is not None, f"delta `{DELTA_ID}` must exist")
    if delta:
        add_check("delta-route-local", delta.get("route_ids") == [ROUTE_ID], f"delta route_ids are `{delta.get('route_ids')}`")
        add_check("delta-credit-capped", delta.get("promotion_ceiling") == "S2", f"delta promotion ceiling is `{delta.get('promotion_ceiling')}`; expected `S2`")
        missing = [ref for ref in REQUIRED_REFS if ref not in delta.get("source_refs", [])]
        add_check("delta-current-refs", not missing, f"missing refs {missing}; present {delta.get('source_refs', [])}")
        combined = " ".join([delta.get("record_delta", ""), delta.get("candidate_native_effect", ""), delta.get("residual_cap", "")]).lower()
        required_terms = ["fixed-point", "lorentzian", "scattering", "momentum", "ir", "glob", "black-hole", "topology", "swampland"]
        missing_terms = [term for term in required_terms if term not in combined]
        add_check("delta-hard-denominators", not missing_terms, f"delta text missing terms {missing_terms}")

    add_check("decision-present", decision is not None, f"decision experiment `{DECISION_ID}` must exist")
    if decision:
        missing_refs = [ref for ref in REQUIRED_REFS if ref not in decision.get("source_refs", [])]
        add_check("decision-current-refs", not missing_refs, f"missing refs {missing_refs}; present {decision.get('source_refs', [])}")
        add_check("decision-hooks-delta", DELTA_ID in decision.get("empirical_delta_hooks", []), f"decision hooks {decision.get('empirical_delta_hooks', [])}")
        record = " ".join([decision.get("target_question", ""), decision.get("public_record", ""), decision.get("minimum_public_artifact", "")]).lower()
        required_terms = ["lorentzian", "scattering", "momentum", "form-factor", "ir", "derivative", "glob", "black-hole", "topology", "swampland"]
        missing_terms = [term for term in required_terms if term not in record]
        add_check("decision-public-artifact-denominators", not missing_terms, f"decision artifact missing terms {missing_terms}")

    add_check("evidence-present", evidence is not None, f"evidence unit `{EVIDENCE_ID}` must exist")
    if evidence:
        present_forbidden = [ref for ref in REQUIRED_REFS if ref in evidence.get("source_refs", [])]
        add_check("fresh-refs-not-acquired-evidence", not present_forbidden, f"fresh refs incorrectly present on acquired evidence unit: {present_forbidden}")
        add_check("evidence-credit-capped", evidence.get("maximum_credit") == "S2", f"evidence maximum credit is `{evidence.get('maximum_credit')}`; expected `S2`")
        add_check("evidence-names-current-delta-handoff", DELTA_ID in evidence.get("empirical_delta_ids", []), f"evidence empirical_delta_ids {evidence.get('empirical_delta_ids', [])}")

    for (rel, collection, key, row_id), refs in CONDITION_REF_REQUIREMENTS.items():
        data = load_json(root, rel)
        row = find_row(data.get(collection, []), key, row_id)
        add_check(f"condition-row-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row is not None:
            missing = [ref for ref in refs if ref not in row.get("source_refs", [])]
            add_check(f"condition-row-refs-{row_id}", not missing, f"missing refs {missing}; present {row.get('source_refs', [])}")

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


def write_asymptotic_safety_observable_audit(root: Path) -> None:
    result = evaluate_asymptotic_safety_observable(root)
    lines = [
        "# Asymptotic-safety Lorentzian-observable source-role audit (generated)",
        "",
        "Generated from the asymptotic-safety route, forecast, decision, empirical-delta, evidence-unit, and route-control ledgers. Do not edit directly; run `make index` after changing these rows.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Required current refs: {refs_text(result['required_refs'])}",
        f"- Lorentzian-observable checks: `{len(result['checks'])}`",
        f"- Lorentzian-observable failures: `{len(result['failures'])}`",
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
        "Current asymptotic-safety papers can strengthen only route-local Lorentzian-observable, scattering, momentum-dependence, black-hole/GLOB, and topology/swampland pressure. They may be exposed through empirical-delta handoff rows, but the fresh refs must not become acquired evidence-unit support or a route promotion beyond S2.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_asymptotic_safety_observable_audit(root)
    outcome = evaluate_asymptotic_safety_observable(root)
    if outcome["failures"]:
        print("ASYMPTOTIC SAFETY OBSERVABLE POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("ASYMPTOTIC SAFETY OBSERVABLE POLICY OK")
