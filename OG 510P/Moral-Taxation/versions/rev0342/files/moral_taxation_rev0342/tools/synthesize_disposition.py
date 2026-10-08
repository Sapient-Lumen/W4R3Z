#!/usr/bin/env python3
"""Synthesize ordered answer packets into a minimal final disposition.

The router finds relevant routes. The precedence resolver orders them. This
synthesizer turns the ordered, profile-backed packet into an auditable answer
shape: what is blocked, what default move is available, who must be assigned,
what cannot be finalized yet, and what quantitative/current-law checks remain.
It deliberately does not read case contracts or expected answers.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Sequence

RUNTIME_STATUS = "final_disposition_synthesizer_invoked"
DECISION_ADAPTER_RUNTIME_STATUS = "decision_adapter_requirements_resolved"
EVIDENCE_REQUEST_RUNTIME_STATUS = "evidence_producer_requests_planned"
RULE_VERSION = 1

REVENUE_OR_PRICE_ACTION_FAMILIES = {
    "tax_revenue_or_rent_capture",
    "user_fee_or_service_charge",
    "rebate_credit_or_compensation",
    "risk_prefunding_or_insurance_pool",
    "subsidy_procurement_or_public_upside",
}
ENFORCEMENT_ACTION_FAMILIES = {
    "penalty_liability_or_enforcement",
    "information_reporting_or_recordkeeping",
}


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_answer_case(tools_dir: pathlib.Path):
    spec = importlib.util.spec_from_file_location("answer_case", tools_dir / "answer_case.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load answer_case.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def load_decision_adapters(tools_dir: pathlib.Path):
    spec = importlib.util.spec_from_file_location("resolve_decision_adapters", tools_dir / "resolve_decision_adapters.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load resolve_decision_adapters.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def dedupe(values: Iterable[Any]) -> List[Any]:
    seen = set()
    out: List[Any] = []
    for value in values:
        if value in (None, "", [], {}):
            continue
        key = json.dumps(value, sort_keys=True, separators=(",", ":")) if isinstance(value, (dict, list)) else str(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def _route_by_id(selected_routes: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(route.get("route_id")): route for route in selected_routes}


def _route_order(selected_routes: Sequence[Dict[str, Any]], precedence_resolution: Dict[str, Any]) -> List[str]:
    ordered = [str(rid) for rid in precedence_resolution.get("ordered_route_ids", []) if rid]
    selected_ids = [str(route.get("route_id")) for route in selected_routes if route.get("route_id")]
    # If the resolver is absent or partial, preserve selected-route order but make that
    # absence visible through audit failures elsewhere.
    return ordered or selected_ids


def _dominant_disposition(precedence_resolution: Dict[str, Any], selected_routes: Sequence[Dict[str, Any]]) -> str:
    gate_names = {g.get("gate") for g in precedence_resolution.get("global_gates", [])}
    if "do_not_price_or_offset_no_go_harm_without_explicit_override" in gate_names:
        return "block_pricing_or_offset_until_no_go_harm_is_resolved"
    if "verify_currentness_before_final_answer" in gate_names:
        return "check_current_sources_before_final_answer"
    ordered = precedence_resolution.get("ordered_steps", [])
    if ordered:
        band = ordered[0].get("precedence_band")
        if band == 20:
            return "protect_floor_access_or_due_process_before_collection"
        if band == 30:
            return "assign_real_actor_controller_or_beneficiary_before_liability"
        if band == 40:
            return "settle_record_measurement_or_contestability_before_finality"
        if band == 50:
            return "apply_enforcement_only_after_floor_actor_and_contest_checks"
        if band == 60:
            return "ordinary_revenue_or_fee_classification_after_higher_order_gates"
        if band == 70:
            return "settle_proceeds_prefunding_or_public_upside_after_classification"
    families = {route.get("policy_action", {}).get("action_family") for route in selected_routes}
    if families & REVENUE_OR_PRICE_ACTION_FAMILIES:
        return "calibrate_revenue_or_compensation_after_gates"
    return "classify_and_apply_profile_default_moves_with_guardrails"


def synthesize_disposition(
    case: Dict[str, Any],
    selected_routes: Sequence[Dict[str, Any]],
    precedence_resolution: Dict[str, Any],
    blocked_shortcuts: Sequence[Any],
    default_moves: Sequence[Any],
    provenance_source_ids: Sequence[str],
    currentness_registry: Sequence[Dict[str, Any]] | None = None,
    as_of_date: str | None = None,
) -> Dict[str, Any]:
    ordered_ids = _route_order(selected_routes, precedence_resolution)
    routes = _route_by_id(selected_routes)
    ordered_routes = [routes[rid] for rid in ordered_ids if rid in routes]
    global_gates = precedence_resolution.get("global_gates", [])
    gate_names = {g.get("gate") for g in global_gates}

    gate_blocks: List[str] = []
    for gate in global_gates:
        name = gate.get("gate")
        reason = gate.get("reason")
        if name:
            gate_blocks.append(f"{name}: {reason}" if reason else str(name))

    hard_blocks = dedupe(
        list(case.get("must_not_answer", []))
        + list(blocked_shortcuts)
        + gate_blocks
    )

    default_moves_by_route = [
        {
            "route_id": route.get("route_id"),
            "default_move": route.get("remedy", {}).get("default_move"),
            "guardrails": route.get("remedy", {}).get("required_guardrails", []),
            "blocked_move": route.get("remedy", {}).get("blocked_move"),
            "precedence_band": route.get("precedence", {}).get("precedence_band"),
        }
        for route in ordered_routes
    ]

    actor_assignments = [
        {
            "route_id": route.get("route_id"),
            "primary_accountable_actor": route.get("accountability", {}).get("primary_accountable_actor"),
            "burden_bearers": route.get("accountability", {}).get("burden_bearers", []),
            "beneficiary_or_rent_recipient": route.get("accountability", {}).get("beneficiary_or_rent_recipient"),
            "evidence_required": route.get("accountability", {}).get("evidence_required", []),
        }
        for route in ordered_routes
    ]

    currentness_checks = []
    for gate in global_gates:
        if gate.get("gate") == "verify_currentness_before_final_answer":
            for sid in gate.get("source_ids", []):
                currentness_checks.append({
                    "source_id": sid,
                    "check": "refresh source-currentness registry entry before final advice or implementation",
                    "reason": gate.get("reason"),
                })
    for route in ordered_routes:
        for claim in route.get("provenance", {}).get("source_currentness_claims", []):
            sid = claim.get("source_id")
            if not sid:
                continue
            currentness_checks.append({
                "route_id": route.get("route_id"),
                "source_id": sid,
                "check": claim.get("current_claim"),
                "reason": claim.get("review_reason"),
            })
    currentness_checks = dedupe(currentness_checks)

    quantitative_checks = []
    for route in ordered_routes:
        action_family = route.get("policy_action", {}).get("action_family")
        remedy_family = route.get("remedy", {}).get("remedy_family")
        if action_family in REVENUE_OR_PRICE_ACTION_FAMILIES:
            quantitative_checks.append({
                "route_id": route.get("route_id"),
                "check": "estimate revenue, distributional incidence, behavioral response, take-up, and administrative cost before choosing rates or amounts",
                "why": "route uses revenue, fee, compensation, prefunding, subsidy, or public-upside instruments",
            })
        if action_family in ENFORCEMENT_ACTION_FAMILIES or remedy_family in {"classification_correction", "record_correction_and_accountable_review"}:
            quantitative_checks.append({
                "route_id": route.get("route_id"),
                "check": "estimate false positives, contest burden, notice failure, remediation capacity, and enforcement proportionality before finality",
                "why": "route can shift legal or administrative risk onto burden bearers",
            })
    quantitative_checks = dedupe(quantitative_checks)

    decision_adapters = load_decision_adapters(pathlib.Path(__file__).resolve().parent)
    adapter_checks = decision_adapters.adapter_checks_for_routes(
        ordered_routes,
        currentness_registry or [],
        as_of_date or "2026-06-18",
    )
    adapter_summary = decision_adapters.summarize_adapter_checks(adapter_checks)
    adapter_markers = decision_adapters.cannot_finalize_markers(adapter_checks)

    cannot_finalize_until = dedupe(
        precedence_resolution.get("must_resolve_before_final_answer", [])
        + (["current_law_source_refresh"] if currentness_checks else [])
        + (["quantitative_model_or_distributional_check"] if quantitative_checks else [])
        + (["explicit_no_go_override_or_prohibition_path"] if "do_not_price_or_offset_no_go_harm_without_explicit_override" in gate_names else [])
        + adapter_markers
        + (["registered_evidence_producer_bundle"] if adapter_checks else [])
    )

    recommended_sequence = []
    for position, route in enumerate(ordered_routes, 1):
        recommended_sequence.append({
            "position": position,
            "route_id": route.get("route_id"),
            "precedence_label": route.get("precedence_label"),
            "first_question": route.get("precedence", {}).get("precedence_reason"),
            "default_move": route.get("remedy", {}).get("default_move"),
            "blocked_move": route.get("remedy", {}).get("blocked_move"),
            "primary_accountable_actor": route.get("accountability", {}).get("primary_accountable_actor"),
            "source_ids": route.get("provenance", {}).get("primary_sources", []),
        })

    return {
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "case_id": case.get("case_id"),
        "dominant_disposition": _dominant_disposition(precedence_resolution, selected_routes),
        "ordered_route_ids": ordered_ids,
        "recommended_sequence": recommended_sequence,
        "hard_blocks": hard_blocks,
        "default_moves": dedupe(default_moves),
        "default_moves_by_route": default_moves_by_route,
        "actor_assignments": actor_assignments,
        "currentness_checks": currentness_checks,
        "quantitative_checks": quantitative_checks,
        "adapter_runtime_status": DECISION_ADAPTER_RUNTIME_STATUS,
        "adapter_checks": adapter_checks,
        "adapter_summary": adapter_summary,
        "adapter_execution_required": bool(adapter_checks),
        "adapter_execution_tool": "tools/execute_decision_adapters.py",
        "adapter_execution_default_status": "blocked_until_external_evidence_bundle_is_validated",
        "registered_evidence_producer_required": bool(adapter_checks),
        "evidence_request_runtime_status": EVIDENCE_REQUEST_RUNTIME_STATUS,
        "evidence_request_tool": "tools/plan_adapter_evidence_requests.py",
        "evidence_producer_contracts_path": "docs/00-meta/evidence-producer-contracts.json",
        "cannot_finalize_until": cannot_finalize_until,
        "provenance_source_ids": dedupe(provenance_source_ids),
        "source_gate_present": bool(currentness_checks),
        "no_go_gate_present": "do_not_price_or_offset_no_go_harm_without_explicit_override" in gate_names,
        "substance_note": "This is a deterministic disposition packet, not jurisdiction-specific legal advice or a fiscal model; adapter checks identify which current-law, jurisdiction-scope, delivery, model, and registered-producer validations must happen before final action.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize final disposition packets from answer-case output.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Synthesize one case id")
    parser.add_argument("--all", action="store_true", help="Synthesize all golden cases")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    answer_case = load_answer_case(root / "tools")
    runtime = answer_case.AnswerRuntime(root, answer_case.DEFAULT_ROUTE_LIMIT, answer_case.DEFAULT_FACTS_ONLY_LIMIT)
    golden = load_json(root / "docs/00-meta/golden-cases.json")
    cases = golden.get("cases", [])
    if args.case_id:
        cases = [case for case in cases if case.get("case_id") == args.case_id]
        if not cases:
            raise SystemExit(f"unknown case id: {args.case_id}")
    elif not args.all:
        raise SystemExit("provide --case-id or --all")

    packets = []
    for case in cases:
        answer = runtime.answer_case(case)
        packets.append(answer.get("disposition", {}))
    payload = {
        "kind": "case_disposition_packets",
        "runtime_status": RUNTIME_STATUS,
        "case_count": len(cases),
        "packets": packets,
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        for packet in packets:
            print(f"{packet.get('case_id')}: {packet.get('dominant_disposition')}")
            if packet.get("cannot_finalize_until"):
                print("  check first: " + " | ".join(str(x) for x in packet.get("cannot_finalize_until", [])[:5]))
            for move in packet.get("default_moves", [])[:3]:
                print(f"  default: {move}")


if __name__ == "__main__":
    main()
