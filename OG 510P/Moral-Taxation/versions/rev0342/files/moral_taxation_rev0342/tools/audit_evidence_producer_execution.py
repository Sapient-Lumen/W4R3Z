#!/usr/bin/env python3
"""Audit executable evidence producers, not only producer contracts.

Rev0329 hardens rev0328's producer runner: local model evidence must be derived
from an explicit model-input bundle, not from adapter ids or route shape alone.
The audit proves empty inputs produce no model evidence, explicit inputs produce
model evidence with hashes and assumptions, stale evidence blocks, and no-go
screens remain blocking until external review clears them.
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
RUNNER_STATUS = "evidence_producer_runner_invoked"
MODEL_INPUT_STATUS = "explicit_model_input_bundle_generated"
EXECUTOR_STATUS = "decision_adapter_execution_evidence_checked"
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


def load_answers() -> Dict[str, Any]:
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
    return json.loads(raw)


def execute_all(answers: List[Dict[str, Any]], bundle: Mapping[str, Any], executor: Any) -> Dict[str, Any]:
    packets = [executor.execute_answer(answer, bundle) for answer in answers]
    results = [r for packet in packets for r in packet.get("adapter_execution_results", [])]
    return {"packets": packets, "results": results, "summary": executor.summarize_execution(results)}


def stale_bundle(bundle: Mapping[str, Any], stale_date: str, as_of_date: str) -> Dict[str, Any]:
    out = copy.deepcopy(dict(bundle))
    out.setdefault("execution_context", {})["as_of_date"] = as_of_date
    for evidence in out.get("adapter_evidence", {}).values():
        if not isinstance(evidence, dict):
            continue
        evidence["created_at"] = stale_date
        if "checked_at" in evidence:
            evidence["checked_at"] = stale_date
        if "run_at" in evidence:
            evidence["run_at"] = stale_date
    return out


def jurisdiction_block_bundle(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(bundle))
    for evidence in out.get("adapter_evidence", {}).values():
        if isinstance(evidence, dict) and evidence.get("evidence_kind") == "jurisdiction_scope_adapter":
            evidence["implementation_status"] = "uncertain_scope"
            evidence["conflict_resolution"] = "unresolved_conflict"
            break
    return out


def strip_model_input_proof(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(bundle))
    for evidence in out.get("adapter_evidence", {}).values():
        if not isinstance(evidence, dict):
            continue
        if evidence.get("evidence_kind") in {"quantitative_model_adapter", "floor_delivery_adapter", "no_go_threshold_adapter"}:
            for key in ["model_input_bundle_id", "model_input_record_hash", "input_hash_basis", "input_locator", "assumption_set_id", "input_values_hash", "input_bundle_runtime_status"]:
                evidence.pop(key, None)
            evidence["inputs_hash"] = "legacy-shape-only-inputs"
    return out


cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
runner = load_module("run_evidence_producers", root / "tools/run_evidence_producers.py")
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")
input_builder = load_module("build_model_input_bundle", root / "tools/build_model_input_bundle.py")

runner_source = (root / "tools/run_evidence_producers.py").read_text(encoding="utf-8")
if RUNNER_STATUS not in runner_source:
    errors.append("run_evidence_producers.py must expose the evidence-producer runner runtime status")
if "explicit_model_input_bundle_required" not in runner_source:
    errors.append("run_evidence_producers.py must skip model adapters when explicit model inputs are absent")
if "STATUS_STALE" not in (root / "tools/execute_decision_adapters.py").read_text(encoding="utf-8"):
    errors.append("execute_decision_adapters.py must block stale evidence")
if "STATUS_INPUT_HASH_MISMATCH" not in (root / "tools/execute_decision_adapters.py").read_text(encoding="utf-8"):
    errors.append("execute_decision_adapters.py must block model evidence without explicit input-hash proof")

payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
answer_count = len(answers)
adapter_checks = [c for a in answers for c in a.get("disposition", {}).get("adapter_checks", [])]
adapter_total = len(adapter_checks)
adapter_type_counts: Dict[str, int] = {}
for packet in adapter_checks:
    typ = str(packet.get("adapter_type"))
    adapter_type_counts[typ] = adapter_type_counts.get(typ, 0) + 1

model_adapter_count = sum(adapter_type_counts.get(t, 0) for t in runner.MODEL_ADAPTER_TYPES)
external_adapter_count = sum(adapter_type_counts.get(t, 0) for t in runner.EXTERNAL_ADAPTER_TYPES)
model_satisfied_expected = adapter_type_counts.get("quantitative_model_adapter", 0) + adapter_type_counts.get("floor_delivery_adapter", 0)

model_inputs = input_builder.bundle_for_answers(answers, as_of_date)
model_input_summary = model_inputs.get("summary", {})

fixture_bundle = runner.bundle_for_answers(root, answers, runner.MODE_INTERFACE_FIXTURE, as_of_date)
fixture_summary = fixture_bundle.get("summary", {})
fixture_exec = execute_all(answers, fixture_bundle, executor)
fixture_exec_summary = fixture_exec["summary"]

no_input_bundle = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date)
no_input_summary = no_input_bundle.get("summary", {})
no_input_exec = execute_all(answers, no_input_bundle, executor)
no_input_summary_exec = no_input_exec["summary"]
no_input_missing = no_input_summary_exec.get("execution_status_counts", {}).get(executor.STATUS_MISSING, 0)

model_bundle = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date, model_input_bundle=model_inputs)
model_summary = model_bundle.get("summary", {})
model_exec = execute_all(answers, model_bundle, executor)
model_exec_summary = model_exec["summary"]
model_missing = model_exec_summary.get("execution_status_counts", {}).get(executor.STATUS_MISSING, 0)
model_no_go_blocks = sum(
    1 for r in model_exec["results"]
    if r.get("adapter_type") == "no_go_threshold_adapter" and r.get("execution_status") == executor.STATUS_BLOCKS
)

legacy_bundle = strip_model_input_proof(model_bundle)
legacy_exec = execute_all(answers, legacy_bundle, executor)
legacy_results = legacy_exec["results"]
legacy_model_incomplete = sum(
    1 for r in legacy_results
    if r.get("adapter_type") in runner.MODEL_ADAPTER_TYPES and r.get("execution_status") == executor.STATUS_INCOMPLETE
)
legacy_model_hash_mismatch = sum(
    1 for r in legacy_results
    if r.get("adapter_type") in runner.MODEL_ADAPTER_TYPES and r.get("execution_status") == executor.STATUS_INPUT_HASH_MISMATCH
)

old_bundle = stale_bundle(fixture_bundle, "2025-01-01", as_of_date)
stale_exec = execute_all(answers, old_bundle, executor)
stale_summary = stale_exec["summary"]
stale_blocked = stale_summary.get("execution_status_counts", {}).get(executor.STATUS_STALE, 0)

jurisdiction_bundle = jurisdiction_block_bundle(fixture_bundle)
jurisdiction_exec = execute_all(answers, jurisdiction_bundle, executor)
jurisdiction_blocked = sum(
    1 for r in jurisdiction_exec["results"]
    if r.get("adapter_type") == "jurisdiction_scope_adapter" and r.get("execution_status") == executor.STATUS_BLOCKS
)

if model_inputs.get("runtime_status") != MODEL_INPUT_STATUS:
    errors.append("model input bundle runtime_status is stale")
if model_input_summary.get("model_input_count") != model_adapter_count:
    errors.append("model input builder must emit one input record per model-style adapter")
if fixture_bundle.get("runtime_status") != RUNNER_STATUS:
    errors.append("fixture producer bundle runtime_status is stale")
if model_bundle.get("runtime_status") != RUNNER_STATUS:
    errors.append("local-model producer bundle runtime_status is stale")
if fixture_summary.get("evidence_count") != adapter_total:
    errors.append("interface fixture runner must produce evidence for every adapter check")
if fixture_exec_summary.get("satisfied_count") != adapter_total or not fixture_exec_summary.get("can_finalize"):
    errors.append("interface fixture evidence should satisfy every adapter interface")
if no_input_summary.get("evidence_count") != 0:
    errors.append("local-model runner without explicit input bundle must produce no evidence")
if no_input_summary.get("skipped_count") != adapter_total:
    errors.append("local-model runner without explicit input bundle must skip every adapter")
if no_input_missing != adapter_total:
    errors.append("executing a no-input local-model bundle must leave every adapter missing")
if model_summary.get("evidence_count") != model_adapter_count:
    errors.append("local-model runner with explicit inputs should produce evidence only for model-style adapters")
if model_summary.get("skipped_count") != external_adapter_count:
    errors.append("local-model runner with explicit inputs should still skip current-law and jurisdiction adapters")
if model_exec_summary.get("satisfied_count") != model_satisfied_expected:
    errors.append("local-model runner should satisfy only quantitative and floor-delivery model adapters")
if model_missing != external_adapter_count:
    errors.append("local-model execution should leave current-law and jurisdiction evidence missing")
if model_no_go_blocks != adapter_type_counts.get("no_go_threshold_adapter", 0):
    errors.append("local no-go threshold screens must block rather than clear no-go gates")
if model_exec_summary.get("can_finalize"):
    errors.append("local model evidence alone must not allow finalization")
if legacy_model_incomplete + legacy_model_hash_mismatch != model_adapter_count:
    errors.append("legacy shape-only model evidence must be blocked for every model-style adapter")
if stale_blocked != adapter_total:
    errors.append("stale registered evidence must block every adapter check")
if jurisdiction_blocked < 1:
    errors.append("jurisdiction-scope evidence with uncertain scope must block finalization")

summary = cube.get("audit_summary", {})
expected_summary_pairs = {
    "evidence_producer_execution_required": True,
    "evidence_producer_runner_runtime_status": RUNNER_STATUS,
    "evidence_producer_runner_answer_count": answer_count,
    "evidence_producer_runner_adapter_check_total": adapter_total,
    "evidence_producer_fixture_evidence_count": fixture_summary.get("evidence_count"),
    "evidence_producer_fixture_unique_key_count": fixture_summary.get("evidence_unique_key_count"),
    "evidence_producer_fixture_satisfied_count": fixture_exec_summary.get("satisfied_count"),
    "evidence_producer_fixture_can_finalize_count": sum(1 for p in fixture_exec["packets"] if p.get("execution_summary", {}).get("can_finalize")),
    "evidence_producer_no_input_evidence_count": no_input_summary.get("evidence_count"),
    "evidence_producer_no_input_skipped_count": no_input_summary.get("skipped_count"),
    "evidence_producer_no_input_missing_count": no_input_missing,
    "evidence_producer_local_model_evidence_count": model_summary.get("evidence_count"),
    "evidence_producer_local_model_skipped_count": model_summary.get("skipped_count"),
    "evidence_producer_local_model_satisfied_count": model_exec_summary.get("satisfied_count"),
    "evidence_producer_local_model_missing_count": model_missing,
    "evidence_producer_local_model_no_go_block_count": model_no_go_blocks,
    "evidence_producer_local_model_can_finalize_count": sum(1 for p in model_exec["packets"] if p.get("execution_summary", {}).get("can_finalize")),
    "evidence_producer_legacy_shape_only_model_block_count": legacy_model_incomplete + legacy_model_hash_mismatch,
    "evidence_producer_stale_blocked_count": stale_blocked,
    "evidence_producer_jurisdiction_uncertain_scope_blocked_count": jurisdiction_blocked,
    "evidence_producer_local_model_type_counts": model_summary.get("produced_adapter_type_counts"),
    "evidence_producer_local_model_skipped_type_counts": model_summary.get("skipped_adapter_type_counts"),
    "evidence_producer_no_input_skipped_reason_counts": no_input_summary.get("skipped_reason_counts"),
}
for key, expected_value in expected_summary_pairs.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("evidence_producer_execution_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json evidence_producer_execution_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Evidence-producer runner runtime status: {RUNNER_STATUS}",
        f"Answer packets checked: {answer_count}",
        f"Adapter checks: {adapter_total}",
        f"Explicit model input records: {model_input_summary.get('model_input_count')}/{model_adapter_count}",
        f"Interface-fixture evidence produced: {fixture_summary.get('evidence_count')}/{adapter_total}",
        f"Interface-fixture satisfied adapters: {fixture_exec_summary.get('satisfied_count')}/{adapter_total}",
        f"No-input local-model evidence produced: {no_input_summary.get('evidence_count')}/0",
        f"No-input local-model skipped adapters: {no_input_summary.get('skipped_count')}/{adapter_total}",
        f"Local-model evidence produced: {model_summary.get('evidence_count')}/{model_adapter_count}",
        f"Local-model external adapters skipped: {model_summary.get('skipped_count')}/{external_adapter_count}",
        f"Local-model satisfied adapters: {model_exec_summary.get('satisfied_count')}/{model_satisfied_expected}",
        f"Local-model missing external adapters: {model_missing}/{external_adapter_count}",
        f"Local-model no-go blocks: {model_no_go_blocks}/{adapter_type_counts.get('no_go_threshold_adapter', 0)}",
        f"Legacy shape-only model evidence blocked: {legacy_model_incomplete + legacy_model_hash_mismatch}/{model_adapter_count}",
        f"Local-model can-finalize answers: {expected_summary_pairs['evidence_producer_local_model_can_finalize_count']}/{answer_count}",
        f"Stale-evidence blocked adapters: {stale_blocked}/{adapter_total}",
        f"Jurisdiction uncertain-scope block count: {jurisdiction_blocked}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"evidence-producer execution report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("evidence producer execution audit ok")
