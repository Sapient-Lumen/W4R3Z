#!/usr/bin/env python3
"""Audit final disposition synthesis in emitted answer packets.

The archive should not stop at route relevance or precedence order. This audit
requires each answer packet to carry a deterministic final-disposition packet
that preserves blocks, default moves, actor assignments, source/currentness
checks, and quantitative/model gaps in the resolver's decision order.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Set

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
DISPOSITION_STATUS = "final_disposition_synthesizer_invoked"
PRECEDENCE_STATUS = "precedence_resolver_invoked"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8

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
RECORD_REMEDY_FAMILIES = {"classification_correction", "record_correction_and_accountable_review"}


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

cube = load_json(root / "cube-index.json")

for rel in ["tools/answer_case.py", "tools/synthesize_disposition.py"]:
    source = (root / rel).read_text(encoding="utf-8")
    for forbidden in [
        "case-contracts",
        "case_contracts",
        "case-contract-schema",
        "expected_route_ids",
        "expected_flags",
        "required_route_families",
        "required_remedy_profiles",
    ]:
        if forbidden in source:
            errors.append(f"{rel} must not read or reference contract answer field {forbidden!r}")

try:
    cache_path = os.environ.get("MT_ANSWER_PACKET_CACHE")
    if cache_path and pathlib.Path(cache_path).exists():
        raw = pathlib.Path(cache_path).read_text(encoding="utf-8")
    else:
        raw = subprocess.check_output(
            [
                sys.executable,
                str(root / "tools/answer_case.py"),
                str(root),
                "--all",
                "--route-limit",
                str(ROUTE_LIMIT),
                "--facts-only-candidate-limit",
                str(FACTS_ONLY_LIMIT),
                "--json",
            ],
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    payload = json.loads(raw)
except Exception as exc:
    errors.append(f"answer_case.py failed under disposition synthesis audit: {exc}")
    payload = {"answers": []}

if payload.get("disposition_runtime_status") != DISPOSITION_STATUS:
    errors.append("answer payload disposition_runtime_status is stale")

answer_count = len(payload.get("answers", []))
disposition_packet_count = 0
ordered_packet_count = 0
sequence_complete_count = 0
hard_block_total = 0
hard_block_recall = 0
default_route_total = 0
default_route_recall = 0
actor_total = 0
actor_recall = 0
source_total = 0
source_recall = 0
currentness_total = 0
currentness_recall = 0
quantitative_total = 0
quantitative_recall = 0
no_go_gate_total = 0
no_go_gate_recall = 0
cannot_finalize_total = 0
cannot_finalize_recall = 0
dominant_counts: Dict[str, int] = {}

for answer in payload.get("answers", []):
    cid = answer.get("case_id")
    disposition = answer.get("disposition", {})
    selected_routes = answer.get("selected_routes", [])
    selected_by_id = {r.get("route_id"): r for r in selected_routes}
    precedence = answer.get("precedence_resolution", {})
    ordered_ids = precedence.get("ordered_route_ids", [])
    selected_ids = answer.get("routing", {}).get("selected_route_ids", [])

    if answer.get("disposition_runtime_status") != DISPOSITION_STATUS:
        errors.append(f"answer {cid} disposition_runtime_status is stale")
    if disposition.get("runtime_status") != DISPOSITION_STATUS:
        errors.append(f"answer {cid} disposition runtime_status is stale")
    else:
        disposition_packet_count += 1

    dominant = disposition.get("dominant_disposition")
    if dominant:
        dominant_counts[dominant] = dominant_counts.get(dominant, 0) + 1
    else:
        errors.append(f"answer {cid} disposition lacks dominant_disposition")

    if precedence.get("runtime_status") != PRECEDENCE_STATUS:
        errors.append(f"answer {cid} disposition audit cannot trust stale precedence runtime")

    if disposition.get("ordered_route_ids") == ordered_ids and set(ordered_ids) == set(selected_ids):
        ordered_packet_count += 1
    else:
        errors.append(f"answer {cid} disposition ordered_route_ids must mirror precedence order")

    sequence_ids = [step.get("route_id") for step in disposition.get("recommended_sequence", [])]
    if sequence_ids == ordered_ids and len(sequence_ids) == len(selected_ids):
        sequence_complete_count += 1
    else:
        errors.append(f"answer {cid} recommended_sequence must cover precedence order")

    hard_blocks = set(disposition.get("hard_blocks", []))
    required_blocks = set(answer.get("must_not_answer", [])) | set(answer.get("blocked_shortcuts", []))
    hard_block_total += len(required_blocks)
    hard_block_recall += len(required_blocks & hard_blocks)
    if not required_blocks.issubset(hard_blocks):
        errors.append(f"answer {cid} disposition lost hard blocks")

    default_by_route = {d.get("route_id"): d for d in disposition.get("default_moves_by_route", [])}
    actor_by_route = {a.get("route_id"): a for a in disposition.get("actor_assignments", [])}
    for rid in ordered_ids:
        route = selected_by_id.get(rid, {})
        expected_default = route.get("remedy", {}).get("default_move")
        if expected_default:
            default_route_total += 1
            if default_by_route.get(rid, {}).get("default_move") == expected_default and expected_default in set(disposition.get("default_moves", [])):
                default_route_recall += 1
            else:
                errors.append(f"answer {cid} disposition lost default move for {rid}")
        expected_actor = route.get("accountability", {}).get("primary_accountable_actor")
        if expected_actor:
            actor_total += 1
            if actor_by_route.get(rid, {}).get("primary_accountable_actor") == expected_actor:
                actor_recall += 1
            else:
                errors.append(f"answer {cid} disposition lost actor assignment for {rid}")

    disp_sources = set(disposition.get("provenance_source_ids", []))
    answer_sources = set(answer.get("provenance_source_ids", []))
    source_total += len(answer_sources)
    source_recall += len(answer_sources & disp_sources)
    if not answer_sources.issubset(disp_sources):
        errors.append(f"answer {cid} disposition lost provenance sources")

    gate_names = {g.get("gate") for g in precedence.get("global_gates", [])}
    cannot = set(disposition.get("cannot_finalize_until", []))
    required_cannot: Set[str] = set(precedence.get("must_resolve_before_final_answer", []))
    currentness_source_ids = {
        sid
        for gate in precedence.get("global_gates", [])
        if gate.get("gate") == "verify_currentness_before_final_answer"
        for sid in gate.get("source_ids", [])
    }
    currentness_packet_sources = {c.get("source_id") for c in disposition.get("currentness_checks", [])}
    currentness_total += len(currentness_source_ids)
    currentness_recall += len(currentness_source_ids & currentness_packet_sources)
    if currentness_source_ids:
        required_cannot.add("current_law_source_refresh")
        if not currentness_source_ids.issubset(currentness_packet_sources):
            errors.append(f"answer {cid} disposition lost currentness source checks")
        if not disposition.get("source_gate_present"):
            errors.append(f"answer {cid} disposition failed to mark source gate present")

    no_go_required = "do_not_price_or_offset_no_go_harm_without_explicit_override" in gate_names
    if no_go_required:
        no_go_gate_total += 1
        required_cannot.add("explicit_no_go_override_or_prohibition_path")
        if disposition.get("no_go_gate_present") and any("do_not_price_or_offset_no_go_harm_without_explicit_override" in str(b) for b in hard_blocks):
            no_go_gate_recall += 1
        else:
            errors.append(f"answer {cid} disposition lost no-go gate")

    quantitative_route_ids = set()
    for rid in ordered_ids:
        route = selected_by_id.get(rid, {})
        action_family = route.get("policy_action", {}).get("action_family")
        remedy_family = route.get("remedy", {}).get("remedy_family")
        if action_family in REVENUE_OR_PRICE_ACTION_FAMILIES or action_family in ENFORCEMENT_ACTION_FAMILIES or remedy_family in RECORD_REMEDY_FAMILIES:
            quantitative_route_ids.add(rid)
    quantitative_packet_route_ids = {q.get("route_id") for q in disposition.get("quantitative_checks", [])}
    quantitative_total += len(quantitative_route_ids)
    quantitative_recall += len(quantitative_route_ids & quantitative_packet_route_ids)
    if quantitative_route_ids:
        required_cannot.add("quantitative_model_or_distributional_check")
        if not quantitative_route_ids.issubset(quantitative_packet_route_ids):
            errors.append(f"answer {cid} disposition lost quantitative/model checks for {sorted(quantitative_route_ids - quantitative_packet_route_ids)}")

    cannot_finalize_total += len(required_cannot)
    cannot_finalize_recall += len(required_cannot & cannot)
    if not required_cannot.issubset(cannot):
        errors.append(f"answer {cid} cannot_finalize_until is missing {sorted(required_cannot - cannot)}")

summary = cube.get("audit_summary", {})
expected_summary = {
    "disposition_synthesis_required": True,
    "disposition_runtime_status": DISPOSITION_STATUS,
    "disposition_answer_count": answer_count,
    "disposition_packet_count": disposition_packet_count,
    "disposition_ordered_packet_count": ordered_packet_count,
    "disposition_sequence_complete_count": sequence_complete_count,
    "disposition_hard_block_recall_count": hard_block_recall,
    "disposition_hard_block_total": hard_block_total,
    "disposition_default_route_recall_count": default_route_recall,
    "disposition_default_route_total": default_route_total,
    "disposition_actor_assignment_recall_count": actor_recall,
    "disposition_actor_assignment_total": actor_total,
    "disposition_source_recall_count": source_recall,
    "disposition_source_total": source_total,
    "disposition_currentness_recall_count": currentness_recall,
    "disposition_currentness_total": currentness_total,
    "disposition_quantitative_check_recall_count": quantitative_recall,
    "disposition_quantitative_check_total": quantitative_total,
    "disposition_no_go_gate_recall_count": no_go_gate_recall,
    "disposition_no_go_gate_total": no_go_gate_total,
    "disposition_cannot_finalize_recall_count": cannot_finalize_recall,
    "disposition_cannot_finalize_total": cannot_finalize_total,
    "disposition_dominant_counts": dominant_counts,
}
for key, expected_value in expected_summary.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("disposition_synthesis_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json disposition_synthesis_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Disposition runtime status: {DISPOSITION_STATUS}",
        f"Disposition answer packets: {answer_count}",
        f"Disposition packets: {disposition_packet_count}/{answer_count}",
        f"Disposition ordered packets: {ordered_packet_count}/{answer_count}",
        f"Disposition sequence-complete packets: {sequence_complete_count}/{answer_count}",
        f"Hard-block recall: {hard_block_recall}/{hard_block_total}",
        f"Default-move route recall: {default_route_recall}/{default_route_total}",
        f"Actor-assignment route recall: {actor_recall}/{actor_total}",
        f"Source recall: {source_recall}/{source_total}",
        f"Currentness-check recall: {currentness_recall}/{currentness_total}",
        f"Quantitative-check recall: {quantitative_recall}/{quantitative_total}",
        f"No-go gate recall: {no_go_gate_recall}/{no_go_gate_total}",
        f"Cannot-finalize recall: {cannot_finalize_recall}/{cannot_finalize_total}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"disposition synthesis audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("disposition synthesis audit ok")
