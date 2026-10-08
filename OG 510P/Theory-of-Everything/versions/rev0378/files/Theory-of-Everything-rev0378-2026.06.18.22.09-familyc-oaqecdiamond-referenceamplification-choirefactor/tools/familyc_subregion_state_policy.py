#!/usr/bin/env python3
"""FamilyC subregion-state portability/source-role policy.

The strongest live route is useful only if new subregion/gravitating-region
state work becomes route-facing pressure without being mis-spent as acquired
evidence.  This check keeps that distinction executable.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from source_role_event_utils import find_ledger_row, missing_source_refs

GENERATED_AUDIT = "docs/30-program/familyc-subregion-state-portability-audit.generated.md"
ROUTE_ID = "R-OQ0057-FAMILYC-EW-CODE"
FORECAST_ID = "DF-0015-FAMILYC-SUBREGION-STATE-DICTIONARY-PORTABILITY"
DELTA_ID = "ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE"
DECISION_ID = "DX-0006-FAMILYC-PUBLIC-RECONSTRUCTION-BENCHMARK"
EVIDENCE_ID = "EU-0001-FAMILYC-EW-RECONSTRUCTION"
REQUIRED_REFS = ["REF-0649", "REF-0650"]


def evaluate_familyc_subregion_state(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    route = find_ledger_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", ROUTE_ID)
    forecast = find_ledger_row(root, "DISCRIMINATOR-FORECAST-LEDGER.json", "forecast_rows", "forecast_id", FORECAST_ID)
    delta = find_ledger_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", DELTA_ID)
    decision = find_ledger_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", DECISION_ID)
    evidence = find_ledger_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", EVIDENCE_ID)

    def add(label: str, passed: bool, detail: str) -> None:
        checks.append({"label": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    add("route present", route is not None, ROUTE_ID)
    if route is not None:
        add("route authority remains bounded S3", route.get("authority_state") == "S3", f"authority_state={route.get('authority_state')}")
        add("route ceiling remains S3", route.get("promotion_ceiling") == "S3", f"promotion_ceiling={route.get('promotion_ceiling')}")

    add("forecast present", forecast is not None, FORECAST_ID)
    if forecast is not None:
        add("forecast route-local", forecast.get("route_id") == ROUTE_ID, f"route_id={forecast.get('route_id')}")
        add("forecast current credit bounded", forecast.get("current_maximum_credit") == "S3", f"current_maximum_credit={forecast.get('current_maximum_credit')}")
        missing = missing_source_refs(forecast, REQUIRED_REFS)
        add("forecast carries current source refs", not missing, f"missing={missing}")
        add("forecast non-promotion language present", "not" in str(forecast.get("non_promotion_warning", "")).lower(), forecast.get("non_promotion_warning", ""))

    add("empirical delta present", delta is not None, DELTA_ID)
    if delta is not None:
        add("delta route-local", delta.get("route_ids") == [ROUTE_ID], f"route_ids={delta.get('route_ids')}")
        add("delta ceiling bounded", delta.get("promotion_ceiling") == "S3", f"promotion_ceiling={delta.get('promotion_ceiling')}")
        missing = missing_source_refs(delta, REQUIRED_REFS)
        add("delta carries current source refs", not missing, f"missing={missing}")
        residual = str(delta.get("residual_cap", "")).lower()
        add("delta residual blocks acquired-evidence overclaim", "acquired" in residual and "witness" in residual, delta.get("residual_cap", ""))

    add("decision row present", decision is not None, DECISION_ID)
    if decision is not None:
        hooks = decision.get("empirical_delta_hooks", [])
        add("decision hooks new delta", DELTA_ID in hooks, f"empirical_delta_hooks={hooks}")
        decision_refs = decision.get("source_refs", [])
        leaked = [ref for ref in REQUIRED_REFS if ref in decision_refs]
        add("multi-route decision avoids fresh source bleed", not leaked, f"leaked_refs={leaked}")

    add("evidence unit present", evidence is not None, EVIDENCE_ID)
    if evidence is not None:
        evidence_refs = evidence.get("source_refs", [])
        leaked = [ref for ref in REQUIRED_REFS if ref in evidence_refs]
        add("fresh theory refs absent from acquired evidence unit", not leaked, f"leaked_refs={leaked}")
        add("evidence maximum credit remains S3", evidence.get("maximum_credit") == "S3", f"maximum_credit={evidence.get('maximum_credit')}")

    return {
        "audit_file": GENERATED_AUDIT,
        "checks": checks,
        "failures": failures,
        "required_refs": REQUIRED_REFS,
    }


def write_familyc_subregion_state_audit(root: Path) -> None:
    result = evaluate_familyc_subregion_state(root)
    lines = [
        "# FamilyC subregion-state portability audit (generated)",
        "",
        "Generated from route, forecast, empirical-delta, decision-experiment, and evidence-unit ledgers. Do not edit directly; run `make index` after changing FamilyC subregion-state portability custody.",
        "",
        f"- Required current theory refs: `{', '.join(result['required_refs'])}`",
        f"- Checks run: `{len(result['checks'])}`",
        f"- Subregion-state portability failures: `{len(result['failures'])}`",
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
        "This audit allows new gravitating-region/subregion-state work to pressure the S3 FamilyC route, but prevents the same references from being carried as acquired evidence-unit support. It promotes no route.",
        "",
    ]
    if result["failures"]:
        lines += ["## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_familyc_subregion_state_audit(root)
    outcome = evaluate_familyc_subregion_state(root)
    if outcome["failures"]:
        print("FAMILYC SUBREGION STATE POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("FAMILYC SUBREGION STATE POLICY OK")
