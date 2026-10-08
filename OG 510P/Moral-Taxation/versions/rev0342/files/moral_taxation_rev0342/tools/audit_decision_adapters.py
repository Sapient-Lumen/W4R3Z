#!/usr/bin/env python3
"""Audit current-law, jurisdiction-scope, delivery, and model adapters.

This checks the riskiest post-disposition boundary: the archive must not make a
final practical recommendation while pretending that volatile law, jurisdiction,
protected-floor delivery, or quantitative modeling has been performed. The audit
recomputes adapter obligations from selected route packets and the currentness
registry; it does not read case contracts or expected answers.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Set, Tuple

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
ADAPTER_STATUS = "decision_adapter_requirements_resolved"
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def adapter_key(packet: Dict[str, Any]) -> Tuple[str, str, str, str]:
    return (
        str(packet.get("adapter_type", "")),
        str(packet.get("route_id", "")),
        str(packet.get("source_id", "")),
        str(packet.get("model_class", packet.get("scope", ""))),
    )


cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
registry = json.loads((root / "docs/00-meta/source-currentness-registry.json").read_text(encoding="utf-8")).get("entries", [])
adapters = load_module("resolve_decision_adapters", root / "tools/resolve_decision_adapters.py")
answer_source = (root / "tools/answer_case.py").read_text(encoding="utf-8")
for required in [
    "resolve_current_law_jurisdiction_and_model_adapters",
    "decision_adapter_runtime_status",
    "adapter_summary",
]:
    if required not in answer_source:
        errors.append(f"answer_case.py must expose adapter boundary marker {required!r}")

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
    errors.append(f"answer_case.py failed under decision-adapter audit: {exc}")
    payload = {"answers": []}

if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
if payload.get("decision_adapter_runtime_status") != ADAPTER_STATUS:
    errors.append("answer payload decision_adapter_runtime_status is stale")

as_of_date = adapters.as_of_date_from_root(root)
answer_count = len(payload.get("answers", []))
adapter_packet_count = 0
adapter_complete_answer_count = 0
route_instance_count = 0
adapter_total = 0
adapter_recall = 0
current_law_total = 0
current_law_recall = 0
current_law_due_soon_total = 0
current_law_due_soon_recall = 0
jurisdiction_total = 0
jurisdiction_recall = 0
quantitative_total = 0
quantitative_recall = 0
floor_total = 0
floor_recall = 0
no_go_total = 0
no_go_recall = 0
cannot_total = 0
cannot_recall = 0
type_counts: Dict[str, int] = {}
due_state_counts: Dict[str, int] = {}

for answer in payload.get("answers", []):
    cid = answer.get("case_id")
    if answer.get("decision_adapter_runtime_status") != ADAPTER_STATUS:
        errors.append(f"answer {cid} decision_adapter_runtime_status is stale")
    steps = {s.get("step") for s in answer.get("answer_steps", [])}
    if "resolve_current_law_jurisdiction_and_model_adapters" not in steps:
        errors.append(f"answer {cid} missing adapter answer step")
    disposition = answer.get("disposition", {})
    if disposition.get("adapter_runtime_status") != ADAPTER_STATUS:
        errors.append(f"answer {cid} disposition adapter_runtime_status is stale")
    selected_routes = answer.get("selected_routes", [])
    route_instance_count += len(selected_routes)
    expected = adapters.adapter_checks_for_routes(selected_routes, registry, as_of_date)
    actual = disposition.get("adapter_checks", [])
    actual_keys = {adapter_key(packet) for packet in actual}
    expected_keys = {adapter_key(packet) for packet in expected}
    adapter_total += len(expected_keys)
    adapter_recall += len(expected_keys & actual_keys)
    adapter_packet_count += 1 if actual else 0
    if expected_keys == actual_keys:
        adapter_complete_answer_count += 1
    else:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        errors.append(f"answer {cid} adapter obligations drift missing={missing[:8]} extra={extra[:8]}")

    expected_summary = adapters.summarize_adapter_checks(expected)
    if disposition.get("adapter_summary") != expected_summary:
        errors.append(f"answer {cid} adapter_summary is stale")

    for packet in expected:
        typ = packet.get("adapter_type")
        type_counts[str(typ)] = type_counts.get(str(typ), 0) + 1
        if typ == "current_law_refresh_adapter":
            current_law_total += 1
            if adapter_key(packet) in actual_keys:
                current_law_recall += 1
            state = str(packet.get("review_due_state"))
            due_state_counts[state] = due_state_counts.get(state, 0) + 1
            if state in {"overdue", "due_soon"}:
                current_law_due_soon_total += 1
                if adapter_key(packet) in actual_keys:
                    current_law_due_soon_recall += 1
        elif typ == "jurisdiction_scope_adapter":
            jurisdiction_total += 1
            if adapter_key(packet) in actual_keys:
                jurisdiction_recall += 1
        elif typ == "quantitative_model_adapter":
            quantitative_total += 1
            if adapter_key(packet) in actual_keys:
                quantitative_recall += 1
        elif typ == "floor_delivery_adapter":
            floor_total += 1
            if adapter_key(packet) in actual_keys:
                floor_recall += 1
        elif typ == "no_go_threshold_adapter":
            no_go_total += 1
            if adapter_key(packet) in actual_keys:
                no_go_recall += 1

    currentness_source_ids = {c.get("source_id") for c in disposition.get("currentness_checks", []) if c.get("source_id")}
    current_law_adapter_source_ids = {c.get("source_id") for c in actual if c.get("adapter_type") == "current_law_refresh_adapter"}
    if not currentness_source_ids.issubset(current_law_adapter_source_ids):
        errors.append(f"answer {cid} has currentness checks not represented in current-law adapters")

    quantitative_route_ids = {q.get("route_id") for q in disposition.get("quantitative_checks", []) if q.get("route_id")}
    quantitative_adapter_route_ids = {c.get("route_id") for c in actual if c.get("adapter_type") == "quantitative_model_adapter"}
    if not quantitative_route_ids.issubset(quantitative_adapter_route_ids):
        errors.append(f"answer {cid} has quantitative checks not represented in quantitative adapters")

    required_markers: Set[str] = set(adapters.cannot_finalize_markers(expected))
    cannot = set(disposition.get("cannot_finalize_until", []))
    cannot_total += len(required_markers)
    cannot_recall += len(required_markers & cannot)
    if not required_markers.issubset(cannot):
        errors.append(f"answer {cid} cannot_finalize_until missing adapter markers {sorted(required_markers - cannot)}")

expected_summary_pairs = {
    "decision_adapters_required": True,
    "decision_adapter_runtime_status": ADAPTER_STATUS,
    "decision_adapter_answer_count": answer_count,
    "decision_adapter_packet_count": adapter_packet_count,
    "decision_adapter_complete_answer_count": adapter_complete_answer_count,
    "decision_adapter_route_instance_count": route_instance_count,
    "decision_adapter_check_recall_count": adapter_recall,
    "decision_adapter_check_total": adapter_total,
    "decision_adapter_current_law_recall_count": current_law_recall,
    "decision_adapter_current_law_total": current_law_total,
    "decision_adapter_current_law_due_soon_recall_count": current_law_due_soon_recall,
    "decision_adapter_current_law_due_soon_total": current_law_due_soon_total,
    "decision_adapter_jurisdiction_recall_count": jurisdiction_recall,
    "decision_adapter_jurisdiction_total": jurisdiction_total,
    "decision_adapter_quantitative_recall_count": quantitative_recall,
    "decision_adapter_quantitative_total": quantitative_total,
    "decision_adapter_floor_delivery_recall_count": floor_recall,
    "decision_adapter_floor_delivery_total": floor_total,
    "decision_adapter_no_go_threshold_recall_count": no_go_recall,
    "decision_adapter_no_go_threshold_total": no_go_total,
    "decision_adapter_cannot_finalize_recall_count": cannot_recall,
    "decision_adapter_cannot_finalize_total": cannot_total,
    "decision_adapter_type_counts": dict(sorted(type_counts.items())),
    "decision_adapter_current_law_review_due_state_counts": dict(sorted(due_state_counts.items())),
    "decision_adapter_as_of_date": as_of_date,
}
summary = cube.get("audit_summary", {})
for key, expected_value in expected_summary_pairs.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("decision_adapter_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json decision_adapter_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Decision-adapter runtime status: {ADAPTER_STATUS}",
        f"Decision-adapter answer packets: {answer_count}",
        f"Adapter packets: {adapter_packet_count}/{answer_count}",
        f"Complete adapter answers: {adapter_complete_answer_count}/{answer_count}",
        f"Adapter route instances: {route_instance_count}",
        f"Adapter check recall: {adapter_recall}/{adapter_total}",
        f"Current-law adapter recall: {current_law_recall}/{current_law_total}",
        f"Due-soon current-law adapter recall: {current_law_due_soon_recall}/{current_law_due_soon_total}",
        f"Jurisdiction adapter recall: {jurisdiction_recall}/{jurisdiction_total}",
        f"Quantitative adapter recall: {quantitative_recall}/{quantitative_total}",
        f"Floor-delivery adapter recall: {floor_recall}/{floor_total}",
        f"No-go-threshold adapter recall: {no_go_recall}/{no_go_total}",
        f"Adapter cannot-finalize recall: {cannot_recall}/{cannot_total}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"decision-adapter audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("decision adapter audit ok")
