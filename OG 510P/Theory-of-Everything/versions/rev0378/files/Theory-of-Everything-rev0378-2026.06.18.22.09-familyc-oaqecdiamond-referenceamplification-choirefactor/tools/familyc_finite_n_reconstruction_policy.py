#!/usr/bin/env python3
"""FamilyC finite-N / QEC / island decoder source-role policy.

The FamilyC entanglement-wedge/code route is the strongest live route.  This
policy lets current finite-N, black-hole-interior QEC, modular-Krylov/island
area, and massless-island papers add route-facing pressure while preventing
those sources from being spent as acquired evidence-unit credit or promotion.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

from source_role_event_utils import find_ledger_row, missing_source_refs

GENERATED_AUDIT = "docs/30-program/familyc-finite-n-reconstruction-source-role-audit.generated.md"
ROUTE_ID = "R-OQ0057-FAMILYC-EW-CODE"
FORECAST_ID = "DF-0022-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY"
DELTA_ID = "ED-0028-FAMILYC-FINITE-N-QEC-ISLAND-PRESSURE"
DECISION_ID = "DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY"
EVIDENCE_ID = "EU-0001-FAMILYC-EW-RECONSTRUCTION"
REQUIRED_REFS = ["REF-0691", "REF-0692", "REF-0693", "REF-0694"]

def _semantic_text(value: Any) -> str:
    """Normalize notation-only spelling differences before policy matching.

    Scientific source terms regularly appear as ``epsilon_OD``, ``epsilon-OD``,
    or prose separated by spaces.  The audit should reject a missing concept,
    not fail because a ledger chose an underscore instead of a hyphen.
    """
    text = str(value).lower()
    for mark in ("‐", "‑", "‒", "–", "—", "−", "_"):
        text = text.replace(mark, "-")
    return " ".join(text.split())


def _contains_any(text: str, alternatives: Iterable[str]) -> bool:
    normalized = _semantic_text(text)
    return any(_semantic_text(item) in normalized for item in alternatives)


CONTROL_ROWS: list[tuple[str, str, str, str, list[str]]] = [
    ("ACQUISITION-PROTOCOL-LEDGER.json", "protocol_rows", "protocol_id", "AP-HOLOGRAPHIC-DECODER-REPLAY", REQUIRED_REFS),
    ("EVIDENCE-SEVERITY-LEDGER.json", "severity_rows", "severity_id", "SV-0001-FAMILYC-PUBLIC-RECONSTRUCTION-SEVERITY", REQUIRED_REFS),
    ("QEC-CODE-SUBSPACE-LEDGER.json", "qec_code_subspace_rows", "qec_code_subspace_id", "QEC-0001-FAMILYC-EW-CODE", ["REF-0691", "REF-0692"]),
    ("LOGICAL-OPERATOR-RECONSTRUCTION-LEDGER.json", "logical_operator_reconstruction_rows", "logical_operator_reconstruction_id", "LOR-0001-FAMILYC-EW-CODE", ["REF-0691", "REF-0692", "REF-0693"]),
    ("DECODER-CERTIFICATION-LEDGER.json", "decoder_certification_rows", "decoder_certification_id", "DCF-0001-FAMILYC-EW-CODE", REQUIRED_REFS),
    ("INFORMATION-FLOW-LEDGER.json", "information_rows", "information_flow_id", "IFL-0001-FAMILYC-EW-CODE", ["REF-0691", "REF-0693", "REF-0694"]),
    ("BLACK-HOLE-THERMODYNAMICS-LEDGER.json", "thermodynamics_rows", "black_hole_thermodynamics_id", "BHT-0001-FAMILYC-EW-CODE", ["REF-0691", "REF-0693", "REF-0694"]),
    ("EVAPORATION-RADIATION-LEDGER.json", "evaporation_rows", "evaporation_radiation_id", "EVR-0001-FAMILYC-EW-CODE", ["REF-0691", "REF-0693", "REF-0694"]),
    ("SUBSYSTEM-FACTORIZATION-LEDGER.json", "factorization_rows", "subsystem_factorization_id", "FAC-0001-FAMILYC-EW-CODE", REQUIRED_REFS),
    ("EDGE-MODE-CENTER-LEDGER.json", "edge_mode_rows", "edge_mode_center_id", "EDG-0001-FAMILYC-EW-CODE", ["REF-0692", "REF-0693", "REF-0694"]),
    ("ALGEBRAIC-LOCALITY-LEDGER.json", "algebraic_rows", "algebraic_locality_id", "ALG-0001-FAMILYC-EW-CODE", REQUIRED_REFS),
    ("ENTANGLEMENT-STRUCTURE-LEDGER.json", "entanglement_structure_rows", "entanglement_structure_id", "ESG-0001-FAMILYC-EW-CODE", REQUIRED_REFS),
    ("MODULAR-FLOW-LEDGER.json", "modular_flow_rows", "modular_flow_id", "MDF-0001-FAMILYC-EW-CODE", ["REF-0692"]),
    ("RELATIVE-ENTROPY-RECOVERY-LEDGER.json", "relative_entropy_recovery_rows", "relative_entropy_recovery_id", "RER-0001-FAMILYC-EW-CODE", ["REF-0691", "REF-0693", "REF-0694"]),
]


def evaluate_familyc_finite_n_reconstruction(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    def add(label: str, passed: bool, detail: str) -> None:
        checks.append({"label": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    route = find_ledger_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", ROUTE_ID)
    forecast = find_ledger_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", FORECAST_ID)
    delta = find_ledger_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", DELTA_ID)
    decision = find_ledger_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID)
    evidence = find_ledger_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID)

    add("route present", route is not None, ROUTE_ID)
    if route is not None:
        add("route remains S3", route.get("authority_state") == "S3", f"authority_state={route.get('authority_state')}")
        add("route ceiling remains S3", route.get("promotion_ceiling") == "S3", f"promotion_ceiling={route.get('promotion_ceiling')}")
        add("route mirrors finite-N forecast", FORECAST_ID in route.get("forecast_ids", []), str(route.get("forecast_ids", [])))
        add("route mirrors finite-N delta", DELTA_ID in route.get("empirical_delta_ids", []), str(route.get("empirical_delta_ids", [])))
        add("route mirrors finite-N decision", DECISION_ID in route.get("decision_experiment_ids", []), str(route.get("decision_experiment_ids", [])))

    add("forecast present", forecast is not None, FORECAST_ID)
    if forecast is not None:
        add("forecast route-local", forecast.get("route_id") == ROUTE_ID, f"route_id={forecast.get('route_id')}")
        add("forecast current credit capped at S3", forecast.get("current_maximum_credit") == "S3", f"current_maximum_credit={forecast.get('current_maximum_credit')}")
        add("forecast carries finite-N refs", not missing_source_refs(forecast, REQUIRED_REFS), f"missing={missing_source_refs(forecast, REQUIRED_REFS)}")
        req = _semantic_text(forecast.get("required_public_record", ""))
        forecast_concepts = {
            "finite-n": ["finite-n"],
            "backreaction": ["backreaction"],
            "island": ["island"],
            "error": ["error", "remainder norm"],
            "full-system": ["full-system"],
            "subregion": ["subregion"],
            "sector-inflow": ["sector-inflow", "center inflow", "incoming sector flux"],
            "factor-block": ["factor-block"],
            "modular-frame": ["modular-frame"],
            "fixed carrier": ["fixed carrier"],
            "target-algebra": ["target-algebra", "target algebra"],
            "epsilon-sub-tr": ["epsilon-sub-tr"],
            "epsilon-OD": ["eps-od", "epsilon-od"],
            "dominant block": ["dominant block", "dominant-block"],
            "worst-sector": ["worst-sector"],
            "coherent-sector": ["coherent-sector", "coherent sector"],
            "diamond/cb": ["diamond/cb", "diamond norm", "cb norm", "cb-norm"],
            "external reference": ["external reference", "reference/ancilla", "reference system"],
            "code/reference dimension": ["code dimension", "d-code", "d code", "reference growth"],
            "replay": ["replay"],
        }
        for label, alternatives in forecast_concepts.items():
            add(
                f"forecast names {label} denominator",
                _contains_any(req, alternatives),
                forecast.get("required_public_record", ""),
            )

    add("empirical delta present", delta is not None, DELTA_ID)
    if delta is not None:
        add("delta route-local", delta.get("route_ids") == [ROUTE_ID], f"route_ids={delta.get('route_ids')}")
        add("delta ceiling capped at S3", delta.get("promotion_ceiling") == "S3", f"promotion_ceiling={delta.get('promotion_ceiling')}")
        add("delta carries finite-N refs", not missing_source_refs(delta, REQUIRED_REFS), f"missing={missing_source_refs(delta, REQUIRED_REFS)}")
        add("delta hooks evidence unit", EVIDENCE_ID in delta.get("evidence_unit_ids", []), str(delta.get("evidence_unit_ids", [])))
        residual = str(delta.get("residual_cap", "")).lower()
        add("delta residual blocks acquired evidence", "no acquired evidence" in residual, delta.get("residual_cap", ""))

    add("decision present", decision is not None, DECISION_ID)
    if decision is not None:
        add("decision route-local", decision.get("route_ids") == [ROUTE_ID], f"route_ids={decision.get('route_ids')}")
        add("decision hooks finite-N delta", DELTA_ID in decision.get("empirical_delta_hooks", []), str(decision.get("empirical_delta_hooks", [])))
        add("decision carries finite-N refs", not missing_source_refs(decision, REQUIRED_REFS), f"missing={missing_source_refs(decision, REQUIRED_REFS)}")
        ceilings = [item.get("promotion_ceiling") for item in decision.get("outcome_effects", []) if isinstance(item, dict)]
        add("decision outcomes do not exceed S3", all(c in {"S1", "S2", "S3"} for c in ceilings), f"ceilings={ceilings}")
        add("decision excludes learned-inverse route", "R-OQ0057-FAMILYC-LEARNED-INVERSE" not in decision.get("route_ids", []), str(decision.get("route_ids", [])))
        decision_record = _semantic_text(
            str(decision.get("public_record", ""))
            + " "
            + str(decision.get("minimum_public_artifact", ""))
        )
        decision_concepts = {
            "full-system": ["full-system"],
            "subregion": ["subregion"],
            "appendix-c": ["appendix-c"],
            "lemma-4": ["lemma-4"],
            "sector-inflow": ["sector-inflow", "center inflow", "incoming sector flux"],
            "factor-block": ["factor-block", "factor geometry"],
            "modular-frame": ["modular-frame", "modular frame"],
            "fixed carrier": ["fixed carrier"],
            "target algebra": ["target algebra", "target-algebra"],
            "epsilon-sub-tr": ["epsilon-sub-tr"],
            "epsilon-OD": ["epsilon-od", "eps-od"],
            "dominant-block": ["dominant-block", "dominant block"],
            "worst-sector": ["worst-sector"],
            "coherent-sector": ["coherent-sector", "coherent sector"],
            "diamond/cb": ["diamond/cb", "diamond norm", "cb norm", "cb-norm"],
            "external reference": ["external reference", "reference/ancilla", "reference system"],
            "code/reference dimension": ["code dimension", "d-code", "d code", "reference growth"],
            "coherence/quotient boundary": ["coherence", "oaqec", "target algebra"],
        }
        for label, alternatives in decision_concepts.items():
            add(
                f"decision names {label} proof obligation",
                _contains_any(decision_record, alternatives),
                decision_record,
            )

    add("evidence unit present", evidence is not None, EVIDENCE_ID)
    if evidence is not None:
        add("evidence unit reciprocally hooks delta", DELTA_ID in evidence.get("empirical_delta_ids", []), str(evidence.get("empirical_delta_ids", [])))
        leaked = [ref for ref in REQUIRED_REFS if ref in evidence.get("source_refs", [])]
        add("fresh refs absent from acquired evidence unit", not leaked, f"leaked_refs={leaked}")
        add("evidence credit remains S3", evidence.get("maximum_credit") == "S3", f"maximum_credit={evidence.get('maximum_credit')}")

    for file_name, collection, id_field, row_id, refs in CONTROL_ROWS:
        row = find_ledger_row(root, file_name, collection, id_field, row_id)
        add(f"control row present {row_id}", row is not None, file_name)
        if row is not None:
            add(f"control row route-local {row_id}", ROUTE_ID in row.get("route_ids", []), f"route_ids={row.get('route_ids')}")
            add(f"control row carries expected refs {row_id}", not missing_source_refs(row, refs), f"missing={missing_source_refs(row, refs)}")
            if row_id == "DCF-0001-FAMILYC-EW-CODE":
                decoder_contract = _semantic_text(
                    str(row.get("denominator_rule", ""))
                    + " "
                    + str(row.get("residual_gap", ""))
                )
                decoder_concepts = {
                    "epsilon-sub-tr": ["epsilon-sub-tr"],
                    "epsilon-OD": ["epsilon-od", "eps-od"],
                    "dominant blocks": ["dominant blocks", "dominant-block"],
                    "worst-sector": ["worst-sector", "one bad sector"],
                    "coherent": ["coherent"],
                    "diamond/cb": ["diamond/cb", "diamond norm", "cb norm", "cb-norm"],
                    "external reference": ["external reference", "reference/ancilla", "reference system"],
                    "code dimension": ["code dimension", "d-code", "d code"],
                }
                for label, alternatives in decoder_concepts.items():
                    add(
                        f"decoder row names {label} source-routing obligation",
                        _contains_any(decoder_contract, alternatives),
                        decoder_contract,
                    )

    return {
        "audit_file": GENERATED_AUDIT,
        "checks": checks,
        "failures": failures,
        "required_refs": REQUIRED_REFS,
        "control_rows_checked": len(CONTROL_ROWS),
    }


def write_familyc_finite_n_reconstruction_audit(root: Path) -> None:
    result = evaluate_familyc_finite_n_reconstruction(root)
    lines = [
        "# FamilyC finite-N / QEC / island decoder source-role audit (generated)",
        "",
        "Generated from route, forecast, empirical-delta, decision, evidence-unit, and FamilyC route-control ledgers. Do not edit directly; run `make index` after changing finite-N/interior-QEC/island custody.",
        "",
        f"- Required finite-N / island refs: `{', '.join(result['required_refs'])}`",
        f"- Checks run: `{len(result['checks'])}`",
        f"- Route-control rows checked: `{result['control_rows_checked']}`",
        f"- FamilyC finite-N source-role failures: `{len(result['failures'])}`",
        "",
        "## Failure details",
        "",
    ]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Check summary",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check.get("detail", "")).replace("|", "\\|")
        lines.append(f"| {check['label']} | `{str(check['passed']).lower()}` | {detail} |")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Finite-N, black-hole-interior QEC, modular-Krylov/island-area, and massless-island sources are route-local pressure only. They cannot enter acquired evidence-unit source credit, exceed S3, or license observed-sector / ToE identity language.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_familyc_finite_n_reconstruction_audit(root)
    outcome = evaluate_familyc_finite_n_reconstruction(root)
    if outcome["failures"]:
        print("FAMILYC FINITE-N RECONSTRUCTION POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("FAMILYC FINITE-N RECONSTRUCTION POLICY OK")
