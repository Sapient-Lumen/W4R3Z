#!/usr/bin/env python3
"""Audit the current-law and jurisdiction evidence truth boundary.

Archive builders may emit reference and strict-schema fixtures, but must refuse
implementation-grade authority provenance. Strict-schema fixtures can exercise
interfaces only under an explicit test context and remain non-promotable.
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
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
AUTHORITY_STATUS = "authority_evidence_bundle_generated"
INTAKE_STATUS = "authority_intake_bundle_generated"
SOURCE_STATUS = "authority_intake_source_manifest_generated"
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
            [sys.executable, str(root / "tools/answer_case.py"), str(root), "--all", "--route-limit", str(ROUTE_LIMIT), "--facts-only-candidate-limit", str(FACTS_ONLY_LIMIT), "--json"],
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    return json.loads(raw)


def execute_all(answers: List[Dict[str, Any]], bundle: Mapping[str, Any], executor: Any) -> Dict[str, Any]:
    packets = [executor.execute_answer(answer, bundle) for answer in answers]
    results = [r for packet in packets for r in packet.get("adapter_execution_results", [])]
    return {"packets": packets, "results": results, "summary": executor.summarize_execution(results)}


def merge_bundle(base: Mapping[str, Any], extra: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(base))
    for pool in ["adapter_evidence", "current_law", "jurisdiction_scope", "models", "floor_delivery", "no_go_threshold"]:
        incoming = extra.get(pool, {}) if isinstance(extra, Mapping) else {}
        if isinstance(incoming, Mapping):
            out.setdefault(pool, {}).update(copy.deepcopy(dict(incoming)))
    context = extra.get("execution_context", {}) if isinstance(extra, Mapping) else {}
    if isinstance(context, Mapping):
        out.setdefault("execution_context", {}).update(copy.deepcopy(dict(context)))
    if extra.get("producer_contracts") and not out.get("producer_contracts"):
        out["producer_contracts"] = copy.deepcopy(extra.get("producer_contracts"))
    return out


cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")
runner = load_module("run_evidence_producers", root / "tools/run_evidence_producers.py")
input_builder = load_module("build_model_input_bundle", root / "tools/build_model_input_bundle.py")
model_source_builder = load_module("build_model_input_source_manifest", root / "tools/build_model_input_source_manifest.py")
authority_builder = load_module("build_authority_evidence_bundle", root / "tools/build_authority_evidence_bundle.py")
intake_builder = load_module("build_authority_intake_bundle", root / "tools/build_authority_intake_bundle.py")
authority_source_builder = load_module("build_authority_intake_source_manifest", root / "tools/build_authority_intake_source_manifest.py")

payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
answer_count = len(answers)
adapter_checks = [c for a in answers for c in a.get("disposition", {}).get("adapter_checks", [])]
authority_types = set(executor.AUTHORITY_ADAPTER_TYPES)
model_types = set(executor.MODEL_ADAPTER_TYPES)
authority_count = sum(1 for c in adapter_checks if c.get("adapter_type") in authority_types)
current_law_count = sum(1 for c in adapter_checks if c.get("adapter_type") == "current_law_refresh_adapter")
jurisdiction_count = sum(1 for c in adapter_checks if c.get("adapter_type") == "jurisdiction_scope_adapter")
model_satisfied_expected = sum(1 for c in adapter_checks if c.get("adapter_type") in {"quantitative_model_adapter", "floor_delivery_adapter"})
no_go_expected = sum(1 for c in adapter_checks if c.get("adapter_type") == "no_go_threshold_adapter")
model_count = sum(1 for c in adapter_checks if c.get("adapter_type") in model_types)

model_inputs = input_builder.bundle_for_answers(answers, as_of_date)
model_strict_sources = model_source_builder.manifest_for_input_bundle(model_inputs, as_of_date, model_source_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE)
strict_model_base = runner.bundle_for_answers(
    root, answers, runner.MODE_LOCAL_MODEL_ONLY, as_of_date,
    model_input_bundle=model_inputs,
    model_input_source_manifest=model_strict_sources,
    strict_model_input_sources=True,
    strict_authority_evidence=True,
)
no_authority_exec = execute_all(answers, strict_model_base, executor)
no_authority_missing = sum(1 for r in no_authority_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == executor.STATUS_MISSING)

reference_source = authority_source_builder.manifest_for_answers(answers, as_of_date, authority_source_builder.CERT_REFERENCE_FIXTURE)
strict_source = authority_source_builder.manifest_for_answers(answers, as_of_date, authority_source_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE)
implementation_builder_refused = False
try:
    authority_source_builder.manifest_for_answers(answers, as_of_date, authority_source_builder.CERT_IMPLEMENTATION_GRADE)
except ValueError:
    implementation_builder_refused = True

no_source_strict_intake = intake_builder.bundle_for_answers(answers, as_of_date, intake_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE)
reference_intake = intake_builder.bundle_for_answers(answers, as_of_date, intake_builder.CERT_REFERENCE_FIXTURE, reference_source)
strict_intake = intake_builder.bundle_for_answers(answers, as_of_date, intake_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE, strict_source)
relabel_attempt_intake = intake_builder.bundle_for_answers(answers, as_of_date, intake_builder.CERT_IMPLEMENTATION_GRADE, strict_source)

reference_authority = authority_builder.bundle_for_answers(root, answers, as_of_date, authority_builder.CERT_REFERENCE_FIXTURE, True)
no_intake_strict_authority = authority_builder.bundle_for_answers(root, answers, as_of_date, authority_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE, True)
strict_authority = authority_builder.bundle_for_answers(root, answers, as_of_date, authority_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE, True, strict_intake)
reference_intake_strict_authority = authority_builder.bundle_for_answers(root, answers, as_of_date, authority_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE, True, reference_intake)

for label, obj, status in [
    ("reference source", reference_source, SOURCE_STATUS),
    ("strict source", strict_source, SOURCE_STATUS),
    ("strict intake", strict_intake, INTAKE_STATUS),
    ("reference intake", reference_intake, INTAKE_STATUS),
    ("reference authority", reference_authority, AUTHORITY_STATUS),
    ("strict authority", strict_authority, AUTHORITY_STATUS),
]:
    if obj.get("runtime_status") != status:
        errors.append(f"{label} runtime_status is stale")

reference_exec = execute_all(answers, merge_bundle(strict_model_base, reference_authority), executor)
no_intake_exec = execute_all(answers, merge_bundle(strict_model_base, no_intake_strict_authority), executor)
strict_exec = execute_all(answers, merge_bundle(strict_model_base, strict_authority), executor)
reference_intake_exec = execute_all(answers, merge_bundle(strict_model_base, reference_intake_strict_authority), executor)

authority_status = executor.STATUS_AUTHORITY_NOT_CERTIFIED
reference_blocks = sum(1 for r in reference_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == authority_status)
no_intake_missing = sum(1 for r in no_intake_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == executor.STATUS_MISSING)
reference_intake_blocks = sum(1 for r in reference_intake_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == authority_status)
strict_authority_blocks = sum(1 for r in strict_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == authority_status)
strict_authority_satisfied = sum(1 for r in strict_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == executor.STATUS_SATISFIED)
strict_model_satisfied = sum(1 for r in strict_exec["results"] if r.get("adapter_type") in {"quantitative_model_adapter", "floor_delivery_adapter"} and r.get("execution_status") == executor.STATUS_SATISFIED)
strict_no_go_blocks = sum(1 for r in strict_exec["results"] if r.get("adapter_type") == "no_go_threshold_adapter" and r.get("execution_status") == executor.STATUS_BLOCKS)
strict_execution_can_finalize = sum(1 for p in strict_exec["packets"] if p.get("execution_summary", {}).get("can_finalize"))

stale_authority = copy.deepcopy(strict_authority)
for record in stale_authority.get("adapter_evidence", {}).values():
    if isinstance(record, dict):
        record["authority_source_freshness_status"] = "stale"
stale_exec = execute_all(answers, merge_bundle(strict_model_base, stale_authority), executor)
stale_blocks = sum(1 for r in stale_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == authority_status)

promotion_tampered = copy.deepcopy(strict_authority)
for record in promotion_tampered.get("adapter_evidence", {}).values():
    if isinstance(record, dict):
        record["promotion_eligible"] = True
promotion_tampered_exec = execute_all(answers, merge_bundle(strict_model_base, promotion_tampered), executor)
promotion_tampered_blocks = sum(
    1
    for r in promotion_tampered_exec["results"]
    if r.get("adapter_type") in authority_types
    and r.get("execution_status") in {authority_status, executor.STATUS_ATTESTATION_NOT_VERIFIED}
)
promotion_tampered_attestation_blocks = sum(
    1
    for r in promotion_tampered_exec["results"]
    if r.get("adapter_type") in authority_types
    and r.get("execution_status") == executor.STATUS_ATTESTATION_NOT_VERIFIED
)

interface_bundle = runner.bundle_for_answers(root, answers, runner.MODE_INTERFACE_FIXTURE, as_of_date, strict_model_input_sources=True, strict_authority_evidence=True)
interface_exec = execute_all(answers, interface_bundle, executor)
interface_authority_blocks = sum(1 for r in interface_exec["results"] if r.get("adapter_type") in authority_types and r.get("execution_status") == authority_status)
interface_model_blocks = sum(1 for r in interface_exec["results"] if r.get("adapter_type") in model_types and r.get("execution_status") == executor.STATUS_INPUT_SOURCE_NOT_CERTIFIED)

checks = [
    (implementation_builder_refused, "archive authority source builder must refuse implementation-grade provenance"),
    (strict_source.get("summary", {}).get("authority_source_record_count") == authority_count, "strict source manifest must emit one record per authority adapter"),
    (strict_source.get("summary", {}).get("promotion_eligible_count") == 0, "archive-generated authority source records must never be promotion eligible"),
    (no_source_strict_intake.get("summary", {}).get("authority_intake_record_count") == 0, "strict intake without source manifest must emit zero records"),
    (no_source_strict_intake.get("summary", {}).get("missing_authority_source_count") == authority_count, "strict intake must count every missing source"),
    (strict_intake.get("summary", {}).get("authority_intake_record_count") == authority_count, "strict intake must emit one record per authority adapter"),
    (relabel_attempt_intake.get("summary", {}).get("authority_intake_record_count") == 0, "strict fixtures must not be relabeled as implementation intake"),
    (relabel_attempt_intake.get("summary", {}).get("invalid_implementation_authority_source_count") == authority_count, "relabel attempts must be counted as invalid implementation sources"),
    (no_intake_strict_authority.get("summary", {}).get("authority_evidence_record_count") == 0, "strict authority evidence without intake must emit zero records"),
    (no_intake_strict_authority.get("summary", {}).get("missing_authority_intake_count") == authority_count, "strict authority evidence must count missing intake"),
    (strict_authority.get("summary", {}).get("authority_evidence_record_count") == authority_count, "strict authority bundle must emit one record per authority adapter"),
    (no_authority_missing == authority_count, "strict model base must leave every authority adapter missing"),
    (no_intake_missing == authority_count, "strict authority without intake must leave every authority adapter missing"),
    (reference_blocks == authority_count, "reference authority fixtures must be certification-blocked"),
    (reference_intake_blocks == authority_count, "reference intake cannot satisfy strict authority execution"),
    (strict_authority_blocks == 0, "explicit strict-test context should exercise authority schemas"),
    (strict_authority_satisfied == authority_count, "strict-test context should satisfy authority adapter schemas"),
    (strict_model_satisfied == model_satisfied_expected, "strict authority merge should preserve quantitative and floor schema satisfactions"),
    (strict_no_go_blocks == no_go_expected, "strict authority merge should preserve no-go blocks"),
    (stale_blocks == authority_count, "stale authority fixtures must be blocked"),
    (promotion_tampered_blocks == authority_count, "a fixture cannot become acceptable by flipping promotion_eligible"),
    (promotion_tampered_attestation_blocks == authority_count, "promotion tamper must trip the external-attestation gate"),
    (interface_authority_blocks == authority_count, "interface fixtures must be authority-blocked"),
    (interface_model_blocks == model_count, "interface fixtures must be model-source-blocked"),
]
for ok, message in checks:
    if not ok:
        errors.append(message)

contracts = json.loads((root / "docs/00-meta/evidence-producer-contracts.json").read_text(encoding="utf-8"))
schema = json.loads((root / "docs/00-meta/evidence-producer-contracts-schema.json").read_text(encoding="utf-8"))
authority_fields = set(executor.AUTHORITY_PROOF_FIELDS)
if set(schema.get("authority_contract_required_proof_fields", [])) != authority_fields:
    errors.append("evidence producer schema must list the executor authority proof fields")
for contract in contracts.get("producer_contracts", []):
    if set(contract.get("adapter_types", [])) & authority_types:
        missing = sorted(authority_fields - set(contract.get("required_evidence_fields", [])))
        if missing:
            errors.append(f"authority producer contract {contract.get('producer_id')} missing proof fields {missing}")

summary = cube.get("audit_summary", {})
expected = {
    "authority_evidence_bundle_required": True,
    "authority_evidence_runtime_status": AUTHORITY_STATUS,
    "authority_intake_runtime_status": INTAKE_STATUS,
    "authority_source_runtime_status": SOURCE_STATUS,
    "authority_evidence_answer_count": answer_count,
    "authority_evidence_adapter_count": authority_count,
    "authority_evidence_current_law_count": current_law_count,
    "authority_evidence_jurisdiction_count": jurisdiction_count,
    "authority_source_reference_record_count": reference_source.get("summary", {}).get("authority_source_record_count"),
    "authority_source_strict_test_record_count": strict_source.get("summary", {}).get("authority_source_record_count"),
    "authority_source_implementation_builder_refused": implementation_builder_refused,
    "authority_intake_no_source_record_count": no_source_strict_intake.get("summary", {}).get("authority_intake_record_count"),
    "authority_intake_missing_source_count": no_source_strict_intake.get("summary", {}).get("missing_authority_source_count"),
    "authority_intake_strict_test_record_count": strict_intake.get("summary", {}).get("authority_intake_record_count"),
    "authority_intake_relabel_attempt_record_count": relabel_attempt_intake.get("summary", {}).get("authority_intake_record_count"),
    "authority_intake_relabel_attempt_invalid_count": relabel_attempt_intake.get("summary", {}).get("invalid_implementation_authority_source_count"),
    "authority_evidence_no_intake_record_count": no_intake_strict_authority.get("summary", {}).get("authority_evidence_record_count"),
    "authority_evidence_no_intake_missing_count": no_intake_strict_authority.get("summary", {}).get("missing_authority_intake_count"),
    "authority_evidence_reference_record_count": reference_authority.get("summary", {}).get("authority_evidence_record_count"),
    "authority_evidence_strict_test_record_count": strict_authority.get("summary", {}).get("authority_evidence_record_count"),
    "authority_evidence_strict_no_bundle_missing_count": no_authority_missing,
    "authority_evidence_no_intake_execution_missing_count": no_intake_missing,
    "authority_evidence_strict_reference_block_count": reference_blocks,
    "authority_evidence_reference_intake_block_count": reference_intake_blocks,
    "authority_evidence_strict_test_satisfied_count": strict_authority_satisfied,
    "authority_evidence_strict_test_model_satisfied_count": strict_model_satisfied,
    "authority_evidence_strict_test_no_go_block_count": strict_no_go_blocks,
    "authority_evidence_strict_test_execution_can_finalize_count": strict_execution_can_finalize,
    "authority_evidence_stale_block_count": stale_blocks,
    "authority_evidence_promotion_flag_tamper_block_count": promotion_tampered_blocks,
    "authority_evidence_promotion_flag_tamper_attestation_block_count": promotion_tampered_attestation_blocks,
    "authority_evidence_strict_interface_authority_block_count": interface_authority_blocks,
    "authority_evidence_strict_interface_model_block_count": interface_model_blocks,
    "authority_evidence_adapter_type_counts": dict(sorted(strict_authority.get("summary", {}).get("adapter_type_counts", {}).items())),
}
for key, value in expected.items():
    if summary.get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("authority_evidence_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json authority_evidence_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    lines = [
        f"Authority evidence runtime status: {AUTHORITY_STATUS}",
        f"Authority intake runtime status: {INTAKE_STATUS}",
        f"Authority source runtime status: {SOURCE_STATUS}",
        f"Answer packets checked: {answer_count}",
        f"Authority adapter checks: {authority_count}",
        f"Current-law authority checks: {current_law_count}",
        f"Jurisdiction-scope authority checks: {jurisdiction_count}",
        f"Strict-schema authority-source records: {strict_source.get('summary', {}).get('authority_source_record_count')}/{authority_count}",
        "Implementation-grade authority source builder refused: yes",
        f"Strict authority intake without source records: {no_source_strict_intake.get('summary', {}).get('authority_intake_record_count')}/{authority_count}",
        f"Missing authority source records: {no_source_strict_intake.get('summary', {}).get('missing_authority_source_count')}/{authority_count}",
        f"Strict-schema authority intake records: {strict_intake.get('summary', {}).get('authority_intake_record_count')}/{authority_count}",
        f"Implementation relabel attempt intake records: {relabel_attempt_intake.get('summary', {}).get('authority_intake_record_count')}/{authority_count}",
        f"Strict authority records without intake: {no_intake_strict_authority.get('summary', {}).get('authority_evidence_record_count')}/{authority_count}",
        f"Strict-schema authority evidence records: {strict_authority.get('summary', {}).get('authority_evidence_record_count')}/{authority_count}",
        f"Strict reference authority blocks: {reference_blocks}/{authority_count}",
        f"Strict-schema authority satisfactions: {strict_authority_satisfied}/{authority_count}",
        f"Stale authority blocks: {stale_blocks}/{authority_count}",
        f"Promotion-flag tamper blocks: {promotion_tampered_blocks}/{authority_count}",
        f"Strict interface authority blocks: {interface_authority_blocks}/{authority_count}",
        f"Strict interface model blocks: {interface_model_blocks}/{model_count}",
    ]
    for line in lines:
        if line not in report:
            errors.append(f"authority evidence audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("authority evidence bundle audit ok")
