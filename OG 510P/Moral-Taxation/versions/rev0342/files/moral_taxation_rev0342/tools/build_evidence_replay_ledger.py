#!/usr/bin/env python3
"""Build a replay ledger for adapter-execution evidence decisions.

This is the post-evidence boundary. It does not fetch law, run models, or store
live legal/model conclusions as doctrine. It records hashes and decision traces
for adapter packets, producer contracts, evidence records, and execution results
so a later run can replay the same external evidence bundle and detect drift,
staleness, tampering, or fixture substitution.
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
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

RUNTIME_STATUS = "evidence_replay_ledger_generated"
RULE_VERSION = 4
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
TRACE_FIELDS = [
    "execution_status",
    "finalization_status",
    "missing_fields",
    "missing_outputs",
    "producer_id",
    "producer_contract_version",
    "evidence_kind",
    "adapter_binding_hash",
    "evidence_adapter_binding_hash",
    "evidence_hash",
    "evidence_locator",
    "evidence_checked_at",
    "evidence_result_status",
    "freshness",
    "cannot_finalize_marker",
    "block_reason",
    "producer_validation_errors",
    "model_input_validation_errors",
    "model_input_source_validation_errors",
    "authority_evidence_validation_errors",
    "external_attestation_verifier_status",
    "external_attestation_validation_errors",
    "adapter_binding_validation_errors",
    "external_attestation_verification_hash",
]


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


def _producer_contract_manifest(bundle: Mapping[str, Any]) -> Any:
    return bundle.get("producer_contracts") or bundle.get("evidence_producer_contracts") or []


def _execution_context(bundle: Mapping[str, Any]) -> Any:
    return bundle.get("execution_context", {}) if isinstance(bundle, Mapping) else {}


def _trace(result: Mapping[str, Any]) -> Dict[str, Any]:
    return {field: result.get(field) for field in TRACE_FIELDS if field in result}


def _producer_contract_hash(executor: Any, evidence: Mapping[str, Any] | None, bundle: Mapping[str, Any]) -> str | None:
    if not evidence:
        return None
    try:
        contract = executor.producer_contract_for_evidence(evidence, bundle)
    except Exception:
        contract = {}
    return compact_hash(contract) if contract else None


def _adapter_packets(answer: Mapping[str, Any]) -> List[Dict[str, Any]]:
    packets: List[Dict[str, Any]] = []
    case_id = str(answer.get("case_id") or "")
    for packet in answer.get("disposition", {}).get("adapter_checks", []):
        item = dict(packet)
        item.setdefault("case_id", case_id)
        packets.append(item)
    return packets


def _selection_summary(answer: Mapping[str, Any]) -> Dict[str, Any]:
    routing = answer.get("routing", {}) if isinstance(answer.get("routing"), Mapping) else {}
    selected = [str(x) for x in routing.get("selected_route_ids", [])]
    facts_only = [str(x) for x in routing.get("facts_only_candidate_route_ids", [])]
    omitted_facts_only = [rid for rid in facts_only if rid not in set(selected)]
    return {
        "case_id": answer.get("case_id"),
        "selected_route_limit": answer.get("selected_route_limit"),
        "primary_route_id": routing.get("primary_route_id"),
        "selected_route_ids": selected,
        "selected_route_count": len(selected),
        "facts_only_candidate_route_ids": facts_only,
        "facts_only_candidate_route_count": len(facts_only),
        "omitted_facts_only_candidate_route_ids": omitted_facts_only,
        "omitted_facts_only_candidate_route_count": len(omitted_facts_only),
    }


def _record_key(case_id: str, adapter_id: str) -> str:
    return f"{case_id}:{adapter_id}"


def ledger_for_answers(root: pathlib.Path, answers: Sequence[Mapping[str, Any]], evidence_bundle: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")
    raw_bundle: Dict[str, Any] = dict(evidence_bundle or {})
    bundle = executor.attach_default_producer_contracts(root, raw_bundle)
    records: List[Dict[str, Any]] = []
    answer_summaries: List[Dict[str, Any]] = []
    for answer in answers:
        execution_packet = executor.execute_answer(answer, bundle)
        results_by_adapter = {
            str(result.get("adapter_id") or ""): result
            for result in execution_packet.get("adapter_execution_results", [])
        }
        for packet in _adapter_packets(answer):
            adapter_id = str(packet.get("adapter_id") or "")
            result = results_by_adapter.get(adapter_id, {})
            evidence = executor.evidence_for_adapter(packet, bundle)
            lookup_keys = executor.evidence_lookup_keys(packet)
            trace = _trace(result)
            attestation_verification = (
                executor.external_attestation_verification_for_evidence(evidence, bundle) if evidence else {}
            )
            adapter_scope_hash = executor.adapter_binding_hash(packet)
            evidence_scope_hash = (evidence or {}).get("adapter_binding_hash")
            adapter_type = str(packet.get("adapter_type") or "")
            strict_model_gate = adapter_type in getattr(executor, "MODEL_ADAPTER_TYPES", set()) and executor.strict_model_input_source_required(bundle)
            strict_authority_gate = adapter_type in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()) and executor.strict_authority_evidence_required(bundle)
            truth_boundary = {
                "adapter_binding_hash": adapter_scope_hash,
                "evidence_adapter_binding_hash": evidence_scope_hash,
                "strict_model_input_source_certification_required": strict_model_gate,
                "strict_authority_evidence_required": strict_authority_gate,
                "input_certification_level": (evidence or {}).get("input_certification_level"),
                "input_source_record_hash": (evidence or {}).get("input_source_record_hash"),
                "input_source_manifest_hash": (evidence or {}).get("input_source_manifest_hash"),
                "authority_certification_level": (evidence or {}).get("authority_certification_level"),
                "authority_evidence_record_hash": (evidence or {}).get("authority_evidence_record_hash"),
                "authority_evidence_bundle_hash": (evidence or {}).get("authority_evidence_bundle_hash"),
                "authority_source_record_hash": (evidence or {}).get("authority_source_record_hash"),
                "authority_source_manifest_hash": (evidence or {}).get("authority_source_manifest_hash"),
                "strict_schema_test_fixture": (evidence or {}).get("strict_schema_test_fixture") is True,
                "evidence_origin": (evidence or {}).get("evidence_origin"),
                "external_source_attestation_status": (evidence or {}).get("external_source_attestation_status"),
                "promotion_eligible": (evidence or {}).get("promotion_eligible") is True,
                "external_attestation_verifier_status": attestation_verification.get("verifier_status"),
                "trusted_external_attestation": attestation_verification.get("trusted_external_attestation") is True,
            }
            rec = {
                "ledger_record_runtime_status": RUNTIME_STATUS,
                "rule_version": RULE_VERSION,
                "case_id": answer.get("case_id"),
                "adapter_id": adapter_id,
                "record_key": _record_key(str(answer.get("case_id") or ""), adapter_id),
                "adapter_type": packet.get("adapter_type"),
                "route_id": packet.get("route_id"),
                "source_id": packet.get("source_id"),
                "model_class": packet.get("model_class"),
                "adapter_packet_hash": compact_hash(packet),
                "adapter_binding_hash": adapter_scope_hash,
                "evidence_adapter_binding_hash": evidence_scope_hash,
                "evidence_lookup_keys": lookup_keys,
                "evidence_present": evidence is not None,
                "evidence_hash": compact_hash(evidence) if evidence else None,
                "producer_id": (evidence or {}).get("producer_id") if evidence else result.get("producer_id"),
                "producer_contract_version": (evidence or {}).get("producer_contract_version") if evidence else result.get("producer_contract_version"),
                "producer_contract_hash": _producer_contract_hash(executor, evidence, bundle),
                **truth_boundary,
                "external_attestation_hash": attestation_verification.get("attestation_hash"),
                "external_attestation_verification_hash": compact_hash(attestation_verification) if attestation_verification else None,
                "evidence_truth_boundary_hash": compact_hash(truth_boundary),
                "execution_status": result.get("execution_status"),
                "finalization_status": result.get("finalization_status"),
                "cannot_finalize_marker": result.get("cannot_finalize_marker"),
                "evidence_locator": result.get("evidence_locator") or (evidence or {}).get("authority_locator") or (evidence or {}).get("run_locator") or (evidence or {}).get("evidence_locator"),
                "evidence_checked_at": result.get("evidence_checked_at") or (evidence or {}).get("checked_at") or (evidence or {}).get("run_at") or (evidence or {}).get("created_at"),
                "decision_trace": trace,
                "decision_trace_hash": compact_hash(trace),
                "result_hash": compact_hash(result),
                "non_doctrine_warning": "Replay ledger stores hashes and decision traces only; it is not current law, jurisdiction clearance, a model result, or route doctrine.",
            }
            records.append(rec)
        selection = _selection_summary(answer)
        answer_summaries.append({
            "case_id": answer.get("case_id"),
            "title": answer.get("title"),
            "execution_summary": execution_packet.get("execution_summary", {}),
            "cannot_finalize_until": execution_packet.get("cannot_finalize_until", []),
            "route_selection": selection,
        })
    status_counts: Dict[str, int] = {}
    finalization_counts: Dict[str, int] = {}
    adapter_type_counts: Dict[str, int] = {}
    for rec in records:
        status = str(rec.get("execution_status"))
        finality = str(rec.get("finalization_status"))
        typ = str(rec.get("adapter_type"))
        status_counts[status] = status_counts.get(status, 0) + 1
        finalization_counts[finality] = finalization_counts.get(finality, 0) + 1
        adapter_type_counts[typ] = adapter_type_counts.get(typ, 0) + 1
    execution_context = _execution_context(bundle)
    execution_context = execution_context if isinstance(execution_context, Mapping) else {}
    promotion_mode = str(execution_context.get("promotion_mode") or "production_candidate")
    non_default_route_limit_count = sum(
        1 for s in answer_summaries
        if s.get("route_selection", {}).get("selected_route_limit") not in (ROUTE_LIMIT, str(ROUTE_LIMIT))
    )
    return {
        "kind": "adapter_execution_replay_ledger",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "answer_count": len(answers),
        "adapter_execution_count": len(records),
        "execution_context_hash": compact_hash(_execution_context(bundle)),
        "evidence_bundle_hash": compact_hash(bundle),
        "producer_contract_manifest_hash": compact_hash(_producer_contract_manifest(bundle)),
        "trusted_external_attestation_verifier_status": executor.trusted_attestation_verifier_status(bundle),
        "promotion_mode": promotion_mode,
        "promotion_scope": {
            "promotion_mode": promotion_mode,
            "default_route_limit": ROUTE_LIMIT,
            "non_default_route_limit_count": non_default_route_limit_count,
            "answer_route_selection_hash": compact_hash([s.get("route_selection", {}) for s in answer_summaries]),
            "sandbox_smoke_test_only": promotion_mode == "sandbox_positive_path_test",
        },
        "ledger_non_doctrine_warning": "This ledger is a replay/checkability surface, not current law, not jurisdiction clearance, and not a model result. It must not be copied into route memos as doctrine.",
        "summary": {
            "record_count": len(records),
            "evidence_present_count": sum(1 for r in records if r.get("evidence_present")),
            "producer_contract_hash_count": sum(1 for r in records if r.get("producer_contract_hash")),
            "adapter_binding_hash_count": sum(1 for r in records if r.get("adapter_binding_hash")),
            "external_adapter_binding_hash_count": sum(1 for r in records if r.get("evidence_origin") == "external_observed" and r.get("evidence_adapter_binding_hash")),
            "adapter_binding_mismatch_count": sum(1 for r in records if r.get("evidence_adapter_binding_hash") not in (None, "", [], {}) and r.get("evidence_adapter_binding_hash") != r.get("adapter_binding_hash")),
            "strict_schema_test_fixture_record_count": sum(1 for r in records if r.get("strict_schema_test_fixture") is True),
            "external_observed_record_count": sum(1 for r in records if r.get("evidence_origin") == "external_observed"),
            "verified_external_attestation_record_count": sum(1 for r in records if r.get("external_source_attestation_status") == "verified_external_attestation"),
            "trusted_external_attestation_verified_record_count": sum(1 for r in records if r.get("trusted_external_attestation") is True),
            "attestation_not_required_record_count": sum(1 for r in records if r.get("external_attestation_verifier_status") == "not_required_for_fixture_or_non_external_evidence"),
            "promotion_eligible_record_count": sum(1 for r in records if r.get("promotion_eligible") is True),
            "strict_model_input_source_required_record_count": sum(1 for r in records if r.get("strict_model_input_source_certification_required") is True),
            "strict_model_input_source_proof_record_count": sum(1 for r in records if r.get("strict_model_input_source_certification_required") is True and r.get("input_certification_level") == "implementation_grade" and r.get("input_source_record_hash") and r.get("input_source_manifest_hash")),
            "strict_authority_evidence_required_record_count": sum(1 for r in records if r.get("strict_authority_evidence_required") is True),
            "strict_authority_evidence_proof_record_count": sum(1 for r in records if r.get("strict_authority_evidence_required") is True and r.get("authority_certification_level") == "implementation_grade" and r.get("authority_evidence_record_hash") and r.get("authority_source_record_hash") and r.get("authority_source_manifest_hash")),
            "status_counts": dict(sorted(status_counts.items())),
            "finalization_status_counts": dict(sorted(finalization_counts.items())),
            "adapter_type_counts": dict(sorted(adapter_type_counts.items())),
            "case_can_finalize_count": sum(1 for s in answer_summaries if s.get("execution_summary", {}).get("can_finalize")),
            "case_blocked_count": sum(1 for s in answer_summaries if not s.get("execution_summary", {}).get("can_finalize")),
            "promotion_mode": promotion_mode,
            "non_default_route_limit_count": non_default_route_limit_count,
            "sandbox_positive_path_record_count": sum(1 for r in records if r.get("trusted_external_attestation") is True and r.get("promotion_eligible") is True),
        },
        "answer_execution_summaries": answer_summaries,
        "ledger_records": records,
        "ledger_hash": compact_hash(records),
    }


def record_map(ledger: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {str(r.get("record_key") or ""): r for r in ledger.get("ledger_records", []) if isinstance(r, Mapping)}


def replay_compare(expected_ledger: Mapping[str, Any], replay_ledger: Mapping[str, Any]) -> Dict[str, Any]:
    expected = record_map(expected_ledger)
    replay = record_map(replay_ledger)
    mismatches: List[Dict[str, Any]] = []
    for key, exp in expected.items():
        got = replay.get(key)
        if not got:
            mismatches.append({"record_key": key, "mismatch_type": "missing_replay_record"})
            continue
        for field in [
            "adapter_packet_hash", "adapter_binding_hash", "evidence_adapter_binding_hash",
            "evidence_hash", "producer_contract_hash",
            "strict_model_input_source_certification_required", "strict_authority_evidence_required",
            "input_certification_level", "input_source_record_hash", "input_source_manifest_hash",
            "authority_certification_level", "authority_evidence_record_hash", "authority_evidence_bundle_hash",
            "authority_source_record_hash", "authority_source_manifest_hash",
            "strict_schema_test_fixture", "evidence_origin",
            "external_source_attestation_status", "promotion_eligible",
            "external_attestation_verifier_status", "trusted_external_attestation",
            "external_attestation_hash", "external_attestation_verification_hash",
            "evidence_truth_boundary_hash",
            "execution_status", "finalization_status", "decision_trace_hash", "result_hash",
        ]:
            if exp.get(field) != got.get(field):
                mismatches.append({
                    "record_key": key,
                    "mismatch_type": field,
                    "expected": exp.get(field),
                    "actual": got.get(field),
                })
    for key in replay:
        if key not in expected:
            mismatches.append({"record_key": key, "mismatch_type": "unexpected_replay_record"})
    return {
        "runtime_status": "evidence_replay_comparison_completed",
        "expected_record_count": len(expected),
        "replay_record_count": len(replay),
        "mismatch_count": len(mismatches),
        "mismatch_type_counts": {name: sum(1 for m in mismatches if m.get("mismatch_type") == name) for name in sorted({str(m.get("mismatch_type")) for m in mismatches})},
        "mismatches": mismatches[:200],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a replay ledger for adapter-execution evidence decisions.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Build ledger for one case id")
    parser.add_argument("--all", action="store_true", help="Build ledger for all golden cases")
    parser.add_argument("--evidence", help="Evidence bundle JSON to replay")
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    bundle = load_json(pathlib.Path(args.evidence).resolve()) if args.evidence else {}
    ledger = ledger_for_answers(root, answers, bundle)
    if args.json:
        print(json.dumps(ledger, separators=(",", ":")))
    else:
        s = ledger.get("summary", {})
        print(f"{ledger.get('runtime_status')}: {s.get('record_count')} records, {s.get('case_can_finalize_count')} finalizable cases")


if __name__ == "__main__":
    main()
