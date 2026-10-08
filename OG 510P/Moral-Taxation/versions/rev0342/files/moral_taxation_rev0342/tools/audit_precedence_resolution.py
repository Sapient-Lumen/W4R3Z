#!/usr/bin/env python3
"""Audit the precedence-resolution runtime boundary.

Candidate recall is not enough: when selected routes collide, answer_case.py must
turn them into a decision order. This audit checks that ordering is produced by
tools/resolve_precedence.py, is attached to every answer packet, and preserves
higher-order gates such as no-go harms, protected floors, actor assignment,
contest/record correction, and source currentness before ordinary revenue or
collection moves.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Dict, List

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
PRECEDENCE_STATUS = "precedence_resolver_invoked"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_resolver():
    spec = importlib.util.spec_from_file_location("resolve_precedence", root / "tools/resolve_precedence.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load resolve_precedence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module

cube = load_json(root / "cube-index.json")
profile_index = load_json(root / "docs/00-meta/route-profile-index.json")
profile_by_id = {e["route_id"]: e for e in profile_index.get("entries", [])}
resolver = load_resolver()

answer_source = (root / "tools/answer_case.py").read_text(encoding="utf-8")
if "resolve_precedence.py" not in answer_source or "resolve_precedence_before_disposition" not in answer_source:
    errors.append("answer_case.py must use tools/resolve_precedence.py and expose a precedence answer step")
if "def precedence_label" in answer_source:
    errors.append("answer_case.py must not keep the old inline precedence_label helper")
if "candidate ranking is not final precedence resolution" in answer_source:
    errors.append("answer_case.py still exposes stale no-precedence limitation text")

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
    errors.append(f"answer_case.py failed under precedence audit: {exc}")
    payload = {"answers": []}

if payload.get("precedence_runtime_status") != PRECEDENCE_STATUS:
    errors.append("answer payload precedence_runtime_status is stale")

answer_count = len(payload.get("answers", []))
route_instance_count = 0
ordered_case_count = 0
sorted_case_count = 0
order_changed_case_count = 0
triggered_rule_case_count = 0
triggered_rule_total = 0
currentness_gate_case_count = 0
no_go_gate_case_count = 0
band_counts: Dict[str, int] = {}
rule_counts: Dict[str, int] = {}

for answer in payload.get("answers", []):
    cid = answer.get("case_id")
    selected_routes = answer.get("selected_routes", [])
    selected_ids = answer.get("routing", {}).get("selected_route_ids", [])
    resolution = answer.get("precedence_resolution", {})
    if answer.get("precedence_runtime_status") != PRECEDENCE_STATUS:
        errors.append(f"answer {cid} precedence_runtime_status is stale")
    if resolution.get("runtime_status") != PRECEDENCE_STATUS:
        errors.append(f"answer {cid} precedence_resolution runtime_status is stale")
    if not selected_ids:
        errors.append(f"answer {cid} has no selected route ids")
        continue

    selected_items = [{"route_id": r.get("route_id"), "score": r.get("score")} for r in selected_routes]
    expected = resolver.resolve_precedence(selected_items, profile_by_id)
    ordered_ids = resolution.get("ordered_route_ids", [])
    expected_ids = expected.get("ordered_route_ids", [])
    if ordered_ids != expected_ids:
        errors.append(f"answer {cid} precedence order drifted expected={expected_ids} actual={ordered_ids}")
    if set(ordered_ids) != set(selected_ids) or len(ordered_ids) != len(selected_ids):
        errors.append(f"answer {cid} precedence ordered ids must be a permutation of selected ids")
    else:
        ordered_case_count += 1
    if ordered_ids != selected_ids:
        order_changed_case_count += 1

    steps = resolution.get("ordered_steps", [])
    if answer.get("precedence_order") != steps:
        errors.append(f"answer {cid} precedence_order must mirror precedence_resolution.ordered_steps")
    bands = [int(s.get("precedence_band")) for s in steps]
    if bands == sorted(bands):
        sorted_case_count += 1
    else:
        errors.append(f"answer {cid} precedence bands are not sorted: {bands}")
    if steps and steps[0].get("precedence_label") != resolution.get("dominant_precedence_label"):
        errors.append(f"answer {cid} dominant precedence label does not match first ordered step")

    step_names = {s.get("step") for s in answer.get("answer_steps", [])}
    if "resolve_precedence_before_disposition" not in step_names:
        errors.append(f"answer {cid} missing resolve_precedence_before_disposition answer step")

    triggered_rules = resolution.get("triggered_rules", [])
    if triggered_rules:
        triggered_rule_case_count += 1
    triggered_rule_total += len(triggered_rules)
    for rule in triggered_rules:
        rule_counts[rule] = rule_counts.get(rule, 0) + 1
    gate_names = {g.get("gate") for g in resolution.get("global_gates", [])}
    if "verify_currentness_before_final_answer" in gate_names:
        currentness_gate_case_count += 1
    if "do_not_price_or_offset_no_go_harm_without_explicit_override" in gate_names:
        no_go_gate_case_count += 1

    no_go_positions = [i for i, s in enumerate(steps) if s.get("features", {}).get("no_go")]
    revenue_or_comp_positions = [
        i for i, s in enumerate(steps)
        if s.get("features", {}).get("action_family") in (resolver.REVENUE_ACTION_FAMILIES | resolver.COMPENSATION_ACTION_FAMILIES)
        and not s.get("features", {}).get("no_go")
    ]
    if no_go_positions and revenue_or_comp_positions and min(no_go_positions) > min(revenue_or_comp_positions):
        errors.append(f"answer {cid} lets pricing/compensation precede no-go route")
    floor_positions = [i for i, s in enumerate(steps) if s.get("features", {}).get("protected_floor")]
    collection_positions = [
        i for i, s in enumerate(steps)
        if s.get("features", {}).get("action_family") in resolver.COLLECTION_ACTION_FAMILIES
        and not s.get("features", {}).get("protected_floor")
        and not s.get("features", {}).get("no_go")
    ]
    if floor_positions and collection_positions and min(floor_positions) > min(collection_positions):
        errors.append(f"answer {cid} lets collection precede protected-floor route")
    actor_positions = [i for i, s in enumerate(steps) if s.get("features", {}).get("actor_assignment")]
    liability_or_comp_positions = [
        i for i, s in enumerate(steps)
        if s.get("features", {}).get("action_family") in (resolver.COLLECTION_ACTION_FAMILIES | resolver.REVENUE_ACTION_FAMILIES | resolver.COMPENSATION_ACTION_FAMILIES)
        and not s.get("features", {}).get("no_go")
        and not s.get("features", {}).get("source_gate")
        and not s.get("features", {}).get("protected_floor")
        and not s.get("features", {}).get("actor_assignment")
    ]
    if actor_positions and liability_or_comp_positions and min(actor_positions) > min(liability_or_comp_positions):
        errors.append(f"answer {cid} lets collection/compensation precede actor assignment")

    for route_packet in selected_routes:
        route_instance_count += 1
        rid = route_packet.get("route_id")
        precedence = route_packet.get("precedence", {})
        expected_precedence = resolver.classify_precedence(profile_by_id.get(rid, {}))
        if precedence.get("precedence_band") != expected_precedence.get("precedence_band"):
            errors.append(f"answer {cid} route {rid} precedence band drifted")
        if route_packet.get("precedence_label") != precedence.get("precedence_label"):
            errors.append(f"answer {cid} route {rid} precedence label shorthand drifted")
        band_key = str(precedence.get("precedence_band"))
        band_counts[band_key] = band_counts.get(band_key, 0) + 1

summary = cube.get("audit_summary", {})
expected_summary = {
    "precedence_resolution_required": True,
    "precedence_runtime_status": PRECEDENCE_STATUS,
    "precedence_answer_count": answer_count,
    "precedence_route_instance_count": route_instance_count,
    "precedence_ordered_case_count": ordered_case_count,
    "precedence_sorted_case_count": sorted_case_count,
    "precedence_order_changed_case_count": order_changed_case_count,
    "precedence_triggered_rule_case_count": triggered_rule_case_count,
    "precedence_triggered_rule_total": triggered_rule_total,
    "precedence_currentness_gate_case_count": currentness_gate_case_count,
    "precedence_no_go_gate_case_count": no_go_gate_case_count,
    "precedence_band_counts": band_counts,
    "precedence_triggered_rule_counts": rule_counts,
}
for key, expected_value in expected_summary.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("precedence_resolution_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json precedence_resolution_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Precedence runtime status: {PRECEDENCE_STATUS}",
        f"Precedence answer packets: {answer_count}",
        f"Precedence route instances: {route_instance_count}",
        f"Precedence ordered cases: {ordered_case_count}/{answer_count}",
        f"Precedence sorted cases: {sorted_case_count}/{answer_count}",
        f"Precedence changed candidate order: {order_changed_case_count}",
        f"Precedence triggered-rule cases: {triggered_rule_case_count}",
        f"Precedence triggered rules: {triggered_rule_total}",
        f"Currentness gate cases: {currentness_gate_case_count}",
        f"No-go gate cases: {no_go_gate_case_count}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"precedence audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("precedence resolution audit ok")
