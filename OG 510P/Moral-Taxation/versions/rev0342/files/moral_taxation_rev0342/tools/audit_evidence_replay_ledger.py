#!/usr/bin/env python3
"""Audit replay ledgers and evidence-origin binding."""
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
LEDGER_STATUS = "evidence_replay_ledger_generated"
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


def tamper_all_evidence(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(bundle))
    for pool_name in ["adapter_evidence", "current_law", "jurisdiction_scope", "models", "floor_delivery", "no_go_threshold"]:
        pool = out.get(pool_name, {})
        if isinstance(pool, dict):
            for key, evidence in pool.items():
                if isinstance(evidence, dict):
                    evidence["replay_tamper_probe"] = f"tampered:{key}"
    return out


def flip_fixture_promotion_flag(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(bundle))
    for pool_name in ["adapter_evidence", "current_law", "jurisdiction_scope", "models", "floor_delivery", "no_go_threshold"]:
        pool = out.get(pool_name, {})
        if isinstance(pool, dict):
            for evidence in pool.values():
                if isinstance(evidence, dict):
                    evidence["promotion_eligible"] = True
    return out


materializer = load_module("materialize_decision_outputs", root / "tools/materialize_decision_outputs.py")
ledger_builder = load_module("build_evidence_replay_ledger", root / "tools/build_evidence_replay_ledger.py")
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")

receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
adapter_checks = [c for a in answers for c in a.get("disposition", {}).get("adapter_checks", [])]
adapter_check_count = len(adapter_checks)

strict_test_bundle = materializer.strict_schema_test_evidence_bundle_for_answers(root, answers, as_of_date)
ledger = ledger_builder.ledger_for_answers(root, answers, strict_test_bundle)
replayed = ledger_builder.ledger_for_answers(root, answers, strict_test_bundle)
comparison = ledger_builder.replay_compare(ledger, replayed)
tampered_ledger = ledger_builder.ledger_for_answers(root, answers, tamper_all_evidence(strict_test_bundle))
tamper_comparison = ledger_builder.replay_compare(ledger, tampered_ledger)
flag_tampered_ledger = ledger_builder.ledger_for_answers(root, answers, flip_fixture_promotion_flag(strict_test_bundle))
flag_tamper_comparison = ledger_builder.replay_compare(ledger, flag_tampered_ledger)

summary = ledger.get("summary", {})
if ledger.get("runtime_status") != LEDGER_STATUS:
    errors.append("evidence replay ledger runtime_status is stale")
if ledger.get("answer_count") != len(answers):
    errors.append("evidence replay ledger answer count drifted")
if ledger.get("adapter_execution_count") != adapter_check_count or summary.get("record_count") != adapter_check_count:
    errors.append("evidence replay ledger record count must equal adapter checks")
if summary.get("evidence_present_count") != adapter_check_count:
    errors.append("strict-schema ledger should have evidence present for every adapter check")
if summary.get("producer_contract_hash_count") != adapter_check_count:
    errors.append("strict-schema ledger should bind every record to a producer contract")
if summary.get("strict_schema_test_fixture_record_count") != adapter_check_count:
    errors.append("every built-in release-audit record must be labeled strict_schema_test_fixture")
if summary.get("external_observed_record_count") != 0:
    errors.append("built-in release-audit ledger must contain zero externally observed records")
if summary.get("verified_external_attestation_record_count") != 0:
    errors.append("built-in release-audit ledger must contain zero verified external attestations")
if summary.get("trusted_external_attestation_verified_record_count") != 0:
    errors.append("built-in release-audit ledger must contain zero cryptographically verified external attestations")
if summary.get("attestation_not_required_record_count") != adapter_check_count:
    errors.append("strict-schema release ledger should mark every record attestation-not-required")
if ledger.get("trusted_external_attestation_verifier_status") != "not_configured_fail_closed":
    errors.append("built-in release-audit ledger must remain fail-closed without a configured trust store")
if summary.get("promotion_eligible_record_count") != 0:
    errors.append("built-in release-audit ledger must contain zero promotion-eligible records")
if not ledger.get("ledger_hash") or ledger.get("ledger_hash") != ledger_builder.compact_hash(ledger.get("ledger_records", [])):
    errors.append("ledger_hash must bind the complete ledger record list")
