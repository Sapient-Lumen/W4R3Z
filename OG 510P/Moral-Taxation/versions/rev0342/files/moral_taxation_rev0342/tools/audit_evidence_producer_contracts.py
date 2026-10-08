#!/usr/bin/env python3
"""Audit evidence-producer contracts and adapter request planning.

Rev0326 made adapter execution require evidence. This audit closes the next gap:
evidence must come from a registered producer contract, and every adapter packet
must be convertible into an external evidence request without storing stale law
or model outputs in the archive.
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
RUNTIME_STATUS = "evidence_producer_contracts_checked"
REQUEST_STATUS = "evidence_producer_requests_planned"
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
ADAPTER_TYPES = {
    "current_law_refresh_adapter",
    "jurisdiction_scope_adapter",
    "quantitative_model_adapter",
    "floor_delivery_adapter",
    "no_go_threshold_adapter",
}


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


def contract_by_adapter_type(contracts: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for contract in contracts.get("producer_contracts", []):
        for typ in contract.get("adapter_types", []):
            out.setdefault(str(typ), []).append(dict(contract))
    return out


def contract_for_adapter(contracts: Mapping[str, Any], adapter_type: str) -> Dict[str, Any]:
    return (contract_by_adapter_type(contracts).get(adapter_type) or [{}])[0]


def producer_fields(packet: Mapping[str, Any], contracts: Mapping[str, Any], as_of_date: str, invalid: bool = False) -> Dict[str, Any]:
    contract = contract_for_adapter(contracts, str(packet.get("adapter_type")))
    modes = list(contract.get("permitted_execution_modes", []))
    return {
        "producer_id": "unregistered_synthetic_producer" if invalid else contract.get("producer_id"),
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

def synthetic_evidence_for_adapter(packet: Mapping[str, Any], contracts: Mapping[str, Any], as_of_date: str, invalid: bool = False) -> Dict[str, Any]:
    typ = packet.get("adapter_type")
    aid = packet.get("adapter_id")
    rid = packet.get("route_id")
    outputs = {name: f"producer-contract-test:{name}" for name in packet.get("required_outputs", [])}
    common = producer_fields(packet, contracts, as_of_date, invalid=invalid)
    if typ == "current_law_refresh_adapter":
        return {**common,"source_id":packet.get("source_id"),"checked_at":as_of_date,"retrieval_method":"producer_contract_interface_test","authority_locator":f"synthetic://producer/current-law/{packet.get('source_id')}","jurisdiction":packet.get("jurisdiction") or "synthetic_jurisdiction","effective_date":packet.get("effective_date") or as_of_date,"result_status":"confirmed_current","reviewer_or_system":"audit_evidence_producer_contracts.py","claim_supported":True}
    if typ == "jurisdiction_scope_adapter":
        return {**common,"jurisdiction":"synthetic_jurisdiction","effective_date":as_of_date,"authority_level":"synthetic_authority_level","preemption_or_treaty_conflict":"none_identified_in_interface_test","implementation_status":"in_force_for_interface_test","conflict_resolution":"synthetic_conflict_rule_recorded"}
    if typ == "no_go_threshold_adapter":
        return {**common,"model_name":"synthetic_no_go_threshold_review","model_version":"producer-contract-test-v1",**synthetic_input_proof(aid),"assumptions":["producer contract interface test; not a real threshold determination"],"run_at":as_of_date,"uncertainty_method":"producer_contract_interface_check","outputs":outputs,"threshold_result":"not_triggered","reviewer_or_system":"audit_evidence_producer_contracts.py","run_locator":f"synthetic://producer/no-go/{rid}"}
    if typ == "floor_delivery_adapter":
        return {**common,"model_name":"synthetic_floor_delivery_model","model_version":"producer-contract-test-v1",**synthetic_input_proof(aid),"assumptions":["producer contract interface test; not a real delivery model"],"run_at":as_of_date,"uncertainty_method":"producer_contract_interface_check","outputs":outputs,"run_locator":f"synthetic://producer/floor/{rid}"}
    return {**common,"model_name":packet.get("model_class") or "synthetic_quantitative_model","model_version":"producer-contract-test-v1",**synthetic_input_proof(aid),"assumptions":["producer contract interface test; not a real fiscal or enforcement model"],"run_at":as_of_date,"uncertainty_method":"producer_contract_interface_check","outputs":outputs,"run_locator":f"synthetic://producer/model/{rid}/{packet.get('model_class')}"}


def evidence_bundle(answers: List[Dict[str, Any]], contracts: Mapping[str, Any], as_of_date: str, invalid: bool = False) -> Dict[str, Any]:
    evidence: Dict[str, Any] = {}
    for answer in answers:
        for packet in answer.get("disposition", {}).get("adapter_checks", []):
            aid = packet.get("adapter_id")
            if aid:
                evidence[str(aid)] = synthetic_evidence_for_adapter(packet, contracts, as_of_date, invalid=invalid)
    return {"producer_contracts": contracts.get("producer_contracts", []), "adapter_evidence": evidence}


cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
contracts_path = root / "docs/00-meta/evidence-producer-contracts.json"
schema_path = root / "docs/00-meta/evidence-producer-contracts-schema.json"
contracts = json.loads(contracts_path.read_text(encoding="utf-8"))
schema = json.loads(schema_path.read_text(encoding="utf-8"))
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")
planner = load_module("plan_adapter_evidence_requests", root / "tools/plan_adapter_evidence_requests.py")

if contracts.get("runtime_status") != RUNTIME_STATUS:
    errors.append("evidence-producer-contracts.json runtime_status is stale")
if contracts.get("revision") != (root / "VERSION").read_text(encoding="utf-8").strip():
    errors.append("evidence-producer-contracts.json revision must match VERSION")
if schema.get("revision") != (root / "VERSION").read_text(encoding="utf-8").strip():
    errors.append("evidence-producer-contracts-schema.json revision must match VERSION")

required_top_level = set(schema.get("required_top_level", []))
missing_top_level = sorted(required_top_level - set(contracts))
if missing_top_level:
    errors.append(f"evidence-producer-contracts.json missing top-level fields {missing_top_level}")
verifier_policy = contracts.get("external_attestation_verifier_policy", {})
if verifier_policy.get("status") != "not_configured_fail_closed":
    errors.append("evidence producer contracts must expose fail-closed verifier status")
if verifier_policy.get("promotion_allowed_without_trusted_verifier") is not False:
    errors.append("evidence producer contracts must forbid promotion without a trusted verifier")
if verifier_policy.get("claimed_status_is_self_authenticating") is not False:
    errors.append("evidence producer contracts must reject self-authenticating claimed statuses")

required_contract_fields = set(schema.get("required_contract_fields", []))
covered_types = set()
producer_ids = []
for contract in contracts.get("producer_contracts", []):
    pid = contract.get("producer_id")
    producer_ids.append(pid)
    missing = sorted(required_contract_fields - set(contract))
    if missing:
        errors.append(f"producer contract {pid} missing fields {missing}")
    if contract.get("output_retention") != "external_evidence_bundle_only":
        errors.append(f"producer contract {pid} must keep output_retention external_evidence_bundle_only")
    if contract.get("stores_doctrine") is not False:
        errors.append(f"producer contract {pid} must not store doctrine")
    for typ in contract.get("adapter_types", []):
        if typ not in ADAPTER_TYPES:
            errors.append(f"producer contract {pid} covers unknown adapter type {typ}")
        covered_types.add(str(typ))
    if not set(executor.PRODUCER_REQUIRED_FIELDS).issubset(set(contract.get("required_evidence_fields", []))):
        errors.append(f"producer contract {pid} does not require executor producer metadata fields")

    if set(contract.get("adapter_types", [])) & getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()):
        authority_fields = set(getattr(executor, "AUTHORITY_PROOF_FIELDS", []))
        missing_authority_fields = sorted(authority_fields - set(contract.get("required_evidence_fields", [])))
        if missing_authority_fields:
            errors.append(f"authority producer contract {pid} missing strict authority evidence fields {missing_authority_fields}")
        if contract.get("requires_implementation_grade_authority_evidence") is not True:
            errors.append(f"authority producer contract {pid} must require implementation-grade authority evidence")
        if contract.get("requires_authority_intake_bundle") is not True:
            errors.append(f"authority producer contract {pid} must require a raw authority-intake bundle")
        if contract.get("requires_authority_source_manifest") is not True:
            errors.append(f"authority producer contract {pid} must require an authority-source manifest")
    if set(contract.get("adapter_types", [])) & getattr(executor, "MODEL_ADAPTER_TYPES", set()):
        model_fields = set(getattr(executor, "MODEL_REQUIRED_FIELDS", []))
        missing_model_fields = sorted(model_fields - set(contract.get("required_evidence_fields", [])))
        if missing_model_fields:
            errors.append(f"model producer contract {pid} missing explicit model input evidence fields {missing_model_fields}")
        if contract.get("requires_explicit_model_input_bundle") is not True:
            errors.append(f"model producer contract {pid} must require an explicit model input bundle")
if len(producer_ids) != len(set(producer_ids)):
    errors.append("evidence producer contract ids must be unique")
if covered_types != ADAPTER_TYPES:
    errors.append(f"evidence producer contracts do not cover all adapter types: missing {sorted(ADAPTER_TYPES-covered_types)} extra {sorted(covered_types-ADAPTER_TYPES)}")

payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
answer_count = len(answers)
adapter_checks = [c for a in answers for c in a.get("disposition", {}).get("adapter_checks", [])]
adapter_total = len(adapter_checks)

requests = planner.requests_for_answers(answers, contracts, executor)
request_summary = planner.summarize_requests(requests)
producer_covered_requests = sum(1 for req in requests if req.get("producer_contract_ids"))
request_with_lookup_keys = sum(1 for req in requests if req.get("accepted_lookup_keys"))
request_with_required_fields = sum(1 for req in requests if req.get("required_evidence_fields"))
request_external_only = sum(1 for req in requests if req.get("output_retention") == ["external_evidence_bundle_only"])
model_request_count = sum(1 for req in requests if req.get("adapter_type") in getattr(executor, "MODEL_ADAPTER_TYPES", set()))
model_requests_with_inputs = sum(1 for req in requests if req.get("requires_explicit_model_input_bundle"))
authority_request_count = sum(1 for req in requests if req.get("adapter_type") in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()))
authority_requests_with_strict_evidence = sum(1 for req in requests if req.get("requires_implementation_grade_authority_evidence"))
authority_requests_with_raw_intake = sum(1 for req in requests if req.get("requires_raw_authority_intake_bundle"))
authority_requests_with_source_manifest = sum(1 for req in requests if req.get("requires_authority_source_manifest"))
if request_summary.get("runtime_status") != REQUEST_STATUS:
    errors.append("evidence request planner runtime status is stale")
if len(requests) != adapter_total:
    errors.append("evidence request planner must emit one request per adapter check")
if producer_covered_requests != adapter_total:
    errors.append("every adapter evidence request must name a producer contract")
if request_with_lookup_keys != adapter_total:
    errors.append("every adapter evidence request must expose accepted lookup keys")
if request_with_required_fields != adapter_total:
    errors.append("every adapter evidence request must expose required evidence fields")
if request_external_only != adapter_total:
    errors.append("every adapter evidence request must preserve external-bundle-only retention")
if model_requests_with_inputs != model_request_count:
    errors.append("every model evidence request must require an explicit model input bundle")
if authority_requests_with_strict_evidence != authority_request_count:
    errors.append("every authority evidence request must require implementation-grade authority evidence")
if authority_requests_with_raw_intake != authority_request_count:
    errors.append("every authority evidence request must require a raw authority-intake bundle")
if authority_requests_with_source_manifest != authority_request_count:
    errors.append("every authority evidence request must require an authority-source manifest")

receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
registered_bundle = evidence_bundle(answers, contracts, as_of_date, invalid=False)
registered_executions = [executor.execute_answer(answer, registered_bundle) for answer in answers]
registered_results = [r for p in registered_executions for r in p.get("adapter_execution_results", [])]
registered_summary = executor.summarize_execution(registered_results)
registered_satisfied = sum(1 for r in registered_results if r.get("execution_status") == executor.STATUS_SATISFIED)
registered_can_finalize = sum(1 for p in registered_executions if p.get("execution_summary", {}).get("can_finalize"))
invalid_bundle = evidence_bundle(answers, contracts, as_of_date, invalid=True)
invalid_executions = [executor.execute_answer(answer, invalid_bundle) for answer in answers]
invalid_results = [r for p in invalid_executions for r in p.get("adapter_execution_results", [])]
invalid_blocked = sum(1 for r in invalid_results if r.get("execution_status") == executor.STATUS_INVALID_PRODUCER)
invalid_can_finalize = sum(1 for p in invalid_executions if p.get("execution_summary", {}).get("can_finalize"))

if registered_satisfied != adapter_total:
    errors.append("registered producer evidence should satisfy every synthetic adapter interface")
if registered_can_finalize != answer_count:
    errors.append("registered producer evidence should allow every synthetic answer to finalize")
if invalid_blocked != adapter_total:
    errors.append("unregistered producer evidence must be blocked for every adapter")
if invalid_can_finalize != 0:
    errors.append("unregistered producer evidence must not allow finalization")

summary = cube.get("audit_summary", {})
expected_summary_pairs = {
    "evidence_producers_required": True,
    "evidence_producer_runtime_status": RUNTIME_STATUS,
    "evidence_producer_contract_count": len(contracts.get("producer_contracts", [])),
    "evidence_producer_adapter_type_count": len(covered_types),
    "evidence_producer_adapter_types": sorted(covered_types),
    "evidence_request_runtime_status": REQUEST_STATUS,
    "evidence_request_count": len(requests),
    "evidence_request_case_count": request_summary.get("case_count"),
    "evidence_request_producer_coverage_count": producer_covered_requests,
    "evidence_request_lookup_key_count": request_with_lookup_keys,
    "evidence_request_external_only_count": request_external_only,
    "evidence_request_model_input_required_count": model_requests_with_inputs,
    "evidence_request_authority_evidence_required_count": authority_requests_with_strict_evidence,
    "evidence_request_authority_intake_required_count": authority_requests_with_raw_intake,
    "evidence_request_authority_source_required_count": authority_requests_with_source_manifest,
    "evidence_executor_registered_satisfied_count": registered_satisfied,
    "evidence_executor_registered_can_finalize_count": registered_can_finalize,
    "evidence_executor_invalid_producer_blocked_count": invalid_blocked,
    "evidence_executor_invalid_producer_can_finalize_count": invalid_can_finalize,
    "evidence_request_type_counts": request_summary.get("adapter_type_counts"),
    "evidence_request_producer_counts": request_summary.get("producer_contract_request_counts"),
    "evidence_executor_registered_producer_counts": registered_summary.get("producer_id_counts"),
}
for key, expected_value in expected_summary_pairs.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

for label, rel in [
    ("evidence_producer_contracts_path", cube.get("evidence_producer_contracts_path")),
    ("evidence_producer_contracts_schema_path", cube.get("evidence_producer_contracts_schema_path")),
    ("evidence_producer_audit_report_path", cube.get("evidence_producer_audit_report_path")),
]:
    if not rel or not (root / rel).exists():
        errors.append(f"cube-index.json {label} must point to an existing file")

report_rel = cube.get("evidence_producer_audit_report_path")
if report_rel and (root / report_rel).exists():
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Evidence-producer runtime status: {RUNTIME_STATUS}",
        f"Evidence-producer contracts: {len(contracts.get('producer_contracts', []))}",
        f"Adapter types covered: {len(covered_types)}/{len(ADAPTER_TYPES)}",
        f"Evidence requests planned: {len(requests)}/{adapter_total}",
        f"Evidence requests with producer coverage: {producer_covered_requests}/{adapter_total}",
        f"Evidence requests requiring explicit model inputs: {model_requests_with_inputs}/{model_request_count}",
        f"Evidence requests requiring implementation-grade authority evidence: {authority_requests_with_strict_evidence}/{authority_request_count}",
        f"Evidence requests requiring raw authority intake: {authority_requests_with_raw_intake}/{authority_request_count}",
        f"Evidence requests requiring authority-source manifests: {authority_requests_with_source_manifest}/{authority_request_count}",
        f"Registered-producer synthetic evidence satisfied adapters: {registered_satisfied}/{adapter_total}",
        f"Invalid-producer evidence blocked adapters: {invalid_blocked}/{adapter_total}",
        f"Invalid-producer can-finalize answers: {invalid_can_finalize}/{answer_count}",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"evidence-producer audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("evidence producer contracts audit ok")
