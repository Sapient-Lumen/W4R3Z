#!/usr/bin/env python3
"""Executable realization-status checks for conditional laboratory routes.

Low-energy lab corridors are important, but they are also easy to overcredit:
a proposal, review, or trigger plan can be mistaken for a detector-local public
record.  This policy checks the two current conditional-S3 lab routes whose
present support is still bounded at S2: GIE/BMV and lab graviton counting.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/route-realization-status-audit.generated.md"

ROUTE_SPECS = [
    {
        "name": "lab-gie-bmv",
        "route_id": "R-OQ0057-LAB-GIE-BMV",
        "evidence_id": "EU-0008-LAB-GIE-MEDIATOR",
        "delta_id": "ED-0017-GIE-BMV-INFERENCE-SPLIT-PRESSURE",
        "decision_id": "DX-0001-DIRECT-GIE-BMV-ENTANGLEMENT",
        "severity_id": "SV-0003-DIRECT-GIE-BMV-SEVERITY",
        "language_id": "LPP-0008-LAB-GIE-BMV",
        "required_refs": ["REF-0643", "REF-0644", "REF-0645", "REF-0646"],
        "route_state": "S2",
        "route_ceiling": "S3",
        "evidence_status": "forecast-public-record",
        "evidence_credit": "S2",
        "route_residual_keywords": ["direct", "public"],
        "decision_public_artifact_keywords": ["calibrated", "controls"],
        "clean_outcome_keywords": ["conditional", "direct", "public"],
        "forbidden_language_keywords": ["entanglement by itself"],
        "extra_rows": [],
    },
    {
        "name": "lab-graviton-counting",
        "route_id": "R-OQ0057-LAB-GRAVITON-COUNTING",
        "evidence_id": "EU-0011-GRAVITON-COUNTING",
        "delta_id": "ED-0018-GRAVITON-REALIZATION-AND-QUANTIZATION-SPLIT-PRESSURE",
        "decision_id": "DX-0013-GRAVITON-COUNTING-STATE-STATISTICS-CORRIDOR",
        "severity_id": "SV-0004-GRAVITON-COUNTING-SEVERITY",
        "language_id": "LPP-0011-LAB-GRAVITON-COUNTING",
        "required_refs": ["REF-0175", "REF-0176", "REF-0647", "REF-0648"],
        "route_state": "S2",
        "route_ceiling": "S3",
        "evidence_status": "forecast-public-record",
        "evidence_credit": "S2",
        "route_residual_keywords": ["realized public", "no S4/S5"],
        "decision_public_artifact_keywords": ["trigger", "calibration", "background", "source-state", "detector-local"],
        "clean_outcome_keywords": ["conditional", "S3", "not full ToE"],
        "forbidden_language_keywords": ["single-graviton proposal proves quantization", "classical GW trigger catalog"],
        "extra_rows": [
            ("protocol", "ACQUISITION-PROTOCOL-LEDGER.json", "protocol_rows", "protocol_id", "AP-SINGLE-GRAVITON-TRIGGER-CORRELATION"),
            ("measurement", "MEASUREMENT-MODEL-LEDGER.json", "measurement_model_rows", "measurement_model_id", "MM-0011-LAB-GRAVITON-COUNTING"),
            ("calibration", "CALIBRATION-TRACEABILITY-LEDGER.json", "calibration_rows", "calibration_id", "CAL-0011-LAB-GRAVITON-COUNTING"),
        ],
    },
]


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(root: Path, rel: str, collection: str, id_field: str, row_id: str) -> dict[str, Any] | None:
    data = load_json(root, rel)
    rows = data.get(collection, [])
    if not isinstance(rows, list):
        return None
    return next((row for row in rows if isinstance(row, dict) and row.get(id_field) == row_id), None)


def missing_refs(row: dict[str, Any] | None, required_refs: list[str]) -> list[str]:
    refs = row.get("source_refs", []) if isinstance(row, dict) else []
    return [ref for ref in required_refs if ref not in refs]


def text_contains_all(value: Any, keywords: list[str]) -> bool:
    text = json.dumps(value, ensure_ascii=False).lower()
    return all(keyword.lower() in text for keyword in keywords)


def evaluate_route_realization_status(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    route_results: list[dict[str, Any]] = []

    for spec in ROUTE_SPECS:
        checks: list[tuple[str, bool, str]] = []
        route = find_row(root, "CANDIDATE-ROUTE-STATE-LEDGER.json", "route_rows", "route_id", spec["route_id"])
        evidence = find_row(root, "EVIDENCE-UNIT-LEDGER.json", "evidence_units", "evidence_unit_id", spec["evidence_id"])
        delta = find_row(root, "EMPIRICAL-DELTA-LEDGER.json", "empirical_deltas", "delta_id", spec["delta_id"])
        decision = find_row(root, "DECISION-EXPERIMENT-LEDGER.json", "decision_experiments", "experiment_id", spec["decision_id"])
        severity = find_row(root, "EVIDENCE-SEVERITY-LEDGER.json", "severity_rows", "severity_id", spec["severity_id"])
        language = find_row(root, "CLAIM-LANGUAGE-PERMISSION-LEDGER.json", "permission_rows", "language_permission_id", spec["language_id"])

        def record(name: str, ok: bool, detail: str) -> None:
            checks.append((name, ok, detail))
            if not ok:
                failures.append(f"{spec['name']}:{name}: {detail}")

        record("route-present", route is not None, f"missing route `{spec['route_id']}`")
        record("evidence-present", evidence is not None, f"missing evidence unit `{spec['evidence_id']}`")
        record("realization-delta-present", delta is not None, f"missing empirical delta `{spec['delta_id']}`")
        record("decision-present", decision is not None, f"missing decision row `{spec['decision_id']}`")
        record("severity-present", severity is not None, f"missing severity row `{spec['severity_id']}`")
        record("language-present", language is not None, f"missing claim-language row `{spec['language_id']}`")

        if route is not None:
            record("current-state-is-bounded", route.get("authority_state") == spec["route_state"], f"authority_state is `{route.get('authority_state')}`")
            record("conditional-ceiling-is-declared", route.get("promotion_ceiling") == spec["route_ceiling"], f"promotion_ceiling is `{route.get('promotion_ceiling')}`")
            record("route-residual-names-missing-record", text_contains_all(route.get("residual_cap", ""), spec["route_residual_keywords"]), f"residual_cap must contain {spec['route_residual_keywords']}")
        if evidence is not None:
            record("evidence-is-forecast-public", evidence.get("record_status") == spec["evidence_status"], f"record_status is `{evidence.get('record_status')}`")
            record("evidence-current-credit-is-bounded", evidence.get("maximum_credit") == spec["evidence_credit"], f"maximum_credit is `{evidence.get('maximum_credit')}`")
            record("evidence-carries-current-realization-refs", not missing_refs(evidence, spec["required_refs"]), f"missing refs {missing_refs(evidence, spec['required_refs'])}")
            record("evidence-links-realization-delta", spec["delta_id"] in evidence.get("empirical_delta_ids", []), f"{spec['delta_id']} missing from evidence empirical_delta_ids")
        if delta is not None:
            record("delta-route-bound", spec["route_id"] in delta.get("route_ids", []), f"{spec['route_id']} missing from delta route_ids")
            record("delta-carries-current-realization-refs", not missing_refs(delta, spec["required_refs"]), f"missing refs {missing_refs(delta, spec['required_refs'])}")
            record("delta-ceiling-is-conditional", delta.get("promotion_ceiling") == spec["route_ceiling"], f"promotion_ceiling is `{delta.get('promotion_ceiling')}`")
            record("delta-state-effect-caps-current-credit", text_contains_all(delta.get("state_effect", ""), [spec["route_state"], "future", "conditional"]), "state_effect must cap current credit and name conditional future record")
        if decision is not None:
            record("decision-carries-current-realization-refs", not missing_refs(decision, spec["required_refs"]), f"missing refs {missing_refs(decision, spec['required_refs'])}")
            record("decision-links-realization-delta", spec["delta_id"] in decision.get("empirical_delta_hooks", []), f"{spec['delta_id']} missing from decision empirical_delta_hooks")
            record("decision-minimum-artifact-is-detector-local", text_contains_all(decision.get("minimum_public_artifact", ""), spec["decision_public_artifact_keywords"]), f"minimum_public_artifact must contain {spec['decision_public_artifact_keywords']}")
            clean = next((item for item in decision.get("outcome_effects", []) if item.get("promotion_ceiling") == spec["route_ceiling"]), {})
            record("clean-outcome-is-conditional", text_contains_all(clean, spec["clean_outcome_keywords"]), f"clean outcome must contain {spec['clean_outcome_keywords']}")
        for label, row in [("severity", severity), ("language", language)]:
            if row is not None:
                record(f"{label}-carries-current-realization-refs", not missing_refs(row, spec["required_refs"]), f"missing refs {missing_refs(row, spec['required_refs'])}")
        if language is not None:
            record("language-forbids-proposal-as-proof", text_contains_all(language.get("forbidden_language", []), spec["forbidden_language_keywords"]), f"forbidden_language must contain {spec['forbidden_language_keywords']}")
        for label, rel, collection, id_field, row_id in spec.get("extra_rows", []):
            row = find_row(root, rel, collection, id_field, row_id)
            record(f"{label}-row-present", row is not None, f"missing {label} row `{row_id}`")
            if row is not None:
                record(f"{label}-carries-current-realization-refs", not missing_refs(row, spec["required_refs"]), f"missing refs {missing_refs(row, spec['required_refs'])}")

        route_results.append({
            "name": spec["name"],
            "route_id": spec["route_id"],
            "evidence_unit_id": spec["evidence_id"],
            "delta_id": spec["delta_id"],
            "required_refs": spec["required_refs"],
            "checks": [{"check": name, "passed": ok, "detail": detail} for name, ok, detail in checks],
            "route_state": route.get("authority_state") if route else "<missing>",
            "route_ceiling": route.get("promotion_ceiling") if route else "<missing>",
            "evidence_status": evidence.get("record_status") if evidence else "<missing>",
            "evidence_credit": evidence.get("maximum_credit") if evidence else "<missing>",
            "failures": [f for f in failures if f.startswith(spec["name"] + ":")],
        })

    return {
        "audit_file": GENERATED_AUDIT,
        "route_count": len(ROUTE_SPECS),
        "route_results": route_results,
        "checks": [check for result in route_results for check in result["checks"]],
        "failures": failures,
    }


def write_route_realization_status_audit(root: Path) -> None:
    result = evaluate_route_realization_status(root)
    lines = [
        "# Route realization-status audit (generated)",
        "",
        "Generated from route, evidence, empirical-delta, decision, severity, claim-language, and lab-control ledgers. Do not edit directly; run `make index` after changing realization-sensitive rows.",
        "",
        f"- Conditional lab routes checked: `{result['route_count']}`",
        f"- Realization-status checks: `{len(result['checks'])}`",
        f"- Realization-status failures: `{len(result['failures'])}`",
        "",
        "| Route | Current state | Conditional ceiling | Evidence status | Evidence credit | Checks | Failures |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for route in result["route_results"]:
        lines.append(
            f"| `{route['route_id']}` | `{route['route_state']}` | `{route['route_ceiling']}` | `{route['evidence_status']}` | `{route['evidence_credit']}` | `{len(route['checks'])}` | `{len(route['failures'])}` |"
        )
    for route in result["route_results"]:
        lines += [
            "",
            f"## {route['route_id']}",
            "",
            f"- Evidence unit: `{route['evidence_unit_id']}`",
            f"- Realization delta: `{route['delta_id']}`",
            "- Required current source refs: " + ", ".join(f"`{ref}`" for ref in route["required_refs"]),
            "",
            "| Check | Passed | Detail |",
            "|---|---:|---|",
        ]
        for check in route["checks"]:
            lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` | {check['detail']} |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    lines += [
        "",
        "## Rule",
        "",
        "A route whose direct detector-local public record is still unrealized may keep a conditional ceiling for a future clean record, but its current authority state and evidence unit must not spend that future result. For the lab GIE/BMV and lab graviton-counting lanes, current support remains proposal/review/feasibility/inference pressure (`S2`) until a direct acquired public record survives nuisance, subsystem, trigger, source-state, background, calibration, classical/hybrid, and model-class controls. This audit creates no support and promotes no route.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_route_realization_status_audit(root)
    result = evaluate_route_realization_status(root)
    if result["failures"]:
        print("ROUTE REALIZATION STATUS FAILED")
        for failure in result["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("ROUTE REALIZATION STATUS OK")
