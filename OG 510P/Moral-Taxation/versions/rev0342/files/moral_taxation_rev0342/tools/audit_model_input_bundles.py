#!/usr/bin/env python3
"""Audit explicit model-input bundles.

This audit blocks the dangerous shortcut where a quantitative, delivery, or
no-go output is produced from an adapter id or route label alone. Model evidence
must be backed by an explicit input record with values, units, assumptions,
uncertainty parameters, and a stable hash.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Mapping

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
RUNTIME_STATUS = "explicit_model_input_bundle_generated"
RUNNER_STATUS = "evidence_producer_runner_invoked"
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
MODEL_ADAPTER_TYPES = {"quantitative_model_adapter", "floor_delivery_adapter", "no_go_threshold_adapter"}


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def load_answers() -> Dict[str, Any]:
    cache_path = os.environ.get("MT_ANSWER_PACKET_CACHE")
    if cache_path and pathlib.Path(cache_path).exists():
        raw = pathlib.Path(cache_path).read_text(encoding="utf-8")
    else:
        raw = subprocess.check_output(
            [sys.executable, str(root / "tools/answer_case.py"), str(root), "--all", "--route-limit", str(ROUTE_LIMIT), "--facts-only-candidate-limit", str(FACTS_ONLY_LIMIT), "--json"],
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    return json.loads(raw)


cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
input_builder = load_module("build_model_input_bundle", root / "tools/build_model_input_bundle.py")
runner = load_module("run_evidence_producers", root / "tools/run_evidence_producers.py")
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")

builder_source = (root / "tools/build_model_input_bundle.py").read_text(encoding="utf-8")
if RUNTIME_STATUS not in builder_source:
    errors.append("build_model_input_bundle.py must expose explicit model input runtime status")
if "adapter ids alone" not in builder_source:
    errors.append("build_model_input_bundle.py must document the adapter-shape shortcut it blocks")
if "model_input_record_hash" not in (root / "tools/execute_decision_adapters.py").read_text(encoding="utf-8"):
    errors.append("execute_decision_adapters.py must require model_input_record_hash for model evidence")

payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
answer_count = len(answers)
adapter_checks = [c for a in answers for c in a.get("disposition", {}).get("adapter_checks", [])]
model_checks = [c for c in adapter_checks if c.get("adapter_type") in MODEL_ADAPTER_TYPES]
model_adapter_count = len(model_checks)
type_counts: Dict[str, int] = {}
for packet in model_checks:
    typ = str(packet.get("adapter_type"))
    type_counts[typ] = type_counts.get(typ, 0) + 1

bundle = input_builder.bundle_for_answers(answers, as_of_date)
summary = bundle.get("summary", {})
records = bundle.get("model_inputs", {})
complete_records = 0
hash_records = 0
non_doctrine_records = 0
for aid, record in records.items():
    required = ["bundle_id", "adapter_id", "adapter_type", "route_id", "model_class", "required_outputs", "input_values", "units", "assumptions", "uncertainty_parameters", "assumption_set_id", "input_locator", "created_at", "input_record_hash", "hash_basis"]
    if all(record.get(field) not in (None, "", [], {}) for field in required):
        complete_records += 1
    if record.get("input_record_hash") and record.get("hash_basis") == "explicit_model_input_bundle":
        hash_records += 1
    if "do not copy values into route doctrine" in str(record.get("non_doctrine_warning")):
        non_doctrine_records += 1

runner_no_input = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date)
runner_with_input = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date, model_input_bundle=bundle)
exec_with_input = [executor.execute_answer(answer, runner_with_input) for answer in answers]
results_with_input = [r for packet in exec_with_input for r in packet.get("adapter_execution_results", [])]
model_input_satisfied = sum(1 for r in results_with_input if r.get("adapter_type") in {"quantitative_model_adapter", "floor_delivery_adapter"} and r.get("execution_status") == executor.STATUS_SATISFIED)
model_input_no_go_block = sum(1 for r in results_with_input if r.get("adapter_type") == "no_go_threshold_adapter" and r.get("execution_status") == executor.STATUS_BLOCKS)
model_input_proof_results = sum(1 for r in results_with_input if r.get("adapter_type") in MODEL_ADAPTER_TYPES and r.get("producer_id"))

legacy_bundle = copy.deepcopy(runner_with_input)
for evidence in legacy_bundle.get("adapter_evidence", {}).values():
    if isinstance(evidence, dict) and evidence.get("evidence_kind") in MODEL_ADAPTER_TYPES:
        for key in ["model_input_bundle_id", "model_input_record_hash", "input_hash_basis", "input_locator", "assumption_set_id", "input_values_hash"]:
            evidence.pop(key, None)
        evidence["inputs_hash"] = "legacy-shape-only-inputs"
legacy_exec = [executor.execute_answer(answer, legacy_bundle) for answer in answers]
legacy_results = [r for packet in legacy_exec for r in packet.get("adapter_execution_results", [])]
legacy_blocked = sum(1 for r in legacy_results if r.get("adapter_type") in MODEL_ADAPTER_TYPES and r.get("execution_status") in {executor.STATUS_INCOMPLETE, executor.STATUS_INPUT_HASH_MISMATCH})

if bundle.get("runtime_status") != RUNTIME_STATUS:
    errors.append("model input bundle runtime status is stale")
if summary.get("model_input_count") != model_adapter_count:
    errors.append("model input bundle must have one record per model-style adapter")
if complete_records != model_adapter_count:
    errors.append("every model input record must include values, units, assumptions, uncertainty, locator, and hash")
if hash_records != model_adapter_count:
    errors.append("every model input record must use explicit_model_input_bundle hash basis")
if non_doctrine_records != model_adapter_count:
    errors.append("every model input record must carry a non-doctrine warning")
if runner_no_input.get("summary", {}).get("evidence_count") != 0:
    errors.append("producer runner without a model-input bundle must not create model evidence")
if runner_no_input.get("summary", {}).get("skipped_count") != len(adapter_checks):
    errors.append("producer runner without model inputs must skip all adapter checks in local-model mode")
if runner_with_input.get("runtime_status") != RUNNER_STATUS:
    errors.append("producer runner with model inputs has stale runtime status")
if runner_with_input.get("summary", {}).get("evidence_count") != model_adapter_count:
    errors.append("producer runner with explicit inputs must produce model evidence for every model adapter")
if model_input_satisfied != type_counts.get("quantitative_model_adapter", 0) + type_counts.get("floor_delivery_adapter", 0):
    errors.append("explicit input bundle should satisfy quantitative and floor-delivery model adapters")
if model_input_no_go_block != type_counts.get("no_go_threshold_adapter", 0):
    errors.append("explicit local no-go inputs must still block no-go threshold clearance")
if model_input_proof_results != model_adapter_count:
    errors.append("every executed model result from explicit inputs must carry registered producer metadata")
if legacy_blocked != model_adapter_count:
    errors.append("legacy model evidence without explicit input proof must be blocked for every model adapter")

cube_summary = cube.get("audit_summary", {})
expected_summary_pairs = {
    "model_input_bundle_required": True,
    "model_input_runtime_status": RUNTIME_STATUS,
    "model_input_answer_count": answer_count,
    "model_input_adapter_count": model_adapter_count,
    "model_input_record_count": summary.get("model_input_count"),
    "model_input_complete_record_count": complete_records,
    "model_input_hash_record_count": hash_records,
    "model_input_non_doctrine_record_count": non_doctrine_records,
    "model_input_runner_without_inputs_evidence_count": runner_no_input.get("summary", {}).get("evidence_count"),
    "model_input_runner_without_inputs_skipped_count": runner_no_input.get("summary", {}).get("skipped_count"),
    "model_input_runner_with_inputs_evidence_count": runner_with_input.get("summary", {}).get("evidence_count"),
    "model_input_runner_with_inputs_satisfied_count": model_input_satisfied,
    "model_input_runner_with_inputs_no_go_block_count": model_input_no_go_block,
    "model_input_legacy_shape_only_blocked_count": legacy_blocked,
    "model_input_adapter_type_counts": dict(sorted(type_counts.items())),
}
for key, expected_value in expected_summary_pairs.items():
    if cube_summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("model_input_bundle_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json model_input_bundle_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Model-input runtime status: {RUNTIME_STATUS}",
        f"Answer packets checked: {answer_count}",
        f"Model adapter checks: {model_adapter_count}",
        f"Model input records: {summary.get('model_input_count')}/{model_adapter_count}",
        f"Complete model input records: {complete_records}/{model_adapter_count}",
        f"No-input local-model evidence produced: {runner_no_input.get('summary', {}).get('evidence_count')}/0",
        f"Explicit-input local-model evidence produced: {runner_with_input.get('summary', {}).get('evidence_count')}/{model_adapter_count}",
        f"Explicit-input model adapters satisfied: {model_input_satisfied}/{type_counts.get('quantitative_model_adapter', 0) + type_counts.get('floor_delivery_adapter', 0)}",
        f"Explicit-input no-go adapters blocked: {model_input_no_go_block}/{type_counts.get('no_go_threshold_adapter', 0)}",
        f"Legacy shape-only model evidence blocked: {legacy_blocked}/{model_adapter_count}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"model-input audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("model input bundle audit ok")
