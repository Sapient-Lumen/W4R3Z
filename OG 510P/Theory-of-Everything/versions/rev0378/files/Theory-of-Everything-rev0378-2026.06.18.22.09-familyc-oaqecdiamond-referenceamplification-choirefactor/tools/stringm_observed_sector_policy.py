#!/usr/bin/env python3
"""Route-local String/M observed-sector atlas source-role checks.

The String/M route is scientifically valuable but high-risk for overcredit: a
large atlas, an isolated vacuum, or a DESI/de Sitter swampland narrative can be
mistaken for observed-sector identity.  This audit keeps current 2025-2026
String/M sources as S2 denominator pressure only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/stringm-observed-sector-atlas-audit.generated.md"
ROUTE_ID = "R-OQ0057-STRINGM-ATLAS"
FORECAST_ID = "DF-0017-STRINGM-FLUX-ATLAS-OBSERVED-SECTOR-QUOTIENT"
LEGACY_FORECAST_ID = "DF-0006-STRING-OBSERVED-SECTOR-INVERSE"
DELTA_ID = "ED-0022-STRINGM-ATLAS-MODULI-MEASURE-COSMOLOGY-PRESSURE"
DECISION_ID = "DX-0008-STRINGM-OBSERVED-SECTOR-INVERSE-ATLAS"
EVIDENCE_ID = "EU-0004-STRINGM-ATLAS-DUALITY-VACUUM"
CURRENT_REFS = ["REF-0673", "REF-0674", "REF-0675", "REF-0676"]
CONDITION_REQUIREMENTS: dict[tuple[str, str, str, str], list[str]] = {
    ("COMPACTIFICATION-GEOMETRY-LEDGER.json", "compactification_geometry_rows", "compactification_geometry_id", "CPG-0004-STRINGM-ATLAS"): ["REF-0673", "REF-0674", "REF-0676"],
    ("MODULI-STABILIZATION-LEDGER.json", "moduli_stabilization_rows", "moduli_stabilization_id", "MDS-0004-STRINGM-ATLAS"): ["REF-0501", "REF-0673", "REF-0674", "REF-0676"],
    ("SWAMPLAND-COMPATIBILITY-LEDGER.json", "swampland_compatibility_rows", "swampland_compatibility_id", "SWC-0004-STRINGM-ATLAS"): ["REF-0502", "REF-0503", "REF-0504", "REF-0674", "REF-0675", "REF-0676"],
    ("VACUUM-ENERGY-LEDGER.json", "vacuum_energy_rows", "vacuum_energy_id", "VED-0004-STRINGM-ATLAS"): ["REF-0499", "REF-0502", "REF-0675"],
    ("COSMOLOGICAL-BACKGROUND-LEDGER.json", "background_rows", "cosmological_background_id", "CBG-0004-STRINGM-ATLAS"): ["REF-0502", "REF-0675"],
    ("MEASURE-DEFINITION-LEDGER.json", "measure_rows", "measure_definition_id", "MEA-0004-STRINGM-ATLAS"): ["REF-0673", "REF-0675"],
    ("TYPICALITY-WEIGHTING-LEDGER.json", "typicality_rows", "typicality_weighting_id", "TYP-0004-STRINGM-ATLAS"): ["REF-0673", "REF-0675"],
    ("SECTOR-SELECTION-LEDGER.json", "sector_rows", "sector_selection_id", "SEC-0004-STRINGM-ATLAS"): ["REF-0673", "REF-0674", "REF-0676"],
    ("PARTICLE-SPECTRUM-LEDGER.json", "particle_spectrum_rows", "particle_spectrum_id", "PSP-0004-STRINGM-ATLAS"): ["REF-0673", "REF-0674", "REF-0676"],
    ("SELECTION-FUNCTION-LEDGER.json", "selection_rows", "selection_function_id", "SF-0004-STRINGM-ATLAS"): ["REF-0673", "REF-0675"],
    ("MULTIPLICITY-CONTROL-LEDGER.json", "multiplicity_rows", "multiplicity_control_id", "MC-0004-STRINGM-ATLAS"): ["REF-0673"],
    ("REPORTING-BIAS-LEDGER.json", "bias_rows", "reporting_bias_id", "RBIA-0004-STRINGM-ATLAS"): ["REF-0673", "REF-0674"],
    ("COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json", "reproducibility_rows", "computational_reproducibility_id", "CRP-0004-STRINGM-ATLAS"): ["REF-0673"],
    ("NUMERICAL-STABILITY-LEDGER.json", "stability_rows", "numerical_stability_id", "NST-0004-STRINGM-ATLAS"): ["REF-0673"],
    ("PROOF-OBLIGATION-LEDGER.json", "proof_obligation_rows", "proof_obligation_id", "POB-0004-STRINGM-ATLAS"): ["REF-0674", "REF-0676"],
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((row for row in rows if isinstance(row, dict) and row.get(key) == value), None)


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def combined_text(row: dict[str, Any], keys: list[str]) -> str:
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


def evaluate_stringm_observed_sector(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    routes = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    forecasts = load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", [])
    deltas = load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", [])
    decisions = load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", [])
    evidence_rows = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])

    route = find_row(routes, "route_id", ROUTE_ID)
    forecast = find_row(forecasts, "forecast_id", FORECAST_ID)
    legacy_forecast = find_row(forecasts, "forecast_id", LEGACY_FORECAST_ID)
    delta = find_row(deltas, "delta_id", DELTA_ID)
    decision = find_row(decisions, "experiment_id", DECISION_ID)
    evidence = find_row(evidence_rows, "evidence_unit_id", EVIDENCE_ID)

    def add(label: str, passed: bool, detail: str) -> None:
        checks.append({"check": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    add("route-present", route is not None, f"route `{ROUTE_ID}` must exist")
    if route:
        add("route-authority-capped", route.get("authority_state") == "S2", f"authority_state is `{route.get('authority_state')}`; expected S2")
        add("route-promotion-capped", route.get("promotion_ceiling") == "S2", f"promotion ceiling is `{route.get('promotion_ceiling')}`; expected S2")
        text = combined_text(route, ["record_process", "inverse_deficiency", "stability_margin", "residual_cap", "earliest_blocker"])
        missing = [term for term in ["quotient", "moduli", "measure", "spectrum", "cosmology", "de sitter", "failed", "s2"] if term not in text]
        add("route-denominator-language", not missing, f"route text missing {missing}")
        add("route-hooks-forecast", FORECAST_ID in route.get("forecast_ids", []), f"forecast_ids {route.get('forecast_ids', [])}")
        add("route-hooks-delta", DELTA_ID in route.get("empirical_delta_ids", []), f"empirical_delta_ids {route.get('empirical_delta_ids', [])}")

    add("forecast-present", forecast is not None, f"forecast `{FORECAST_ID}` must exist")
    if forecast:
        add("forecast-route-local", forecast.get("route_id") == ROUTE_ID, f"forecast route is `{forecast.get('route_id')}`")
        add("forecast-credit-capped", forecast.get("current_maximum_credit") == "S2", f"forecast current maximum is `{forecast.get('current_maximum_credit')}`")
        missing = [ref for ref in CURRENT_REFS if ref not in forecast.get("source_refs", [])]
        add("forecast-current-refs", not missing, f"missing refs {missing}; present {forecast.get('source_refs', [])}")
        text = combined_text(forecast, ["required_public_record", "negative_result_credit", "non_promotion_warning"])
        missing_terms = [term for term in ["flux", "quotient", "moduli", "measure", "spectrum", "de sitter", "failed", "not"] if term not in text]
        add("forecast-public-denominators", not missing_terms, f"forecast text missing {missing_terms}")

    add("legacy-forecast-present", legacy_forecast is not None, f"forecast `{LEGACY_FORECAST_ID}` must exist")
    if legacy_forecast:
        missing = [ref for ref in CURRENT_REFS if ref not in legacy_forecast.get("source_refs", [])]
        add("legacy-forecast-current-refs", not missing, f"missing refs {missing}; present {legacy_forecast.get('source_refs', [])}")
        add("legacy-forecast-credit-capped", legacy_forecast.get("current_maximum_credit") == "S2", f"current max is `{legacy_forecast.get('current_maximum_credit')}`")

    add("delta-present", delta is not None, f"delta `{DELTA_ID}` must exist")
    if delta:
        add("delta-route-local", delta.get("route_ids") == [ROUTE_ID], f"delta route_ids {delta.get('route_ids')}")
        add("delta-ceiling-capped", delta.get("promotion_ceiling") == "S2", f"delta ceiling is `{delta.get('promotion_ceiling')}`")
        missing = [ref for ref in CURRENT_REFS if ref not in delta.get("source_refs", [])]
        add("delta-current-refs", not missing, f"missing refs {missing}; present {delta.get('source_refs', [])}")
        text = combined_text(delta, ["record_delta", "candidate_native_effect", "state_effect", "residual_cap"])
        missing_terms = [term for term in ["flux", "moduli", "measure", "spectrum", "cosmolog", "swampland", "s2", "blocks"] if term not in text]
        add("delta-denominator-language", not missing_terms, f"delta text missing {missing_terms}")

    add("decision-present", decision is not None, f"decision `{DECISION_ID}` must exist")
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"decision routes {decision.get('route_ids')}")
        missing = [ref for ref in CURRENT_REFS if ref not in decision.get("source_refs", [])]
        add("decision-current-refs", not missing, f"missing refs {missing}; present {decision.get('source_refs', [])}")
        add("decision-hooks-delta", DELTA_ID in decision.get("empirical_delta_hooks", []), f"hooks {decision.get('empirical_delta_hooks', [])}")
        text = combined_text(decision, ["public_record", "minimum_public_artifact", "non_promotion_clause", "outcome_effects"])
        missing_terms = [term for term in ["flux", "quotient", "moduli", "measure", "cosmology", "failed", "s2"] if term not in text]
        add("decision-public-artifact-denominators", not missing_terms, f"decision text missing {missing_terms}")

    add("evidence-present", evidence is not None, f"evidence `{EVIDENCE_ID}` must exist")
    if evidence:
        fresh_on_evidence = [ref for ref in CURRENT_REFS if ref in evidence.get("source_refs", [])]
        add("fresh-refs-not-acquired-evidence", not fresh_on_evidence, f"fresh refs incorrectly on evidence unit: {fresh_on_evidence}")
        add("evidence-credit-capped", evidence.get("maximum_credit") == "S2", f"maximum credit is `{evidence.get('maximum_credit')}`")
        add("evidence-delta-handoff", DELTA_ID in evidence.get("empirical_delta_ids", []), f"empirical_delta_ids {evidence.get('empirical_delta_ids', [])}")

    for (rel, collection, key, row_id), refs in CONDITION_REQUIREMENTS.items():
        row = find_row(load_json(root, rel).get(collection, []), key, row_id)
        add(f"condition-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row is not None:
            missing = [ref for ref in refs if ref not in row.get("source_refs", [])]
            add(f"condition-refs-{row_id}", not missing, f"missing refs {missing}; present {row.get('source_refs', [])}")
            add(f"condition-ceiling-{row_id}", row.get("maximum_authority_effect") == "S2", f"maximum authority effect `{row.get('maximum_authority_effect')}`")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": ROUTE_ID,
        "current_refs": CURRENT_REFS,
        "checks": checks,
        "failures": failures,
    }


def write_stringm_observed_sector_audit(root: Path) -> None:
    result = evaluate_stringm_observed_sector(root)
    lines = [
        "# String/M observed-sector atlas source-role audit (generated)",
        "",
        "Generated from the String/M route, forecast, empirical-delta, decision, evidence-unit, and route-control rows. Do not edit directly; run `make index` after changing String/M observed-sector custody.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Current pressure refs: {refs_text(result['current_refs'])}",
        f"- String/M observed-sector checks: `{len(result['checks'])}`",
        f"- String/M observed-sector failures: `{len(result['failures'])}`",
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
        "Current String/M flux-vacuum, Landau-Ginzburg/Minkowski stabilization, and DESI/de Sitter swampland sources can tighten only route-local quotient, moduli, measure, spectrum, vacuum-energy, and cosmology denominators. The fresh refs must not become acquired evidence-unit support and cannot promote the String/M route beyond S2.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_stringm_observed_sector_audit(root)
    outcome = evaluate_stringm_observed_sector(root)
    if outcome["failures"]:
        print("STRINGM OBSERVED-SECTOR POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("STRINGM OBSERVED-SECTOR POLICY OK")
