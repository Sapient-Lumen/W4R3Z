#!/usr/bin/env python3
"""Negative-control route-overlap and route-mirror policy.

Negative controls are falsifiers, not portable decorations.  A decision,
severity row, evidence unit, or route row that spends a negative-control handle
must have route overlap with that control.  Otherwise a falsifier from one route
can silently become authority-shaping language in another route.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/negative-control-route-overlap-audit.generated.md"


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def route_ids_for_row(row: dict[str, Any]) -> set[str]:
    routes: set[str] = set()
    rid = row.get("route_id")
    if isinstance(rid, str) and rid.startswith("R-"):
        routes.add(rid)
    for rid in row.get("route_ids", []) or []:
        if isinstance(rid, str) and rid.startswith("R-"):
            routes.add(rid)
    ceilings = row.get("route_authority_ceilings")
    if isinstance(ceilings, dict):
        routes.update(str(key) for key in ceilings if str(key).startswith("R-"))
    return routes


def uniq_in_order(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if isinstance(item, str) and item not in out:
            out.append(item)
    return out


def evaluate_negative_control_route_overlap(root: Path) -> dict[str, Any]:
    controls = load_json(root, "NEGATIVE-CONTROL-LEDGER.json").get("controls", [])
    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    control_route = {row.get("control_id", ""): row.get("route_id", "") for row in controls if isinstance(row, dict)}
    controls_by_route: dict[str, list[str]] = defaultdict(list)
    for row in controls:
        if not isinstance(row, dict):
            continue
        cid = row.get("control_id", "")
        rid = row.get("route_id", "")
        if cid and rid:
            controls_by_route[rid].append(cid)

    failures: list[str] = []
    route_checks: list[dict[str, Any]] = []
    reference_checks: list[dict[str, Any]] = []
    seen_refs: set[tuple[str, str, str]] = set()

    def check_refs(surface: str, row_id: str, routes: set[str], ids: list[str]) -> None:
        for cid in ids:
            if not isinstance(cid, str):
                continue
            target_route = control_route.get(cid)
            passed = bool(target_route) and (not routes or target_route in routes)
            key = (surface, row_id, cid)
            if key in seen_refs:
                continue
            seen_refs.add(key)
            reference_checks.append({
                "surface": surface,
                "row_id": row_id,
                "control_id": cid,
                "row_routes": sorted(routes),
                "control_route": target_route or "<unknown>",
                "passed": passed,
            })
            if not target_route:
                failures.append(f"{surface} `{row_id}` references unknown negative control `{cid}`")
            elif routes and target_route not in routes:
                failures.append(f"{surface} `{row_id}` routes {sorted(routes)} reference negative control `{cid}` owned by `{target_route}`")

    for row in route_rows:
        if not isinstance(row, dict):
            continue
        rid = row.get("route_id", "<missing-route-id>")
        expected = uniq_in_order(controls_by_route.get(rid, []))
        mirrored = uniq_in_order(row.get("negative_control_ids", []) or [])
        adversarial = uniq_in_order(row.get("adversarial_countermodels", []) or [])
        mirror_passed = mirrored == expected
        adversarial_passed = set(adversarial).issubset(set(expected)) and bool(adversarial)
        route_checks.append({
            "route_id": rid,
            "expected_controls": expected,
            "negative_control_ids": mirrored,
            "adversarial_countermodels": adversarial,
            "mirror_passed": mirror_passed,
            "adversarial_passed": adversarial_passed,
        })
        if not mirror_passed:
            failures.append(f"route `{rid}` negative_control_ids expected {expected} but found {mirrored}")
        if not adversarial_passed:
            failures.append(f"route `{rid}` adversarial_countermodels must be nonempty and route-local subset of {expected}; found {adversarial}")
        check_refs("route.adversarial_countermodels", rid, {rid}, adversarial)
        check_refs("route.negative_control_ids", rid, {rid}, mirrored)

    surfaces = [
        ("decision", "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", "negative_controls"),
        ("severity", "EVIDENCE-SEVERITY-LEDGER.json", "severity_rows", "severity_id", "negative_control_ids"),
        ("evidence-unit", "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", "negative_control_ids"),
        ("defeater", "EPISTEMIC-DEFEATER-LEDGER.json", "defeater_rows", "defeater_id", "negative_control_ids"),
        ("contrast", "CONTRAST-CLASS-LEDGER.json", "contrast_rows", "contrast_class_id", "negative_control_ids"),
    ]
    for label, rel, rows_key, id_key, nc_key in surfaces:
        data = load_json(root, rel)
        for row in data.get(rows_key, []) or []:
            if not isinstance(row, dict):
                continue
            ids = uniq_in_order(row.get(nc_key, []) or [])
            if not ids:
                continue
            row_id = row.get(id_key, "<missing-row-id>")
            check_refs(label, row_id, route_ids_for_row(row), ids)

    referenced_controls = {check["control_id"] for check in reference_checks}
    orphan_controls = sorted(cid for cid in control_route if cid and cid not in referenced_controls)
    for cid in orphan_controls:
        failures.append(f"negative control `{cid}` is not referenced by any checked route/decision/severity/evidence/defeater/contrast row")

    cross_route_failures = [check for check in reference_checks if not check["passed"]]
    return {
        "audit_file": GENERATED_AUDIT,
        "control_rows": len(controls),
        "route_rows": len(route_rows),
        "route_checks": route_checks,
        "reference_checks": reference_checks,
        "cross_route_failures": cross_route_failures,
        "orphan_controls": orphan_controls,
        "failures": failures,
    }


def refs_text(items: list[str]) -> str:
    return ", ".join(f"`{item}`" for item in items) if items else "—"


def write_negative_control_route_overlap_audit(root: Path) -> None:
    result = evaluate_negative_control_route_overlap(root)
    lines = [
        "# Negative-control route-overlap audit (generated)",
        "",
        "Generated from `NEGATIVE-CONTROL-LEDGER.json`, route-state rows, and negative-control-bearing decision/severity/evidence/defeater/contrast rows. Do not edit directly; run `make index` after changing falsifier handles.",
        "",
        f"- Negative-control rows: `{result['control_rows']}`",
        f"- Route rows checked: `{result['route_rows']}`",
        f"- Route mirror checks: `{len(result['route_checks'])}`",
        f"- Negative-control references checked: `{len(result['reference_checks'])}`",
        f"- Cross-route negative-control failures: `{len(result['cross_route_failures'])}`",
        f"- Orphan negative controls: `{len(result['orphan_controls'])}`",
        f"- Negative-control route-overlap failures: `{len(result['failures'])}`",
        "",
        "## Route mirror summary",
        "",
        "| Route | Expected route-local controls | Mirrored controls | Adversarial controls | Mirror passed | Adversarial passed |",
        "|---|---|---|---|---:|---:|",
    ]
    for item in result["route_checks"]:
        lines.append(
            f"| `{item['route_id']}` | {refs_text(item['expected_controls'])} | {refs_text(item['negative_control_ids'])} | {refs_text(item['adversarial_countermodels'])} | `{str(item['mirror_passed']).lower()}` | `{str(item['adversarial_passed']).lower()}` |"
        )
    lines += ["", "## Failure details", ""]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("None.")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "This audit makes falsifier custody route-local and visible at the route head. It does not create support, relax a ceiling, or promote a route; failing a negative control can only cap, rollback, or quarantine the affected route-local claim path.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_negative_control_route_overlap_audit(root)
    outcome = evaluate_negative_control_route_overlap(root)
    if outcome["failures"]:
        print("NEGATIVE-CONTROL ROUTE-OVERLAP FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("NEGATIVE-CONTROL ROUTE-OVERLAP OK")
