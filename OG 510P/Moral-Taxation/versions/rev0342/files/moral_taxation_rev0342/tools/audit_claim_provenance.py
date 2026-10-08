#!/usr/bin/env python3
"""Audit claim-level provenance in emitted answer packets.

Source IDs alone are not enough. This check requires each selected route in the
answer packet to expose the decision claims it is making, the profile field that
supports each claim, and the sources that travel with that claim.
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
CLAIM_STATUS = "profile_index_claim_packets_emitted"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

cube = load_json(root / "cube-index.json")
profile_index = load_json(root / "docs/00-meta/route-profile-index.json")
sources = {s["id"]: s for s in load_json(root / "SOURCES.json").get("sources", [])}
entry_by_id = {e["route_id"]: e for e in profile_index.get("entries", [])}

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
    errors.append(f"answer_case.py failed under claim provenance audit: {exc}")
    payload = {"answers": []}

if payload.get("claim_runtime_status") != CLAIM_STATUS:
    errors.append("answer payload claim_runtime_status is stale")

route_instance_count = 0
claim_packet_total = 0
required_claim_total = 0
required_claim_recall = 0
source_edge_total = 0
source_edge_recall = 0
currentness_claim_total = 0
currentness_claim_recall = 0
claim_packet_complete_answers = 0
missing_claim_examples: List[Dict[str, Any]] = []

required_base_types = {
    "route_classification",
    "policy_category_error",
    "accountability_assignment",
    "remedy_default_and_blocked_move",
}

for answer in payload.get("answers", []):
    answer_claim_packets = answer.get("claim_packets", [])
    answer_claim_keys = {
        (c.get("route_id"), c.get("claim_type"), c.get("claim_text"))
        for c in answer_claim_packets
    }
    answer_complete = True
    if answer.get("claim_runtime_status") != CLAIM_STATUS:
        errors.append(f"answer {answer.get('case_id')} claim_runtime_status is stale")
        answer_complete = False
    if not answer_claim_packets:
        errors.append(f"answer {answer.get('case_id')} has no top-level claim_packets")
        answer_complete = False

    for route_packet in answer.get("selected_routes", []):
        route_instance_count += 1
        rid = route_packet.get("route_id")
        entry = entry_by_id.get(rid, {})
        packets = route_packet.get("claim_packets", [])
        claim_packet_total += len(packets)
        packet_types = {p.get("claim_type") for p in packets}
        required_types = set(required_base_types)
        if entry.get("source_currentness_refs"):
            required_types.add("source_currentness_claim")
        required_claim_total += len(required_types)
        hits = len(required_types & packet_types)
        required_claim_recall += hits
        if hits != len(required_types):
            answer_complete = False
            missing_claim_examples.append({
                "case_id": answer.get("case_id"),
                "route_id": rid,
                "missing_claim_types": sorted(required_types - packet_types),
            })

        primary_sources = set(entry.get("primary_sources", []))
        currentness_refs = set(entry.get("source_currentness_refs", []))
        route_source_edges: Set[tuple[str, str]] = set()
        for packet in packets:
            ctype = packet.get("claim_type")
            claim_text = str(packet.get("claim_text", "")).strip()
            source_ids = packet.get("source_ids", [])
            profile_field = str(packet.get("profile_field", "")).strip()
            if not claim_text:
                errors.append(f"claim packet for {rid} has blank claim_text")
            if not profile_field:
                errors.append(f"claim packet for {rid} has blank profile_field")
            if not source_ids:
                errors.append(f"claim packet for {rid} has no source_ids")
            for sid in source_ids:
                source_edge_total += 1
                if sid in sources and (sid in primary_sources or sid in currentness_refs):
                    source_edge_recall += 1
                else:
                    errors.append(f"claim packet for {rid} cites unsupported source {sid}")
                route_source_edges.add((str(ctype), sid))
            if ctype == "source_currentness_claim":
                currentness_claim_total += 1
                if set(source_ids) & currentness_refs:
                    currentness_claim_recall += 1
                else:
                    errors.append(f"currentness claim packet for {rid} does not cite a currentness ref")
            key = (rid, ctype, packet.get("claim_text"))
            if key not in answer_claim_keys:
                errors.append(f"top-level answer claim_packets lost route claim {key}")

        uncovered_primary = primary_sources - {sid for _, sid in route_source_edges}
        if uncovered_primary:
            errors.append(f"claim packets for {rid} do not expose primary sources {sorted(uncovered_primary)[:8]}")
            answer_complete = False

    if answer_complete:
        claim_packet_complete_answers += 1

if missing_claim_examples:
    errors.append("claim packets missing required claim types: " + json.dumps(missing_claim_examples[:8], separators=(",", ":")))

summary = cube.get("audit_summary", {})
expected_summary = {
    "claim_provenance_required": True,
    "claim_runtime_status": CLAIM_STATUS,
    "claim_packet_answer_count": len(payload.get("answers", [])),
    "claim_packet_route_instance_count": route_instance_count,
    "claim_packet_total": claim_packet_total,
    "claim_packet_required_type_recall_count": required_claim_recall,
    "claim_packet_required_type_total": required_claim_total,
    "claim_packet_source_edge_recall_count": source_edge_recall,
    "claim_packet_source_edge_total": source_edge_total,
    "claim_packet_currentness_recall_count": currentness_claim_recall,
    "claim_packet_currentness_total": currentness_claim_total,
    "claim_packet_complete_answer_count": claim_packet_complete_answers,
}
for key, expected_value in expected_summary.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("claim_provenance_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json claim_provenance_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Claim runtime status: {CLAIM_STATUS}",
        f"Claim-bearing answer packets: {len(payload.get('answers', []))}",
        f"Claim route instances: {route_instance_count}",
        f"Claim packets: {claim_packet_total}",
        f"Required claim-type recall: {required_claim_recall}/{required_claim_total}",
        f"Claim source-edge recall: {source_edge_recall}/{source_edge_total}",
        f"Currentness claim recall: {currentness_claim_recall}/{currentness_claim_total}",
        f"Complete claim-packet answers: {claim_packet_complete_answers}/{len(payload.get('answers', []))}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"claim provenance audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("claim provenance audit ok")
