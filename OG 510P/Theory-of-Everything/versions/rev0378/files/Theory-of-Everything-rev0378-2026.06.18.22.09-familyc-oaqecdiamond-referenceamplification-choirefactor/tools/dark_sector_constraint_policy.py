#!/usr/bin/env python3
"""Dark-sector / direct-detection denominator source-role checks.

Current dark-matter, axion, and sterile-neutrino search limits are broad
observed-cosmology denominators. They tighten what any route may say about dark
matter or hidden sectors, but they are not acquired evidence-unit support for a
ToE candidate and they do not identify the dark sector.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/dark-sector-constraint-source-role-audit.generated.md"
BASE_DARK_SECTOR_REF = "REF-0404"
CURRENT_DARK_SECTOR_REFS = ["REF-0706", "REF-0707", "REF-0708", "REF-0709"]
REQUIRED_DARK_SECTOR_REFS = [BASE_DARK_SECTOR_REF] + CURRENT_DARK_SECTOR_REFS
WRAPPER_TOKEN = "METADATA-PROVENANCE-WRAPPER"
S_LEVEL = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5}
LEDGER_SPECS = [
    (
        "VACUUM-ENERGY-LEDGER.json",
        "vacuum_energy_rows",
        "vacuum_energy_id",
        ["dark_matter_or_dark_sector_gap", "forbidden_inference", "dark_sector_constraint_credit_rule"],
    ),
    (
        "COSMOLOGICAL-BACKGROUND-LEDGER.json",
        "background_rows",
        "cosmological_background_id",
        ["parameterization_or_initial_condition_gap", "public_record_or_inference_gap", "forbidden_inference", "dark_sector_constraint_credit_rule"],
    ),
    (
        "THERMAL-HISTORY-LEDGER.json",
        "thermal_history_rows",
        "thermal_history_id",
        ["structure_formation_or_growth_gap", "timing_or_observed_abundance_gap", "forbidden_inference", "dark_sector_constraint_credit_rule"],
    ),
]


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def route_ids_for_row(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key, val in row.items():
        if "route" not in key:
            continue
        if isinstance(val, str) and val.startswith("R-"):
            out.append(val)
        elif isinstance(val, list):
            out.extend(item for item in val if isinstance(item, str) and item.startswith("R-"))
    dedup: list[str] = []
    for rid in out:
        if rid not in dedup:
            dedup.append(rid)
    return dedup


def duplicate_refs(row: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    dup: list[str] = []
    for ref in row.get("source_refs", []) or []:
        if ref in seen and ref not in dup:
            dup.append(ref)
        seen.add(ref)
    return dup


def text_terms(row: dict[str, Any], keys: list[str]) -> str:
    parts: list[str] = []
    for key in keys:
        val = row.get(key)
        if isinstance(val, str):
            parts.append(val)
        elif isinstance(val, list):
            parts.extend(str(x) for x in val)
        elif isinstance(val, dict):
            parts.extend(str(x) for x in val.values())
    return " ".join(parts).lower()


def all_evidence_unit_refs(root: Path) -> dict[str, list[str]]:
    rows = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])
    return {row.get("evidence_unit_id", "<missing>"): list(row.get("source_refs", []) or []) for row in rows if isinstance(row, dict)}


def row_identifier(row: dict[str, Any], id_field: str) -> str:
    return str(row.get(id_field, "<missing>"))


def is_wrapper_row(row_id: str) -> bool:
    return WRAPPER_TOKEN in row_id


def evaluate_dark_sector_constraint(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    ledger_summaries: list[dict[str, Any]] = []

    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    routes = {row.get("route_id"): row for row in route_rows if isinstance(row, dict) and isinstance(row.get("route_id"), str)}
    route_ceiling = {rid: row.get("promotion_ceiling") or row.get("authority_state") for rid, row in routes.items()}

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    add("route-count-unchanged", len(route_rows) == 13, f"route_rows={len(route_rows)}")

    acquired_ref_hits: list[str] = []
    for eu_id, refs in all_evidence_unit_refs(root).items():
        bad = [ref for ref in CURRENT_DARK_SECTOR_REFS if ref in refs]
        if bad:
            acquired_ref_hits.append(f"{eu_id}:{','.join(bad)}")
    add("current-dark-sector-refs-not-acquired-evidence", not acquired_ref_hits, f"hits={acquired_ref_hits}")

    total_rows = 0
    route_bearing_rows = 0
    wrapper_rows = 0
    route_specific_rows = 0

    for rel, collection, id_field, language_keys in LEDGER_SPECS:
        rows = load_json(root, rel).get(collection, [])
        ledger_failures_before = len(failures)
        for row in rows:
            if not isinstance(row, dict):
                continue
            total_rows += 1
            row_id = row_identifier(row, id_field)
            routes_for_row = route_ids_for_row(row)
            refs = row.get("source_refs", []) or []
            dup = duplicate_refs(row)
            add(f"dark-sector-source-refs-deduped-{row_id}", not dup, f"duplicate_refs={dup}")
            if routes_for_row:
                route_bearing_rows += 1
            present_current_refs = [ref for ref in CURRENT_DARK_SECTOR_REFS if ref in refs]

            if is_wrapper_row(row_id):
                wrapper_rows += 1
                add(f"dark-sector-wrapper-no-current-refs-{row_id}", not present_current_refs, f"present_current_refs={present_current_refs}")
                continue

            route_specific_rows += 1
            missing = [ref for ref in REQUIRED_DARK_SECTOR_REFS if ref not in refs]
            add(f"dark-sector-current-refs-present-{row_id}", not missing, f"missing_refs={missing}")
            add(f"dark-sector-row-route-cardinality-{row_id}", len(routes_for_row) == 1, f"routes={routes_for_row}")

            effect = row.get("maximum_authority_effect")
            for rid in routes_for_row:
                ceiling = route_ceiling.get(rid)
                passed = effect in S_LEVEL and ceiling in S_LEVEL and S_LEVEL[effect] <= S_LEVEL[ceiling]
                add(f"dark-sector-row-ceiling-{row_id}-{rid}", passed, f"effect={effect}; route_ceiling={ceiling}")

            role = row.get("dark_sector_constraint_credit_role")
            cap = row.get("dark_sector_constraint_credit_cap")
            rule = row.get("dark_sector_constraint_credit_rule")
            add(f"dark-sector-credit-role-{row_id}", role == "denominator-control-only", f"role={role}")
            add(f"dark-sector-credit-cap-S0-{row_id}", cap == "S0", f"cap={cap}")
            add(f"dark-sector-credit-rule-present-{row_id}", isinstance(rule, str) and "not" in rule.lower() and "identify" in rule.lower(), f"rule={rule}")

            text = text_terms(row, language_keys)
            required_terms = ["dark", "matter", "not"]
            missing_terms = [term for term in required_terms if term not in text]
            add(f"dark-sector-denominator-language-{row_id}", not missing_terms, f"missing_terms={missing_terms}")
        ledger_summaries.append({"ledger_file": rel, "rows": len(rows), "failures": len(failures) - ledger_failures_before})

    # Current dark-sector refs are broad denominator refs, but they may live only
    # on the cosmology/vacuum/thermal denominator ledgers and freshness policy.
    misplaced: list[str] = []
    allowed_files = {spec[0] for spec in LEDGER_SPECS} | {"FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json"}
    for path in sorted(root.glob("*.json")):
        if path.name in allowed_files:
            continue
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue

        def walk(x: Any) -> bool:
            if isinstance(x, dict):
                return any(walk(v) for v in x.values())
            if isinstance(x, list):
                return any(walk(v) for v in x)
            return isinstance(x, str) and x in CURRENT_DARK_SECTOR_REFS

        if walk(obj):
            misplaced.append(path.name)
    add("current-dark-sector-refs-only-in-denominator-ledgers", not misplaced, f"misplaced_files={misplaced}")

    return {
        "audit_file": GENERATED_AUDIT,
        "checks": checks,
        "failures": failures,
        "ledger_summaries": ledger_summaries,
        "route_count": len(route_rows),
        "current_refs": CURRENT_DARK_SECTOR_REFS,
        "route_bearing_rows": route_bearing_rows,
        "route_specific_rows": route_specific_rows,
        "wrapper_rows": wrapper_rows,
        "total_rows": total_rows,
    }


def write_dark_sector_constraint_audit(root: Path) -> None:
    result = evaluate_dark_sector_constraint(root)
    lines = [
        "# Dark-sector constraint source-role audit (generated)",
        "",
        "Generated from current dark-sector source custody and cosmology/vacuum/thermal denominator ledgers. Do not edit directly; run `make index` after changing dark-sector source-role rows.",
        "",
        f"- Route rows: `{result['route_count']}`",
        f"- Current dark-sector refs: `{', '.join(result['current_refs'])}`",
        f"- Route-bearing denominator rows checked: `{result['route_bearing_rows']}`",
        f"- Route-specific denominator rows checked: `{result['route_specific_rows']}`",
        f"- Metadata-wrapper rows checked: `{result['wrapper_rows']}`",
        f"- Dark-sector checks: `{len(result['checks'])}`",
        f"- Dark-sector failures: `{len(result['failures'])}`",
        "",
        "## Ledger summary",
        "",
        "| Ledger | Rows | Failures |",
        "|---|---:|---:|",
    ]
    for row in result["ledger_summaries"]:
        lines.append(f"| `{row['ledger_file']}` | `{row['rows']}` | `{row['failures']}` |")
    lines += ["", "## Failure details", ""]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Current LZ/XENONnT/KATRIN/ADMX dark-sector refs are denominator pressure only. They constrain dark-matter, axion-like, sterile-sector, and hidden-sector wording, but they do not identify dark matter, solve vacuum energy, or increase any route's authority state.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_dark_sector_constraint_audit(root)
    outcome = evaluate_dark_sector_constraint(root)
    if outcome["failures"]:
        print("DARK SECTOR CONSTRAINT POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("DARK SECTOR CONSTRAINT POLICY OK")
