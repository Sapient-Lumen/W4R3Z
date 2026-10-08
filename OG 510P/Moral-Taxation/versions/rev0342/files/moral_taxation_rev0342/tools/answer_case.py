#!/usr/bin/env python3
"""Emit a compact, deterministic answer packet for a golden case.

This is still not jurisdiction-specific legal advice and it is not a fiscal
model. It is the checked answer-emission layer after routing: candidate routes
are converted into profile-backed obligations, actor assignments, blocked
shortcuts, guardrails, source packets, currentness hooks, and claim-level
provenance packets. The script reads live case facts, route records, and the
generated runtime profile index; it deliberately does not read answer contracts.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List

RUNTIME_STATUS = "profile_backed_answer_packet_emitted"
CLAIM_RUNTIME_STATUS = "profile_index_claim_packets_emitted"
PRECEDENCE_RUNTIME_STATUS = "precedence_resolver_invoked"
DISPOSITION_RUNTIME_STATUS = "final_disposition_synthesizer_invoked"
DECISION_ADAPTER_RUNTIME_STATUS = "decision_adapter_requirements_resolved"
EVIDENCE_REQUEST_RUNTIME_STATUS = "evidence_producer_requests_planned"
DEFAULT_ROUTE_LIMIT = 5
DEFAULT_FACTS_ONLY_LIMIT = 8


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_route_case(tools_dir: pathlib.Path):
    spec = importlib.util.spec_from_file_location("route_case", tools_dir / "route_case.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load route_case.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module



def load_precedence_resolver(tools_dir: pathlib.Path):
    spec = importlib.util.spec_from_file_location("resolve_precedence", tools_dir / "resolve_precedence.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load resolve_precedence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def load_disposition_synthesizer(tools_dir: pathlib.Path):
    spec = importlib.util.spec_from_file_location("synthesize_disposition", tools_dir / "synthesize_disposition.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load synthesize_disposition.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module

def dedupe(values: Iterable[Any]) -> List[Any]:
    seen = set()
    out: List[Any] = []
    for value in values:
        key = json.dumps(value, sort_keys=True, separators=(",", ":")) if isinstance(value, (dict, list)) else str(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def short_list(values: Iterable[Any], limit: int = 8) -> List[Any]:
    return list(dedupe(values))[:limit]


class AnswerRuntime:
    def __init__(self, root: pathlib.Path, route_limit: int, facts_only_limit: int = DEFAULT_FACTS_ONLY_LIMIT) -> None:
        self.root = root
        self.route_limit = route_limit
        self.facts_only_limit = facts_only_limit
        self.cube = load_json(root / "cube-index.json")
        self.sources = {s["id"]: s for s in load_json(root / "SOURCES.json").get("sources", [])}
        self.profile_index = {
            e["route_id"]: e
            for e in load_json(root / "docs/00-meta/route-profile-index.json").get("entries", [])
        }
        receipt = load_json(root / "REVISION-RECEIPT.json")
        self.as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
        self.currentness_registry = load_json(root / "docs/00-meta/source-currentness-registry.json").get("entries", [])
        self.route_by_id = {r["id"]: r for r in self.cube.get("route_records", [])}
        self.route_case = load_route_case(root / "tools")
        self.precedence = load_precedence_resolver(root / "tools")
        self.disposition_synthesizer = load_disposition_synthesizer(root / "tools")
        self.prepared_routes = self.route_case.prepare_routes(root, self.cube.get("route_records", []))

    def route_case_result(self, case: Dict[str, Any]) -> Dict[str, Any]:
        combined = self.route_case.rank_case(case, self.prepared_routes, self.route_limit, facts_only=False)
        facts = self.route_case.rank_case(case, self.prepared_routes, self.facts_only_limit, facts_only=True)
        combined["facts_only_candidate_route_ids"] = facts.get("candidate_route_ids", [])
        combined["facts_only_primary_route_id"] = facts.get("primary_route_id")
        combined["facts_only_ranked_candidates"] = facts.get("ranked_candidates", [])
        return combined


    def source_packet(self, ids: Iterable[str], route_claims: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        packet = []
        for sid in sorted(set(ids), key=lambda x: int(x[1:]) if str(x).startswith("S") and str(x)[1:].isdigit() else 10**9):
            src = self.sources.get(sid, {})
            packet.append({
                "source_id": sid,
                "title": src.get("title"),
                "url": src.get("url"),
                "currentness_claims": route_claims.get(sid, []),
            })
        return packet

    def claim_packets_for_route(
        self,
        rid: str,
        route: Dict[str, Any],
        remedy: Dict[str, Any],
        action: Dict[str, Any],
        actor: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        primary_sources = route.get("primary_sources", [])
        packets: List[Dict[str, Any]] = [
            {
                "claim_type": "route_classification",
                "route_id": rid,
                "claim_text": f"Classify through route {rid} in family {route.get('family')}; do not decide from the instrument label alone.",
                "profile_field": "route.family|route.route_axes|route.primary_sources",
                "source_ids": primary_sources,
            },
            {
                "claim_type": "policy_category_error",
                "route_id": rid,
                "claim_text": action.get("category_error_to_block"),
                "profile_field": "policy_action.category_error_to_block",
                "source_ids": primary_sources,
            },
            {
                "claim_type": "accountability_assignment",
                "route_id": rid,
                "claim_text": (
                    f"Primary accountable actor: {actor.get('primary_accountable_actor')}; "
                    f"burden bearers: {', '.join(str(x) for x in short_list(actor.get('burden_bearers', []), 6))}."
                ),
                "profile_field": "accountability.primary_accountable_actor|accountability.burden_bearers",
                "source_ids": primary_sources,
            },
            {
                "claim_type": "remedy_default_and_blocked_move",
                "route_id": rid,
                "claim_text": f"Default move: {remedy.get('default_move')} Blocked move: {remedy.get('blocked_move')}",
                "profile_field": "remedy.default_move|remedy.blocked_move",
                "source_ids": primary_sources,
            },
        ]
        for claim in route.get("source_currentness_claims", []):
            sid = claim.get("source_id")
            if not sid:
                continue
            packets.append({
                "claim_type": "source_currentness_claim",
                "route_id": rid,
                "claim_text": claim.get("current_claim"),
                "profile_field": "route.source_currentness_claims.current_claim",
                "source_ids": [sid],
                "review_reason": claim.get("review_reason"),
            })
        return packets

    def selected_route_packet(self, item: Dict[str, Any]) -> Dict[str, Any]:
        rid = item.get("route_id")
        profile = self.profile_index.get(rid, {})
        route = {
            "family": profile.get("family"),
            "path": profile.get("route_path"),
            "axes": profile.get("route_axes", {}),
            "primary_sources": profile.get("primary_sources", []),
            "source_currentness_refs": profile.get("source_currentness_refs", []),
            "source_currentness_claims": profile.get("source_currentness_claims", []),
        }
        remedy = profile.get("remedy", {})
        action = profile.get("policy_action", {})
        actor = profile.get("accountability", {})
        claim_packets = self.claim_packets_for_route(str(rid), route, remedy, action, actor)
        precedence = self.precedence.classify_precedence(profile)
        return {
            "route_id": rid,
            "family": route.get("family"),
            "route_path": route.get("path"),
            "route_axes": route.get("axes", {}),
            "score": item.get("score"),
            "axis_score": item.get("axis_score"),
            "fact_score": item.get("fact_score"),
            "evidence_basis": {
                "axis_matches": item.get("axis_matches", {}),
                "text_hits": item.get("text_hits", []),
            },
            "precedence_label": precedence.get("precedence_label"),
            "precedence": precedence,
            "policy_action": {
                "action_family": action.get("action_family"),
                "primary_instrument": action.get("primary_instrument"),
                "benefit_nexus": action.get("benefit_nexus"),
                "legitimate_use": action.get("legitimate_use"),
                "category_error_to_block": action.get("category_error_to_block"),
                "required_distinctions": short_list(action.get("required_distinctions", []), 8),
                "escalation_trigger": action.get("escalation_trigger"),
            },
            "accountability": {
                "primary_accountable_actor": actor.get("primary_accountable_actor"),
                "secondary_accountable_actors": short_list(actor.get("secondary_accountable_actors", []), 8),
                "burden_bearers": short_list(actor.get("burden_bearers", []), 8),
                "beneficiary_or_rent_recipient": actor.get("beneficiary_or_rent_recipient"),
                "bottleneck_or_channel_actor": short_list(actor.get("bottleneck_or_channel_actor", []), 8),
                "responsibility_basis": short_list(actor.get("responsibility_basis", []), 8),
                "evidence_required": short_list(actor.get("evidence_required", []), 8),
                "anti_misattribution_rule": actor.get("anti_misattribution_rule"),
                "fallback_public_duty": actor.get("fallback_public_duty"),
            },
            "remedy": {
                "remedy_family": remedy.get("remedy_family"),
                "incidence_problem": remedy.get("incidence_problem"),
                "default_move": remedy.get("default_move"),
                "blocked_move": remedy.get("blocked_move"),
                "required_guardrails": short_list(remedy.get("required_guardrails", []), 8),
                "escalation_trigger": remedy.get("escalation_trigger"),
                "proceeds_integrity": remedy.get("proceeds_integrity"),
                "review_linkage": short_list(remedy.get("review_linkage", []), 8),
                "severity": remedy.get("severity"),
                "confidence": remedy.get("confidence"),
            },
            "provenance": {
                "primary_sources": route.get("primary_sources", []),
                "source_currentness_refs": route.get("source_currentness_refs", []),
                "source_currentness_claims": route.get("source_currentness_claims", []),
            },
            "claim_packets": claim_packets,
        }

    def answer_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        ranked = self.route_case_result(case)
        ranked_items = ranked.get("ranked_candidates", [])[: self.route_limit]
        selected = [self.selected_route_packet(item) for item in ranked_items]
        selected_ids = [r["route_id"] for r in selected]
        precedence_resolution = self.precedence.resolve_precedence(ranked_items, self.profile_index)
        decision_route_ids = precedence_resolution.get("ordered_route_ids", [])
        claim_packets = [packet for r in selected for packet in r.get("claim_packets", [])]
        route_source_ids = [sid for r in selected for sid in r.get("provenance", {}).get("primary_sources", [])]
        case_source_ids = case.get("source_ids", [])
        currentness_claims: Dict[str, List[Dict[str, str]]] = {}
        for r in selected:
            for claim in r.get("provenance", {}).get("source_currentness_claims", []):
                sid = claim.get("source_id")
                if sid:
                    currentness_claims.setdefault(sid, []).append({
                        "route_id": r.get("route_id"),
                        "current_claim": claim.get("current_claim", ""),
                        "review_reason": claim.get("review_reason", ""),
                    })

        blocked_shortcuts = short_list(
            list(case.get("must_not_answer", []))
            + [r.get("remedy", {}).get("blocked_move") for r in selected]
            + [r.get("policy_action", {}).get("category_error_to_block") for r in selected],
            64,
        )
        default_moves = short_list([r.get("remedy", {}).get("default_move") for r in selected], 32)
        review_triggers = short_list(
            [r.get("remedy", {}).get("escalation_trigger") for r in selected]
            + [r.get("policy_action", {}).get("escalation_trigger") for r in selected]
            + [case.get("review_trigger")],
            64,
        )
        all_sources = short_list(list(case_source_ids) + route_source_ids, 128)
        disposition = self.disposition_synthesizer.synthesize_disposition(
            case=case,
            selected_routes=selected,
            precedence_resolution=precedence_resolution,
            blocked_shortcuts=blocked_shortcuts,
            default_moves=default_moves,
            provenance_source_ids=all_sources,
            currentness_registry=self.currentness_registry,
            as_of_date=self.as_of_date,
        )

        return {
            "case_id": case.get("case_id"),
            "title": case.get("title"),
            "runtime_status": RUNTIME_STATUS,
            "claim_runtime_status": CLAIM_RUNTIME_STATUS,
            "precedence_runtime_status": PRECEDENCE_RUNTIME_STATUS,
            "disposition_runtime_status": DISPOSITION_RUNTIME_STATUS,
            "decision_adapter_runtime_status": DECISION_ADAPTER_RUNTIME_STATUS,
            "evidence_request_runtime_status": EVIDENCE_REQUEST_RUNTIME_STATUS,
            "selected_route_limit": self.route_limit,
            "routing": {
                "primary_route_id": ranked.get("primary_route_id"),
                "selected_route_ids": selected_ids,
                "combined_candidate_route_ids": ranked.get("candidate_route_ids", []),
                "facts_only_primary_route_id": ranked.get("facts_only_primary_route_id"),
                "facts_only_candidate_route_ids": ranked.get("facts_only_candidate_route_ids", []),
            },
            "selected_routes": selected,
            "answer_steps": [
                {
                    "step": "classify_action_and_route",
                    "route_ids": selected_ids,
                    "action_families": short_list([r.get("policy_action", {}).get("action_family") for r in selected], 16),
                },
                {
                    "step": "resolve_precedence_before_disposition",
                    "decision_route_ids": decision_route_ids,
                    "triggered_rules": precedence_resolution.get("triggered_rules", []),
                    "dominant_precedence_label": precedence_resolution.get("dominant_precedence_label"),
                },
                {
                    "step": "assign_real_accountability_before_collection_or_compensation",
                    "primary_accountable_actors": short_list([r.get("accountability", {}).get("primary_accountable_actor") for r in selected], 16),
                },
                {
                    "step": "block_category_errors_and_prohibited_shortcuts",
                    "blocked_shortcuts": blocked_shortcuts,
                },
                {
                    "step": "apply_default_moves_with_guardrails",
                    "default_moves": default_moves,
                    "guardrails": short_list([g for r in selected for g in r.get("remedy", {}).get("required_guardrails", [])], 32),
                },
                {
                    "step": "bind_decision_claims_to_profile_fields_and_sources",
                    "claim_packet_count": len(claim_packets),
                    "claim_types": short_list([c.get("claim_type") for c in claim_packets], 16),
                },
                {
                    "step": "verify_sources_currentness_and_unresolved_model_gaps",
                    "source_ids": all_sources,
                    "currentness_source_ids": short_list([sid for r in selected for sid in r.get("provenance", {}).get("source_currentness_refs", [])], 32),
                },
                {
                    "step": "resolve_current_law_jurisdiction_and_model_adapters",
                    "adapter_runtime_status": disposition.get("adapter_runtime_status"),
                    "adapter_type_counts": disposition.get("adapter_summary", {}).get("adapter_type_counts", {}),
                    "adapter_check_count": disposition.get("adapter_summary", {}).get("adapter_check_count", 0),
                },
                {
                    "step": "plan_registered_evidence_producer_requests",
                    "evidence_request_runtime_status": disposition.get("evidence_request_runtime_status"),
                    "evidence_request_tool": disposition.get("evidence_request_tool"),
                    "evidence_producer_contracts_path": disposition.get("evidence_producer_contracts_path"),
                },
                {
                    "step": "execute_decision_adapters_with_external_evidence_bundle",
                    "execution_tool": "tools/execute_decision_adapters.py",
                    "default_execution_status": disposition.get("adapter_execution_default_status"),
                    "adapter_execution_required": disposition.get("adapter_execution_required"),
                    "registered_evidence_producer_required": disposition.get("registered_evidence_producer_required"),
                },
            ],
            "precedence_resolution": precedence_resolution,
            "precedence_order": precedence_resolution.get("ordered_steps", []),
            "disposition": disposition,
            "default_moves": default_moves,
            "blocked_shortcuts": blocked_shortcuts,
            "must_not_answer": case.get("must_not_answer", []),
            "review_triggers": review_triggers,
            "case_source_ids": case_source_ids,
            "provenance_source_ids": all_sources,
            "claim_packets": claim_packets,
            "source_packet": self.source_packet(all_sources, currentness_claims),
            "profile_obligation_counts": {
                "selected_routes": len(selected),
                "default_moves": len(default_moves),
                "blocked_shortcuts": len(blocked_shortcuts),
                "guardrails": len(short_list([g for r in selected for g in r.get("remedy", {}).get("required_guardrails", [])], 128)),
                "source_ids": len(all_sources),
                "currentness_claim_sources": len(currentness_claims),
            },
            "unknowns": [
                "precedence resolution is rule-based and must still be checked against jurisdiction-specific current law",
                "adapter checks identify current-law and jurisdiction validations but do not perform live legal research",
                "adapter checks identify quantitative model requirements but do not estimate revenue, distribution, behavior, take-up, or administrative cost",
                "adapter execution requires an external evidence bundle validated by tools/execute_decision_adapters.py",
                "human reviewer must resolve conflicts between co-equal routes before final advice",
            ],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit compact answer packets for golden cases.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Answer one case id, e.g. GC-001")
    parser.add_argument("--all", action="store_true", help="Answer all golden cases")
    parser.add_argument("--route-limit", type=int, default=DEFAULT_ROUTE_LIMIT, help="Candidate route count to include")
    parser.add_argument("--facts-only-candidate-limit", type=int, default=DEFAULT_FACTS_ONLY_LIMIT, help="Facts-only candidate count to include")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    golden = load_json(root / "docs/00-meta/golden-cases.json")
    cases = golden.get("cases", [])
    if args.case_id:
        cases = [case for case in cases if case.get("case_id") == args.case_id]
        if not cases:
            raise SystemExit(f"unknown case id: {args.case_id}")
    elif not args.all:
        raise SystemExit("provide --case-id or --all")

    runtime = AnswerRuntime(root, args.route_limit, args.facts_only_candidate_limit)
    answers = [runtime.answer_case(case) for case in cases]
    payload = {
        "kind": "case_answer_packets",
        "runtime_status": RUNTIME_STATUS,
        "claim_runtime_status": CLAIM_RUNTIME_STATUS,
        "precedence_runtime_status": PRECEDENCE_RUNTIME_STATUS,
        "disposition_runtime_status": DISPOSITION_RUNTIME_STATUS,
        "decision_adapter_runtime_status": DECISION_ADAPTER_RUNTIME_STATUS,
        "evidence_request_runtime_status": EVIDENCE_REQUEST_RUNTIME_STATUS,
        "case_count": len(cases),
        "route_limit": args.route_limit,
        "facts_only_candidate_limit": args.facts_only_candidate_limit,
        "answers": answers,
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        for answer in answers:
            print(f"{answer['case_id']}: {answer['title']}")
            print("  routes: " + ", ".join(answer["routing"]["selected_route_ids"]))
            for move in answer.get("default_moves", [])[:5]:
                print(f"  default: {move}")
            if answer.get("blocked_shortcuts"):
                print("  block: " + " | ".join(str(x) for x in answer["blocked_shortcuts"][:5]))


if __name__ == "__main__":
    main()
