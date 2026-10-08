#!/usr/bin/env python3
"""Strong-field GW public-test source-role and nested-ceiling checks.

The gravitational-wave route is scientifically important but unusually easy to
overcredit: public catalogs, no-deviation GR tests, one loud black-hole event,
and future detector runway can collapse into one persuasive story.  This audit
keeps current catalog/test records as S2 constraint pressure and keeps future
LISA/next-generation runway refs off acquired-evidence/current-credit surfaces.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/gw-strongfield-public-test-source-role-audit.generated.md"
ROUTE_ID = "R-OQ0057-GW-STRONGFIELD-GR"
FORECAST_ID = "DF-0004-STRONGFIELD-GW-DEVIATION"
DELTA_ID = "ED-0004-GWTC5-STRONGFIELD-GR-CONSTRAINTS"
FUTURE_DELTA_ID = "ED-0011-LISA-AND-NEXTGEN-GW-FORECAST-CORRIDOR"
DECISION_ID = "DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION"
EVIDENCE_ID = "EU-0009-GW-STRONGFIELD-CATALOG"
CREDIT_ID = "CA-GW-STRONGFIELD-GR"
CURRENT_TEST_REFS = ["REF-0677", "REF-0678"]
CURRENT_CATALOG_REFS = ["REF-0624", "REF-0625", "REF-0629"]
FUTURE_RUNWAY_REFS = ["REF-0213", "REF-0214", "REF-0630", "REF-0631", "REF-0632"]

REQUIRED_CURRENT_TEST_PLACEMENTS: list[tuple[str, str, str, str]] = [
    ("DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", FORECAST_ID),
    ("EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", DELTA_ID),
    ("DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID),
    ("EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID),
    ("CREDIT-ALLOCATION-LEDGER.json", "credit_rows", "credit_id", CREDIT_ID),
    ("EVIDENCE-SEVERITY-LEDGER.json", "severity_rows", "severity_id", "SV-0005-GW-STRONGFIELD-SEVERITY"),
    ("MEASUREMENT-MODEL-LEDGER.json", "measurement_model_rows", "measurement_model_id", "MM-0009-GW-STRONGFIELD-GR"),
    ("SYSTEMATIC-UNCERTAINTY-LEDGER.json", "systematic_rows", "systematic_id", "SYS-0009-GW-STRONGFIELD-GR"),
    ("CALIBRATION-TRACEABILITY-LEDGER.json", "calibration_rows", "calibration_id", "CAL-0009-GW-STRONGFIELD-GR"),
    ("GRAVITATIONAL-RADIATION-LEDGER.json", "radiation_rows", "gravitational_radiation_id", "GRR-0009-GW-STRONGFIELD-GR"),
]

FORBID_FUTURE_ON_CURRENT_CREDIT: list[tuple[str, str, str, str]] = [
    ("EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID),
    ("CREDIT-ALLOCATION-LEDGER.json", "credit_rows", "credit_id", CREDIT_ID),
]

REQUIRE_FUTURE_RUNWAY_ON_FORECAST: list[tuple[str, str, str, str]] = [
    ("EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", FUTURE_DELTA_ID),
    ("DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID),
]


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(root: Path, rel: str, collection: str, id_field: str, row_id: str) -> dict[str, Any] | None:
    rows = load_json(root, rel).get(collection, [])
    return next((row for row in rows if isinstance(row, dict) and row.get(id_field) == row_id), None)


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


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def evaluate_gw_strongfield_public_test(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    def add(label: str, passed: bool, detail: str) -> None:
        checks.append({"check": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    route = find_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", ROUTE_ID)
    decision = find_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID)
    evidence = find_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID)
    credit = find_row(root, "CREDIT-ALLOCATION-LEDGER.json", "credit_rows", "credit_id", CREDIT_ID)

    add("route-present", route is not None, f"route `{ROUTE_ID}` must exist")
    if route:
        add("route-authority-S2", route.get("authority_state") == "S2", f"authority_state `{route.get('authority_state')}`")
        add("route-ceiling-S2", route.get("promotion_ceiling") == "S2", f"promotion_ceiling `{route.get('promotion_ceiling')}`")
        text = combined_text(route, ["inverse_deficiency", "abstention_or_no_verdict_rule", "residual_cap", "earliest_blocker"])
        missing = [term for term in ["many", "constraint", "not", "candidate", "s2"] if term not in text]
        add("route-nonidentifiability-language", not missing, f"missing terms {missing}")

    add("decision-present", decision is not None, f"decision `{DECISION_ID}` must exist")
    if decision:
        add("decision-route-local", decision.get("route_ids") == [ROUTE_ID], f"routes {decision.get('route_ids')}")
        nested = decision.get("outcome_effects", [])
        too_high = [item for item in nested if isinstance(item, dict) and item.get("promotion_ceiling") not in {None, "S0", "S1", "S2"}]
        add("nested-outcomes-capped-S2", not too_high, f"too-high outcome ceilings {[item.get('outcome_class') for item in too_high]}")
        text = combined_text(decision, ["public_record", "minimum_public_artifact", "non_promotion_clause", "rev0327_nested_ceiling_note"])
        missing = [term for term in ["waveform", "calibration", "selection", "candidate", "split"] if term not in text]
        add("decision-denominator-language", not missing, f"missing terms {missing}")

    for rel, collection, id_field, row_id in REQUIRED_CURRENT_TEST_PLACEMENTS:
        row = find_row(root, rel, collection, id_field, row_id)
        add(f"current-test-row-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row:
            missing = [ref for ref in CURRENT_TEST_REFS if ref not in row.get("source_refs", [])]
            add(f"current-test-refs-{row_id}", not missing, f"missing refs {missing}; present {row.get('source_refs', [])}")

    for rel, collection, id_field, row_id in FORBID_FUTURE_ON_CURRENT_CREDIT:
        row = find_row(root, rel, collection, id_field, row_id)
        add(f"current-credit-row-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row:
            present = [ref for ref in FUTURE_RUNWAY_REFS if ref in row.get("source_refs", [])]
            add(f"future-refs-not-current-credit-{row_id}", not present, f"future refs on current credit/evidence row: {present}")
            text = combined_text(row, ["record_description", "credit_spend_rule", "current_credit_basis", "source_role_events", "rev0327_source_role_note"])
            missing = [term for term in ["future", "runway", "not", "credit"] if term not in text]
            add(f"future-runway-not-credit-language-{row_id}", not missing, f"missing terms {missing}")

    for rel, collection, id_field, row_id in REQUIRE_FUTURE_RUNWAY_ON_FORECAST:
        row = find_row(root, rel, collection, id_field, row_id)
        add(f"future-runway-row-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row:
            missing = [ref for ref in ["REF-0630", "REF-0631", "REF-0632"] if ref not in row.get("source_refs", [])]
            add(f"future-runway-refs-{row_id}", not missing, f"missing refs {missing}; present {row.get('source_refs', [])}")

    if evidence:
        add("evidence-current-catalog-refs", not [ref for ref in CURRENT_CATALOG_REFS if ref not in evidence.get("source_refs", [])], f"source refs {evidence.get('source_refs', [])}")
    if credit:
        add("credit-current-test-refs", not [ref for ref in CURRENT_TEST_REFS if ref not in credit.get("source_refs", [])], f"source refs {credit.get('source_refs', [])}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": ROUTE_ID,
        "current_test_refs": CURRENT_TEST_REFS,
        "future_runway_refs": FUTURE_RUNWAY_REFS,
        "checks": checks,
        "failures": failures,
    }


def write_gw_strongfield_public_test_audit(root: Path) -> None:
    result = evaluate_gw_strongfield_public_test(root)
    lines = [
        "# GW strong-field public-test source-role audit (generated)",
        "",
        "Generated from the strong-field GW route, decision, evidence, credit, and control rows. Do not edit directly; run `make index` after changing GW catalog/test source roles.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Current GR-test refs: {refs_text(result['current_test_refs'])}",
        f"- Future/runway refs fenced from current evidence-credit: {refs_text(result['future_runway_refs'])}",
        f"- GW strong-field source-role checks: `{len(result['checks'])}`",
        f"- GW strong-field source-role failures: `{len(result['failures'])}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` | {detail} |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in result["failures"])
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "GW catalog growth, parameterized GR tests, GW250114 spectroscopy, and future LISA/next-generation runway all remain route-local pressure. Current acquired evidence and credit are capped at S2; future runway refs must not appear on acquired evidence-unit or current-credit rows, and nested decision outcomes must not exceed the route ceiling.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_gw_strongfield_public_test_audit(root)
    outcome = evaluate_gw_strongfield_public_test(root)
    if outcome["failures"]:
        print("GW STRONGFIELD PUBLIC-TEST POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("GW STRONGFIELD PUBLIC-TEST POLICY OK")
