#!/usr/bin/env python3
"""Executable checks for current-vs-conditional claim-language authority.

Some routes legitimately retain a higher *promotion ceiling* than their current
state.  That ceiling must not leak into current prose.  This policy keeps claim
language rows honest: a conditional ceiling can be named only with explicit
current-state, conditional-trigger, and non-promotion qualifiers.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/claim-language-current-boundary-audit.generated.md"
S_LEVEL_RE = re.compile(r"^S([0-5])$")


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def s_level(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    m = S_LEVEL_RE.match(value)
    return int(m.group(1)) if m else None


def row_text(row: dict[str, Any], fields: list[str]) -> str:
    values = [row.get(field) for field in fields]
    return json.dumps(values, ensure_ascii=False).lower()


def evaluate_claim_language_current_boundary(root: Path) -> dict[str, Any]:
    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    routes = {
        row.get("route_id"): row
        for row in route_rows
        if isinstance(row, dict) and isinstance(row.get("route_id"), str)
    }
    permission_rows = load_json(root, "CLAIM-LANGUAGE-PERMISSION-LEDGER.json").get("permission_rows", [])

    failures: list[str] = []
    checks: list[dict[str, Any]] = []
    conditional_rows = 0
    route_specific_rows = 0
    multi_route_rows = 0

    def record(language_id: str, route_id: str, check: str, ok: bool, detail: str) -> None:
        checks.append({
            "language_permission_id": language_id,
            "route_id": route_id,
            "check": check,
            "status": "pass" if ok else "fail",
            "detail": detail,
        })
        if not ok:
            failures.append(f"{language_id}:{route_id}:{check}: {detail}")

    for row in permission_rows:
        if not isinstance(row, dict):
            continue
        language_id = str(row.get("language_permission_id", "<missing>"))
        route_ids = [rid for rid in row.get("route_ids", []) if isinstance(rid, str) and rid in routes]
        if not route_ids:
            continue
        if len(route_ids) > 1:
            multi_route_rows += 1
            # Metadata/provenance wrapper rows can list many routes but cannot spend
            # claim language as route evidence.  The route-condition ceiling policy
            # checks their per-route caps; here we only block explicit route-current
            # wording from multi-route wrappers.
            text = row_text(row, ["allowed_language", "required_context", "required_qualifiers", "ceiling_spend_rule"])
            mentions_current_s = bool(re.search(r"current\s+s[0-5]", text))
            record(language_id, "<multi-route>", "multi-route-wrapper-does-not-state-current-S-language", not mentions_current_s, "multi-route claim-language rows must remain custody/index language only")
            continue
        route_specific_rows += 1
        route_id = route_ids[0]
        route = routes[route_id]
        current = route.get("authority_state")
        ceiling = route.get("promotion_ceiling")
        current_level = s_level(current)
        ceiling_level = s_level(ceiling)
        max_effect = row.get("maximum_authority_effect")
        max_level = s_level(max_effect)
        text = row_text(row, ["allowed_language", "required_context", "required_qualifiers", "ceiling_spend_rule", "forbidden_language"])
        allowed_text = row_text(row, ["allowed_language"])
        context_text = row_text(row, ["required_context", "required_qualifiers", "ceiling_spend_rule"])
        forbidden_text = row_text(row, ["forbidden_language"])

        record(language_id, route_id, "maximum-effect-not-above-route-ceiling", max_level is not None and ceiling_level is not None and max_level <= ceiling_level, f"maximum_authority_effect={max_effect}; route ceiling={ceiling}")
        record(language_id, route_id, "route-id-mentioned", route_id.lower() in json.dumps(row, ensure_ascii=False).lower(), "row must name its route id")

        if current_level is None or ceiling_level is None:
            record(language_id, route_id, "route-S-fields-parse", False, f"current={current}; ceiling={ceiling}")
            continue

        if current_level < ceiling_level:
            conditional_rows += 1
            current_phrase = f"current {str(current).lower()}"
            conditional_phrase = f"conditional {str(ceiling).lower()}"
            unqualified_phrase = f"unqualified {str(ceiling).lower()} current"
            record(language_id, route_id, "declares-current-authority-state", row.get("current_authority_state") == current, f"current_authority_state={row.get('current_authority_state')}; route current={current}")
            record(language_id, route_id, "declares-conditional-ceiling", row.get("conditional_authority_ceiling") == ceiling, f"conditional_authority_ceiling={row.get('conditional_authority_ceiling')}; route ceiling={ceiling}")
            qualifiers = row.get("required_qualifiers", [])
            record(language_id, route_id, "required-qualifiers-present", isinstance(qualifiers, list) and bool(qualifiers), "conditional rows must carry explicit required_qualifiers")
            record(language_id, route_id, "allowed-language-names-current-state", current_phrase in text, f"must contain `{current_phrase}`")
            record(language_id, route_id, "conditional-ceiling-is-explicitly-conditional", conditional_phrase in text, f"must contain `{conditional_phrase}`")
            record(language_id, route_id, "required-context-mentions-current-and-conditional", current_phrase in context_text and ((conditional_phrase in context_text) or ("conditional" in context_text and str(ceiling).lower() in context_text)), "required_context/qualifiers/spend rule must say current-vs-conditional")
            record(language_id, route_id, "forbids-unqualified-current-ceiling", unqualified_phrase in forbidden_text, f"forbidden_language must contain `{unqualified_phrase}`")
            record(language_id, route_id, "no-bare-maximum-ceiling-language", f"maximum `{str(ceiling).lower()}` wording" not in allowed_text, "allowed_language must not use bare maximum-ceiling wording for conditional routes")
        else:
            # Non-conditional rows may use maximum/current wording, but their max
            # effect must equal the current route state if they present a spendable
            # route-local permission.
            record(language_id, route_id, "nonconditional-current-equals-ceiling", current_level == ceiling_level, f"current={current}; ceiling={ceiling}")
            record(language_id, route_id, "maximum-effect-not-above-current", max_level is not None and max_level <= current_level, f"maximum_authority_effect={max_effect}; route current={current}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_rows": len(routes),
        "claim_language_rows": len(permission_rows),
        "route_specific_rows": route_specific_rows,
        "conditional_current_boundary_rows": conditional_rows,
        "multi_route_rows": multi_route_rows,
        "checks": checks,
        "failures": failures,
    }


def write_claim_language_current_boundary_audit(root: Path) -> None:
    result = evaluate_claim_language_current_boundary(root)
    lines = [
        "# Claim-language current-boundary audit (generated)",
        "",
        "Generated from `CLAIM-LANGUAGE-PERMISSION-LEDGER.json` and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit directly; run `make index` after changing claim-language rows.",
        "",
        f"- Route rows: `{result['route_rows']}`",
        f"- Claim-language rows: `{result['claim_language_rows']}`",
        f"- Route-specific claim-language rows checked: `{result['route_specific_rows']}`",
        f"- Conditional current-boundary rows checked: `{result['conditional_current_boundary_rows']}`",
        f"- Multi-route claim-language rows checked: `{result['multi_route_rows']}`",
        f"- Claim-language current-boundary failures: `{len(result['failures'])}`",
        "",
        "## Rule",
        "",
        "A route with `authority_state` below `promotion_ceiling` may name the higher ceiling only as conditional future language. Its claim-language permission row must declare the current state, declare the conditional ceiling, include current-vs-conditional qualifiers, forbid unqualified current use of the higher ceiling, and avoid bare `maximum S# wording` phrasing.",
        "",
    ]
    if result["failures"]:
        lines += ["## Failures", ""]
        lines += [f"- {failure}" for failure in result["failures"]]
    else:
        lines += ["## Failures", "", "None."]
    lines += ["", "## Checked rows", "", "| language permission | route | checks | failures |", "|---|---:|---:|---:|"]
    summary: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for check in result["checks"]:
        key = (check["language_permission_id"], check["route_id"])
        summary.setdefault(key, []).append(check)
    for (language_id, route_id), entries in sorted(summary.items()):
        fail_count = sum(1 for entry in entries if entry["status"] != "pass")
        lines.append(f"| `{language_id}` | `{route_id}` | `{len(entries)}` | `{fail_count}` |")
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = evaluate_claim_language_current_boundary(root)
    if result["failures"]:
        print("CLAIM-LANGUAGE CURRENT-BOUNDARY FAILURES")
        for failure in result["failures"]:
            print(f"- {failure}")
        sys.exit(1)
    print("CLAIM-LANGUAGE CURRENT-BOUNDARY OK")
