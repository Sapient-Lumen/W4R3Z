#!/usr/bin/env python3
"""Route-state mirror checks for forecast/delta/decision pressure.

The route table is the operator-facing control surface.  Forecasts, empirical
pressure deltas, and decision experiments can be route-facing in their own
ledgers, but if the route row does not mirror those hooks the pressure becomes
easy to orphan during future edits.  This policy requires every route row to
carry exact mirror fields derived from the three executable pressure ledgers.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/route-pressure-mirror-audit.generated.md"
MIRROR_FIELDS = {
    "forecast_ids": ("DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id"),
    "empirical_delta_ids": ("EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id"),
    "decision_experiment_ids": ("DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id"),
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def uniq_sorted(items: list[str]) -> list[str]:
    return sorted(dict.fromkeys(item for item in items if isinstance(item, str)))


def expected_route_pressure(root: Path) -> dict[str, dict[str, list[str]]]:
    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    expected: dict[str, dict[str, list[str]]] = {
        row.get("route_id", "<missing-route-id>"): {field: [] for field in MIRROR_FIELDS}
        for row in route_rows
        if isinstance(row, dict)
    }

    forecasts = load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", [])
    for row in forecasts:
        if not isinstance(row, dict):
            continue
        fid = row.get("forecast_id")
        routes: list[str] = []
        if isinstance(row.get("route_id"), str):
            routes.append(row["route_id"])
        routes.extend(rid for rid in row.get("route_ids", []) if isinstance(rid, str))
        for rid in routes:
            expected.setdefault(rid, {field: [] for field in MIRROR_FIELDS})["forecast_ids"].append(fid)

    deltas = load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", [])
    for row in deltas:
        if not isinstance(row, dict):
            continue
        did = row.get("delta_id")
        for rid in row.get("route_ids", []):
            if isinstance(rid, str):
                expected.setdefault(rid, {field: [] for field in MIRROR_FIELDS})["empirical_delta_ids"].append(did)

    decisions = load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", [])
    for row in decisions:
        if not isinstance(row, dict):
            continue
        xid = row.get("experiment_id")
        for rid in row.get("route_ids", []):
            if isinstance(rid, str):
                expected.setdefault(rid, {field: [] for field in MIRROR_FIELDS})["decision_experiment_ids"].append(xid)

    for rid, fields in expected.items():
        for field, values in fields.items():
            fields[field] = uniq_sorted(values)
    return expected


def evaluate_route_pressure_mirror(root: Path) -> dict[str, Any]:
    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    expected = expected_route_pressure(root)
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    route_ids_in_rows = {row.get("route_id") for row in route_rows if isinstance(row, dict)}

    for rid in sorted(expected):
        if rid not in route_ids_in_rows:
            failures.append(f"pressure ledger references unknown route `{rid}`")
            checks.append({"route_id": rid, "field": "route-row", "expected": [], "actual": [], "passed": False})

    for row in route_rows:
        if not isinstance(row, dict):
            continue
        rid = row.get("route_id", "<missing-route-id>")
        expected_fields = expected.get(rid, {field: [] for field in MIRROR_FIELDS})
        for field in MIRROR_FIELDS:
            actual = row.get(field, [])
            if not isinstance(actual, list):
                actual_norm: list[str] = []
            else:
                actual_norm = uniq_sorted(actual)
            want = expected_fields.get(field, [])
            passed = actual_norm == want
            checks.append({"route_id": rid, "field": field, "expected": want, "actual": actual_norm, "passed": passed})
            if not passed:
                failures.append(f"{rid}.{field} expected {want} but found {actual_norm}")

    return {
        "audit_file": GENERATED_AUDIT,
        "routes_checked": len(route_rows),
        "mirror_fields": list(MIRROR_FIELDS),
        "checks": checks,
        "failures": failures,
    }


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def write_route_pressure_mirror_audit(root: Path) -> None:
    result = evaluate_route_pressure_mirror(root)
    lines = [
        "# Route pressure mirror audit (generated)",
        "",
        "Generated from `CANDIDATE-ROUTE-STATE-LEDGER.json`, `DISCRIMINATOR-FORECAST-LEDGER.json`, `EMPIRICAL-DELTA-LEDGER.json`, and `DECISION-EXPERIMENT-LEDGER.json`. Do not edit directly; run `make index` after changing route-facing pressure rows.",
        "",
        f"- Routes checked: `{result['routes_checked']}`",
        f"- Mirror fields checked per route: `{len(result['mirror_fields'])}`",
        f"- Route-pressure mirror checks: `{len(result['checks'])}`",
        f"- Route-pressure mirror failures: `{len(result['failures'])}`",
        "",
        "| Route | Field | Expected from pressure ledgers | Actual route-row mirror | Passed |",
        "|---|---|---|---|---:|",
    ]
    for check in result["checks"]:
        lines.append(
            f"| `{check['route_id']}` | `{check['field']}` | {refs_text(check['expected'])} | {refs_text(check['actual'])} | `{str(check['passed']).lower()}` |"
        )
    if result["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in result["failures"])
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Mirroring route-facing pressure into route-state rows makes live obligations visible at the route head. It does not change authority state, promote a route, or let a route spend pressure rows as independent evidence.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_route_pressure_mirror_audit(root)
    outcome = evaluate_route_pressure_mirror(root)
    if outcome["failures"]:
        print("ROUTE PRESSURE MIRROR FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("ROUTE PRESSURE MIRROR OK")
