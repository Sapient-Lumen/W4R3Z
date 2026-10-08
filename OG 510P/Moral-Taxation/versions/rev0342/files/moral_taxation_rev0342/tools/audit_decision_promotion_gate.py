#!/usr/bin/env python3
"""Audit promotion: schema-conformance evidence must never become a decision."""
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
PROMOTION_STATUS = "decision_promotion_gate_evaluated"
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
                    evidence["promotion_tamper_probe"] = f"tampered:{key}"
    return out


def forge_ledger_origin_without_rehash(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(ledger))
    for record in out.get("ledger_records", []):
        if isinstance(record, dict):
            record["strict_schema_test_fixture"] = False
            record["evidence_origin"] = "external_observed"
            record["external_source_attestation_status"] = "verified_external_attestation"
            record["promotion_eligible"] = True
            record["external_attestation_verifier_status"] = "verified_external_attestation"
            record["trusted_external_attestation"] = True
    return out


materializer = load_module("materialize_decision_outputs", root / "tools/materialize_decision_outputs.py")
ledger_builder = load_module("build_evidence_replay_ledger", root / "tools/build_evidence_replay_ledger.py")
promoter = load_module("promote_decision_release", root / "tools/promote_decision_release.py")
runner = load_module("run_evidence_producers", root / "tools/run_evidence_producers.py")

receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
case_count = len(answers)
adapter_check_count = sum(len(a.get("disposition", {}).get("adapter_checks", [])) for a in answers)

strict_bundle = materializer.strict_schema_test_evidence_bundle_for_answers(root, answers, as_of_date)
ledger = ledger_builder.ledger_for_answers(root, answers, strict_bundle)
replayed = ledger_builder.ledger_for_answers(root, answers, strict_bundle)
comparison = ledger_builder.replay_compare(ledger, replayed)
promotion = promoter.promotion_from_ledger(ledger, comparison)

empty_ledger = ledger_builder.ledger_for_answers(root, answers, {})
empty_replay = ledger_builder.ledger_for_answers(root, answers, {})
empty_promotion = promoter.promotion_from_ledger(empty_ledger, ledger_builder.replay_compare(empty_ledger, empty_replay))

interface_bundle = runner.bundle_for_answers(root, answers, runner.MODE_INTERFACE_FIXTURE, as_of_date, strict_model_input_sources=True, strict_authority_evidence=True)
interface_ledger = ledger_builder.ledger_for_answers(root, answers, interface_bundle)
interface_promotion = promoter.promotion_from_ledger(interface_ledger, ledger_builder.replay_compare(interface_ledger, ledger_builder.ledger_for_answers(root, answers, interface_bundle)))

tampered_ledger = ledger_builder.ledger_for_answers(root, answers, tamper_all_evidence(strict_bundle))
tamper_comparison = ledger_builder.replay_compare(ledger, tampered_ledger)
tamper_promotion = promoter.promotion_from_ledger(ledger, tamper_comparison)

forged_ledger = forge_ledger_origin_without_rehash(ledger)
forged_promotion = promoter.promotion_from_ledger(forged_ledger, None)

summary = promotion.get("summary", {})
if promotion.get("runtime_status") != PROMOTION_STATUS:
    errors.append("promotion gate runtime_status is stale")
if promotion.get("ledger_runtime_status") != "evidence_replay_ledger_generated":
    errors.append("promotion gate must consume a replay ledger")
if promotion.get("trusted_external_attestation_verifier_status") != promoter.TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_STATUS:
    errors.append("promotion gate must expose fail-closed trusted-attestation verifier status")
if promoter.TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_ERROR not in promotion.get("global_promotion_errors", []):
    errors.append("promotion gate must fail closed until a trusted external attestation verifier exists")
if promotion.get("replay_mismatch_count") != 0:
    errors.append("same-bundle promotion replay must have zero mismatches")
if summary.get("case_count") != case_count:
    errors.append("promotion case count must equal answer count")
