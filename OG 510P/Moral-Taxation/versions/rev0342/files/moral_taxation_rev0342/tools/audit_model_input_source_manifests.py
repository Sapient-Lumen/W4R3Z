#!/usr/bin/env python3
"""Audit the model-input evidence truth boundary.

Archive builders may emit reference and strict-schema fixtures. They must refuse
implementation-grade provenance. Strict-schema fixtures may exercise adapter
interfaces only under an explicit test context and can never promote.
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
RUNTIME_STATUS = "model_input_source_manifest_generated"
INPUT_STATUS = "explicit_model_input_bundle_generated"
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
MODEL_TYPES = {"quantitative_model_adapter", "floor_delivery_adapter", "no_go_threshold_adapter"}


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


def execute_all(answers: List[Dict[str, Any]], bundle: Mapping[str, Any], executor: Any) -> Dict[str, Any]:
    packets = [executor.execute_answer(answer, bundle) for answer in answers]
    results = [r for packet in packets for r in packet.get("adapter_execution_results", [])]
    return {"packets": packets, "results": results, "summary": executor.summarize_execution(results)}


cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
input_builder = load_module("build_model_input_bundle", root / "tools/build_model_input_bundle.py")
source_builder = load_module("build_model_input_source_manifest", root / "tools/build_model_input_source_manifest.py")
runner = load_module("run_evidence_producers", root / "tools/run_evidence_producers.py")
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")

payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
answer_count = len(answers)
adapter_checks = [c for a in answers for c in a.get("disposition", {}).get("adapter_checks", [])]
model_checks = [c for c in adapter_checks if c.get("adapter_type") in MODEL_TYPES]
model_adapter_count = len(model_checks)
type_counts: Dict[str, int] = {}
for packet in model_checks:
    typ = str(packet.get("adapter_type"))
    type_counts[typ] = type_counts.get(typ, 0) + 1
model_satisfied_expected = type_counts.get("quantitative_model_adapter", 0) + type_counts.get("floor_delivery_adapter", 0)
no_go_expected = type_counts.get("no_go_threshold_adapter", 0)
authority_expected = sum(1 for c in adapter_checks if c.get("adapter_type") in {"current_law_refresh_adapter", "jurisdiction_scope_adapter"})

model_inputs = input_builder.bundle_for_answers(answers, as_of_date)
reference_manifest = source_builder.manifest_for_input_bundle(model_inputs, as_of_date, source_builder.CERT_REFERENCE_FIXTURE)
strict_test_manifest = source_builder.manifest_for_input_bundle(model_inputs, as_of_date, source_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE)
implementation_builder_refused = False
try:
    source_builder.manifest_for_input_bundle(model_inputs, as_of_date, source_builder.CERT_IMPLEMENTATION_GRADE)
except ValueError:
    implementation_builder_refused = True

if model_inputs.get("runtime_status") != INPUT_STATUS:
    errors.append("model input bundle runtime_status is stale")
if reference_manifest.get("runtime_status") != RUNTIME_STATUS or strict_test_manifest.get("runtime_status") != RUNTIME_STATUS:
    errors.append("model input source manifest runtime_status is stale")
if not implementation_builder_refused:
    errors.append("archive source builder must refuse implementation-grade model-input provenance")

required = {
    "manifest_id", "source_record_id", "model_input_record_hash", "input_values_hash",
    "input_certification_level", "implementation_grade_input_source", "strict_schema_test_fixture",
    "evidence_origin", "external_source_attestation_status", "promotion_eligible", "source_contract_id",
    "source_locator", "coverage_period", "extraction_date", "source_freshness_status",
    "units_verified", "provenance_hash", "source_record_hash", "non_doctrine_warning",
}
reference_records = reference_manifest.get("model_input_sources", {})
strict_records = strict_test_manifest.get("model_input_sources", {})
complete_reference = sum(1 for r in reference_records.values() if all(field in r and r.get(field) not in (None, "", [], {}) for field in required - {"promotion_eligible"}) and r.get("promotion_eligible") is False)
complete_strict = sum(1 for r in strict_records.values() if all(field in r and r.get(field) not in (None, "", [], {}) for field in required - {"promotion_eligible"}) and r.get("promotion_eligible") is False)

strict_no_source_bundle = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date, model_input_bundle=model_inputs, strict_model_input_sources=True)
strict_reference_bundle = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date, model_input_bundle=model_inputs, model_input_source_manifest=reference_manifest, strict_model_input_sources=True)
strict_test_bundle = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date, model_input_bundle=model_inputs, model_input_source_manifest=strict_test_manifest, strict_model_input_sources=True)

no_source_exec = execute_all(answers, strict_no_source_bundle, executor)
reference_exec = execute_all(answers, strict_reference_bundle, executor)
strict_test_exec = execute_all(answers, strict_test_bundle, executor)
source_status = executor.STATUS_INPUT_SOURCE_NOT_CERTIFIED
no_source_blocks = sum(1 for r in no_source_exec["results"] if r.get("adapter_type") in MODEL_TYPES and r.get("execution_status") == source_status)
reference_blocks = sum(1 for r in reference_exec["results"] if r.get("adapter_type") in MODEL_TYPES and r.get("execution_status") == source_status)
strict_test_source_blocks = sum(1 for r in strict_test_exec["results"] if r.get("adapter_type") in MODEL_TYPES and r.get("execution_status") == source_status)
strict_test_satisfied = sum(1 for r in strict_test_exec["results"] if r.get("adapter_type") in {"quantitative_model_adapter", "floor_delivery_adapter"} and r.get("execution_status") == executor.STATUS_SATISFIED)
strict_test_no_go_blocks = sum(1 for r in strict_test_exec["results"] if r.get("adapter_type") == "no_go_threshold_adapter" and r.get("execution_status") == executor.STATUS_BLOCKS)
strict_test_missing_authority = strict_test_exec["summary"].get("execution_status_counts", {}).get(executor.STATUS_MISSING, 0)
strict_test_can_finalize = sum(1 for p in strict_test_exec["packets"] if p.get("execution_summary", {}).get("can_finalize"))

stale_manifest = copy.deepcopy(strict_test_manifest)
for record in stale_manifest.get("model_input_sources", {}).values():
    if isinstance(record, dict):
        record["source_freshness_status"] = "stale"
stale_bundle = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date, model_input_bundle=model_inputs, model_input_source_manifest=stale_manifest, strict_model_input_sources=True)
stale_exec = execute_all(answers, stale_bundle, executor)
stale_blocks = sum(1 for r in stale_exec["results"] if r.get("adapter_type") in MODEL_TYPES and r.get("execution_status") == source_status)

promotion_tampered = copy.deepcopy(strict_test_manifest)
for record in promotion_tampered.get("model_input_sources", {}).values():
    if isinstance(record, dict):
        record["promotion_eligible"] = True
promotion_tampered_bundle = runner.bundle_for_answers(root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date, model_input_bundle=model_inputs, model_input_source_manifest=promotion_tampered, strict_model_input_sources=True)
promotion_tampered_exec = execute_all(answers, promotion_tampered_bundle, executor)
promotion_tampered_blocks = sum(
    1
    for r in promotion_tampered_exec["results"]
    if r.get("adapter_type") in MODEL_TYPES
    and r.get("execution_status") in {source_status, executor.STATUS_ATTESTATION_NOT_VERIFIED}
)
promotion_tampered_attestation_blocks = sum(
    1
    for r in promotion_tampered_exec["results"]
    if r.get("adapter_type") in MODEL_TYPES
    and r.get("execution_status") == executor.STATUS_ATTESTATION_NOT_VERIFIED
)

checks = [
    (reference_manifest.get("summary", {}).get("model_input_source_count") == model_adapter_count, "reference manifest must emit one source record per model input"),
    (strict_test_manifest.get("summary", {}).get("model_input_source_count") == model_adapter_count, "strict-test manifest must emit one source record per model input"),
    (complete_reference == model_adapter_count and complete_strict == model_adapter_count, "every source record must carry explicit truth-boundary fields"),
    (strict_test_manifest.get("summary", {}).get("strict_schema_test_fixture_count") == model_adapter_count, "strict-test manifest must label every record as a strict schema fixture"),
    (strict_test_manifest.get("summary", {}).get("promotion_eligible_count") == 0, "archive-generated model source records must never be promotion eligible"),
    (no_source_blocks == model_adapter_count, "strict execution must block every model adapter when the source manifest is missing"),
    (reference_blocks == model_adapter_count, "strict execution must block reference fixtures"),
    (strict_test_source_blocks == 0, "explicit strict-test context should exercise model adapter schemas"),
    (strict_test_satisfied == model_satisfied_expected, "strict-test context should satisfy quantitative and floor-delivery schemas"),
    (strict_test_no_go_blocks == no_go_expected, "strict-test local no-go screens must remain blocking"),
    (strict_test_missing_authority == authority_expected, "model-only strict tests must leave authority adapters missing"),
    (strict_test_can_finalize == 0, "model-only strict tests must not finalize full answer packets"),
    (stale_blocks == model_adapter_count, "strict execution must block stale strict-test source records"),
    (promotion_tampered_blocks == model_adapter_count, "a fixture cannot become acceptable by flipping promotion_eligible"),
    (promotion_tampered_attestation_blocks == model_adapter_count, "promotion tamper must trip the external-attestation gate"),
]
for ok, message in checks:
    if not ok:
        errors.append(message)

contracts = json.loads((root / "docs/00-meta/evidence-producer-contracts.json").read_text(encoding="utf-8"))
schema = json.loads((root / "docs/00-meta/evidence-producer-contracts-schema.json").read_text(encoding="utf-8"))
source_fields = set(executor.INPUT_SOURCE_PROOF_FIELDS)
if set(schema.get("model_contract_required_input_source_fields", [])) != source_fields:
    errors.append("evidence producer schema must list the executor input-source proof fields")
for contract in contracts.get("producer_contracts", []):
    if set(contract.get("adapter_types", [])) & MODEL_TYPES:
        missing = sorted(source_fields - set(contract.get("required_evidence_fields", [])))
        if missing:
            errors.append(f"model producer contract {contract.get('producer_id')} missing input-source fields {missing}")
        if contract.get("requires_implementation_grade_input_source") is not True:
            errors.append(f"model producer contract {contract.get('producer_id')} must require implementation-grade input sources")

summary = cube.get("audit_summary", {})
expected = {
    "model_input_source_manifest_required": True,
    "model_input_source_runtime_status": RUNTIME_STATUS,
    "model_input_source_answer_count": answer_count,
    "model_input_source_model_adapter_count": model_adapter_count,
    "model_input_source_reference_record_count": len(reference_records),
    "model_input_source_strict_test_record_count": len(strict_records),
    "model_input_source_complete_reference_count": complete_reference,
    "model_input_source_complete_strict_test_count": complete_strict,
    "model_input_source_implementation_builder_refused": implementation_builder_refused,
    "model_input_source_strict_no_manifest_block_count": no_source_blocks,
    "model_input_source_strict_reference_block_count": reference_blocks,
    "model_input_source_strict_test_satisfied_count": strict_test_satisfied,
    "model_input_source_strict_test_no_go_block_count": strict_test_no_go_blocks,
    "model_input_source_strict_test_missing_authority_count": strict_test_missing_authority,
    "model_input_source_strict_test_can_finalize_count": strict_test_can_finalize,
    "model_input_source_stale_block_count": stale_blocks,
    "model_input_source_promotion_flag_tamper_block_count": promotion_tampered_blocks,
    "model_input_source_promotion_flag_tamper_attestation_block_count": promotion_tampered_attestation_blocks,
    "model_input_source_adapter_type_counts": dict(sorted(type_counts.items())),
}
for key, value in expected.items():
    if summary.get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("model_input_source_manifest_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json model_input_source_manifest_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    lines = [
        f"Model-input source runtime status: {RUNTIME_STATUS}",
        f"Answer packets checked: {answer_count}",
        f"Model adapter checks: {model_adapter_count}",
        f"Reference source records: {len(reference_records)}/{model_adapter_count}",
        f"Strict-schema test source records: {len(strict_records)}/{model_adapter_count}",
        "Implementation-grade source builder refused: yes",
        f"Strict no-source blocks: {no_source_blocks}/{model_adapter_count}",
        f"Strict reference-fixture blocks: {reference_blocks}/{model_adapter_count}",
        f"Strict-schema quantitative and floor schemas satisfied: {strict_test_satisfied}/{model_satisfied_expected}",
        f"Strict-schema no-go adapters blocked: {strict_test_no_go_blocks}/{no_go_expected}",
        f"Stale source-manifest blocks: {stale_blocks}/{model_adapter_count}",
        f"Promotion-flag tamper blocks: {promotion_tampered_blocks}/{model_adapter_count}",
        f"Promotion-flag tamper external-attestation blocks: {promotion_tampered_attestation_blocks}/{model_adapter_count}",
    ]
    for line in lines:
        if line not in report:
            errors.append(f"model-input source audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("model input source manifest audit ok")