if "not current law" not in str(ledger.get("ledger_non_doctrine_warning", "")):
    errors.append("ledger must carry a non-doctrine warning")

for rec in ledger.get("ledger_records", []):
    key = rec.get("record_key")
    if rec.get("ledger_record_runtime_status") != LEDGER_STATUS:
        errors.append(f"ledger record {key} has stale runtime status")
    for field in ["adapter_packet_hash", "adapter_binding_hash", "evidence_hash", "producer_contract_hash", "evidence_truth_boundary_hash", "decision_trace_hash", "result_hash"]:
        if not rec.get(field):
            errors.append(f"ledger record {key} missing {field}")
    truth = {
        "adapter_binding_hash": rec.get("adapter_binding_hash"),
        "evidence_adapter_binding_hash": rec.get("evidence_adapter_binding_hash"),
        "strict_model_input_source_certification_required": rec.get("strict_model_input_source_certification_required") is True,
        "strict_authority_evidence_required": rec.get("strict_authority_evidence_required") is True,
        "input_certification_level": rec.get("input_certification_level"),
        "input_source_record_hash": rec.get("input_source_record_hash"),
        "input_source_manifest_hash": rec.get("input_source_manifest_hash"),
        "authority_certification_level": rec.get("authority_certification_level"),
        "authority_evidence_record_hash": rec.get("authority_evidence_record_hash"),
        "authority_evidence_bundle_hash": rec.get("authority_evidence_bundle_hash"),
        "authority_source_record_hash": rec.get("authority_source_record_hash"),
        "authority_source_manifest_hash": rec.get("authority_source_manifest_hash"),
        "strict_schema_test_fixture": rec.get("strict_schema_test_fixture") is True,
        "evidence_origin": rec.get("evidence_origin"),
        "external_source_attestation_status": rec.get("external_source_attestation_status"),
        "promotion_eligible": rec.get("promotion_eligible") is True,
        "external_attestation_verifier_status": rec.get("external_attestation_verifier_status"),
        "trusted_external_attestation": rec.get("trusted_external_attestation") is True,
    }
    if rec.get("evidence_truth_boundary_hash") != ledger_builder.compact_hash(truth):
        errors.append(f"ledger record {key} truth-boundary hash drifted")
    if rec.get("strict_schema_test_fixture") is not True or rec.get("evidence_origin") != "archive_generated_strict_schema_test_fixture":
        errors.append(f"ledger record {key} obscures its fixture origin")
    if rec.get("promotion_eligible") is not False:
        errors.append(f"ledger record {key} must not be promotion eligible")
    if "not current law" not in str(rec.get("non_doctrine_warning", "")):
        errors.append(f"ledger record {key} missing non-doctrine warning")
    if {"raw_evidence", "evidence_snapshot", "evidence_record", "authority_text", "model_output_snapshot"}.intersection(rec):
        errors.append(f"ledger record {key} stores forbidden raw evidence")

if comparison.get("mismatch_count") != 0:
    errors.append("same-bundle replay must have zero mismatches")
if tamper_comparison.get("mismatch_count", 0) < adapter_check_count:
    errors.append("evidence tampering must be detected for every adapter record")
if flag_tamper_comparison.get("mismatch_count", 0) < adapter_check_count:
    errors.append("fixture promotion-flag tampering must be detected for every adapter record")
