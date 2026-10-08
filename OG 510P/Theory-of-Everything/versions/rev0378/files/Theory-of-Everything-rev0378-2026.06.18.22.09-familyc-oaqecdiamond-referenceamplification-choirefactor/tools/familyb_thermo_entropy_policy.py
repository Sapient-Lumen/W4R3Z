#!/usr/bin/env python3
"""Check FamilyB thermodynamic/entropic source-role pressure.

FamilyB can use relative-entropy, semiclassical spacetime-thermodynamics,
non-Riemannian, non-extensive horizon-entropy, and nonequilibrium
entropy-production papers as route-local denominators. They must not become
acquired evidence-unit source credit, black-hole microstate closure, or route
promotion.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/familyb-thermo-entropy-source-role-audit.generated.md"
ROUTE_ID = "R-OQ0057-FAMILYB-THERMO-ENTROPIC"
EVIDENCE_ID = "EU-0003-FAMILYB-THERMO-PROOF"
FORECAST_IDS = [
    "DF-0009-FAMILYB-THERMO-ENTROPIC-LOCAL-LAW-RECOVERY",
    "DF-0019-FAMILYB-NONEQUILIBRIUM-HORIZON-ENTROPY-CALIBRATION",
]
DELTA_IDS = [
    "ED-0015-FAMILYB-THERMO-LOCAL-LAW-SCOPE-PRESSURE",
    "ED-0025-FAMILYB-NONEQUILIBRIUM-ENTROPY-CALIBRATION-PRESSURE",
]
DECISION_ID = "DX-0007-FAMILYB-LOCAL-LAW-RECOVERY-STRESS-TEST"
FRESH_FAMILYB_REFS = ["REF-0163", "REF-0666", "REF-0667", "REF-0683", "REF-0684"]
NEW_FAMILYB_REFS = ["REF-0683", "REF-0684"]

CONTROL_ROWS: list[tuple[str, str, str, str, list[str]]] = [
    ("RELATIVE-ENTROPY-RECOVERY-LEDGER.json", "relative_entropy_recovery_rows", "relative_entropy_recovery_id", "RER-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0163"]),
    ("HORIZON-STRUCTURE-LEDGER.json", "horizon_rows", "horizon_structure_id", "HZN-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0163", "REF-0666", "REF-0667", "REF-0683"]),
    ("BLACK-HOLE-THERMODYNAMICS-LEDGER.json", "thermodynamics_rows", "black_hole_thermodynamics_id", "BHT-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0163", "REF-0666", "REF-0683"]),
    ("EVAPORATION-RADIATION-LEDGER.json", "evaporation_rows", "evaporation_radiation_id", "EVR-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0666", "REF-0683", "REF-0684"]),
    ("SEMICLASSICAL-BACKREACTION-LEDGER.json", "backreaction_rows", "backreaction_consistency_id", "BKR-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0163", "REF-0666", "REF-0684"]),
    ("EQUATION-OF-STATE-LEDGER.json", "equation_of_state_rows", "equation_of_state_id", "EOS-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0163", "REF-0666", "REF-0667", "REF-0683", "REF-0684"]),
    ("FLUCTUATION-DISSIPATION-LEDGER.json", "fluctuation_dissipation_rows", "fluctuation_dissipation_id", "FDT-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0666", "REF-0684"]),
    ("TRANSPORT-COEFFICIENT-LEDGER.json", "transport_coefficient_rows", "transport_coefficient_id", "TRC-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0666", "REF-0684"]),
    ("STRESS-ENERGY-SOURCE-LEDGER.json", "source_rows", "stress_energy_source_id", "SET-0003-FAMILYB-THERMO-ENTROPIC", ["REF-0163", "REF-0666", "REF-0684"]),
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


def duplicate_refs(row: dict[str, Any] | None) -> list[str]:
    refs = row.get("source_refs", []) if isinstance(row, dict) else []
    seen: set[str] = set()
    dup: list[str] = []
    for ref in refs:
        if ref in seen and ref not in dup:
            dup.append(ref)
        seen.add(ref)
    return dup


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


def evaluate_familyb_thermo_entropy(root: Path) -> dict[str, Any]:
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
        add("route-ceiling-remains-S1", route.get("promotion_ceiling") == "S1", f"promotion_ceiling={route.get('promotion_ceiling')}")
        for fid in FORECAST_IDS:
            add(f"route-mirrors-forecast-{fid}", fid in route.get("forecast_ids", []), f"forecast_ids={route.get('forecast_ids')}")
        for did in DELTA_IDS:
            add(f"route-mirrors-delta-{did}", did in route.get("empirical_delta_ids", []), f"empirical_delta_ids={route.get('empirical_delta_ids')}")
        text = text_of(route, ["residual_cap", "earliest_blocker", "source_role_events", "rev0330_familyb_pressure_note"])
        missing_terms = [term for term in ["nonequilibrium", "entropy", "calibration", "microscopic", "s1", "not acquired", "no route promotion"] if term not in text]
        add("route-denominator-language", not missing_terms, f"missing_terms={missing_terms}")

    for fid in FORECAST_IDS:
        row = find_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", fid)
        add(f"forecast-present-{fid}", row is not None, fid)
        if row:
            add(f"forecast-route-local-{fid}", row.get("route_id") == ROUTE_ID, f"route_id={row.get('route_id')}")
            add(f"forecast-credit-S1-{fid}", row.get("current_maximum_credit") == "S1", f"current_maximum_credit={row.get('current_maximum_credit')}")
            req = FRESH_FAMILYB_REFS if fid == FORECAST_IDS[0] else ["REF-0683", "REF-0684"]
            miss = missing_refs(row, req)
            add(f"forecast-current-refs-{fid}", not miss, f"missing_refs={miss}")
            dup = duplicate_refs(row)
            add(f"forecast-source-refs-deduped-{fid}", not dup, f"duplicate_refs={dup}")
            record = text_of(row, ["required_public_record", "non_promotion_warning", "positive_result_credit"])
            missing_terms = [term for term in ["entropy", "calibration", "nonequilibrium", "not", "promotion"] if term not in record]
            add(f"forecast-denominator-language-{fid}", not missing_terms, f"missing_terms={missing_terms}")

    for did in DELTA_IDS:
        row = find_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", did)
        add(f"delta-present-{did}", row is not None, did)
        if row:
            add(f"delta-route-local-{did}", row.get("route_ids") == [ROUTE_ID], f"route_ids={row.get('route_ids')}")
            add(f"delta-evidence-link-{did}", EVIDENCE_ID in (row.get("evidence_unit_ids") or []), f"evidence_unit_ids={row.get('evidence_unit_ids')}")
            add(f"delta-ceiling-S1-{did}", row.get("promotion_ceiling") == "S1", f"promotion_ceiling={row.get('promotion_ceiling')}")
            req = FRESH_FAMILYB_REFS if did == DELTA_IDS[0] else ["REF-0683", "REF-0684"]
            miss = missing_refs(row, req)
            add(f"delta-current-refs-{did}", not miss, f"missing_refs={miss}")
            dup = duplicate_refs(row)
            add(f"delta-source-refs-deduped-{did}", not dup, f"duplicate_refs={dup}")
            record = text_of(row, ["record_delta", "candidate_native_effect", "residual_cap"])
            missing_terms = [term for term in ["entropy", "calibration", "nonequilibrium", "microscopic", "many-to-one"] if term not in record]
            add(f"delta-denominator-language-{did}", not missing_terms, f"missing_terms={missing_terms}")

    add("decision-present", decision is not None, DECISION_ID)
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"route_ids={decision.get('route_ids')}")
        for did in DELTA_IDS:
            add(f"decision-hooks-{did}", did in (decision.get("empirical_delta_hooks") or []), f"empirical_delta_hooks={decision.get('empirical_delta_hooks')}")
        miss = missing_refs(decision, FRESH_FAMILYB_REFS)
        add("decision-current-refs", not miss, f"missing_refs={miss}")
        dup = duplicate_refs(decision)
        add("decision-source-refs-deduped", not dup, f"duplicate_refs={dup}")
        too_high = [item for item in decision.get("outcome_effects", []) if isinstance(item, dict) and item.get("promotion_ceiling") != "S1"]
        add("decision-outcomes-capped-S1", not too_high, f"too_high={too_high}")
        record = text_of(decision, ["target_question", "public_record", "minimum_public_artifact", "non_promotion_clause", "outcome_effects"])
        missing_terms = [term for term in ["entropy", "calibration", "stochastic", "noise", "s1"] if term not in record]
        add("decision-denominator-language", not missing_terms, f"missing_terms={missing_terms}")

    add("evidence-present", evidence is not None, EVIDENCE_ID)
    if evidence:
        for did in DELTA_IDS:
            add(f"evidence-reciprocal-delta-{did}", did in (evidence.get("empirical_delta_ids") or []), f"empirical_delta_ids={evidence.get('empirical_delta_ids')}")
        forbidden = present_refs(evidence, FRESH_FAMILYB_REFS)
        add("fresh-refs-not-acquired-evidence", not forbidden, f"forbidden_present={forbidden}")
        add("evidence-credit-S1", evidence.get("maximum_credit") == "S1", f"maximum_credit={evidence.get('maximum_credit')}")
        record = text_of(evidence, ["record_description", "credit_spend_rule"])
        missing_terms = [term for term in ["pressure", "not acquired", "entropy", "noise"] if term not in record]
        add("evidence-noncredit-language", not missing_terms, f"missing_terms={missing_terms}")

    control_results: list[dict[str, Any]] = []
    for rel, collection, id_field, row_id, refs in CONTROL_ROWS:
        row = find_row(root, rel, collection, id_field, row_id)
        miss = missing_refs(row, refs)
        dup = duplicate_refs(row)
        passed = row is not None and not miss and not dup
        control_results.append({"ledger_file": rel, "row_id": row_id, "required_refs": refs, "missing_refs": miss, "duplicate_refs": dup, "passed": passed})
        add(f"control-row-current-refs-{row_id}", row is not None and not miss, f"missing_refs={miss}")
        add(f"control-row-source-refs-deduped-{row_id}", not dup, f"duplicate_refs={dup}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": ROUTE_ID,
        "evidence_id": EVIDENCE_ID,
        "forecast_ids": FORECAST_IDS,
        "delta_ids": DELTA_IDS,
        "decision_id": DECISION_ID,
        "fresh_refs": FRESH_FAMILYB_REFS,
        "new_refs": NEW_FAMILYB_REFS,
        "checks": checks,
        "control_results": control_results,
        "failures": failures,
    }


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def write_familyb_thermo_entropy_audit(root: Path) -> None:
    result = evaluate_familyb_thermo_entropy(root)
    lines = [
        "# FamilyB thermodynamic / entropy source-role audit (generated)",
        "",
        "Generated from the FamilyB route, forecast, empirical-delta, decision, evidence-unit, and route-control rows. Do not edit directly; run `make index` after changing FamilyB thermodynamic pressure.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Evidence unit checked: `{result['evidence_id']}`",
        f"- Fresh FamilyB refs: {refs_text(result['fresh_refs'])}",
        f"- New nonequilibrium/calibration refs: {refs_text(result['new_refs'])}",
        f"- FamilyB thermodynamic checks: `{len(result['checks'])}`",
        f"- FamilyB thermodynamic failures: `{len(result['failures'])}`",
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
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "FamilyB thermodynamic, relative-entropy, nonequilibrium, and horizon-calibration sources are S1 route-local denominator pressure. They can tighten replay obligations, but they cannot become acquired evidence-unit source credit, black-hole microstate closure, observed-sector identity, or route promotion.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_familyb_thermo_entropy_audit(root)
    outcome = evaluate_familyb_thermo_entropy(root)
    if outcome["failures"]:
        print("FAMILYB THERMO ENTROPY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("FAMILYB THERMO ENTROPY OK")
