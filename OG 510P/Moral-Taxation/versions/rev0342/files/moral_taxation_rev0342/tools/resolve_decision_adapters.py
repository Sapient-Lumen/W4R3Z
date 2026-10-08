#!/usr/bin/env python3
"""Resolve final-disposition adapter requirements for current law and models.

Precedence decides what comes first. Disposition synthesis decides what is
blocked, defaulted, or still unresolved. This module adds the next narrow waist:
which outside checks must be performed before implementation. It consumes
selected route packets and the source-currentness registry. It deliberately does
not read golden-case contracts or expected answers.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Mapping, Sequence

RUNTIME_STATUS = "decision_adapter_requirements_resolved"
RULE_VERSION = 1
REVIEW_DUE_SOON_DAYS = 45

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
FLOOR_REMEDY_FAMILIES = {"channel_access_and_cure", "floor_repair_and_no_rent_relief"}
RECORD_REMEDY_FAMILIES = {"classification_correction", "record_correction_and_accountable_review"}
MULTI_OR_LIVE_SCALES = {"cross_border", "state_or_provincial", "local", "multi_scale", "national", "club", "failure_state"}
UNSETTLED_LEGAL_STATES = {"unknown", "guidance_only", "proposed_rule", "litigated", "interim_framework", "voluntary_standard"}


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_answer_case(tools_dir: pathlib.Path):
    spec = importlib.util.spec_from_file_location("answer_case", tools_dir / "answer_case.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load answer_case.py")
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


def _as_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, list):
        return {str(v) for v in values if v is not None}
    return {str(values)}


def _as_date(value: str | None) -> _dt.date | None:
    if not value:
        return None
    try:
        return _dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def as_of_date_from_root(root: pathlib.Path) -> str:
    receipt = load_json(root / "REVISION-RECEIPT.json")
    created = str(receipt.get("created_at_utc", ""))
    parsed = _as_date(created)
    return parsed.isoformat() if parsed else "2026-06-18"


def registry_by_source(entries: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(e.get("source_id")): dict(e) for e in entries if e.get("source_id")}


def review_due_state(entry: Mapping[str, Any], as_of_date: str) -> str:
    as_of = _as_date(as_of_date)
    due = _as_date(str(entry.get("review_due", "")))
    if not as_of or not due:
        return "unknown_review_due"
    if due < as_of:
        return "overdue"
    delta = (due - as_of).days
    if delta <= REVIEW_DUE_SOON_DAYS:
        return "due_soon"
    return "not_due_yet"


def route_axes(route: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(route.get("route_axes") or route.get("axes") or {})


def route_policy_action(route: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(route.get("policy_action") or {})


def route_remedy(route: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(route.get("remedy") or {})


def route_precedence(route: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(route.get("precedence") or {})


def route_source_refs(route: Mapping[str, Any]) -> List[str]:
    provenance = dict(route.get("provenance") or {})
    refs = provenance.get("source_currentness_refs") or route.get("source_currentness_refs") or []
    return [str(x) for x in refs if x]


def route_currentness_claims(route: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    provenance = dict(route.get("provenance") or {})
    claims = provenance.get("source_currentness_claims") or route.get("source_currentness_claims") or []
    return {str(c.get("source_id")): dict(c) for c in claims if c.get("source_id")}


def route_id(route: Mapping[str, Any]) -> str:
    return str(route.get("route_id") or route.get("id") or "")


def _adapter_packet(route: Mapping[str, Any], adapter_type: str, obligation: str, **extra: Any) -> Dict[str, Any]:
    rid = route_id(route)
    packet = {
        "adapter_type": adapter_type,
        "route_id": rid,
        "adapter_id": f"{adapter_type}:{rid}:{extra.get('source_id') or extra.get('model_class') or extra.get('scope') or 'route'}",
        "obligation": obligation,
    }
    packet.update({k: v for k, v in extra.items() if v not in (None, "", [], {})})
    return packet


def adapter_checks_for_route(route: Mapping[str, Any], currentness_registry: Sequence[Mapping[str, Any]], as_of_date: str) -> List[Dict[str, Any]]:
    axes = route_axes(route)
    action = route_policy_action(route)
    remedy = route_remedy(route)
    precedence = route_precedence(route)
    registry = registry_by_source(currentness_registry)
    checks: List[Dict[str, Any]] = []

    claims = route_currentness_claims(route)
    for sid in route_source_refs(route):
        entry = registry.get(sid, {"source_id": sid})
        claim = claims.get(sid, {})
        checks.append(_adapter_packet(
            route,
            "current_law_refresh_adapter",
            "refresh volatile or implementation-sensitive source before final legal advice or implementation",
            source_id=sid,
            jurisdiction=entry.get("jurisdiction"),
            source_type=entry.get("source_type"),
            source_status=entry.get("status"),
            effective_date=entry.get("effective_date"),
            last_checked=entry.get("last_checked"),
            review_due=entry.get("review_due"),
            review_due_state=review_due_state(entry, as_of_date),
            volatility=entry.get("volatility"),
            current_claim=claim.get("current_claim"),
            review_reason=claim.get("review_reason") or entry.get("note"),
        ))

    scales = _as_set(axes.get("scale"))
    legal_states = _as_set(axes.get("legal_status"))
    source_freshness = _as_set(axes.get("source_freshness"))
    if (scales & MULTI_OR_LIVE_SCALES) and (legal_states & UNSETTLED_LEGAL_STATES or source_freshness - {"stable_reference"} or route_source_refs(route)):
        checks.append(_adapter_packet(
            route,
            "jurisdiction_scope_adapter",
            "resolve jurisdiction, effective date, authority level, and conflict rule before applying the disposition",
            scope=":".join(sorted(scales)) or "unspecified",
            legal_status=sorted(legal_states),
            source_freshness=sorted(source_freshness),
            required_inputs=["jurisdiction", "effective_date", "authority_level", "preemption_or_treaty_conflict", "implementation_status"],
        ))

    action_family = str(action.get("action_family", ""))
    remedy_family = str(remedy.get("remedy_family", ""))
    incidence = sorted(_as_set(axes.get("incidence")))
    floor_risk = sorted(_as_set(axes.get("floor_risk")))
    burden = sorted(_as_set(axes.get("burden_mechanic")))
    if action_family in REVENUE_OR_PRICE_ACTION_FAMILIES:
        checks.append(_adapter_packet(
            route,
            "quantitative_model_adapter",
            "estimate incidence, revenue, distribution, behavioral response, take-up, administrative cost, and uncertainty before rates or amounts are chosen",
            model_class="fiscal_incidence_distribution_model",
            action_family=action_family,
            required_outputs=["revenue", "incidence_by_group", "behavioral_response", "take_up", "administrative_cost", "uncertainty_range"],
            incidence=incidence,
            floor_risk=floor_risk,
            burden_mechanic=burden,
        ))
    if action_family in ENFORCEMENT_ACTION_FAMILIES or remedy_family in RECORD_REMEDY_FAMILIES:
        checks.append(_adapter_packet(
            route,
            "quantitative_model_adapter",
            "estimate false positives, false negatives, contest burden, notice failure, remediation capacity, and proportionality before finality or enforcement",
            model_class="enforcement_error_contest_capacity_model",
            action_family=action_family,
            remedy_family=remedy_family,
            required_outputs=["false_positive_rate", "false_negative_rate", "contest_time_cost", "notice_failure_rate", "remediation_capacity", "proportionality_range"],
        ))
    if remedy_family in FLOOR_REMEDY_FAMILIES or "protected_floor" in incidence:
        checks.append(_adapter_packet(
            route,
            "floor_delivery_adapter",
            "verify take-up, no-rent fallback, accessibility, language, timing, and nonforfeiture before relying on a floor or cure remedy",
            model_class="protected_floor_delivery_model",
            remedy_family=remedy_family,
            required_outputs=["eligible_population", "take_up", "friction_points", "fallback_capacity", "nonforfeiture_rule", "accessibility_coverage"],
            floor_risk=floor_risk,
        ))
    if int(precedence.get("precedence_band") or 90) <= 10:
        checks.append(_adapter_packet(
            route,
            "no_go_threshold_adapter",
            "verify whether the no-go or noncompensable-harm threshold is triggered before any price, offset, permit, or compensation route is considered",
            model_class="no_go_threshold_review",
            required_outputs=["harm_threshold", "irreversibility", "affected_right_or_floor", "available_nonpricing_remedy", "explicit_override_authority"],
        ))
    return dedupe(checks)


def adapter_checks_for_routes(routes: Sequence[Mapping[str, Any]], currentness_registry: Sequence[Mapping[str, Any]], as_of_date: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    for route in routes:
        checks.extend(adapter_checks_for_route(route, currentness_registry, as_of_date))
    return dedupe(checks)


def summarize_adapter_checks(checks: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    by_type: Dict[str, int] = {}
    due_states: Dict[str, int] = {}
    route_ids = set()
    for check in checks:
        typ = str(check.get("adapter_type"))
        by_type[typ] = by_type.get(typ, 0) + 1
        if check.get("route_id"):
            route_ids.add(str(check.get("route_id")))
        state = check.get("review_due_state")
        if state:
            due_states[str(state)] = due_states.get(str(state), 0) + 1
    return {
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "adapter_check_count": len(checks),
        "route_count_with_adapters": len(route_ids),
        "adapter_type_counts": dict(sorted(by_type.items())),
        "current_law_review_due_state_counts": dict(sorted(due_states.items())),
    }


def cannot_finalize_markers(checks: Sequence[Mapping[str, Any]]) -> List[str]:
    types = {str(check.get("adapter_type")) for check in checks}
    markers = []
    if "current_law_refresh_adapter" in types:
        markers.append("current_law_adapter_validation")
    if "jurisdiction_scope_adapter" in types:
        markers.append("jurisdiction_scope_adapter_validation")
    if "quantitative_model_adapter" in types:
        markers.append("quantitative_model_adapter_validation")
    if "floor_delivery_adapter" in types:
        markers.append("floor_delivery_adapter_validation")
    if "no_go_threshold_adapter" in types:
        markers.append("no_go_threshold_adapter_validation")
    return markers


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve current-law and model adapter requirements for golden-case answers.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Resolve one case id")
    parser.add_argument("--all", action="store_true", help="Resolve all golden cases")
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
        answer = runtime.answer_case(case)
        checks = answer.get("disposition", {}).get("adapter_checks", [])
        results.append({
            "case_id": case.get("case_id"),
            "adapter_summary": summarize_adapter_checks(checks),
            "adapter_checks": checks,
        })
    payload = {
        "kind": "case_decision_adapter_requirements",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "case_count": len(results),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        for result in results:
            summary = result["adapter_summary"]
            print(f"{result['case_id']}: {summary.get('adapter_check_count')} adapter checks " + json.dumps(summary.get("adapter_type_counts", {}), sort_keys=True))


if __name__ == "__main__":
    main()
