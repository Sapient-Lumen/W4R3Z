#!/usr/bin/env python3
"""Audit the answer-emission runtime boundary.

The router already proves that expected route candidates can be recovered. This
check proves the next layer: answer_case.py converts those candidates into a
profile-backed answer packet without reading answer contracts, and without
losing remedy, accountability, blocked-shortcut, or source obligations.
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
version = (root / "VERSION").read_text(encoding="utf-8").strip()
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
golden = json.loads((root / "docs/00-meta/golden-cases.json").read_text(encoding="utf-8"))
contracts_doc = json.loads((root / "docs/00-meta/case-contracts.json").read_text(encoding="utf-8"))
remedies = {p["route_id"]: p for p in json.loads((root / "docs/00-meta/remedy-profiles.json").read_text(encoding="utf-8")).get("profiles", [])}
actions = {p["route_id"]: p for p in json.loads((root / "docs/00-meta/policy-action-profiles.json").read_text(encoding="utf-8")).get("profiles", [])}
actors = {p["route_id"]: p for p in json.loads((root / "docs/00-meta/actor-accountability-profiles.json").read_text(encoding="utf-8")).get("profiles", [])}
sources = {s["id"]: s for s in json.loads((root / "SOURCES.json").read_text(encoding="utf-8")).get("sources", [])}
route_by_id = {r["id"]: r for r in cube.get("route_records", [])}
case_by_id = {c["case_id"]: c for c in golden.get("cases", [])}
active_contracts = [c for c in contracts_doc.get("contracts", []) if c.get("status") == "active"]

answer_source = (root / "tools/answer_case.py").read_text(encoding="utf-8")
for forbidden in [
    "case-contracts",
    "case_contracts",
    "case-contract-schema",
    "expected_route_ids",
    "expected_flags",
    "required_route_families",
    "required_remedy_profiles",
]:
    if forbidden in answer_source:
        errors.append(f"answer_case.py must not read or reference contract answer field {forbidden!r}")

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
    errors.append(f"answer_case.py failed: {exc}")
    payload = {"answers": []}

if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer_case.py returned stale runtime_status")
if payload.get("route_limit") != ROUTE_LIMIT:
    errors.append("answer_case.py returned stale route_limit")
if payload.get("facts_only_candidate_limit") != FACTS_ONLY_LIMIT:
    errors.append("answer_case.py returned stale facts-only candidate limit")
answers = payload.get("answers", [])
answer_by_id = {a.get("case_id"): a for a in answers}
if len(answer_by_id) != len(active_contracts):
    errors.append("answer_case.py answer count must match active case-contract count")

expected_route_total = 0
expected_route_recall = 0
candidate_misses = []
must_not_total = 0
must_not_recall = 0
blocked_obligation_total = 0
blocked_obligation_recall = 0
profile_obligation_total = 0
profile_obligation_recall = 0
source_obligation_total = 0
source_obligation_recall = 0
currentness_obligation_total = 0
currentness_obligation_recall = 0
step_complete_cases = 0
contract_free_cases = 0
source_packet_complete_cases = 0
profile_packet_complete_cases = 0

required_steps = {
    "classify_action_and_route",
    "assign_real_accountability_before_collection_or_compensation",
    "block_category_errors_and_prohibited_shortcuts",
    "apply_default_moves_with_guardrails",
    "resolve_precedence_before_disposition",
    "verify_sources_currentness_and_unresolved_model_gaps",
    "resolve_current_law_jurisdiction_and_model_adapters",
}

for con in active_contracts:
    cid = con.get("case_id")
    answer = answer_by_id.get(cid)
    case = case_by_id.get(cid, {})
    expected: Set[str] = set(con.get("expected_route_ids", []))
    expected_route_total += len(expected)
    if not answer:
        candidate_misses.append({"case_id": cid, "missing": sorted(expected), "candidates": []})
        continue

    if answer.get("runtime_status") == ANSWER_STATUS:
        contract_free_cases += 1
    selected_ids = answer.get("routing", {}).get("selected_route_ids", [])
    selected_set = set(selected_ids)
    if expected.issubset(selected_set):
        expected_route_recall += len(expected)
    else:
        expected_route_recall += len(expected & selected_set)
        candidate_misses.append({"case_id": cid, "missing": sorted(expected - selected_set), "candidates": selected_ids})

    selected_packets = {r.get("route_id"): r for r in answer.get("selected_routes", [])}
    if set(selected_packets) != selected_set:
        errors.append(f"answer {cid} selected_routes must match routing.selected_route_ids")
    if len(selected_ids) > ROUTE_LIMIT:
        errors.append(f"answer {cid} selected route count exceeds route limit")
    if len(selected_ids) != len(set(selected_ids)):
        errors.append(f"answer {cid} selected routes contain duplicates")

    steps = {s.get("step") for s in answer.get("answer_steps", [])}
    if required_steps.issubset(steps):
        step_complete_cases += 1
    else:
        errors.append(f"answer {cid} is missing required answer steps {sorted(required_steps - steps)}")

    blocked = set(answer.get("blocked_shortcuts", []))
    must_not = set(case.get("must_not_answer", []))
    must_not_total += len(must_not)
    must_not_recall += len(must_not & blocked)
    if answer.get("must_not_answer") != case.get("must_not_answer", []):
        errors.append(f"answer {cid} must_not_answer must mirror golden case warnings")

    provenance_ids = set(answer.get("provenance_source_ids", []))
    source_packet_ids = {s.get("source_id") for s in answer.get("source_packet", [])}
    case_source_ids = set(case.get("source_ids", []))
    if case_source_ids.issubset(provenance_ids) and provenance_ids == source_packet_ids:
        source_packet_complete_cases += 1
    else:
        errors.append(f"answer {cid} source packet does not cover case/provenance sources")
    for sid in provenance_ids:
        source_obligation_total += 1
        if sid in sources and sid in source_packet_ids:
            source_obligation_recall += 1
        else:
            errors.append(f"answer {cid} cites missing source {sid}")

    expected_profile_ok = True
    for rid in selected_ids:
        route = route_by_id.get(rid)
        remedy = remedies.get(rid)
        action = actions.get(rid)
        actor = actors.get(rid)
        packet = selected_packets.get(rid, {})
        profile_obligation_total += 3
        if not route or not remedy or not action or not actor:
            expected_profile_ok = False
            errors.append(f"answer {cid} selected route {rid} lacks live route/remedy/action/actor profile")
            continue
        if packet.get("remedy", {}).get("default_move") == remedy.get("default_move"):
            profile_obligation_recall += 1
        else:
            expected_profile_ok = False
            errors.append(f"answer {cid} route {rid} lost remedy default_move")
        if packet.get("policy_action", {}).get("action_family") == action.get("action_family"):
            profile_obligation_recall += 1
        else:
            expected_profile_ok = False
            errors.append(f"answer {cid} route {rid} lost policy action_family")
        if packet.get("accountability", {}).get("primary_accountable_actor") == actor.get("primary_accountable_actor"):
            profile_obligation_recall += 1
        else:
            expected_profile_ok = False
            errors.append(f"answer {cid} route {rid} lost primary accountable actor")

        for value in [remedy.get("blocked_move"), action.get("category_error_to_block")]:
            if not value:
                continue
            blocked_obligation_total += 1
            if value in blocked:
                blocked_obligation_recall += 1
            else:
                errors.append(f"answer {cid} route {rid} failed to expose blocked shortcut {value!r}")

        route_sources = set(route.get("primary_sources", []))
        for sid in route_sources:
            source_obligation_total += 1
            if sid in provenance_ids and sid in source_packet_ids and sid in sources:
                source_obligation_recall += 1
            else:
                errors.append(f"answer {cid} route {rid} primary source {sid} not exposed in source packet")

        currentness_refs = set(route.get("source_currentness_refs", []))
        claims = {
            c.get("source_id")
            for c in packet.get("provenance", {}).get("source_currentness_claims", [])
        }
        for sid in currentness_refs:
            currentness_obligation_total += 1
            if sid in provenance_ids and sid in claims:
                currentness_obligation_recall += 1
            else:
                errors.append(f"answer {cid} route {rid} currentness source {sid} not exposed with route claim")

    if expected_profile_ok:
        profile_packet_complete_cases += 1

if candidate_misses:
    errors.append("answer packets missed expected route candidates: " + json.dumps(candidate_misses[:8], separators=(",", ":")))

summary = cube.get("audit_summary", {})
expected_summary_pairs = {
    "answer_skeletons_required": True,
    "answer_skeleton_runtime_status": ANSWER_STATUS,
    "answer_skeleton_case_count": len(active_contracts),
    "answer_skeleton_route_limit": ROUTE_LIMIT,
    "answer_skeleton_facts_only_candidate_limit": FACTS_ONLY_LIMIT,
    "answer_skeleton_expected_route_recall_count": expected_route_recall,
    "answer_skeleton_expected_route_total": expected_route_total,
    "answer_skeleton_candidate_miss_count": len(candidate_misses),
    "answer_skeleton_must_not_recall_count": must_not_recall,
    "answer_skeleton_must_not_total": must_not_total,
    "answer_skeleton_blocked_shortcut_recall_count": blocked_obligation_recall,
    "answer_skeleton_blocked_shortcut_total": blocked_obligation_total,
    "answer_skeleton_profile_obligation_recall_count": profile_obligation_recall,
    "answer_skeleton_profile_obligation_total": profile_obligation_total,
    "answer_skeleton_source_obligation_recall_count": source_obligation_recall,
    "answer_skeleton_source_obligation_total": source_obligation_total,
    "answer_skeleton_currentness_obligation_recall_count": currentness_obligation_recall,
    "answer_skeleton_currentness_obligation_total": currentness_obligation_total,
    "answer_skeleton_step_complete_case_count": step_complete_cases,
    "answer_skeleton_contract_free_case_count": contract_free_cases,
    "answer_skeleton_source_packet_complete_case_count": source_packet_complete_cases,
    "answer_skeleton_profile_packet_complete_case_count": profile_packet_complete_cases,
}
for key, expected_value in expected_summary_pairs.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("answer_skeleton_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json answer_skeleton_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Answer runtime status: {ANSWER_STATUS}",
        f"Answer packets: {len(active_contracts)}",
        f"Answer route-limit recall: {expected_route_recall}/{expected_route_total}",
        f"Answer candidate misses: {len(candidate_misses)}",
        f"Must-not-answer recall: {must_not_recall}/{must_not_total}",
        f"Blocked-shortcut recall: {blocked_obligation_recall}/{blocked_obligation_total}",
        f"Profile-obligation recall: {profile_obligation_recall}/{profile_obligation_total}",
        f"Source-obligation recall: {source_obligation_recall}/{source_obligation_total}",
        f"Currentness-obligation recall: {currentness_obligation_recall}/{currentness_obligation_total}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"answer skeleton audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("answer skeleton audit ok")
