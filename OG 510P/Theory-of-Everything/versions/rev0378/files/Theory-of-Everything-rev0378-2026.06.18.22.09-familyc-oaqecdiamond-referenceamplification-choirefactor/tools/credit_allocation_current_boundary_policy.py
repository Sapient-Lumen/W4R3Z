#!/usr/bin/env python3
"""Executable checks for credit-allocation current-vs-conditional authority.

Route-ceiling and claim-language policies already prevent many authority leaks,
but credit-allocation rows are where route-local evidence units are aggregated.
For routes whose promotion ceiling exceeds current authority, those rows must not
state the higher ceiling as present credit.  The higher ceiling may be retained
only as an explicitly conditional future pocket with a named trigger.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/credit-allocation-current-boundary-audit.generated.md"
S_LEVEL_RE = re.compile(r"^S([0-5])$")


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def s_level(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    m = S_LEVEL_RE.match(value)
    return int(m.group(1)) if m else None


def text_of(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).lower()


def evaluate_credit_allocation_current_boundary(root: Path) -> dict[str, Any]:
    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    routes = {
        row.get("route_id"): row
        for row in route_rows
        if isinstance(row, dict) and isinstance(row.get("route_id"), str)
    }
    credit_rows = load_json(root, "CREDIT-ALLOCATION-LEDGER.json").get("credit_rows", [])

    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    conditional_rows = 0

    def record(credit_id: str, route_id: str, check: str, ok: bool, detail: str) -> None:
        checks.append({
            "credit_id": credit_id,
            "route_id": route_id,
            "check": check,
            "status": "pass" if ok else "fail",
            "detail": detail,
        })
        if not ok:
            failures.append(f"{credit_id}:{route_id}:{check}: {detail}")

    for row in credit_rows:
        if not isinstance(row, dict):
            continue
        credit_id = str(row.get("credit_id", "<missing>"))
        route_id = str(row.get("route_id", "<missing>"))
        route = routes.get(route_id)
        record(credit_id, route_id, "route-present", route is not None, f"route_id={route_id}")
        if route is None:
            continue
        current = route.get("authority_state")
        ceiling = route.get("promotion_ceiling")
        max_effect = row.get("maximum_authority_effect")
        current_level = s_level(current)
        ceiling_level = s_level(ceiling)
        max_level = s_level(max_effect)
        basis = str(row.get("current_credit_basis", ""))
        basis_l = basis.lower()
        row_l = text_of(row)
        current_phrase = f"current route authority remains `{str(current).lower()}`"
        bare_ceiling_current_phrase = f"current route authority remains `{str(ceiling).lower()}`"
        conditional_phrase = f"conditional `{str(ceiling).lower()}`"

        record(credit_id, route_id, "S-fields-parse", current_level is not None and ceiling_level is not None and max_level is not None, f"current={current}; ceiling={ceiling}; max={max_effect}")
        if current_level is None or ceiling_level is None or max_level is None:
            continue
        record(credit_id, route_id, "maximum-effect-not-above-route-ceiling", max_level <= ceiling_level, f"maximum_authority_effect={max_effect}; route ceiling={ceiling}")
        record(credit_id, route_id, "basis-names-current-route-authority", current_phrase in basis_l, f"basis must contain `{current_phrase}`")
        record(credit_id, route_id, "basis-does-not-state-higher-current-authority", not (current_level < ceiling_level and bare_ceiling_current_phrase in basis_l), f"basis must not contain `{bare_ceiling_current_phrase}`")

        if current_level < ceiling_level:
            conditional_rows += 1
            if max_level > current_level:
                record(credit_id, route_id, "declares-current-credit-state", row.get("current_credit_state") == current, f"current_credit_state={row.get('current_credit_state')}; route current={current}")
                record(credit_id, route_id, "declares-conditional-authority-ceiling", row.get("conditional_authority_ceiling") == ceiling, f"conditional_authority_ceiling={row.get('conditional_authority_ceiling')}; route ceiling={ceiling}")
                record(credit_id, route_id, "basis-marks-ceiling-conditional", conditional_phrase in basis_l, f"basis must contain `{conditional_phrase}`")
                trigger = row.get("conditional_trigger")
                trigger_l = str(trigger).lower()
                trigger_ok = isinstance(trigger, str) and "future" in trigger_l and ("public" in trigger_l or "record" in trigger_l)
                record(credit_id, route_id, "conditional-trigger-is-public-record-like", trigger_ok, f"conditional_trigger={trigger!r}")
                unqualified_forbidden = "unqualified" in row_l and str(ceiling).lower() in row_l and "current" in row_l
                record(credit_id, route_id, "forbids-unqualified-current-ceiling", unqualified_forbidden, "row must visibly forbid unqualified current use of the conditional ceiling")
            else:
                record(credit_id, route_id, "current-only-row-does-not-need-conditional-trigger", max_level <= current_level, f"maximum_authority_effect={max_effect}; route current={current}")
        else:
            record(credit_id, route_id, "nonconditional-max-not-above-current", max_level <= current_level, f"maximum_authority_effect={max_effect}; current={current}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_rows": len(routes),
        "credit_rows": len(credit_rows),
        "conditional_route_credit_rows": conditional_rows,
        "checks": checks,
        "failures": failures,
    }


def write_credit_allocation_current_boundary_audit(root: Path) -> None:
    result = evaluate_credit_allocation_current_boundary(root)
    lines = [
        "# Credit-allocation current-boundary audit (generated)",
        "",
        "Generated from `CREDIT-ALLOCATION-LEDGER.json` and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit directly; run `make index` after changing credit allocation rows.",
        "",
        f"- Route rows: `{result['route_rows']}`",
        f"- Credit rows: `{result['credit_rows']}`",
        f"- Conditional-route credit rows checked: `{result['conditional_route_credit_rows']}`",
        f"- Credit-allocation current-boundary checks: `{len(result['checks'])}`",
        f"- Credit-allocation current-boundary failures: `{len(result['failures'])}`",
        "",
        "## Rule",
        "",
        "Credit allocation rows aggregate evidence units, so their prose must name the route's current authority state. A row may retain a higher conditional ceiling only with explicit `current_credit_state`, `conditional_authority_ceiling`, and `conditional_trigger` fields and with text forbidding unqualified current use of the higher ceiling.",
        "",
    ]
    if result["failures"]:
        lines += ["## Failures", ""]
        lines += [f"- {failure}" for failure in result["failures"]]
    else:
        lines += ["## Failures", "", "None."]
    lines += ["", "## Checked rows", "", "| credit row | route | checks | failures |", "|---|---:|---:|---:|"]
    by_row: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for check in result["checks"]:
        by_row.setdefault((check["credit_id"], check["route_id"]), []).append(check)
    for (credit_id, route_id), entries in sorted(by_row.items()):
        fail_count = sum(1 for entry in entries if entry["status"] != "pass")
        lines.append(f"| `{credit_id}` | `{route_id}` | `{len(entries)}` | `{fail_count}` |")
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = evaluate_credit_allocation_current_boundary(root)
    if result["failures"]:
        print("CREDIT-ALLOCATION CURRENT-BOUNDARY FAILURES")
        for failure in result["failures"]:
            print(f"- {failure}")
        sys.exit(1)
    print("CREDIT-ALLOCATION CURRENT-BOUNDARY OK")