if summary.get("adapter_record_count") != adapter_check_count:
    errors.append("promotion adapter record count must equal adapter checks")
if summary.get("promoted_case_count") != 0 or summary.get("held_case_count") != case_count:
    errors.append("archive-generated strict-schema evidence must promote zero cases and hold all cases")
if summary.get("externally_observed_adapter_record_count") != 0:
    errors.append("built-in promotion audit must report zero externally observed records")
if summary.get("promotion_eligible_adapter_record_count") != 0:
    errors.append("built-in promotion audit must report zero promotion-eligible records")
if summary.get("strict_schema_test_fixture_adapter_record_count") != adapter_check_count:
    errors.append("built-in promotion audit must label every adapter record as strict-schema test")
if set(promotion.get("global_promotion_errors", [])) != {promoter.TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_ERROR}:
    errors.append("same-bundle strict-test ledger should have only the deliberate fail-closed verifier error globally")
if not promotion.get("promotion_packet_hash"):
    errors.append("promotion packet missing hash")
if "Archive-generated fixtures" not in str(promotion.get("non_doctrine_warning", "")):
    errors.append("promotion warning must explicitly exclude archive-generated fixtures")

case_promotions = promotion.get("case_promotions", [])
if len(case_promotions) != case_count:
    errors.append("promotion gate must emit one case decision per answer")
for case in case_promotions:
    cid = case.get("case_id")
    if case.get("can_promote_to_final_disposition") is not False:
        errors.append(f"strict-schema case {cid} was incorrectly promoted")
    if case.get("record_error_count") != case.get("record_count"):
        errors.append(f"strict-schema case {cid} must have a truth-boundary error on every adapter record")
    flattened = [err for rec in case.get("record_errors", []) for err in rec.get("record_errors", [])]
    for required in [
        "strict_schema_test_fixture_not_promotion_eligible",
        "evidence_origin_not_external_observed",
        "external_source_attestation_not_verified",
        "evidence_record_not_promotion_eligible",
        "external_attestation_verifier_not_verified",
    ]:
        if required not in flattened:
            errors.append(f"strict-schema case {cid} missing promotion reason {required}")
    if not case.get("case_promotion_hash"):
        errors.append(f"case promotion {cid} missing hash")

for label, packet in [("empty", empty_promotion), ("interface", interface_promotion), ("tamper", tamper_promotion), ("forged-ledger", forged_promotion)]:
    if packet.get("summary", {}).get("promoted_case_count") != 0:
        errors.append(f"{label} promotion must promote zero cases")
    if packet.get("summary", {}).get("held_case_count") != case_count:
        errors.append(f"{label} promotion must hold all cases")
if tamper_promotion.get("replay_mismatch_count", 0) <= 0:
    errors.append("tampered evidence promotion must expose replay mismatches")
if "ledger_hash_does_not_match_records" not in forged_promotion.get("global_promotion_errors", []):
    errors.append("forged ledger origin fields must fail ledger-hash recomputation")
