#!/usr/bin/env python3
"""Route-local source-role checks for the lab graviton-counting lane.

Classical gravitational-wave catalogs may supply source-trigger/timing custody
for proposed single-graviton experiments. LISA or mission-runway references must
not be spent as detector-local quantum-click or graviton-counting evidence.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/graviton-counting-source-role-audit.generated.md"
GRAVITON_ROUTE = "R-OQ0057-LAB-GRAVITON-COUNTING"
LISA_OR_RUNWAY_REFS = {"REF-0213", "REF-0214", "REF-0630", "REF-0631", "REF-0632"}
CLASSICAL_TRIGGER_REFS = {"REF-0218", "REF-0624", "REF-0625", "REF-0629"}
CORE_SINGLE_GRAVITON_REFS = {"REF-0175", "REF-0176", "REF-0647", "REF-0648"}
ALLOWED_TRIGGER_ROWS = {
    "PRC-GWOSC-STRAIN-CATALOG",
    "AP-SINGLE-GRAVITON-TRIGGER-CORRELATION",
    "DX-0013-GRAVITON-COUNTING-STATE-STATISTICS-CORRIDOR",
    "IA-0005-GW-WAVEFORM-DETECTOR-CATALOG-COVARIANCE",
}
REQUIRED_CORE_ROWS = {
    "EU-0011-GRAVITON-COUNTING",
    "PRC-GRAVITON-LAB-CATALOG",
    "AP-SINGLE-GRAVITON-TRIGGER-CORRELATION",
    "MM-0011-LAB-GRAVITON-COUNTING",
    "SYS-0011-LAB-GRAVITON-COUNTING",
    "CAL-0011-LAB-GRAVITON-COUNTING",
    "SV-0004-GRAVITON-COUNTING-SEVERITY",
    "CA-LAB-GRAVITON-COUNTING",
    "DX-0013-GRAVITON-COUNTING-STATE-STATISTICS-CORRIDOR",
    "ED-0006-SINGLE-GRAVITON-STIMULATED-ACCESS",
    "ED-0007-GRAVITON-COUNTING-STATE-TOMOGRAPHY",
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def row_identifier(row: dict[str, Any]) -> str:
    preferred = [
        "evidence_unit_id",
        "carrier_id",
        "protocol_id",
        "measurement_model_id",
        "systematic_id",
        "calibration_id",
        "severity_id",
        "credit_id",
        "experiment_id",
        "delta_id",
        "route_id",
        "defeater_id",
        "forecast_id",
        "id",
    ]
    for key in preferred:
        value = row.get(key)
        if isinstance(value, str):
            return value
    for key, value in row.items():
        if key.endswith("_id") and isinstance(value, str):
            return value
    return "<unidentified-row>"


def route_ids_for_row(row: dict[str, Any]) -> list[str]:
    routes: list[str] = []
    for key, val in row.items():
        if "route" not in key:
            continue
        if isinstance(val, str) and val.startswith("R-"):
            routes.append(val)
        elif isinstance(val, list):
            routes.extend(item for item in val if isinstance(item, str) and item.startswith("R-"))
    out: list[str] = []
    for rid in routes:
        if rid and rid not in out:
            out.append(rid)
    return out


def iter_graviton_route_rows(root: Path):
    for path in sorted(root.glob("*LEDGER.json")):
        try:
            data = load_json(root, path.name)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        for rows_key, rows in data.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                routes = route_ids_for_row(row)
                if GRAVITON_ROUTE not in routes:
                    continue
                refs = [ref for ref in row.get("source_refs", []) if isinstance(ref, str)]
                yield path.name, rows_key, row_identifier(row), routes, refs


def evaluate_graviton_source_role(root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    missing_core_rows: list[str] = []
    source_role_failures: list[dict[str, Any]] = []
    observed_required_rows: set[str] = set()

    for file_name, rows_key, rid, routes, refs in iter_graviton_route_rows(root):
        refset = set(refs)
        lisa_refs = sorted(refset & LISA_OR_RUNWAY_REFS)
        trigger_refs = sorted(refset & CLASSICAL_TRIGGER_REFS)
        core_refs = sorted(refset & CORE_SINGLE_GRAVITON_REFS)
        passed = True
        reasons: list[str] = []
        if rid in REQUIRED_CORE_ROWS:
            observed_required_rows.add(rid)
            if not core_refs:
                passed = False
                reasons.append("missing route-local single-graviton/graviton-detection source ref")
        if lisa_refs:
            passed = False
            reasons.append(f"LISA/runway refs on graviton-counting row: {', '.join(lisa_refs)}")
        if trigger_refs and rid not in ALLOWED_TRIGGER_ROWS:
            passed = False
            reasons.append(f"classical GW trigger refs on non-trigger graviton row: {', '.join(trigger_refs)}")
        item = {
            "file": file_name,
            "rows_key": rows_key,
            "row_id": rid,
            "routes": routes,
            "core_refs": core_refs,
            "trigger_refs": trigger_refs,
            "lisa_or_runway_refs": lisa_refs,
            "passed": passed,
            "reasons": reasons,
        }
        rows.append(item)
        if not passed:
            source_role_failures.append(item)
            failures.append(f"{file_name}:{rid}: {'; '.join(reasons)}")

    for rid in sorted(REQUIRED_CORE_ROWS - observed_required_rows):
        missing_core_rows.append(rid)
        failures.append(f"missing required graviton-counting row under route fields: {rid}")

    return {
        "audit_file": GENERATED_AUDIT,
        "required_core_rows": len(REQUIRED_CORE_ROWS),
        "missing_core_rows": missing_core_rows,
        "placements": rows,
        "failures": failures,
        "source_role_failures": source_role_failures,
    }


def write_graviton_source_role_audit(root: Path) -> None:
    result = evaluate_graviton_source_role(root)
    rows = sorted(result["placements"], key=lambda x: (x["file"], x["row_id"]))
    displayed_rows = [
        item for item in rows
        if item["core_refs"]
        or item["trigger_refs"]
        or item["lisa_or_runway_refs"]
        or not item["passed"]
        or item["row_id"] in REQUIRED_CORE_ROWS
    ]
    suppressed_empty_pass_rows = len(rows) - len(displayed_rows)
    lines = [
        "# Graviton-counting source-role audit (generated)",
        "",
        "Generated from route-bearing `*LEDGER.json` rows for `R-OQ0057-LAB-GRAVITON-COUNTING`. Do not edit directly; run `make index` after changing graviton-counting source custody.",
        "",
        f"- Required core single-graviton rows: `{result['required_core_rows']}`",
        f"- Missing core single-graviton rows: `{len(result['missing_core_rows'])}`",
        f"- Source-role placements checked: `{len(rows)}`",
        f"- Source-role placements displayed: `{len(displayed_rows)}`",
        f"- Empty/pass placements suppressed: `{suppressed_empty_pass_rows}`",
        f"- Source-role failures: `{len(result['failures'])}`",
        "",
        "## Display policy",
        "",
        "The full executable check still scans every route-bearing row. This generated restart surface displays only rows with core single-graviton refs, classical trigger refs, LISA/runway refs, failures, or required core-row status, because hundreds of empty passing route rows added noise without changing custody semantics.",
        "",
        "| Row | Core single-graviton refs | Classical trigger refs | LISA/runway refs | Passed |",
        "|---|---|---|---|---:|",
    ]
    for item in displayed_rows:
        row = f"`{item['file']}:{item['row_id']}`"
        core = ", ".join(f"`{ref}`" for ref in item["core_refs"]) or "—"
        trigger = ", ".join(f"`{ref}`" for ref in item["trigger_refs"]) or "—"
        lisa = ", ".join(f"`{ref}`" for ref in item["lisa_or_runway_refs"]) or "—"
        lines.append(f"| {row} | {core} | {trigger} | {lisa} | `{str(item['passed']).lower()}` |")
    lines += [
        "",
        "## Source-role rule",
        "",
        "Classical gravitational-wave catalogs may act as source-trigger/timing carriers only on explicitly trigger-bearing rows. LISA mission, construction, or hardware-runway refs must not be spent as detector-local single-graviton/click evidence for the lab graviton-counting route.",
        "",
        "## Non-promotion rule",
        "",
        "This audit creates no new support. It preserves the distinction between trigger covariance, detector-local transition/count evidence, and ToE-candidate identity.",
        "",
    ]
    if result["failures"]:
        lines += ["## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_graviton_source_role_audit(root)
    outcome = evaluate_graviton_source_role(root)
    if outcome["failures"]:
        print("GRAVITON SOURCE ROLE FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("GRAVITON SOURCE ROLE OK")