if flag_tamper_comparison.get("mismatch_type_counts", {}).get("promotion_eligible", 0) != adapter_check_count:
    errors.append("replay comparison must expose promotion_eligible drift for every adapter record")

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
expected = {
    "evidence_replay_ledger_required": True,
    "evidence_replay_ledger_runtime_status": LEDGER_STATUS,
    "evidence_replay_answer_count": len(answers),
    "evidence_replay_record_count": adapter_check_count,
    "evidence_replay_evidence_present_count": summary.get("evidence_present_count"),
    "evidence_replay_producer_contract_hash_count": summary.get("producer_contract_hash_count"),
    "evidence_replay_adapter_binding_hash_record_count": summary.get("adapter_binding_hash_count"),
    "evidence_replay_external_adapter_binding_hash_record_count": summary.get("external_adapter_binding_hash_count"),
    "evidence_replay_adapter_binding_mismatch_count": summary.get("adapter_binding_mismatch_count"),
    "evidence_replay_strict_schema_test_fixture_record_count": summary.get("strict_schema_test_fixture_record_count"),
    "evidence_replay_external_observed_record_count": summary.get("external_observed_record_count"),
    "evidence_replay_promotion_eligible_record_count": summary.get("promotion_eligible_record_count"),
    "evidence_replay_strict_model_input_source_required_record_count": summary.get("strict_model_input_source_required_record_count"),
    "evidence_replay_strict_model_input_source_proof_record_count": summary.get("strict_model_input_source_proof_record_count"),
    "evidence_replay_strict_authority_evidence_required_record_count": summary.get("strict_authority_evidence_required_record_count"),
    "evidence_replay_strict_authority_evidence_proof_record_count": summary.get("strict_authority_evidence_proof_record_count"),
    "evidence_replay_trusted_external_attestation_verified_record_count": summary.get("trusted_external_attestation_verified_record_count"),
    "evidence_replay_attestation_not_required_record_count": summary.get("attestation_not_required_record_count"),
    "evidence_replay_trusted_external_attestation_verifier_status": ledger.get("trusted_external_attestation_verifier_status"),
    "evidence_replay_schema_execution_can_finalize_count": summary.get("case_can_finalize_count"),
    "evidence_replay_schema_execution_blocked_count": summary.get("case_blocked_count"),
    "evidence_replay_same_bundle_mismatch_count": comparison.get("mismatch_count"),
    "evidence_replay_hash_tamper_mismatch_count": tamper_comparison.get("mismatch_count"),
    "evidence_replay_promotion_flag_tamper_mismatch_count": flag_tamper_comparison.get("mismatch_count"),
    "evidence_replay_status_counts": summary.get("status_counts"),
    "evidence_replay_adapter_type_counts": summary.get("adapter_type_counts"),
}
for key, value in expected.items():
    if cube.get("audit_summary", {}).get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("evidence_replay_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json evidence_replay_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    lines = [
        f"Evidence replay runtime status: {LEDGER_STATUS}",
        f"Answer packets checked: {len(answers)}",
        f"Adapter ledger records: {adapter_check_count}/{adapter_check_count}",
        f"Strict-schema fixture records: {summary.get('strict_schema_test_fixture_record_count')}/{adapter_check_count}",
        f"Externally observed records: {summary.get('external_observed_record_count')}/{adapter_check_count}",
        f"Promotion-eligible records: {summary.get('promotion_eligible_record_count')}/{adapter_check_count}",
        f"Strict model-input source proof records: {summary.get('strict_model_input_source_proof_record_count')}/{summary.get('strict_model_input_source_required_record_count')}",
        f"Strict authority evidence proof records: {summary.get('strict_authority_evidence_proof_record_count')}/{summary.get('strict_authority_evidence_required_record_count')}",
        f"Trusted external attestation verified records: {summary.get('trusted_external_attestation_verified_record_count')}/{adapter_check_count}",
        f"Adapter binding hashes recorded: {summary.get('adapter_binding_hash_count')}/{adapter_check_count}",
        f"External adapter binding hashes: {summary.get('external_adapter_binding_hash_count')}/{adapter_check_count}",
        f"Adapter binding mismatches: {summary.get('adapter_binding_mismatch_count')}",
        f"Attestation-not-required fixture records: {summary.get('attestation_not_required_record_count')}/{adapter_check_count}",
        f"Trusted external attestation verifier status: {ledger.get('trusted_external_attestation_verifier_status')}",
        f"Schema-execution finalizable cases: {summary.get('case_can_finalize_count')}/{len(answers)}",
        f"Same-bundle replay mismatches: {comparison.get('mismatch_count')}",
        f"Evidence-tamper replay mismatches: {tamper_comparison.get('mismatch_count')}",
        f"Promotion-flag replay mismatches: {flag_tamper_comparison.get('mismatch_count')}",
    ]
    for line in lines:
        if line not in report:
            errors.append(f"evidence replay audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("evidence replay ledger audit ok")
