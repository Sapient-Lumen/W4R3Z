#!/usr/bin/env python3
"""Audit the signed positive-path evidence mechanics without certifying doctrine.

This audit guards the riskiest unfinished edge after rev0339: the system should
have a real executable positive path for signed external-like evidence, but that
path must not let a sandbox fixture become final public advice.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import sys
from typing import Any, List, Mapping

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


builder = load_module("build_signed_external_evidence_smoke_bundle", root / "tools/build_signed_external_evidence_smoke_bundle.py")
answer_case = load_module("answer_case", root / "tools/answer_case.py")
ledger_builder = load_module("build_evidence_replay_ledger", root / "tools/build_evidence_replay_ledger.py")
promoter = load_module("promote_decision_release", root / "tools/promote_decision_release.py")
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")

case_id = "GC-001"
route_limit = 5
facts_only_limit = 8
as_of_date = "2026-06-18"
bundle = builder.build_bundle(root, case_id, route_limit, facts_only_limit, as_of_date)

golden = json.loads((root / "docs/00-meta/golden-cases.json").read_text(encoding="utf-8"))
case = next(c for c in golden.get("cases", []) if c.get("case_id") == case_id)
runtime = answer_case.AnswerRuntime(root, route_limit, facts_only_limit)
answer = runtime.answer_case(case)
answers = [answer]
execution = executor.execute_answer(answer, executor.attach_default_producer_contracts(root, bundle))
ledger = ledger_builder.ledger_for_answers(root, answers, bundle)
replayed = ledger_builder.ledger_for_answers(root, answers, bundle)
comparison = ledger_builder.replay_compare(ledger, replayed)
promotion = promoter.promotion_from_ledger(ledger, comparison)

summary = ledger.get("summary", {})
promo_summary = promotion.get("summary", {})
records = ledger.get("ledger_records", [])
case_promotions = promotion.get("case_promotions", [])

if bundle.get("runtime_status") != "signed_external_evidence_smoke_bundle_generated":
    errors.append("positive smoke bundle runtime status is stale")
if bundle.get("execution_context", {}).get("promotion_mode") != promoter.PROMOTION_MODE_SANDBOX:
    errors.append("positive smoke bundle must use sandbox promotion mode")
expected_records = len(answer.get("disposition", {}).get("adapter_checks", []))
model_records = sum(1 for rec in records if rec.get("adapter_type") in promoter.MODEL_ADAPTER_TYPES)
authority_records = sum(1 for rec in records if rec.get("adapter_type") in promoter.AUTHORITY_ADAPTER_TYPES)
if bundle.get("adapter_record_count") != expected_records:
    errors.append("GC-001 default-route smoke bundle should cover every selected adapter record")
if execution.get("execution_summary", {}).get("satisfied_count") != expected_records or execution.get("execution_summary", {}).get("blocked_count") != 0:
    errors.append("signed strict smoke bundle did not satisfy the default adapter execution path")
if summary.get("record_count") != expected_records:
    errors.append("positive smoke ledger should contain every default selected adapter record")
if summary.get("strict_model_input_source_required_record_count") != model_records or summary.get("strict_model_input_source_proof_record_count") != model_records:
    errors.append("positive smoke ledger did not exercise strict implementation-grade model-input source proof for every model adapter")
if summary.get("strict_authority_evidence_required_record_count") != authority_records or summary.get("strict_authority_evidence_proof_record_count") != authority_records:
    errors.append("positive smoke ledger did not exercise strict implementation-grade authority proof for every authority adapter")
for rec in records:
    if rec.get("evidence_origin") != "external_observed":
        errors.append("positive smoke record did not enter the external-observed code path")
    if rec.get("trusted_external_attestation") is not True:
        errors.append("positive smoke record did not verify cryptographically")
    if rec.get("promotion_eligible") is not True:
        errors.append("positive smoke record did not exercise promotion-eligible record logic")
    if rec.get("finalization_status") != "satisfied":
        errors.append("positive smoke record was not execution-satisfied")
    if rec.get("adapter_binding_hash") != rec.get("evidence_adapter_binding_hash"):
        errors.append("positive smoke record lost adapter binding equality")
if comparison.get("mismatch_count") != 0:
    errors.append("positive smoke replay should be stable")
if promo_summary.get("promoted_case_count") != 0:
    errors.append("sandbox smoke path must not count as final promoted cases")
if promo_summary.get("sandbox_positive_path_case_count") != 1:
    errors.append("sandbox smoke path should report one positive-path case")
if promo_summary.get("held_case_count") != 0:
    errors.append("sandbox smoke path should not be held when all mechanics verify")
if case_promotions and case_promotions[0].get("can_promote_to_final_disposition") is not False:
    errors.append("sandbox smoke case must not be finalizable")
if case_promotions and case_promotions[0].get("can_promote_to_sandbox_positive_path") is not True:
    errors.append("sandbox smoke case did not expose positive-path success")
if promotion.get("promotion_mode") != promoter.PROMOTION_MODE_SANDBOX:
    errors.append("promotion packet did not preserve sandbox promotion mode")

# Route-limit gating: prove the old narrow harness cannot become a production
# shortcut around omitted routes. The main positive path now uses the default
# route limit; this separate narrow probe keeps the scope gate under test.
narrow_route_limit = 1
narrow_bundle = builder.build_bundle(root, case_id, narrow_route_limit, facts_only_limit, as_of_date)
narrow_runtime = answer_case.AnswerRuntime(root, narrow_route_limit, facts_only_limit)
narrow_answer = narrow_runtime.answer_case(case)
narrow_ledger = ledger_builder.ledger_for_answers(root, [narrow_answer], narrow_bundle)
narrow_replay = ledger_builder.ledger_for_answers(root, [narrow_answer], narrow_bundle)
narrow_comparison = ledger_builder.replay_compare(narrow_ledger, narrow_replay)
production_like_ledger = copy.deepcopy(narrow_ledger)
production_like_ledger["promotion_mode"] = promoter.PROMOTION_MODE_PRODUCTION
production_like_ledger["promotion_scope"]["promotion_mode"] = promoter.PROMOTION_MODE_PRODUCTION
production_like = promoter.promotion_from_ledger(production_like_ledger, narrow_comparison)
if production_like.get("summary", {}).get("promoted_case_count") != 0:
    errors.append("non-default route-limit ledger promoted outside sandbox")
if promoter.SCOPE_NON_DEFAULT_ROUTE_LIMIT_ERROR not in production_like.get("global_promotion_errors", []):
    errors.append("non-default route-limit production attempt did not fail closed")

# Adapter-binding gating: alter a signed record's binding without resigning;
# execution must reject the mismatch before finalization.
tampered_bundle = copy.deepcopy(bundle)
adapter_pool = tampered_bundle.get("adapter_evidence", {})
keys = list(adapter_pool)
if keys:
    adapter_pool[keys[0]]["adapter_binding_hash"] = "tampered-binding-hash"
    tampered_execution = executor.execute_answer(answer, executor.attach_default_producer_contracts(root, tampered_bundle))
    statuses = [r.get("execution_status") for r in tampered_execution.get("adapter_execution_results", [])]
    validation_errors = [err for result in tampered_execution.get("adapter_execution_results", []) for err in result.get("adapter_binding_validation_errors", [])]
    if executor.STATUS_ATTESTATION_NOT_VERIFIED not in statuses:
        errors.append("tampered adapter binding did not block execution")
    if "adapter_binding_hash_mismatch" not in validation_errors:
        errors.append("tampered adapter binding did not report adapter_binding_hash_mismatch")
else:
    errors.append("positive smoke bundle did not expose a record for binding tamper probe")

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
expected = {
    "positive_external_evidence_path_required": True,
    "positive_external_evidence_runtime_status": bundle.get("runtime_status"),
    "positive_external_evidence_case_id": case_id,
    "positive_external_evidence_route_limit": route_limit,
    "positive_external_evidence_adapter_record_count": summary.get("record_count"),
    "positive_external_evidence_verified_record_count": summary.get("trusted_external_attestation_verified_record_count"),
    "positive_external_evidence_strict_model_proof_record_count": summary.get("strict_model_input_source_proof_record_count"),
    "positive_external_evidence_strict_authority_proof_record_count": summary.get("strict_authority_evidence_proof_record_count"),
    "positive_external_evidence_replay_mismatch_count": comparison.get("mismatch_count"),
    "positive_external_evidence_final_promoted_case_count": promo_summary.get("promoted_case_count"),
    "positive_external_evidence_sandbox_case_count": promo_summary.get("sandbox_positive_path_case_count"),
    "positive_external_evidence_route_limit_gate_blocked": promoter.SCOPE_NON_DEFAULT_ROUTE_LIMIT_ERROR in production_like.get("global_promotion_errors", []),
}
for key, value in expected.items():
    if cube.get("audit_summary", {}).get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("positive_external_evidence_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json positive_external_evidence_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    lines = [
        "Positive external evidence smoke path: enabled",
        f"Smoke bundle runtime status: {bundle.get('runtime_status')}",
        f"Smoke case: {case_id} with default route limit {route_limit}",
        f"Verified smoke adapter records: {summary.get('trusted_external_attestation_verified_record_count')}/{summary.get('record_count')}",
        f"Strict model-input source proofs: {summary.get('strict_model_input_source_proof_record_count')}/{summary.get('strict_model_input_source_required_record_count')}",
        f"Strict authority evidence proofs: {summary.get('strict_authority_evidence_proof_record_count')}/{summary.get('strict_authority_evidence_required_record_count')}",
        f"Replay mismatches: {comparison.get('mismatch_count')}",
        f"Final promoted cases: {promo_summary.get('promoted_case_count')}",
        f"Sandbox positive-path cases: {promo_summary.get('sandbox_positive_path_case_count')}",
        "Non-default route-limit production gate: blocked",
    ]
    for line in lines:
        if line not in report:
            errors.append(f"positive external evidence report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("positive external evidence path audit ok")
