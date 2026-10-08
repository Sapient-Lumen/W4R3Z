#!/usr/bin/env python3
"""Check DESI / Lyman-alpha / Euclid cosmology source-role separation.

This policy keeps acquired DESI DR2 likelihood/chain custody separate from
interpretation papers, Lyman-alpha follow-up combinations, unreleased spectra
or redshift custody, and future Euclid release runway. The route can receive
S2 pressure, but not dark-energy ontology or Theory-of-Everything promotion.
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

GENERATED_AUDIT = "docs/30-program/cosmology-source-role-audit.generated.md"
ROUTE_ID = "R-OQ0057-COSMO-DARK-ENERGY-BAO"
EVIDENCE_ID = "EU-0012-DESI-BAO-LIKELIHOOD"
DECISION_ID = "DX-0004-DESI-LATE-TIME-DARK-ENERGY-DYNAMICS"
FORECAST_IDS = [
    "DF-0013-DESI-DR2-COSMOLOGY-TENSION-SPLIT",
    "DF-0021-DESI-LYA-EUCLID-SPECTRA-STAGING-REPLAY",
]
DELTA_IDS = [
    "ED-0009-DESI-DR2-COSMOLOGY-CONSTRAINT-CORRIDOR",
    "ED-0019-DESI-DR2-EXTENDED-DE-COMBINATION-PRESSURE",
    "ED-0027-DESI-LYA-EUCLID-SPECTRA-STAGING-PRESSURE",
]
OFFICIAL_PRODUCT_REFS = ["REF-0211", "REF-0219", "REF-0626", "REF-0688"]
INTERPRETATION_REFS = ["REF-0651", "REF-0689", "REF-0690", "REF-0675"]
RUNWAY_REFS = ["REF-0637"]
PRESSURE_REFS = ["REF-0651", "REF-0689", "REF-0690", "REF-0637"]
NEW_REFS = ["REF-0688", "REF-0689", "REF-0690"]

CONTROL_ROWS: list[tuple[str, str, str, str, list[str]]] = [
    ("LIKELIHOOD-UPDATE-LEDGER.json", "update_rows", "likelihood_update_id", "LU-0012-COSMO-DARK-ENERGY-BAO", ["REF-0688", "REF-0689", "REF-0690", "REF-0637"]),
    ("MEASUREMENT-MODEL-LEDGER.json", "measurement_model_rows", "measurement_model_id", "MM-0012-COSMO-DARK-ENERGY-BAO", ["REF-0688"]),
    ("SYSTEMATIC-UNCERTAINTY-LEDGER.json", "systematic_rows", "systematic_id", "SYS-0012-COSMO-DARK-ENERGY-BAO", ["REF-0688", "REF-0689", "REF-0690"]),
    ("CALIBRATION-TRACEABILITY-LEDGER.json", "calibration_rows", "calibration_id", "CAL-0012-COSMO-DARK-ENERGY-BAO", ["REF-0688"]),
    ("CLAIM-LANGUAGE-PERMISSION-LEDGER.json", "permission_rows", "language_permission_id", "LPP-0012-COSMO-DARK-ENERGY-BAO", ["REF-0689", "REF-0690"]),
    ("COSMOLOGICAL-BACKGROUND-LEDGER.json", "background_rows", "cosmological_background_id", "CBG-0012-COSMO-DARK-ENERGY-BAO", ["REF-0689", "REF-0690", "REF-0637"]),
    ("VACUUM-ENERGY-LEDGER.json", "vacuum_energy_rows", "vacuum_energy_id", "VED-0012-COSMO-DARK-ENERGY-BAO", ["REF-0675", "REF-0689", "REF-0690"]),
    ("THERMAL-HISTORY-LEDGER.json", "thermal_history_rows", "thermal_history_id", "THS-0012-COSMO-DARK-ENERGY-BAO", ["REF-0689", "REF-0690", "REF-0637"]),
    ("PRIOR-SENSITIVITY-LEDGER.json", "prior_rows", "prior_sensitivity_id", "PS-0012-DESI-COSMOLOGY-PRIOR-BOUNDS", ["REF-0689", "REF-0690"]),
    ("MODEL-CAPACITY-LEDGER.json", "capacity_rows", "model_capacity_id", "CAP-0012-COSMO-DESI-BAO", ["REF-0689", "REF-0690"]),
    ("SELECTION-FUNCTION-LEDGER.json", "selection_rows", "selection_function_id", "SF-0012-COSMO-DESI-BAO", ["REF-0688", "REF-0689"]),
    ("MULTIPLICITY-CONTROL-LEDGER.json", "multiplicity_rows", "multiplicity_control_id", "MC-0012-COSMO-DESI-BAO", ["REF-0689"]),
    ("REPORTING-BIAS-LEDGER.json", "bias_rows", "reporting_bias_id", "RBIA-0012-COSMO-DESI-BAO", ["REF-0689", "REF-0690"]),
    ("COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json", "reproducibility_rows", "computational_reproducibility_id", "CRP-0012-COSMO-DARK-ENERGY-BAO", ["REF-0688"]),
    ("NUMERICAL-STABILITY-LEDGER.json", "stability_rows", "numerical_stability_id", "NST-0012-COSMO-DARK-ENERGY-BAO", ["REF-0688", "REF-0690"]),
    ("SOFTWARE-SUPPLY-CHAIN-LEDGER.json", "supply_chain_rows", "software_supply_chain_id", "SSC-0012-COSMO-DARK-ENERGY-BAO", ["REF-0688"]),
    ("EVIDENCE-SEVERITY-LEDGER.json", "severity_rows", "severity_id", "SV-0006-DESI-DARK-ENERGY-SEVERITY", ["REF-0688", "REF-0689", "REF-0690"]),
    ("CONTRAST-CLASS-LEDGER.json", "contrast_rows", "contrast_class_id", "CC-0011-DESI-DARK-ENERGY-PRIOR-CONTRAST", ["REF-0689", "REF-0690"]),
]



def evaluate_cosmology_source_role(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    route = find_ledger_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", ROUTE_ID)
    evidence = find_ledger_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID)
    decision = find_ledger_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID)
    carrier = find_ledger_row(root, "PUBLIC-RECORD-CARRIER-LEDGER.json", "carrier_rows", "carrier_id", "PRC-DESI-BAO-LIKELIHOOD")
    protocol = find_ledger_row(root, "ACQUISITION-PROTOCOL-LEDGER.json", "protocol_rows", "protocol_id", "AP-DESI-LIKELIHOOD-REPLAY")

    add("route-present", route is not None, ROUTE_ID)
    if route:
        add("route-authority-S2", route.get("authority_state") == "S2", f"authority_state={route.get('authority_state')}")
        add("route-ceiling-S2", route.get("promotion_ceiling") == "S2", f"promotion_ceiling={route.get('promotion_ceiling')}")
        for fid in FORECAST_IDS:
            add(f"route-mirrors-forecast-{fid}", fid in route.get("forecast_ids", []), f"forecast_ids={route.get('forecast_ids')}")
        for did in DELTA_IDS:
            add(f"route-mirrors-delta-{did}", did in route.get("empirical_delta_ids", []), f"empirical_delta_ids={route.get('empirical_delta_ids')}")
        text = text_from_fields(route, ["residual_cap", "source_role_events", "rev0332_cosmology_source_role_note"])
        missing = [term for term in ["spectra", "redshift", "lyman", "euclid", "not acquired", "no route"] if term not in text]
        add("route-source-staging-language", not missing, f"missing_terms={missing}")

    add("evidence-present", evidence is not None, EVIDENCE_ID)
    if evidence:
        add("evidence-route-local", evidence.get("route_ids") == [ROUTE_ID], f"route_ids={evidence.get('route_ids')}")
        for did in DELTA_IDS:
            add(f"evidence-reciprocal-delta-{did}", did in (evidence.get("empirical_delta_ids") or []), f"empirical_delta_ids={evidence.get('empirical_delta_ids')}")
        miss = missing_source_refs(evidence, ["REF-0211", "REF-0219", "REF-0626", "REF-0688"])
        add("evidence-official-product-refs", not miss, f"missing_refs={miss}")
        forbidden = present_source_refs(evidence, ["REF-0651", "REF-0689", "REF-0690", "REF-0637", "REF-0675"])
        add("interpretation-and-runway-refs-not-acquired-evidence", not forbidden, f"forbidden_present={forbidden}")
        add("evidence-source-refs-deduped", not duplicate_source_refs(evidence), f"duplicate_refs={duplicate_source_refs(evidence)}")
        record = text_from_fields(evidence, ["record_description", "support_kind"])
        missing = [term for term in ["chains", "follow-up", "route-local pressure", "not acquired"] if term not in record]
        add("evidence-source-role-language", not missing, f"missing_terms={missing}")

    for label, row in [("carrier", carrier), ("protocol", protocol)]:
        add(f"{label}-present", row is not None, label)
        if row:
            miss = missing_source_refs(row, ["REF-0211", "REF-0219", "REF-0626", "REF-0688"] if label == "carrier" else ["REF-0211", "REF-0219", "REF-0626", "REF-0688"])
            add(f"{label}-official-product-refs", not miss, f"missing_refs={miss}")
            forbidden = present_source_refs(row, ["REF-0651", "REF-0689", "REF-0690", "REF-0637", "REF-0675"])
            add(f"{label}-pressure-refs-not-acquired-product-custody", not forbidden, f"forbidden_present={forbidden}")
            text = text_from_fields(row, ["record_object", "versioning_or_freeze_rule", "calibration_or_metadata_requirements", "failure_to_record_effect"])
            missing = [term for term in ["spectra", "redshift", "chains"] if term not in text]
            add(f"{label}-source-staging-language", not missing, f"missing_terms={missing}")

    for fid in FORECAST_IDS:
        row = find_ledger_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", fid)
        add(f"forecast-present-{fid}", row is not None, fid)
        if row:
            add(f"forecast-route-local-{fid}", row.get("route_id") == ROUTE_ID, f"route_id={row.get('route_id')}")
            add(f"forecast-credit-S2-{fid}", row.get("current_maximum_credit") == "S2", f"current_maximum_credit={row.get('current_maximum_credit')}")
            req = ["REF-0688", "REF-0689", "REF-0690", "REF-0637"] if fid == FORECAST_IDS[1] else ["REF-0211", "REF-0626", "REF-0651", "REF-0689", "REF-0690"]
            miss = missing_source_refs(row, req)
            add(f"forecast-required-refs-{fid}", not miss, f"missing_refs={miss}")
            add(f"forecast-source-refs-deduped-{fid}", not duplicate_source_refs(row), f"duplicate_refs={duplicate_source_refs(row)}")
            text = text_from_fields(row, ["required_public_record", "positive_result_credit", "negative_result_credit", "non_promotion_warning"])
            missing = [term for term in ["spectra", "lyman", "s2", "not"] if term not in text]
            add(f"forecast-denominator-language-{fid}", not missing, f"missing_terms={missing}")

    for did in DELTA_IDS:
        row = find_ledger_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", did)
        add(f"delta-present-{did}", row is not None, did)
        if row:
            add(f"delta-route-local-{did}", row.get("route_ids") == [ROUTE_ID], f"route_ids={row.get('route_ids')}")
            add(f"delta-evidence-link-{did}", EVIDENCE_ID in (row.get("evidence_unit_ids") or []), f"evidence_unit_ids={row.get('evidence_unit_ids')}")
            add(f"delta-ceiling-S2-{did}", row.get("promotion_ceiling") == "S2", f"promotion_ceiling={row.get('promotion_ceiling')}")
            req = {
                "ED-0009-DESI-DR2-COSMOLOGY-CONSTRAINT-CORRIDOR": ["REF-0211", "REF-0626", "REF-0688"],
                "ED-0019-DESI-DR2-EXTENDED-DE-COMBINATION-PRESSURE": ["REF-0211", "REF-0626", "REF-0651", "REF-0689", "REF-0690"],
                "ED-0027-DESI-LYA-EUCLID-SPECTRA-STAGING-PRESSURE": ["REF-0688", "REF-0689", "REF-0690", "REF-0637"],
            }[did]
            miss = missing_source_refs(row, req)
            add(f"delta-required-refs-{did}", not miss, f"missing_refs={miss}")
            add(f"delta-source-refs-deduped-{did}", not duplicate_source_refs(row), f"duplicate_refs={duplicate_source_refs(row)}")
            text = text_from_fields(row, ["record_delta", "candidate_native_effect", "state_effect", "residual_cap"])
            missing = [term for term in ["s2", "many", "not"] if term not in text]
            add(f"delta-denominator-language-{did}", not missing, f"missing_terms={missing}")

    add("decision-present", decision is not None, DECISION_ID)
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"route_ids={decision.get('route_ids')}")
        for did in DELTA_IDS:
            add(f"decision-hooks-{did}", did in (decision.get("empirical_delta_hooks") or []), f"empirical_delta_hooks={decision.get('empirical_delta_hooks')}")
        miss = missing_source_refs(decision, ["REF-0211", "REF-0626", "REF-0651", "REF-0688", "REF-0689", "REF-0690", "REF-0637"])
        add("decision-required-refs", not miss, f"missing_refs={miss}")
        add("decision-source-refs-deduped", not duplicate_source_refs(decision), f"duplicate_refs={duplicate_source_refs(decision)}")
        too_high = [item for item in decision.get("outcome_effects", []) if isinstance(item, dict) and item.get("promotion_ceiling") not in {"S1", "S2"}]
        add("decision-outcomes-capped-S2", not too_high, f"too_high={too_high}")
        text = text_from_fields(decision, ["public_record", "minimum_public_artifact", "non_promotion_clause", "rev0332_cosmology_source_role_note", "outcome_effects"])
        missing = [term for term in ["spectra", "lyman", "euclid", "s2"] if term not in text]
        add("decision-source-staging-language", not missing, f"missing_terms={missing}")

    for rel, collection, id_field, row_id, refs in CONTROL_ROWS:
        row = find_ledger_row(root, rel, collection, id_field, row_id)
        add(f"control-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row:
            miss = missing_source_refs(row, refs)
            add(f"control-required-refs-{row_id}", not miss, f"missing_refs={miss}")
            add(f"control-source-refs-deduped-{row_id}", not duplicate_source_refs(row), f"duplicate_refs={duplicate_source_refs(row)}")
            add(f"control-route-local-{row_id}", ROUTE_ID in (row.get("route_ids") or [row.get("route_id")]), f"route_ids={row.get('route_ids') or row.get('route_id')}")

    return {"audit_file": GENERATED_AUDIT, "checks": checks, "failures": failures}


def write_cosmology_source_role_audit(root: Path) -> None:
    result = evaluate_cosmology_source_role(root)
    checks = result["checks"]
    failures = result["failures"]
    family_counts: dict[str, dict[str, int]] = {}
    for item in checks:
        prefix = str(item["check"]).split("-", 1)[0]
        bucket = family_counts.setdefault(prefix, {"total": 0, "failures": 0})
        bucket["total"] += 1
        if not item["passed"]:
            bucket["failures"] += 1

    lines = [
        "# Cosmology DESI/Lyman-alpha/Euclid source-role audit (generated)",
        "",
        "This generated audit enforces the split between acquired DESI likelihood custody, interpretation pressure, Lyman-alpha/Euclid staging, and route-local cosmology handoff language.",
        "",
        f"- Cosmology source-role checks: `{len(checks)}`",
        f"- Cosmology source-role failures: `{len(failures)}`",
        "- Display mode: `compressed-family-summary-plus-failures`",
        "",
        "## Check-family summary",
        "",
        "| Family | Checks | Failures |",
        "|---|---:|---:|",
    ]
    for family, counts in sorted(family_counts.items()):
        lines.append(f"| `{family}` | `{counts['total']}` | `{counts['failures']}` |")

    lines += [
        "",
        "## Failure details",
        "",
    ]
    if failures:
        lines += [f"- {failure}" for failure in failures]
    else:
        lines.append("None.")

    lines += [
        "",
        "## Compression rule",
        "",
        "The evaluator still executes every row-level source-role check. The generated restart surface suppresses the old all-pass row table so it cannot dominate the human restart path.",
        "",
        "No route score, authority ceiling, evidence-unit source credit, or dark-energy ontology claim is promoted by this audit.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    write_cosmology_source_role_audit(root)
    result = evaluate_cosmology_source_role(root)
    if result["failures"]:
        print("Cosmology source-role policy failed:", file=sys.stderr)
        for failure in result["failures"]:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Cosmology source-role checks: {len(result['checks'])}; failures: 0")


if __name__ == "__main__":
    main()
