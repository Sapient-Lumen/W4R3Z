#!/usr/bin/env python3
"""Resolve selected candidate routes into a substantive decision order.

The router answers "what routes are implicated?"; this resolver answers "what
must be settled first when those routes collide?" It is intentionally small and
profile-driven. It consumes already-selected route/profile packets and does not
read golden-case contracts or expected answers.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RUNTIME_STATUS = "precedence_resolver_invoked"
RULE_VERSION = 1

BANDS = {
    10: "veto_no_go_or_noncompensable_harm_before_pricing_or_compensation",
    15: "release_integrity_and_source_currentness_gate_before_downstream_use",
    20: "protected_floor_due_process_access_and_cure_before_collection",
    30: "real_actor_controller_beneficiary_and_burden_bearer_before_liability",
    40: "record_contestability_measurement_and_correction_before_finality",
    50: "penalty_liability_and_enforcement_after_floor_and_actor_checks",
    60: "ordinary_revenue_fee_rent_and_benefit_nexus_after_gates",
    70: "proceeds_prefunding_public_upside_and_anti_supplantation_after_classification",
    90: "ordinary_calibration_after_gates_conflicts_and_sources",
}

COLLECTION_ACTION_FAMILIES = {
    "penalty_liability_or_enforcement",
    "tax_revenue_or_rent_capture",
    "user_fee_or_service_charge",
    "information_reporting_or_recordkeeping",
}
REVENUE_ACTION_FAMILIES = {"tax_revenue_or_rent_capture", "user_fee_or_service_charge"}
COMPENSATION_ACTION_FAMILIES = {"rebate_credit_or_compensation", "risk_prefunding_or_insurance_pool"}
FLOOR_REMEDY_FAMILIES = {"channel_access_and_cure", "floor_repair_and_no_rent_relief"}
SOURCE_ACTION_FAMILIES = {"source_release_integrity"}
ACTOR_FAMILIES = {"actor_accountability", "controller_ai"}
PROTECTED_RIGHTS = {
    "health", "housing", "family", "disability_access", "financial_access", "public_service_access",
    "labor_status", "migration_status", "environmental_justice", "connectivity", "property", "liberty",
    "counsel", "treaty_relief", "indigenous_sovereignty", "worker_voice", "public_safety", "privacy",
}
PROTECTED_FLOOR_RISKS = {
    "low_income", "low_income_taxpayer", "public_service_access", "bankless", "unbanked",
    "disability", "disabled", "elderly", "child", "family", "immigrant", "asylum_seeker",
    "diaspora_family", "expat", "indigenous_community", "disaster_victim", "worker",
    "caregiver", "rural_household", "tenant", "ratepayer", "patient",
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


def _as_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, list):
        return {str(v) for v in values if v is not None}
    return {str(values)}


def route_features(profile: Dict[str, Any]) -> Dict[str, Any]:
    axes = profile.get("route_axes") or profile.get("axes") or {}
    action = profile.get("policy_action", {})
    remedy = profile.get("remedy", {})
    actor = profile.get("accountability", {})
    action_family = str(action.get("action_family", ""))
    remedy_family = str(remedy.get("remedy_family", ""))
    family = str(profile.get("family", ""))
    rid = str(profile.get("route_id", ""))
    moral_ops = _as_set(axes.get("moral_operation"))
    remedy_types = _as_set(axes.get("remedy_type"))
    rights = _as_set(axes.get("rights_affected"))
    incidence = _as_set(axes.get("incidence"))
    proof = _as_set(axes.get("proof_posture"))
    review = _as_set(axes.get("review_trigger"))
    floor = _as_set(axes.get("floor_risk"))
    burden = _as_set(axes.get("burden_mechanic"))
    source_refs = _as_set(profile.get("source_currentness_refs"))

    no_go = (
        action_family == "prohibition_no_go_or_veto"
        or "no_go_rule" in remedy_types
        or "prohibition_no_go" in moral_ops
        or "noncompensable_harm" in moral_ops
        or "injunction" in remedy_types
    )
    source_gate = (
        family == "release_integrity_currentness"
        or action_family in SOURCE_ACTION_FAMILIES
        or "source_integrity" in moral_ops
        or "current_law_integrity" in moral_ops
    )
    protected_floor = (
        "protected_floor" in incidence
        or remedy_family in FLOOR_REMEDY_FAMILIES
        or bool(rights & PROTECTED_RIGHTS)
        or ({"hardship_relief", "waiver", "fallback_channel", "notice_cure", "refund_reissue", "victim_relief", "direct_care_support"} & remedy_types)
        or (bool(floor & PROTECTED_FLOOR_RISKS) and (remedy_family in FLOOR_REMEDY_FAMILIES or action_family in {"public_option_or_fallback_channel", "administrative_access_or_contest"}))
    )
    actor_assignment = (
        family in ACTOR_FAMILIES
        or "controller" in incidence
        or "beneficiary" in incidence
        or "remitter" in incidence
        or "actor_accountability" in moral_ops
        or "gatekeeper_accountability" in moral_ops
        or "controller" in rid
        or "beneficial_ownership" in rid
        or bool(actor.get("primary_accountable_actor")) and (
            "real_actor" in str(actor.get("controller_test", ""))
            or "practical power" in str(actor.get("controller_test", ""))
        )
    )
    record_contest = (
        remedy_family in {"classification_correction", "record_correction_and_accountable_review"}
        or {"record_correction", "independent_review", "audit", "safe_harbor", "contest_window", "burden_shift", "disclosure"} & remedy_types
        or {"third_party_or_record_mismatch", "status_authority_or_liability_contested", "record_asymmetry", "model_output"} & proof
        or {"record_or_measurement_staleness", "remedy_or_contest_failure", "safe_harbor_or_cure_window"} & review
    )
    enforcement = action_family == "penalty_liability_or_enforcement" or family == "legal_enforcement_penalty"
    revenue = action_family in REVENUE_ACTION_FAMILIES or {"rent_capture", "harm_pricing", "public_capacity_funding"} & moral_ops
    proceeds = (
        action_family in {"risk_prefunding_or_insurance_pool", "subsidy_procurement_or_public_upside"}
        or remedy_family in {"risk_prefunding_and_clawback", "public_upside_and_anti_supplantation", "rent_capture_with_pass_through_control"}
        or {"clawback", "anti_supplantation", "backstop_reserve_prefunding", "community_benefit"} & remedy_types
        or "proceeds_integrity" in burden
    )
    return {
        "route_id": rid,
        "family": family,
        "action_family": action_family,
        "remedy_family": remedy_family,
        "source_currentness_refs": sorted(source_refs),
        "no_go": bool(no_go),
        "source_gate": bool(source_gate),
        "protected_floor": bool(protected_floor),
        "actor_assignment": bool(actor_assignment),
        "record_contest": bool(record_contest),
        "enforcement": bool(enforcement),
        "revenue": bool(revenue),
        "proceeds": bool(proceeds),
    }


def classify_precedence(profile: Dict[str, Any]) -> Dict[str, Any]:
    features = route_features(profile)
    if features["no_go"]:
        band = 10
        reason = "No-go or noncompensable-harm routes are veto-like; they cannot be converted into pricing, offset, or ordinary compensation without a separate justification."
    elif features["source_gate"]:
        band = 15
        reason = "Source-release/currentness routes gate downstream use; stale or unverified law/source state must be checked before final disposition."
    elif features["protected_floor"]:
        band = 20
        reason = "Protected floors, access, due-process, hardship, and cure conditions must be preserved before collection, fee, penalty, or compensation design."
    elif features["actor_assignment"] and (features["family"] in ACTOR_FAMILIES or "controller" in features["route_id"] or "beneficial_ownership" in features["route_id"] or "actor_accountability" in features["route_id"]):
        band = 30
        reason = "Dedicated actor/controller/beneficiary routes identify the real responsible party before collection, liability, or compensation are assigned."
    elif features["actor_assignment"]:
        band = 30
        reason = "Real controller, beneficiary, bottleneck, and burden-bearer assignment must precede liability, collection, or compensation."
    elif features["record_contest"]:
        band = 40
        reason = "Record, measurement, contestability, and correction questions must be settled before finality or penalty/liability action."
    elif features["enforcement"]:
        band = 50
        reason = "Penalty and enforcement routes come after floor, actor, and contest checks."
    elif features["revenue"]:
        band = 60
        reason = "Ordinary revenue, fee, rent, or benefit-nexus classification comes after no-go, floor, actor, source, and contest gates."
    elif features["proceeds"]:
        band = 70
        reason = "Proceeds, prefunding, public-upside, and anti-supplantation choices follow route classification and upstream gates."
    else:
        band = 90
        reason = "Ordinary calibration route after higher-order gates, conflicts, and source checks."
    return {
        "precedence_band": band,
        "precedence_label": BANDS[band],
        "precedence_reason": reason,
        "features": features,
    }


def _score(item: Dict[str, Any]) -> float:
    try:
        return float(item.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0


def resolve_precedence(selected_items: Sequence[Dict[str, Any]], profile_by_id: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []
    for position, item in enumerate(selected_items):
        rid = str(item.get("route_id"))
        profile = profile_by_id.get(rid, {"route_id": rid})
        classified = classify_precedence(profile)
        steps.append({
            "route_id": rid,
            "input_position": position,
            "candidate_score": item.get("score"),
            "precedence_band": classified["precedence_band"],
            "precedence_label": classified["precedence_label"],
            "precedence_reason": classified["precedence_reason"],
            "features": classified["features"],
            "sort_key": [classified["precedence_band"], -_score(item), rid],
        })
    ordered_steps = sorted(steps, key=lambda s: (s["precedence_band"], -float(s.get("candidate_score") or 0), s["route_id"]))

    action_families = {s["features"].get("action_family") for s in steps}
    has_no_go = any(s["features"].get("no_go") for s in steps)
    has_floor = any(s["features"].get("protected_floor") for s in steps)
    has_actor = any(s["features"].get("actor_assignment") for s in steps)
    has_source_gate = any(s["features"].get("source_gate") for s in steps)
    has_collection = bool(action_families & COLLECTION_ACTION_FAMILIES)
    has_revenue_or_compensation = bool(action_families & (REVENUE_ACTION_FAMILIES | COMPENSATION_ACTION_FAMILIES))

    triggered_rules: List[str] = []
    if has_no_go and has_revenue_or_compensation:
        triggered_rules.append("no_go_before_pricing_or_compensation")
    if has_floor and has_collection:
        triggered_rules.append("floor_before_collection_fee_penalty_or_forfeiture")
    if has_actor and (has_collection or has_revenue_or_compensation):
        triggered_rules.append("actor_assignment_before_liability_collection_or_compensation")
    if has_source_gate:
        triggered_rules.append("currentness_and_release_integrity_before_final_answer")
    if any(s["features"].get("record_contest") for s in steps) and has_collection:
        triggered_rules.append("contest_record_and_measurement_before_finality_or_penalty")
    if any(s["features"].get("revenue") for s in steps) and (has_floor or has_actor or has_no_go):
        triggered_rules.append("ordinary_revenue_classification_after_no_go_floor_and_actor_checks")

    currentness_source_ids = sorted({sid for s in steps for sid in s["features"].get("source_currentness_refs", [])})
    global_gates = []
    if currentness_source_ids:
        global_gates.append({
            "gate": "verify_currentness_before_final_answer",
            "source_ids": currentness_source_ids,
            "reason": "At least one selected route relies on source-currentness refs; final advice must refresh these before disposition.",
        })
    if has_no_go:
        global_gates.append({
            "gate": "do_not_price_or_offset_no_go_harm_without_explicit_override",
            "source_ids": [],
            "reason": "A selected route has no-go/noncompensable-harm features.",
        })

    return {
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "input_route_ids": [str(item.get("route_id")) for item in selected_items],
        "ordered_route_ids": [s["route_id"] for s in ordered_steps],
        "ordered_steps": ordered_steps,
        "dominant_precedence_band": ordered_steps[0]["precedence_band"] if ordered_steps else None,
        "dominant_precedence_label": ordered_steps[0]["precedence_label"] if ordered_steps else None,
        "triggered_rules": triggered_rules,
        "global_gates": global_gates,
        "must_resolve_before_final_answer": triggered_rules + [g["gate"] for g in global_gates],
        "explanation": "Candidate score determines relevance; precedence band determines which obligation is settled first when selected routes collide.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve precedence for answer-case selected routes.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Resolve one golden case id")
    parser.add_argument("--all", action="store_true", help="Resolve all golden cases through answer_case.py")
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

    results = []
    for case in cases:
        ranked = runtime.route_case_result(case)
        items = ranked.get("ranked_candidates", [])[: answer_case.DEFAULT_ROUTE_LIMIT]
        results.append({
            "case_id": case.get("case_id"),
            "title": case.get("title"),
            "precedence_resolution": resolve_precedence(items, runtime.profile_index),
        })
    payload = {
        "kind": "case_precedence_resolution_results",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "case_count": len(results),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        for result in results:
            resolution = result["precedence_resolution"]
            print(f"{result['case_id']}: " + " > ".join(resolution.get("ordered_route_ids", [])))
            if resolution.get("triggered_rules"):
                print("  rules: " + ", ".join(resolution["triggered_rules"]))


if __name__ == "__main__":
    main()
