#!/usr/bin/env python3
"""Route-condition credit ceiling checks, including multi-route rows.

A condition, support, forecast, decision, delta, evidence, or claim-binding row
may pressure a route, but the row must not be spendable above that route's own
ceiling.  Earlier revisions checked only single-route rows and counted multi-
route rows as intentionally excluded.  That was a real loophole: a family-level
S3 row naming S1/S2 routes could later be read as route-local authority.

This policy now accepts multi-route S-level rows only when they carry an
explicit `route_authority_ceilings` map.  The row-level S-field is treated as a
family-level envelope; the map is the route-spendable cap.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/route-condition-ceiling-audit.generated.md"
S_LEVEL_RE = re.compile(r"^S([0-5])$")
AUTHORITY_FIELDS = (
    "maximum_authority_effect",
    "maximum_credit",
    "current_maximum_credit",
    "promotion_ceiling",
    "maximum_authority_credit",
    "maximum_route_effect",
    "maximum_credit_if_passed",
    "realist_status_ceiling",
    "current_update_ceiling",
    "current_authority_state",
    "conditional_authority_ceiling",
)


def iter_authority_field_levels(value: Any, path: str = "") -> list[tuple[str, str, int, str]]:
    """Return S-level authority fields from a JSON row, including nested clauses.

    Decision experiments often carry conditional `outcome_effects`; treating only
    the row top level as spendable authority left a loophole where a nested
    `promotion_ceiling` could exceed the named route ceiling.
    """
    found: list[tuple[str, str, int, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in AUTHORITY_FIELDS:
                level = s_level(child)
                if level is not None:
                    found.append((child_path, key, level, str(child)))
            found.extend(iter_authority_field_levels(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]" if path else f"[{index}]"
            found.extend(iter_authority_field_levels(child, child_path))
    return found


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def s_level(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    m = S_LEVEL_RE.match(value)
    return int(m.group(1)) if m else None


def row_id(row: dict[str, Any], fallback: str) -> str:
    preferred = [
        "route_id",
        "forecast_id",
        "delta_id",
        "experiment_id",
        "evidence_unit_id",
        "binding_id",
    ]
    for key in preferred:
        if key in row and isinstance(row[key], str):
            return row[key]
    for key, value in row.items():
        if key.endswith("_id") and isinstance(value, str):
            return value
    return fallback


def route_ids_for(row: dict[str, Any], known_routes: set[str]) -> list[str]:
    route_ids: list[str] = []
    route_id = row.get("route_id")
    if isinstance(route_id, str):
        route_ids.append(route_id)
    raw_many = row.get("route_ids")
    if isinstance(raw_many, list):
        route_ids.extend(item for item in raw_many if isinstance(item, str))
    return sorted({rid for rid in route_ids if rid in known_routes})


def iter_json_row_collections(root: Path):
    for path in sorted(root.glob("*.json")):
        if path.name in {"AUTHORITY-DEPENDENCY-GRAPH.json"}:
            continue
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for collection_name, value in data.items():
            if not isinstance(value, list):
                continue
            for index, row in enumerate(value):
                if isinstance(row, dict):
                    yield path.name, collection_name, index, row


def authority_field_levels(row: dict[str, Any]) -> dict[str, tuple[int, str]]:
    out: dict[str, tuple[int, str]] = {}
    for path, _field, level, raw_value in iter_authority_field_levels(row):
        out[path] = (level, raw_value)
    return out


def evaluate_route_condition_ceiling(root: Path) -> dict[str, Any]:
    route_ledger = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json")
    routes = {
        row.get("route_id"): row
        for row in route_ledger.get("route_rows", [])
        if isinstance(row, dict) and isinstance(row.get("route_id"), str)
    }
    route_caps = {rid: s_level(row.get("promotion_ceiling")) for rid, row in routes.items()}
    failures: list[str] = []
    checked_rows: list[dict[str, Any]] = []
    single_route_authority_fields = 0
    multi_route_authority_rows = 0
    multi_route_route_ceiling_checks = 0

    for file_name, collection, index, row in iter_json_row_collections(root):
        rids = route_ids_for(row, set(routes))
        if not rids:
            continue
        row_label = row_id(row, f"row-{index}")
        field_levels = authority_field_levels(row)
        if not field_levels:
            continue

        if len(rids) == 1:
            route_id = rids[0]
            route_cap = route_caps.get(route_id)
            if route_cap is None:
                continue
            for field, (level, raw_value) in field_levels.items():
                single_route_authority_fields += 1
                ok = level <= route_cap
                check = {
                    "file": file_name,
                    "collection": collection,
                    "row_id": row_label,
                    "route_id": route_id,
                    "field": field,
                    "row_value": raw_value,
                    "route_promotion_ceiling": routes[route_id].get("promotion_ceiling"),
                    "status": "pass" if ok else "fail",
                    "mode": "single-route-field",
                }
                checked_rows.append(check)
                if not ok:
                    failures.append(
                        f"{file_name}:{row_label} field `{field}` is `{raw_value}` but route `{route_id}` is capped at `{routes[route_id].get('promotion_ceiling')}`"
                    )
            continue

        # Multi-route rows must carry an explicit route-spendable ceiling map.
        multi_route_authority_rows += 1
        per_route = row.get("route_authority_ceilings")
        if not isinstance(per_route, dict):
            failures.append(f"{file_name}:{row_label} is multi-route with S-level fields but lacks `route_authority_ceilings`")
            continue
        missing = [rid for rid in rids if rid not in per_route]
        unknown = sorted(set(per_route) - set(rids))
        if missing:
            failures.append(f"{file_name}:{row_label} route_authority_ceilings missing routes {missing}")
        if unknown:
            failures.append(f"{file_name}:{row_label} route_authority_ceilings names non-row routes {unknown}")
        envelope_level = max(level for level, _raw in field_levels.values())
        for route_id in rids:
            route_cap = route_caps.get(route_id)
            value = per_route.get(route_id)
            level = s_level(value)
            multi_route_route_ceiling_checks += 1
            ok = level is not None and route_cap is not None and level <= route_cap and level <= envelope_level
            check = {
                "file": file_name,
                "collection": collection,
                "row_id": row_label,
                "route_id": route_id,
                "field": "route_authority_ceilings",
                "row_value": value,
                "route_promotion_ceiling": routes[route_id].get("promotion_ceiling"),
                "status": "pass" if ok else "fail",
                "mode": "multi-route-spendable-cap",
            }
            checked_rows.append(check)
            if level is None:
                failures.append(f"{file_name}:{row_label} route `{route_id}` has malformed route_authority_ceilings value `{value}`")
            elif route_cap is not None and level > route_cap:
                failures.append(
                    f"{file_name}:{row_label} route `{route_id}` spendable cap `{value}` exceeds route promotion ceiling `{routes[route_id].get('promotion_ceiling')}`"
                )
            elif level > envelope_level:
                failures.append(
                    f"{file_name}:{row_label} route `{route_id}` spendable cap `{value}` exceeds the row-level authority envelope"
                )

    return {
        "audit_file": GENERATED_AUDIT,
        "route_count": len(routes),
        "checked_authority_fields": len(checked_rows),
        "single_route_authority_fields": single_route_authority_fields,
        "multi_route_authority_rows": multi_route_authority_rows,
        "multi_route_route_ceiling_checks": multi_route_route_ceiling_checks,
        "checks": checked_rows,
        "failures": failures,
    }


def write_route_condition_ceiling_audit(root: Path) -> None:
    result = evaluate_route_condition_ceiling(root)
    from collections import Counter

    def field_name(path: str) -> str:
        return path.split(".")[-1]

    route_counts = Counter(check["route_id"] for check in result["checks"])
    route_failures = Counter(check["route_id"] for check in result["checks"] if check["status"] != "pass")
    field_counts = Counter(field_name(check["field"]) for check in result["checks"])
    field_failures = Counter(field_name(check["field"]) for check in result["checks"] if check["status"] != "pass")
    file_counts = Counter(check["file"] for check in result["checks"])
    file_failures = Counter(check["file"] for check in result["checks"] if check["status"] != "pass")

    lines = [
        "# Route-condition ceiling audit (generated)",
        "",
        "Generated from route-local and multi-route JSON rows. Do not edit directly; run `make index` after changing route caps or condition ledgers.",
        "",
        f"- Route rows: `{result['route_count']}`",
        f"- Authority ceiling checks: `{result['checked_authority_fields']}`",
        f"- Single-route authority fields checked: `{result['single_route_authority_fields']}`",
        f"- Multi-route authority rows checked: `{result['multi_route_authority_rows']}`",
        f"- Multi-route route-spendable cap checks: `{result['multi_route_route_ceiling_checks']}`",
        f"- Ceiling failures: `{len(result['failures'])}`",
        "",
        "## Rule",
        "",
        "A single-route support, condition, forecast, decision, delta, evidence, carrier, protocol, ontology, contrast, severity, or control row may not state a recognized S-level spendable-authority field above the named route's own `promotion_ceiling`, including nested conditional clauses such as `outcome_effects[*].promotion_ceiling`. A multi-route row with any S-level authority field must carry `route_authority_ceilings`; those per-route values are the only route-spendable caps and must not exceed either the row envelope or the route's own ceiling.",
        "",
        "## Authority fields covered",
        "",
        ", ".join(f"`{field}`" for field in AUTHORITY_FIELDS),
        "",
        "## Compact coverage",
        "",
        "The full PASS table is deliberately not retained: it was mostly audit exhaust. The evaluator still checks every field above; this generated surface retains route, authority-field, file summaries, and any failures.",
        "",
        "| Route | Checks | Failures |",
        "|---|---:|---:|",
    ]
    for route_id, count in sorted(route_counts.items()):
        lines.append(f"| `{route_id}` | `{count}` | `{route_failures.get(route_id, 0)}` |")
    lines += ["", "| Authority field | Checks | Failures |", "|---|---:|---:|"]
    for field, count in sorted(field_counts.items()):
        lines.append(f"| `{field}` | `{count}` | `{field_failures.get(field, 0)}` |")
    total_file_failures = sum(file_failures.values())
    top_files = sorted(file_counts.items(), key=lambda item: (-item[1], item[0]))[:12]
    lines += [
        "",
        "## File coverage summary",
        "",
        f"- Files with authority checks: `{len(file_counts)}`",
        f"- File-level failed checks: `{total_file_failures}`",
        "- Full per-file PASS rows are intentionally suppressed; failures, if any, are listed below.",
        "",
        "| Top file by check volume | Checks | Failures |",
        "|---|---:|---:|",
    ]
    for file_name, count in top_files:
        lines.append(f"| `{file_name}` | `{count}` | `{file_failures.get(file_name, 0)}` |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in result["failures"])
    lines += [
        "",
        "## Multi-route spend rule",
        "",
        "Multi-route rows can still express family-level constraints, but route-local promotion or credit may spend only the named route's `route_authority_ceilings` value. This closes no-lint gaps for multi-route authority rows without requiring the archive to clone every family-level row into thirteen separate ledgers.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_route_condition_ceiling_audit(root)
    outcome = evaluate_route_condition_ceiling(root)
    if outcome["failures"]:
        print("ROUTE CONDITION CEILING POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("ROUTE CONDITION CEILING POLICY OK")
