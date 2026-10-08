#!/usr/bin/env python3
"""Audit the execution boundary for decision adapters.

Adapter requirements are not the same as performed legal research or modeling.
This audit proves that the archive has a separate execution gate: empty external
evidence blocks every adapter, while complete evidence-shaped payloads from
registered producer contracts can satisfy the interface without the cube
pretending to own live law or model outputs.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Mapping

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
RUNTIME_STATUS = "decision_adapter_execution_evidence_checked"
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


def contract_for_adapter(contracts: Mapping[str, Any], adapter_type: str) -> Dict[str, Any]:
    for contract in contracts.get("producer_contracts", []):
        if adapter_type in contract.get("adapter_types", []):
            return dict(contract)
    return {}


def producer_fields(packet: Mapping[str, Any], contracts: Mapping[str, Any], as_of_date: str) -> Dict[str, Any]:
    contract = contract_for_adapter(contracts, str(packet.get("adapter_type")))
    modes = list(contract.get("permitted_execution_modes", []))
    return {
        "producer_id": contract.get("producer_id"),
        "producer_contract_version": contract.get("contract_version"),
        "evidence_kind": packet.get("adapter_type"),
        "created_at": as_of_date,
        "producer_mode": modes[0] if modes else "synthetic_interface_test",
    }




def synthetic_input_proof(aid: Any) -> Dict[str, Any]:
    h = f"synthetic-inputs:{aid}"
    return {
        "inputs_hash": h,
        "model_input_bundle_id": "synthetic-interface-model-input-bundle",
        "model_input_record_hash": h,
        "input_hash_basis": "explicit_model_input_bundle",
        "input_locator": f"synthetic://model-input/{aid}",
        "assumption_set_id": f"synthetic-assumption-set:{aid}",
        "input_values_hash": h,
    }

def synthetic_evidence_for_adapter(packet: Mapping[str, Any], contracts: Mapping[str, Any], as_of_date: str) -> Dict[str, Any]:
    typ = packet.get("adapter_type")
    aid = packet.get("adapter_id")
    rid = packet.get("route_id")
    required_outputs = list(packet.get("required_outputs", []))
    outputs = {name: f"synthetic-interface-test:{name}" for name in required_outputs}
    common = producer_fields(packet, contracts, as_of_date)
    if typ == "current_law_refresh_adapter":
        return {
            **common,
            "source_id": packet.get("source_id"),
            "checked_at": as_of_date,
            "retrieval_method": "synthetic_interface_test_no_external_claim",
            "authority_locator": f"synthetic://adapter-execution/current-law/{packet.get('source_id')}",
            "jurisdiction": packet.get("jurisdiction") or "synthetic_jurisdiction",
            "effective_date": packet.get("effective_date") or as_of_date,
            "result_status": "confirmed_current",
            "reviewer_or_system": "audit_adapter_execution.py",
            "claim_supported": True,
        }
    if typ == "jurisdiction_scope_adapter":
        return {
            **common,
            "jurisdiction": "synthetic_jurisdiction",
            "effective_date": as_of_date,
            "authority_level": "synthetic_authority_level",
            "preemption_or_treaty_conflict": "none_identified_in_synthetic_interface_test",
            "implementation_status": "in_force_for_synthetic_interface_test",
            "conflict_resolution": "synthetic_conflict_rule_recorded",
        }
    if typ == "no_go_threshold_adapter":
        return {
            **common,
            "model_name": "synthetic_no_go_threshold_review",
            "model_version": "interface-test-v1",
            **synthetic_input_proof(aid),
            "assumptions": ["synthetic interface test; not a real threshold determination"],
            "run_at": as_of_date,
            "uncertainty_method": "synthetic_interface_check",
            "outputs": outputs,
            "threshold_result": "not_triggered",
            "reviewer_or_system": "audit_adapter_execution.py",
            "run_locator": f"synthetic://adapter-execution/no-go/{rid}",
        }
    if typ == "floor_delivery_adapter":
        return {
            **common,
            "model_name": "synthetic_floor_delivery_model",
            "model_version": "interface-test-v1",
            **synthetic_input_proof(aid),
            "assumptions": ["synthetic interface test; not a real delivery model"],
            "run_at": as_of_date,
            "uncertainty_method": "synthetic_interface_check",
            "outputs": outputs,
            "run_locator": f"synthetic://adapter-execution/floor/{rid}",
        }
    if typ == "quantitative_model_adapter":
        return {
            **common,
            "model_name": packet.get("model_class") or "synthetic_quantitative_model",
            "model_version": "interface-test-v1",
            **synthetic_input_proof(aid),
            "assumptions": ["synthetic interface test; not a real fiscal or enforcement model"],
            "run_at": as_of_date,
            "uncertainty_method": "synthetic_interface_check",
            "outputs": outputs,
            "run_locator": f"synthetic://adapter-execution/model/{rid}/{packet.get('model_class')}",
        }
    return {**common, "synthetic_unrecognized_adapter": True}


def synthetic_evidence_bundle(answers: List[Dict[str, Any]], contracts: Mapping[str, Any], as_of_date: str) -> Dict[str, Any]:
    evidence: Dict[str, Any] = {}
    for answer in answers:
        for packet in answer.get("disposition", {}).get("adapter_checks", []):
            aid = packet.get("adapter_id")
            if aid:
                evidence[str(aid)] = synthetic_evidence_for_adapter(packet, contracts, as_of_date)
    return {"producer_contracts": contracts.get("producer_contracts", []), "adapter_evidence": evidence}


cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
contracts = json.loads((root / "docs/00-meta/evidence-producer-contracts.json").read_text(encoding="utf-8"))
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")
answer_source = (root / "tools/answer_case.py").read_text(encoding="utf-8")
if "resolve_current_law_jurisdiction_and_model_adapters" not in answer_source:
    errors.append("answer_case.py must still expose the adapter-resolution answer step before execution")
if "execute_adapter" not in (root / "tools/execute_decision_adapters.py").read_text(encoding="utf-8"):
    errors.append("execute_decision_adapters.py must expose per-adapter execution validation")
if "STATUS_INVALID_PRODUCER" not in (root / "tools/execute_decision_adapters.py").read_text(encoding="utf-8"):
    errors.append("execute_decision_adapters.py must block unregistered evidence producers")

try:
    payload = load_answers()
except Exception as exc:
    errors.append(f"answer_case.py failed under adapter-execution audit: {exc}")
    payload = {"answers": []}

if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")

answers = payload.get("answers", [])
answer_count = len(answers)
all_adapter_checks = [c for a in answers for c in a.get("disposition", {}).get("adapter_checks", [])]
adapter_total = len(all_adapter_checks)
type_counts: Dict[str, int] = {}
for packet in all_adapter_checks:
    typ = str(packet.get("adapter_type"))
    type_counts[typ] = type_counts.get(typ, 0) + 1

empty_executions = [executor.execute_answer(answer, {}) for answer in answers]
empty_results = [r for p in empty_executions for r in p.get("adapter_execution_results", [])]
empty_summary = executor.summarize_execution(empty_results)
empty_missing = sum(1 for r in empty_results if r.get("execution_status") == executor.STATUS_MISSING)
empty_can_finalize = sum(1 for p in empty_executions if p.get("execution_summary", {}).get("can_finalize"))
empty_marker_count = sum(len(p.get("cannot_finalize_until", [])) for p in empty_executions)

if len(empty_results) != adapter_total:
    errors.append("empty-evidence execution did not emit one result per adapter check")
if empty_missing != adapter_total:
    errors.append("empty evidence must block every adapter as missing external evidence")
if empty_can_finalize != 0:
    errors.append("empty evidence must not allow any answer to finalize")
if empty_marker_count != adapter_total:
    errors.append("empty evidence must emit one cannot-finalize marker per adapter check")

receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
synthetic_bundle = synthetic_evidence_bundle(answers, contracts, as_of_date)
synthetic_executions = [executor.execute_answer(answer, synthetic_bundle) for answer in answers]
synthetic_results = [r for p in synthetic_executions for r in p.get("adapter_execution_results", [])]
synthetic_summary = executor.summarize_execution(synthetic_results)
synthetic_satisfied = sum(1 for r in synthetic_results if r.get("execution_status") == executor.STATUS_SATISFIED)
synthetic_can_finalize = sum(1 for p in synthetic_executions if p.get("execution_summary", {}).get("can_finalize"))
synthetic_registered = synthetic_summary.get("registered_producer_result_count")

if len(synthetic_results) != adapter_total:
    errors.append("synthetic evidence execution did not emit one result per adapter check")
if synthetic_satisfied != adapter_total:
    errors.append("complete synthetic evidence should satisfy every adapter interface")
if synthetic_can_finalize != answer_count:
    errors.append("complete synthetic evidence should satisfy every answer packet interface")
if synthetic_registered != adapter_total:
    errors.append("complete synthetic evidence must be accepted only through registered producer contracts")

expected_summary_pairs = {
    "adapter_execution_required": True,
    "adapter_execution_runtime_status": RUNTIME_STATUS,
    "adapter_execution_answer_count": answer_count,
    "adapter_execution_adapter_check_total": adapter_total,
    "adapter_execution_empty_missing_count": empty_missing,
    "adapter_execution_empty_blocked_count": empty_summary.get("blocked_count"),
    "adapter_execution_empty_can_finalize_count": empty_can_finalize,
    "adapter_execution_empty_marker_count": empty_marker_count,
    "adapter_execution_synthetic_satisfied_count": synthetic_satisfied,
    "adapter_execution_synthetic_can_finalize_count": synthetic_can_finalize,
    "adapter_execution_synthetic_registered_producer_count": synthetic_registered,
    "adapter_execution_type_counts": dict(sorted(type_counts.items())),
    "adapter_execution_empty_status_counts": empty_summary.get("execution_status_counts"),
    "adapter_execution_synthetic_status_counts": synthetic_summary.get("execution_status_counts"),
}
summary = cube.get("audit_summary", {})
for key, expected_value in expected_summary_pairs.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("adapter_execution_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json adapter_execution_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Adapter-execution runtime status: {RUNTIME_STATUS}",
        f"Adapter-execution answer packets: {answer_count}",
        f"Adapter-execution adapter checks: {adapter_total}",
        f"Empty-evidence missing adapters: {empty_missing}/{adapter_total}",
        f"Empty-evidence blocked adapters: {empty_summary.get('blocked_count')}/{adapter_total}",
        f"Empty-evidence can-finalize answers: {empty_can_finalize}/{answer_count}",
        f"Empty-evidence cannot-finalize markers: {empty_marker_count}/{adapter_total}",
        f"Synthetic-evidence satisfied adapters: {synthetic_satisfied}/{adapter_total}",
        f"Synthetic-evidence can-finalize answers: {synthetic_can_finalize}/{answer_count}",
        f"Synthetic-evidence registered producer results: {synthetic_registered}/{adapter_total}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"adapter-execution audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("adapter execution audit ok")