for case in forged_promotion.get("case_promotions", []):
    all_errors = [err for rec in case.get("record_errors", []) for err in rec.get("record_errors", [])]
    if "evidence_truth_boundary_hash_mismatch" not in all_errors:
        errors.append(f"forged ledger case {case.get('case_id')} must fail truth-boundary hash validation")

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
expected = {
    "decision_promotion_gate_required": True,
    "decision_promotion_runtime_status": PROMOTION_STATUS,
    "decision_promotion_case_count": case_count,
    "decision_promotion_adapter_record_count": adapter_check_count,
    "decision_promotion_schema_execution_can_finalize_count": ledger.get("summary", {}).get("case_can_finalize_count"),
    "decision_promotion_strict_test_promoted_case_count": summary.get("promoted_case_count"),
    "decision_promotion_strict_test_held_case_count": summary.get("held_case_count"),
    "decision_promotion_external_observed_record_count": summary.get("externally_observed_adapter_record_count"),
    "decision_promotion_promotion_eligible_record_count": summary.get("promotion_eligible_adapter_record_count"),
    "decision_promotion_strict_schema_test_record_count": summary.get("strict_schema_test_fixture_adapter_record_count"),
    "decision_promotion_trusted_external_attestation_verified_record_count": summary.get("trusted_external_attestation_verified_adapter_record_count"),
    "decision_promotion_strict_model_input_source_required_record_count": summary.get("strict_model_input_source_required_record_count"),
    "decision_promotion_strict_model_input_source_proof_record_count": summary.get("strict_model_input_source_proof_record_count"),
    "decision_promotion_strict_authority_evidence_required_record_count": summary.get("strict_authority_evidence_required_record_count"),
    "decision_promotion_strict_authority_evidence_proof_record_count": summary.get("strict_authority_evidence_proof_record_count"),
    "decision_promotion_adapter_binding_hash_record_count": summary.get("adapter_binding_hash_record_count"),
    "decision_promotion_external_adapter_binding_hash_record_count": summary.get("external_adapter_binding_hash_record_count"),
    "decision_promotion_adapter_binding_mismatch_record_count": summary.get("adapter_binding_mismatch_record_count"),
    "decision_promotion_empty_promoted_case_count": empty_promotion.get("summary", {}).get("promoted_case_count"),
    "decision_promotion_interface_promoted_case_count": interface_promotion.get("summary", {}).get("promoted_case_count"),
    "decision_promotion_tamper_mismatch_count": tamper_comparison.get("mismatch_count"),
    "decision_promotion_tamper_promoted_case_count": tamper_promotion.get("summary", {}).get("promoted_case_count"),
    "decision_promotion_forged_ledger_promoted_case_count": forged_promotion.get("summary", {}).get("promoted_case_count"),
    "decision_promotion_trusted_external_attestation_verifier_status": promotion.get("trusted_external_attestation_verifier_status"),
}
for key, value in expected.items():
    if cube.get("audit_summary", {}).get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("decision_promotion_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json decision_promotion_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    lines = [
        f"Decision promotion runtime status: {PROMOTION_STATUS}",
        f"Answer packets checked: {case_count}",
        f"Adapter ledger records: {adapter_check_count}/{adapter_check_count}",
        f"Schema-execution finalizable cases before promotion: {ledger.get('summary', {}).get('case_can_finalize_count')}/{case_count}",
        f"Strict-schema promoted cases: {summary.get('promoted_case_count')}/{case_count}",
        f"Strict-schema held cases: {summary.get('held_case_count')}/{case_count}",
        f"Externally observed adapter records: {summary.get('externally_observed_adapter_record_count')}/{adapter_check_count}",
        f"Promotion-eligible adapter records: {summary.get('promotion_eligible_adapter_record_count')}/{adapter_check_count}",
        f"Cryptographically verified external attestations: {summary.get('trusted_external_attestation_verified_adapter_record_count')}/{adapter_check_count}",
        f"Strict model-input source proof records: {summary.get('strict_model_input_source_proof_record_count')}/{summary.get('strict_model_input_source_required_record_count')}",
        f"Strict authority evidence proof records: {summary.get('strict_authority_evidence_proof_record_count')}/{summary.get('strict_authority_evidence_required_record_count')}",
        f"Adapter binding hashes recorded: {summary.get('adapter_binding_hash_record_count')}/{adapter_check_count}",
        f"External adapter binding hashes: {summary.get('external_adapter_binding_hash_record_count')}/{adapter_check_count}",
        f"Adapter binding mismatches: {summary.get('adapter_binding_mismatch_record_count')}",
        f"Trusted external attestation verifier status: {promotion.get('trusted_external_attestation_verifier_status')}",
        f"Tamper replay mismatches: {tamper_comparison.get('mismatch_count')}",
        f"Forged-ledger promoted cases: {forged_promotion.get('summary', {}).get('promoted_case_count')}/{case_count}",
    ]
    for line in lines:
        if line not in report:
            errors.append(f"decision promotion audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("decision promotion gate audit ok")
