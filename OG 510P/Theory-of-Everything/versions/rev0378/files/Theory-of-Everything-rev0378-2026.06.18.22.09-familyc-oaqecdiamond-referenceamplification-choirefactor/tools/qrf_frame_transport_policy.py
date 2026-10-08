#!/usr/bin/env python3
"""Check QRF frame-transport source role and cross-route handoff isolation.

The QRF/relational route can use frame-switching, crossed-product, boundary,
and large-gauge papers as route-local S2 pressure.  Those sources must not be
spent as acquired evidence-unit support, and FamilyC-only subregion-state
pressure must not hang off the QRF evidence unit.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/qrf-frame-transport-source-role-audit.generated.md"
QRF_ROUTE = "R-OQ0057-FRAME-QRF-RELATIONAL"
QRF_EVIDENCE = "EU-0010-QRF-FRAME-TRANSPORT"
QRF_DELTA = "ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE"
FAMILYC_SUBREGION_DELTA = "ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE"
QRF_FORECAST = "DF-0011-QRF-RELATIONAL-PUBLIC-WITNESS-PORTABILITY"
QRF_DECISION = "DX-0012-QRF-PUBLIC-WITNESS-PORTABILITY-ASSAY"
NEW_QRF_REFS = ["REF-0679", "REF-0680"]
BASE_QRF_REFS = ["REF-0120", "REF-0197", "REF-0206", "REF-0207"]
REQUIRED_QRF_PRESSURE_REFS = BASE_QRF_REFS + NEW_QRF_REFS
FORBIDDEN_EVIDENCE_REFS = ["REF-0649", "REF-0650", "REF-0679", "REF-0680"]

CONTROL_ROWS = [
    ("ACQUISITION-PROTOCOL-LEDGER.json", "protocol_rows", "protocol_id", "AP-REFERENCE-FRAME-TRANSPORT-ASSAY"),
    ("OBSERVABLE-QUOTIENT-LEDGER.json", "observable_rows", "observable_quotient_id", "OBSQ-0010-FRAME-QRF-RELATIONAL"),
    ("GAUGE-SYMMETRY-LEDGER.json", "gauge_rows", "gauge_symmetry_id", "GSY-0010-FRAME-QRF-RELATIONAL"),
    ("ALGEBRAIC-LOCALITY-LEDGER.json", "algebraic_rows", "algebraic_locality_id", "ALG-0010-FRAME-QRF-RELATIONAL"),
    ("EDGE-MODE-CENTER-LEDGER.json", "edge_mode_rows", "edge_mode_center_id", "EDG-0010-FRAME-QRF-RELATIONAL"),
    ("SUBSYSTEM-FACTORIZATION-LEDGER.json", "factorization_rows", "subsystem_factorization_id", "FAC-0010-FRAME-QRF-RELATIONAL"),
    ("TRANSPORTABILITY-LEDGER.json", "transport_rows", "transport_id", "TR-0010-FRAME-QRF-RELATIONAL"),
]


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(root: Path, ledger_file: str, row_collection: str, id_field: str, row_id: str) -> dict[str, Any] | None:
    data = load_json(root, ledger_file)
    rows = data.get(row_collection, [])
    if not isinstance(rows, list):
        return None
    return next((row for row in rows if isinstance(row, dict) and row.get(id_field) == row_id), None)


def refs_missing(row: dict[str, Any] | None, refs: list[str]) -> list[str]:
    present = row.get("source_refs", []) if isinstance(row, dict) else []
    return [ref for ref in refs if ref not in present]


def refs_present(row: dict[str, Any] | None, refs: list[str]) -> list[str]:
    present = row.get("source_refs", []) if isinstance(row, dict) else []
    return [ref for ref in refs if ref in present]


def collect_qrf_like_list_values(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key, val in row.items():
        if isinstance(val, list):
            for item in val:
                if isinstance(item, str) and (item == QRF_ROUTE or item == QRF_EVIDENCE or "FRAME-QRF" in item):
                    out.append(f"{key}:{item}")
    return out


def evaluate_qrf_frame_transport(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    route = find_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", QRF_ROUTE)
    forecast = find_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", QRF_FORECAST)
    decision = find_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", QRF_DECISION)
    evidence = find_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", QRF_EVIDENCE)
    qrf_delta = find_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", QRF_DELTA)
    familyc_delta = find_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", FAMILYC_SUBREGION_DELTA)

    def add_check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    add_check("qrf-route-present", route is not None, "QRF route row exists")
    if route:
        add_check("qrf-route-authority-s2", route.get("authority_state") == "S2", f"authority_state={route.get('authority_state')}")
        add_check("qrf-route-ceiling-s2", route.get("promotion_ceiling") == "S2", f"promotion_ceiling={route.get('promotion_ceiling')}")

    add_check("qrf-delta-present", qrf_delta is not None, "route-local QRF delta exists")
    if qrf_delta:
        add_check("qrf-delta-route-local", qrf_delta.get("route_ids") == [QRF_ROUTE], f"route_ids={qrf_delta.get('route_ids')}")
        add_check("qrf-delta-evidence-link", QRF_EVIDENCE in (qrf_delta.get("evidence_unit_ids") or []), f"evidence_unit_ids={qrf_delta.get('evidence_unit_ids')}")
        add_check("qrf-delta-ceiling-s2", qrf_delta.get("promotion_ceiling") == "S2", f"promotion_ceiling={qrf_delta.get('promotion_ceiling')}")
        missing = refs_missing(qrf_delta, REQUIRED_QRF_PRESSURE_REFS)
        add_check("qrf-delta-current-source-refs", not missing, f"missing={missing}")

    if evidence:
        evidence_deltas = evidence.get("empirical_delta_ids") or []
        add_check("qrf-evidence-includes-qrf-delta", QRF_DELTA in evidence_deltas, f"empirical_delta_ids={evidence_deltas}")
        add_check("qrf-evidence-excludes-familyc-only-delta", FAMILYC_SUBREGION_DELTA not in evidence_deltas, f"empirical_delta_ids={evidence_deltas}")
        forbidden = refs_present(evidence, FORBIDDEN_EVIDENCE_REFS)
        add_check("qrf-evidence-new-refs-not-acquired-credit", not forbidden, f"forbidden_present={forbidden}")
    else:
        add_check("qrf-evidence-present", False, "QRF evidence unit missing")

    if familyc_delta:
        add_check("familyc-delta-excludes-qrf-route", QRF_ROUTE not in (familyc_delta.get("route_ids") or []), f"route_ids={familyc_delta.get('route_ids')}")
        add_check("familyc-delta-excludes-qrf-evidence", QRF_EVIDENCE not in (familyc_delta.get("evidence_unit_ids") or []), f"evidence_unit_ids={familyc_delta.get('evidence_unit_ids')}")
        leaked = collect_qrf_like_list_values(familyc_delta)
        add_check("familyc-delta-excludes-qrf-control-handles", not leaked, f"leaked={leaked[:8]}")
    else:
        add_check("familyc-delta-present", False, "FamilyC subregion-state delta missing")

    if forecast:
        missing = refs_missing(forecast, REQUIRED_QRF_PRESSURE_REFS)
        add_check("qrf-forecast-current-source-refs", not missing, f"missing={missing}")
    else:
        add_check("qrf-forecast-present", False, "QRF forecast missing")

    if decision:
        missing = refs_missing(decision, REQUIRED_QRF_PRESSURE_REFS)
        add_check("qrf-decision-current-source-refs", not missing, f"missing={missing}")
        hooks = decision.get("empirical_delta_hooks") or []
        add_check("qrf-decision-hooks-qrf-delta", QRF_DELTA in hooks, f"empirical_delta_hooks={hooks}")
    else:
        add_check("qrf-decision-present", False, "QRF decision row missing")

    control_results: list[dict[str, Any]] = []
    for ledger_file, row_collection, id_field, row_id in CONTROL_ROWS:
        row = find_row(root, ledger_file, row_collection, id_field, row_id)
        missing = refs_missing(row, NEW_QRF_REFS)
        passed = row is not None and not missing
        control_results.append({"ledger_file": ledger_file, "row_id": row_id, "missing_refs": missing, "passed": passed})
        add_check(f"control-row-current-refs-{row_id}", passed, f"missing={missing}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": QRF_ROUTE,
        "qrf_delta_id": QRF_DELTA,
        "familyc_delta_id": FAMILYC_SUBREGION_DELTA,
        "new_qrf_refs": NEW_QRF_REFS,
        "required_qrf_pressure_refs": REQUIRED_QRF_PRESSURE_REFS,
        "checks": checks,
        "control_results": control_results,
        "failures": failures,
    }


def write_qrf_frame_transport_audit(root: Path) -> None:
    result = evaluate_qrf_frame_transport(root)
    lines = [
        "# QRF frame-transport source-role audit (generated)",
        "",
        "Generated from QRF route, forecast, decision, empirical-delta, evidence-unit, and route-control rows. Do not edit directly; run `make index` after changing QRF frame-transport source custody.",
        "",
        f"- Route: `{result['route_id']}`",
        f"- QRF delta: `{result['qrf_delta_id']}`",
        f"- FamilyC-only delta fenced off: `{result['familyc_delta_id']}`",
        f"- Current QRF source refs: {', '.join(f'`{ref}`' for ref in result['new_qrf_refs'])}",
        f"- QRF source-role checks: `{len(result['checks'])}`",
        f"- QRF source-role failures: `{len(result['failures'])}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check.get("detail", "")).replace("|", "\\|")
        lines.append(f"| `{check.get('check')}` | `{str(check.get('passed')).lower()}` | {detail} |")
    lines += ["", "## Control rows", "", "| Ledger row | Missing current QRF refs | Passed |", "|---|---|---:|"]
    for item in result["control_results"]:
        missing = ", ".join(f"`{ref}`" for ref in item["missing_refs"]) or "—"
        lines.append(f"| `{item['ledger_file']}:{item['row_id']}` | {missing} | `{str(item['passed']).lower()}` |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "QRF, large-gauge, boundary/corner, and crossed-product sources are route-local S2 witness-portability pressure. They cannot be spent as FamilyC subregion-state support, acquired evidence-unit credit, observer-independent entropy closure, or ToE/candidate identity.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_qrf_frame_transport_audit(root)
    outcome = evaluate_qrf_frame_transport(root)
    if outcome["failures"]:
        print("QRF FRAME TRANSPORT POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("QRF FRAME TRANSPORT POLICY OK")
