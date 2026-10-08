#!/usr/bin/env python3
"""Forecast and future-record credit discipline.

A discriminator forecast is useful only if it cannot spend a future record as
current route authority.  This policy checks two high-risk failure modes:
forecast rows without source custody, and current forecast/evidence credit that
outruns the route's current authority state.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/forecast-credit-realization-audit.generated.md"
S_RANK = {f"S{i}": i for i in range(6)}
FUTURE_RECORD_STATUSES = {"forecast-public-record"}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def rank(state: Any) -> int:
    return S_RANK.get(str(state), -1)


def route_state_map(root: Path) -> dict[str, str]:
    rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    return {row.get("route_id", ""): row.get("authority_state", "") for row in rows if isinstance(row, dict)}


def evaluate_forecast_credit_realization(root: Path) -> dict[str, Any]:
    routes = route_state_map(root)
    forecasts = load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", [])
    evidence = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])
    failures: list[str] = []
    forecast_checks: list[dict[str, Any]] = []
    evidence_checks: list[dict[str, Any]] = []

    for row in forecasts:
        if not isinstance(row, dict):
            continue
        fid = row.get("forecast_id", "<missing-forecast-id>")
        route_id = row.get("route_id", "<missing-route>")
        route_state = routes.get(route_id, "<missing>")
        current_credit = row.get("current_maximum_credit", "<missing>")
        refs = [ref for ref in row.get("source_refs", []) if isinstance(ref, str)]
        source_ok = bool(refs)
        credit_ok = rank(current_credit) <= rank(route_state)
        item = {
            "forecast_id": fid,
            "route_id": route_id,
            "route_state": route_state,
            "current_maximum_credit": current_credit,
            "source_ref_count": len(refs),
            "source_ok": source_ok,
            "credit_ok": credit_ok,
        }
        forecast_checks.append(item)
        if not source_ok:
            failures.append(f"forecast {fid} has no source_refs")
        if not credit_ok:
            failures.append(f"forecast {fid} current_maximum_credit {current_credit} exceeds route {route_id} state {route_state}")

    for row in evidence:
        if not isinstance(row, dict):
            continue
        status = row.get("record_status")
        if status not in FUTURE_RECORD_STATUSES:
            continue
        eid = row.get("evidence_unit_id", "<missing-evidence-id>")
        current_credit = row.get("maximum_credit", "<missing>")
        route_ids = [rid for rid in row.get("route_ids", []) if isinstance(rid, str)]
        route_states = {rid: routes.get(rid, "<missing>") for rid in route_ids}
        credit_ok = all(rank(current_credit) <= rank(state) for state in route_states.values()) if route_states else False
        refs = [ref for ref in row.get("source_refs", []) if isinstance(ref, str)]
        item = {
            "evidence_unit_id": eid,
            "record_status": status,
            "route_states": route_states,
            "maximum_credit": current_credit,
            "source_ref_count": len(refs),
            "credit_ok": credit_ok,
        }
        evidence_checks.append(item)
        if not route_states:
            failures.append(f"forecast-public evidence {eid} has no route_ids")
        if not refs:
            failures.append(f"forecast-public evidence {eid} has no source_refs")
        if not credit_ok:
            failures.append(f"forecast-public evidence {eid} maximum_credit {current_credit} exceeds at least one current route state {route_states}")

    return {
        "audit_file": GENERATED_AUDIT,
        "forecast_checks": forecast_checks,
        "evidence_checks": evidence_checks,
        "forecast_rows": len(forecast_checks),
        "forecast_source_failures": sum(1 for item in forecast_checks if not item["source_ok"]),
        "forecast_credit_failures": sum(1 for item in forecast_checks if not item["credit_ok"]),
        "future_evidence_rows": len(evidence_checks),
        "future_evidence_credit_failures": sum(1 for item in evidence_checks if not item["credit_ok"]),
        "failures": failures,
    }


def write_forecast_credit_realization_audit(root: Path) -> None:
    result = evaluate_forecast_credit_realization(root)
    lines = [
        "# Forecast-credit realization audit (generated)",
        "",
        "Generated from `DISCRIMINATOR-FORECAST-LEDGER.json`, `EVIDENCE-UNIT-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit directly; run `make index` after changing forecast or future-record credit.",
        "",
        f"- Forecast rows checked: `{result['forecast_rows']}`",
        f"- Forecast source-ref failures: `{result['forecast_source_failures']}`",
        f"- Forecast current-credit failures: `{result['forecast_credit_failures']}`",
        f"- Forecast-public evidence rows checked: `{result['future_evidence_rows']}`",
        f"- Forecast-public evidence credit failures: `{result['future_evidence_credit_failures']}`",
        f"- Total forecast-credit realization failures: `{len(result['failures'])}`",
        "",
        "| Forecast | Route | Route state | Current maximum credit | Source refs | Source OK | Credit OK |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in result["forecast_checks"]:
        lines.append(
            f"| `{item['forecast_id']}` | `{item['route_id']}` | `{item['route_state']}` | `{item['current_maximum_credit']}` | `{item['source_ref_count']}` | `{str(item['source_ok']).lower()}` | `{str(item['credit_ok']).lower()}` |"
        )
    lines += [
        "",
        "| Forecast-public evidence | Routes | Maximum credit | Source refs | Credit OK |",
        "|---|---|---:|---:|---:|",
    ]
    for item in result["evidence_checks"]:
        route_text = ", ".join(f"`{rid}`→`{state}`" for rid, state in item["route_states"].items()) or "—"
        lines.append(
            f"| `{item['evidence_unit_id']}` | {route_text} | `{item['maximum_credit']}` | `{item['source_ref_count']}` | `{str(item['credit_ok']).lower()}` |"
        )
    lines += [
        "",
        "## Rule",
        "",
        "A forecast may describe conditional future credit, but `current_maximum_credit` and forecast-public evidence `maximum_credit` must not exceed the current route authority state. Every discriminator forecast must carry explicit source refs so source custody does not depend on indirectly traversing other ledgers.",
        "",
        "## Non-promotion rule",
        "",
        "This audit creates no support and promotes no route. It only prevents proposal, design, or future-record language from being spent as present authority.",
        "",
    ]
    if result["failures"]:
        lines += ["## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_forecast_credit_realization_audit(root)
    outcome = evaluate_forecast_credit_realization(root)
    if outcome["failures"]:
        print("FORECAST CREDIT REALIZATION FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("FORECAST CREDIT REALIZATION OK")
