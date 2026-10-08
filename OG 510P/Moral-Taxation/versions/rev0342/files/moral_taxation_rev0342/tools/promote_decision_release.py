#!/usr/bin/env python3
"""Promote replay-checked adapter executions into finalization decisions.

This is the post-replay gate. It does not fetch law, run models, or store raw
external evidence. It consumes a replay ledger and decides which case-level
answer packets are promotion-ready for final disposition and which must remain
held because strict evidence is missing, drifted, blocked, or only test-grade.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Mapping, Sequence

RUNTIME_STATUS = "decision_promotion_gate_evaluated"
RULE_VERSION = 7
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
LEDGER_STATUS = "evidence_replay_ledger_generated"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
STATUS_PROMOTED = "promoted_verified_external_evidence_ready_for_final_disposition"
STATUS_SANDBOX = "sandbox_positive_path_verified_not_final_disposition"
STATUS_HELD = "held_not_finalizable_or_not_replay_clean"
PROMOTION_MODE_PRODUCTION = "production_candidate"
PROMOTION_MODE_SANDBOX = "sandbox_positive_path_test"
SCOPE_NON_DEFAULT_ROUTE_LIMIT_ERROR = "non_default_route_limit_not_finalizable_outside_sandbox"
SCOPE_UNKNOWN_MODE_ERROR = "unknown_promotion_mode"
STRICT_MODEL_GATE_ERROR = "strict_model_input_source_gate_not_enabled"
STRICT_MODEL_PROOF_ERROR = "strict_model_input_source_proof_not_implementation_grade"
STRICT_AUTHORITY_GATE_ERROR = "strict_authority_evidence_gate_not_enabled"
STRICT_AUTHORITY_PROOF_ERROR = "strict_authority_evidence_proof_not_implementation_grade"
MODEL_ADAPTER_TYPES = {"quantitative_model_adapter", "floor_delivery_adapter", "no_go_threshold_adapter"}
AUTHORITY_ADAPTER_TYPES = {"current_law_refresh_adapter", "jurisdiction_scope_adapter"}
NON_DOCTRINE_WARNING = (
    "Promotion remains fail-closed until a trusted external attestation verifier is "
    "configured; after that it may authorize only replay-clean, externally observed, "
    "independently attested implementation evidence. Archive-generated fixtures and "
    "schema tests are never promotion eligible. Sandbox positive-path tests may prove "
    "mechanics but never final disposition. It is not current law, not a jurisdiction "
    "conclusion, not a model result, and not route doctrine."
)
FORBIDDEN_RAW_KEYS = {"raw_evidence", "evidence_snapshot", "evidence_record", "authority_text", "model_output_snapshot"}
REQUIRED_RECORD_HASH_FIELDS = ["adapter_packet_hash", "adapter_binding_hash", "evidence_hash", "producer_contract_hash", "evidence_truth_boundary_hash", "decision_trace_hash", "result_hash"]
TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_STATUS = "not_configured_fail_closed"
TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_CONFIGURED_STATUS = "configured_trust_store_present"
TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_ERROR = "trusted_external_attestation_verifier_not_configured"


def compact_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def dedupe(values: Iterable[Any]) -> List[Any]:
    seen = set()
    out: List[Any] = []
    for value in values:
        if value in (None, "", [], {}):
            continue
        key = json.dumps(value, sort_keys=True, separators=(",", ":")) if isinstance(value, (dict, list)) else str(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def load_answers(root: pathlib.Path, case_id: str | None, all_cases: bool, route_limit: int, facts_only_limit: int) -> List[Dict[str, Any]]:
    cache_path = os.environ.get("MT_ANSWER_PACKET_CACHE")
    if cache_path and pathlib.Path(cache_path).exists() and all_cases and not case_id:
        payload = json.loads(pathlib.Path(cache_path).read_text(encoding="utf-8"))
    else:
        args = [
            sys.executable,
            str(root / "tools/answer_case.py"),
            str(root),
            "--route-limit",
            str(route_limit),
            "--facts-only-candidate-limit",
            str(facts_only_limit),
            "--json",
        ]
        if case_id:
            args.extend(["--case-id", case_id])
        elif all_cases:
            args.append("--all")
        else:
            raise SystemExit("provide --case-id or --all")
        payload = json.loads(subprocess.check_output(args, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}))
    if payload.get("runtime_status") != ANSWER_STATUS:
        raise SystemExit("answer_case.py returned a stale runtime status")
    return payload.get("answers", [])


def records_by_case(ledger: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in ledger.get("ledger_records", []):
        if not isinstance(record, Mapping):
            continue
        case_id = str(record.get("case_id") or "")
        grouped.setdefault(case_id, []).append(dict(record))
    return grouped


def ledger_global_errors(ledger: Mapping[str, Any], replay_comparison: Mapping[str, Any] | None = None) -> List[str]:
    errors: List[str] = []
    if ledger.get("trusted_external_attestation_verifier_status") != TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_CONFIGURED_STATUS:
        errors.append(TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_ERROR)
    if ledger.get("runtime_status") != LEDGER_STATUS:
        errors.append("ledger_runtime_status_not_current")
    if not ledger.get("ledger_hash"):
        errors.append("ledger_hash_missing")
    elif ledger.get("ledger_hash") != compact_hash(ledger.get("ledger_records", [])):
        errors.append("ledger_hash_does_not_match_records")
    if "not current law" not in str(ledger.get("ledger_non_doctrine_warning", "")):
        errors.append("ledger_non_doctrine_warning_missing")
    summary = ledger.get("summary", {}) if isinstance(ledger.get("summary"), Mapping) else {}
    if summary.get("record_count") != ledger.get("adapter_execution_count"):
        errors.append("ledger_record_count_drift")
    scope = ledger.get("promotion_scope", {}) if isinstance(ledger.get("promotion_scope"), Mapping) else {}
    promotion_mode = str(ledger.get("promotion_mode") or scope.get("promotion_mode") or PROMOTION_MODE_PRODUCTION)
    if promotion_mode not in {PROMOTION_MODE_PRODUCTION, PROMOTION_MODE_SANDBOX}:
        errors.append(f"{SCOPE_UNKNOWN_MODE_ERROR}:{promotion_mode}")
    if promotion_mode != PROMOTION_MODE_SANDBOX and int(scope.get("non_default_route_limit_count") or 0) > 0:
        errors.append(SCOPE_NON_DEFAULT_ROUTE_LIMIT_ERROR)
    if replay_comparison is not None:
        if replay_comparison.get("runtime_status") != "evidence_replay_comparison_completed":
            errors.append("replay_comparison_runtime_status_not_current")
        if replay_comparison.get("mismatch_count") != 0:
            errors.append("same_bundle_replay_mismatch")
    return dedupe(errors)


def record_errors(record: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in REQUIRED_RECORD_HASH_FIELDS:
        if not record.get(field):
            errors.append(f"missing_{field}")
    truth_boundary = {
        "adapter_binding_hash": record.get("adapter_binding_hash"),
        "evidence_adapter_binding_hash": record.get("evidence_adapter_binding_hash"),
        "strict_model_input_source_certification_required": record.get("strict_model_input_source_certification_required") is True,
        "strict_authority_evidence_required": record.get("strict_authority_evidence_required") is True,
        "input_certification_level": record.get("input_certification_level"),
        "input_source_record_hash": record.get("input_source_record_hash"),
        "input_source_manifest_hash": record.get("input_source_manifest_hash"),
        "authority_certification_level": record.get("authority_certification_level"),
        "authority_evidence_record_hash": record.get("authority_evidence_record_hash"),
        "authority_evidence_bundle_hash": record.get("authority_evidence_bundle_hash"),
        "authority_source_record_hash": record.get("authority_source_record_hash"),
        "authority_source_manifest_hash": record.get("authority_source_manifest_hash"),
        "strict_schema_test_fixture": record.get("strict_schema_test_fixture") is True,
        "evidence_origin": record.get("evidence_origin"),
        "external_source_attestation_status": record.get("external_source_attestation_status"),
        "promotion_eligible": record.get("promotion_eligible") is True,
        "external_attestation_verifier_status": record.get("external_attestation_verifier_status"),
        "trusted_external_attestation": record.get("trusted_external_attestation") is True,
    }
    if record.get("evidence_truth_boundary_hash") != compact_hash(truth_boundary):
        errors.append("evidence_truth_boundary_hash_mismatch")
    if record.get("evidence_present") is not True:
        errors.append("evidence_not_present")
    if record.get("strict_schema_test_fixture") is True:
        errors.append("strict_schema_test_fixture_not_promotion_eligible")
    if record.get("evidence_origin") != "external_observed":
        errors.append("evidence_origin_not_external_observed")
    if record.get("external_source_attestation_status") != "verified_external_attestation":
        errors.append("external_source_attestation_not_verified")
    if record.get("external_attestation_verifier_status") != "verified_external_attestation" or record.get("trusted_external_attestation") is not True:
        errors.append("external_attestation_verifier_not_verified")
    if record.get("promotion_eligible") is not True:
        errors.append("evidence_record_not_promotion_eligible")
    adapter_type = str(record.get("adapter_type") or "")
    if adapter_type in MODEL_ADAPTER_TYPES:
        if record.get("strict_model_input_source_certification_required") is not True:
            errors.append(STRICT_MODEL_GATE_ERROR)
        if record.get("input_certification_level") != "implementation_grade" or not record.get("input_source_record_hash") or not record.get("input_source_manifest_hash"):
            errors.append(STRICT_MODEL_PROOF_ERROR)
    if adapter_type in AUTHORITY_ADAPTER_TYPES:
        if record.get("strict_authority_evidence_required") is not True:
            errors.append(STRICT_AUTHORITY_GATE_ERROR)
        if (record.get("authority_certification_level") != "implementation_grade" or not record.get("authority_evidence_record_hash")
                or not record.get("authority_source_record_hash") or not record.get("authority_source_manifest_hash")):
            errors.append(STRICT_AUTHORITY_PROOF_ERROR)
    if record.get("evidence_origin") == "external_observed" or record.get("promotion_eligible") is True:
        if not record.get("evidence_adapter_binding_hash"):
            errors.append("evidence_adapter_binding_hash_missing")
        elif record.get("evidence_adapter_binding_hash") != record.get("adapter_binding_hash"):
            errors.append("evidence_adapter_binding_hash_mismatch")
    if record.get("finalization_status") != "satisfied":
        errors.append("adapter_not_satisfied")
    if str(record.get("execution_status") or "").startswith("blocked") or str(record.get("execution_status") or "") == "executed_evidence_blocks_finalization":
        errors.append(f"blocking_execution_status:{record.get('execution_status')}")
    if "not current law" not in str(record.get("non_doctrine_warning", "")):
        errors.append("record_non_doctrine_warning_missing")
    forbidden = sorted(FORBIDDEN_RAW_KEYS.intersection(record))
    if forbidden:
        errors.append("raw_evidence_snapshot_forbidden:" + ",".join(forbidden))
    return dedupe(errors)


def classify_case(case_id: str, records: Sequence[Mapping[str, Any]], global_errors: Sequence[str], promotion_mode: str = PROMOTION_MODE_PRODUCTION) -> Dict[str, Any]:
    per_record_errors: List[Dict[str, Any]] = []
    blockers: List[Dict[str, Any]] = []
    for record in records:
        errs = record_errors(record)
        if errs:
            per_record_errors.append({
                "record_key": record.get("record_key"),
                "adapter_id": record.get("adapter_id"),
                "adapter_type": record.get("adapter_type"),
                "route_id": record.get("route_id"),
                "execution_status": record.get("execution_status"),
                "finalization_status": record.get("finalization_status"),
                "cannot_finalize_marker": record.get("cannot_finalize_marker"),
                "record_errors": errs,
            })
        if record.get("finalization_status") != "satisfied" or record.get("cannot_finalize_marker"):
            blockers.append({
                "adapter_id": record.get("adapter_id"),
                "adapter_type": record.get("adapter_type"),
                "route_id": record.get("route_id"),
                "execution_status": record.get("execution_status"),
                "finalization_status": record.get("finalization_status"),
                "cannot_finalize_marker": record.get("cannot_finalize_marker"),
            })
    reasons = list(global_errors)
    if not records:
        reasons.append("case_has_no_ledger_records")
    if per_record_errors:
        reasons.append("case_record_promotion_errors_present")
    if reasons:
        status = STATUS_HELD
    elif promotion_mode == PROMOTION_MODE_SANDBOX:
        status = STATUS_SANDBOX
    else:
        status = STATUS_PROMOTED
    record_hashes = [record.get("result_hash") for record in records if record.get("result_hash")]
    return {
        "case_id": case_id,
        "promotion_status": status,
        "promotion_mode": promotion_mode,
        "can_promote_to_final_disposition": status == STATUS_PROMOTED,
        "can_promote_to_sandbox_positive_path": status == STATUS_SANDBOX,
        "record_count": len(records),
        "satisfied_record_count": sum(1 for record in records if record.get("finalization_status") == "satisfied"),
        "blocked_record_count": sum(1 for record in records if record.get("finalization_status") != "satisfied"),
        "promotion_reasons": dedupe(reasons or ["all_adapter_records_satisfied_and_replay_clean"]),
        "blocked_adapters": blockers,
        "cannot_finalize_markers": dedupe([record.get("cannot_finalize_marker") for record in records if record.get("cannot_finalize_marker")]),
        "record_error_count": len(per_record_errors),
        "record_errors": per_record_errors[:100],
        "case_promotion_hash": compact_hash({
            "case_id": case_id,
            "status": status,
            "record_hashes": record_hashes,
            "global_errors": list(global_errors),
            "blocked_adapters": blockers,
            "promotion_mode": promotion_mode,
        }),
        "non_doctrine_warning": NON_DOCTRINE_WARNING,
    }


def promotion_from_ledger(ledger: Mapping[str, Any], replay_comparison: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    global_errors = ledger_global_errors(ledger, replay_comparison)
    grouped = records_by_case(ledger)
    scope = ledger.get("promotion_scope", {}) if isinstance(ledger.get("promotion_scope"), Mapping) else {}
    promotion_mode = str(ledger.get("promotion_mode") or scope.get("promotion_mode") or PROMOTION_MODE_PRODUCTION)
    cases = [classify_case(case_id, grouped[case_id], global_errors, promotion_mode) for case_id in sorted(grouped)]
    status_counts: Dict[str, int] = {}
    for case in cases:
        status_counts[str(case.get("promotion_status"))] = status_counts.get(str(case.get("promotion_status")), 0) + 1
    promoted = sum(1 for case in cases if case.get("can_promote_to_final_disposition"))
    sandbox = sum(1 for case in cases if case.get("can_promote_to_sandbox_positive_path"))
    held = len(cases) - promoted - sandbox
    blocked_records = sum(int(case.get("blocked_record_count", 0)) for case in cases)
    satisfied_records = sum(int(case.get("satisfied_record_count", 0)) for case in cases)
    return {
        "kind": "decision_promotion_gate_packet",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "trusted_external_attestation_verifier_status": ledger.get("trusted_external_attestation_verifier_status", TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_STATUS),
        "promotion_mode": promotion_mode,
        "promotion_scope": ledger.get("promotion_scope", {}),
        "ledger_runtime_status": ledger.get("runtime_status"),
        "ledger_hash": ledger.get("ledger_hash"),
        "evidence_bundle_hash": ledger.get("evidence_bundle_hash"),
        "producer_contract_manifest_hash": ledger.get("producer_contract_manifest_hash"),
        "replay_comparison_status": (replay_comparison or {}).get("runtime_status"),
        "replay_mismatch_count": (replay_comparison or {}).get("mismatch_count") if replay_comparison is not None else None,
        "global_promotion_errors": global_errors,
        "summary": {
            "case_count": len(cases),
            "promoted_case_count": promoted,
            "held_case_count": held,
            "sandbox_positive_path_case_count": sandbox,
            "promotion_mode": promotion_mode,
            "adapter_record_count": sum(int(case.get("record_count", 0)) for case in cases),
            "satisfied_adapter_record_count": satisfied_records,
            "blocked_adapter_record_count": blocked_records,
            "externally_observed_adapter_record_count": sum(1 for records in grouped.values() for record in records if record.get("evidence_origin") == "external_observed"),
            "promotion_eligible_adapter_record_count": sum(1 for records in grouped.values() for record in records if record.get("promotion_eligible") is True),
            "strict_schema_test_fixture_adapter_record_count": sum(1 for records in grouped.values() for record in records if record.get("strict_schema_test_fixture") is True),
            "trusted_external_attestation_verified_adapter_record_count": sum(1 for records in grouped.values() for record in records if record.get("trusted_external_attestation") is True),
            "adapter_binding_hash_record_count": sum(1 for records in grouped.values() for record in records if record.get("adapter_binding_hash")),
            "external_adapter_binding_hash_record_count": sum(1 for records in grouped.values() for record in records if record.get("evidence_origin") == "external_observed" and record.get("evidence_adapter_binding_hash")),
            "adapter_binding_mismatch_record_count": sum(1 for records in grouped.values() for record in records if record.get("evidence_adapter_binding_hash") not in (None, "", [], {}) and record.get("evidence_adapter_binding_hash") != record.get("adapter_binding_hash")),
            "strict_model_input_source_required_record_count": sum(1 for records in grouped.values() for record in records if record.get("strict_model_input_source_certification_required") is True),
            "strict_model_input_source_proof_record_count": sum(1 for records in grouped.values() for record in records if record.get("strict_model_input_source_certification_required") is True and record.get("input_certification_level") == "implementation_grade" and record.get("input_source_record_hash") and record.get("input_source_manifest_hash")),
            "strict_authority_evidence_required_record_count": sum(1 for records in grouped.values() for record in records if record.get("strict_authority_evidence_required") is True),
            "strict_authority_evidence_proof_record_count": sum(1 for records in grouped.values() for record in records if record.get("strict_authority_evidence_required") is True and record.get("authority_certification_level") == "implementation_grade" and record.get("authority_evidence_record_hash") and record.get("authority_source_record_hash") and record.get("authority_source_manifest_hash")),
            "promotion_status_counts": dict(sorted(status_counts.items())),
            "trusted_external_attestation_verifier_status": ledger.get("trusted_external_attestation_verifier_status", TRUSTED_EXTERNAL_ATTESTATION_VERIFIER_STATUS),
            "all_promoted": bool(cases) and promoted == len(cases),
            "all_resolved_without_hold": bool(cases) and held == 0,
        },
        "case_promotions": cases,
        "promotion_packet_hash": compact_hash(cases),
        "non_doctrine_warning": NON_DOCTRINE_WARNING,
    }


def promotion_for_answers(
    root: pathlib.Path,
    answers: Sequence[Mapping[str, Any]],
    evidence_bundle: Mapping[str, Any] | None = None,
    replay_check: bool = True,
) -> Dict[str, Any]:
    ledger_builder = load_module("build_evidence_replay_ledger", root / "tools/build_evidence_replay_ledger.py")
    ledger = ledger_builder.ledger_for_answers(root, answers, evidence_bundle or {})
    comparison = None
    if replay_check:
        replayed = ledger_builder.ledger_for_answers(root, answers, evidence_bundle or {})
        comparison = ledger_builder.replay_compare(ledger, replayed)
    return promotion_from_ledger(ledger, comparison)


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote replay-clean adapter evidence executions to finalization decisions.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Evaluate one case id")
    parser.add_argument("--all", action="store_true", help="Evaluate all golden cases")
    parser.add_argument("--evidence", help="Evidence bundle JSON")
    parser.add_argument("--ledger", help="Prebuilt replay ledger JSON")
    parser.add_argument("--no-replay-check", action="store_true", help="Do not run same-bundle replay comparison")
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    if args.ledger:
        ledger = load_json(pathlib.Path(args.ledger).resolve())
        packet = promotion_from_ledger(ledger, None)
    else:
        answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
        bundle = load_json(pathlib.Path(args.evidence).resolve()) if args.evidence else {}
        packet = promotion_for_answers(root, answers, bundle, not args.no_replay_check)
    if args.json:
        print(json.dumps(packet, separators=(",", ":")))
    else:
        s = packet.get("summary", {})
        print(f"{packet.get('runtime_status')}: {s.get('promoted_case_count')} promoted, {s.get('held_case_count')} held")


if __name__ == "__main__":
    main()
