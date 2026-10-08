#!/usr/bin/env python3
"""Materialize promotion-gated decision outputs.

The promotion gate says whether a replay-clean strict evidence bundle is ready for
case-level finalization. This materializer is the next boundary: it emits a
case-facing decision packet that cleanly separates promoted determinations from
held determinations, carries the hashes needed to audit the evidence/replay path,
and refuses to store raw evidence, current-law text, or model-output snapshots as
doctrine.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Mapping, Sequence

RUNTIME_STATUS = "decision_output_packets_materialized"
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
PROMOTION_STATUS = "decision_promotion_gate_evaluated"
RULE_VERSION = 3
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
STATUS_FINALIZED = "finalized_from_promoted_external_observed_replay_clean_evidence"
STATUS_HELD = "held_pending_external_observed_replay_clean_evidence"
NON_DOCTRINE_WARNING = (
    "This decision-output packet is a release artifact derived from routing, "
    "disposition, adapter evidence, replay, and promotion hashes. It is not "
    "current law, not legal advice, not a stored model result, and not route "
    "doctrine; real use must retain and refresh the external evidence bundle."
)
FORBIDDEN_RAW_KEYS = {
    "raw_evidence",
    "evidence_snapshot",
    "evidence_record",
    "authority_text",
    "model_output_snapshot",
    "raw_authority_text",
    "raw_model_output",
}


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


def merge_bundle(base: Mapping[str, Any], extra: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(base))
    for pool_name in ["adapter_evidence", "current_law", "jurisdiction_scope", "models", "floor_delivery", "no_go_threshold"]:
        incoming = extra.get(pool_name, {}) if isinstance(extra, Mapping) else {}
        if isinstance(incoming, Mapping):
            out.setdefault(pool_name, {}).update(copy.deepcopy(dict(incoming)))
    ctx = extra.get("execution_context", {}) if isinstance(extra, Mapping) else {}
    if isinstance(ctx, Mapping):
        out.setdefault("execution_context", {}).update(copy.deepcopy(dict(ctx)))
    for key in ["producer_contracts", "evidence_producer_contracts"]:
        if extra.get(key) and not out.get(key):
            out[key] = copy.deepcopy(extra.get(key))
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


def strict_schema_test_evidence_bundle_for_answers(root: pathlib.Path, answers: Sequence[Mapping[str, Any]], as_of_date: str) -> Dict[str, Any]:
    """Build an archive-generated schema-conformance bundle.

    The bundle exercises every adapter interface and replay path, but every
    record is explicitly internal, non-external, and promotion-ineligible.
    During the combined semantic suite, a deterministic temporary cache avoids
    rebuilding the same 1,724-record graph for replay, promotion, and output.
    """
    cache_identity = compact_hash({
        "root": root.name,
        "as_of_date": as_of_date,
        "case_adapter_ids": [
            [
                answer.get("case_id"),
                [check.get("adapter_id") for check in answer.get("disposition", {}).get("adapter_checks", [])],
            ]
            for answer in answers
        ],
        "rule_version": RULE_VERSION,
    })
    cache_path_text = os.environ.get("MT_STRICT_SCHEMA_TEST_EVIDENCE_CACHE")
    cache_path = pathlib.Path(cache_path_text) if cache_path_text else None
    if cache_path and cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = None
        if isinstance(cached, dict) and cached.get("strict_schema_test_cache_identity") == cache_identity:
            return cached

    runner = load_module("run_evidence_producers", root / "tools/run_evidence_producers.py")
    input_builder = load_module("build_model_input_bundle", root / "tools/build_model_input_bundle.py")
    source_builder = load_module("build_model_input_source_manifest", root / "tools/build_model_input_source_manifest.py")
    authority_builder = load_module("build_authority_evidence_bundle", root / "tools/build_authority_evidence_bundle.py")
    intake_builder = load_module("build_authority_intake_bundle", root / "tools/build_authority_intake_bundle.py")
    authority_source_builder = load_module("build_authority_intake_source_manifest", root / "tools/build_authority_intake_source_manifest.py")

    model_inputs = input_builder.bundle_for_answers(answers, as_of_date)
    model_source_manifest = source_builder.manifest_for_input_bundle(
        model_inputs, as_of_date, source_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE
    )
    strict_model_base = runner.bundle_for_answers(
        root,
        answers,
        runner.MODE_LOCAL_MODEL_ONLY,
        as_of_date,
        model_input_bundle=model_inputs,
        model_input_source_manifest=model_source_manifest,
        strict_model_input_sources=True,
        strict_authority_evidence=True,
    )
    authority_source_manifest = authority_source_builder.manifest_for_answers(
        answers, as_of_date, authority_source_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE
    )
    authority_intake = intake_builder.bundle_for_answers(
        answers, as_of_date, intake_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE, authority_source_manifest
    )
    authority_evidence = authority_builder.bundle_for_answers(
        root, answers, as_of_date, authority_builder.CERT_STRICT_SCHEMA_TEST_FIXTURE, True, authority_intake
    )
    bundle = merge_bundle(strict_model_base, authority_evidence)
    bundle.setdefault("execution_context", {})["allow_internal_strict_schema_test_fixture"] = True
    bundle.setdefault("execution_context", {})["decision_output_reference_bundle"] = (
        "archive_generated_strict_schema_test_fixture_never_promotion_eligible"
    )
    bundle["strict_schema_test_cache_identity"] = cache_identity
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = cache_path.with_suffix(cache_path.suffix + ".tmp")
        temporary.write_text(json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        temporary.replace(cache_path)
    return bundle


def implementation_evidence_bundle_for_answers(root: pathlib.Path, answers: Sequence[Mapping[str, Any]], as_of_date: str) -> Dict[str, Any]:
    """Backward-compatible alias; no implementation evidence is generated."""
    return strict_schema_test_evidence_bundle_for_answers(root, answers, as_of_date)


def _records_by_case(ledger: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in ledger.get("ledger_records", []):
        if not isinstance(record, Mapping):
            continue
        case_id = str(record.get("case_id") or "")
        grouped.setdefault(case_id, []).append(dict(record))
    return grouped


def _case_promotions_by_id(promotion: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(case.get("case_id")): dict(case) for case in promotion.get("case_promotions", []) if isinstance(case, Mapping)}


def _hash_fields_for_records(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for record in records:
        out.append({
            "record_key": record.get("record_key"),
            "adapter_id": record.get("adapter_id"),
            "adapter_type": record.get("adapter_type"),
            "route_id": record.get("route_id"),
            "execution_status": record.get("execution_status"),
            "finalization_status": record.get("finalization_status"),
            "adapter_packet_hash": record.get("adapter_packet_hash"),
            "adapter_binding_hash": record.get("adapter_binding_hash"),
            "evidence_adapter_binding_hash": record.get("evidence_adapter_binding_hash"),
            "evidence_hash": record.get("evidence_hash"),
            "producer_contract_hash": record.get("producer_contract_hash"),
            "evidence_truth_boundary_hash": record.get("evidence_truth_boundary_hash"),
            "decision_trace_hash": record.get("decision_trace_hash"),
            "result_hash": record.get("result_hash"),
            "strict_schema_test_fixture": record.get("strict_schema_test_fixture"),
            "evidence_origin": record.get("evidence_origin"),
            "external_source_attestation_status": record.get("external_source_attestation_status"),
            "promotion_eligible": record.get("promotion_eligible"),
            "external_attestation_verifier_status": record.get("external_attestation_verifier_status"),
            "trusted_external_attestation": record.get("trusted_external_attestation"),
            "external_attestation_verification_hash": record.get("external_attestation_verification_hash"),
        })
    return out


def _decision_summary_for_answer(answer: Mapping[str, Any]) -> Dict[str, Any]:
    disposition = answer.get("disposition", {}) if isinstance(answer.get("disposition"), Mapping) else {}
    return {
        "dominant_disposition": disposition.get("dominant_disposition"),
        "primary_route_id": (answer.get("routing", {}) or {}).get("primary_route_id") if isinstance(answer.get("routing", {}), Mapping) else None,
        "ordered_route_ids": disposition.get("ordered_route_ids", []),
        "recommended_sequence": disposition.get("recommended_sequence", []),
        "default_moves_by_route": disposition.get("default_moves_by_route", []),
        "actor_assignments": disposition.get("actor_assignments", []),
        "hard_blocks": disposition.get("hard_blocks", []),
        "cannot_finalize_until_from_disposition": disposition.get("cannot_finalize_until", []),
        "adapter_summary": disposition.get("adapter_summary", {}),
    }


def _held_reason_packet(case_promotion: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "promotion_reasons": case_promotion.get("promotion_reasons", []),
        "cannot_finalize_markers": case_promotion.get("cannot_finalize_markers", []),
        "blocked_adapters": case_promotion.get("blocked_adapters", []),
        "record_error_count": case_promotion.get("record_error_count", 0),
        "record_errors": case_promotion.get("record_errors", []),
    }


def materialize_outputs_from_promotion(
    answers: Sequence[Mapping[str, Any]],
    ledger: Mapping[str, Any],
    promotion: Mapping[str, Any],
) -> Dict[str, Any]:
    if promotion.get("runtime_status") != PROMOTION_STATUS:
        raise SystemExit("promotion packet runtime_status is stale")
    promotions = _case_promotions_by_id(promotion)
    records = _records_by_case(ledger)
    outputs: List[Dict[str, Any]] = []
    for answer in sorted(answers, key=lambda a: str(a.get("case_id"))):
        case_id = str(answer.get("case_id"))
        case_promotion = promotions.get(case_id, {})
        case_records = records.get(case_id, [])
        promoted = case_promotion.get("can_promote_to_final_disposition") is True
        decision_summary = _decision_summary_for_answer(answer)
        status = STATUS_FINALIZED if promoted else STATUS_HELD
        output: Dict[str, Any] = {
            "case_id": case_id,
            "title": answer.get("title"),
            "decision_output_status": status,
            "can_issue_final_determination": promoted,
            "promotion_status": case_promotion.get("promotion_status"),
            "dominant_disposition": decision_summary.get("dominant_disposition"),
            "primary_route_id": decision_summary.get("primary_route_id"),
            "ordered_route_ids": decision_summary.get("ordered_route_ids", []),
            "recommended_sequence": decision_summary.get("recommended_sequence", []),
            "default_moves_by_route": decision_summary.get("default_moves_by_route", []),
            "actor_assignments": decision_summary.get("actor_assignments", []),
            "blocked_or_forbidden_moves": decision_summary.get("hard_blocks", []),
            "adapter_summary": decision_summary.get("adapter_summary", {}),
            "ledger_hash": ledger.get("ledger_hash"),
            "evidence_bundle_hash": ledger.get("evidence_bundle_hash"),
            "producer_contract_manifest_hash": ledger.get("producer_contract_manifest_hash"),
            "case_promotion_hash": case_promotion.get("case_promotion_hash"),
            "case_record_count": len(case_records),
            "case_record_hashes": _hash_fields_for_records(case_records),
            "decision_output_non_doctrine_warning": NON_DOCTRINE_WARNING,
        }
        if promoted:
            output["finalization_scope"] = "case_level_final_disposition_under_supplied_external_observed_replay_clean_evidence"
            output["finalized_statement"] = (
                "The case may be carried forward to final disposition under this externally observed, independently attested evidence bundle, "
                "subject to the blocked moves and guardrails preserved in the disposition packet."
            )
            output["hold_reasons"] = []
            output["remaining_cannot_finalize_until"] = []
        else:
            hold = _held_reason_packet(case_promotion)
            output["finalization_scope"] = "not_finalizable_under_supplied_evidence_bundle"
            output["finalized_statement"] = "Do not issue a final determination from this evidence state."
            output["hold_reasons"] = hold
            output["remaining_cannot_finalize_until"] = dedupe(
                list(hold.get("cannot_finalize_markers", []))
                + list(hold.get("promotion_reasons", []))
                + list(decision_summary.get("cannot_finalize_until_from_disposition", []))
            )
        output["decision_output_hash"] = compact_hash({
            "case_id": output["case_id"],
            "status": output["decision_output_status"],
            "ordered_route_ids": output["ordered_route_ids"],
            "case_promotion_hash": output["case_promotion_hash"],
            "case_record_hashes": output["case_record_hashes"],
            "remaining_cannot_finalize_until": output.get("remaining_cannot_finalize_until", []),
        })
        outputs.append(output)

    status_counts: Dict[str, int] = {}
    for out in outputs:
        status_counts[str(out.get("decision_output_status"))] = status_counts.get(str(out.get("decision_output_status")), 0) + 1
    promoted_count = sum(1 for out in outputs if out.get("can_issue_final_determination"))
    held_count = len(outputs) - promoted_count
    packet = {
        "kind": "promotion_gated_decision_output_packets",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "promotion_runtime_status": promotion.get("runtime_status"),
        "ledger_runtime_status": ledger.get("runtime_status"),
        "ledger_hash": ledger.get("ledger_hash"),
        "evidence_bundle_hash": ledger.get("evidence_bundle_hash"),
        "producer_contract_manifest_hash": ledger.get("producer_contract_manifest_hash"),
        "replay_mismatch_count": promotion.get("replay_mismatch_count"),
        "summary": {
            "case_count": len(outputs),
            "finalized_case_count": promoted_count,
            "held_case_count": held_count,
            "decision_output_status_counts": dict(sorted(status_counts.items())),
            "adapter_record_count": sum(int(out.get("case_record_count", 0)) for out in outputs),
            "raw_evidence_stored": False,
        },
        "case_decision_outputs": outputs,
        "decision_output_packet_hash": compact_hash(outputs),
        "non_doctrine_warning": NON_DOCTRINE_WARNING,
    }
    return packet


def materialize_outputs_for_answers(
    root: pathlib.Path,
    answers: Sequence[Mapping[str, Any]],
    evidence_bundle: Mapping[str, Any] | None = None,
    replay_check: bool = True,
) -> Dict[str, Any]:
    ledger_builder = load_module("build_evidence_replay_ledger", root / "tools/build_evidence_replay_ledger.py")
    promoter = load_module("promote_decision_release", root / "tools/promote_decision_release.py")
    bundle = evidence_bundle or {}
    ledger = ledger_builder.ledger_for_answers(root, answers, bundle)
    comparison = None
    if replay_check:
        replayed = ledger_builder.ledger_for_answers(root, answers, bundle)
        comparison = ledger_builder.replay_compare(ledger, replayed)
    promotion = promoter.promotion_from_ledger(ledger, comparison)
    return materialize_outputs_from_promotion(answers, ledger, promotion)


def recursive_forbidden_key_hits(value: Any, path: str = "$.") -> List[str]:
    hits: List[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in FORBIDDEN_RAW_KEYS:
                hits.append(path + str(key))
            hits.extend(recursive_forbidden_key_hits(child, path + str(key) + "."))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            hits.extend(recursive_forbidden_key_hits(child, path + f"[{idx}]."))
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize promotion-gated final decision output packets.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Evaluate one case id")
    parser.add_argument("--all", action="store_true", help="Evaluate all golden cases")
    parser.add_argument("--evidence", help="Evidence bundle JSON to evaluate")
    parser.add_argument("--strict-schema-test-evidence", action="store_true", help="Build the archive-generated schema-conformance evidence bundle; it can never promote")
    parser.add_argument("--implementation-reference-evidence", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-replay-check", action="store_true", help="Do not run same-bundle replay comparison")
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    receipt = load_json(root / "REVISION-RECEIPT.json")
    as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
    bundle: Mapping[str, Any]
    if args.evidence:
        bundle = load_json(pathlib.Path(args.evidence).resolve())
    elif args.strict_schema_test_evidence or args.implementation_reference_evidence:
        bundle = strict_schema_test_evidence_bundle_for_answers(root, answers, as_of_date)
    else:
        bundle = {}
    packet = materialize_outputs_for_answers(root, answers, bundle, not args.no_replay_check)
    if args.json:
        print(json.dumps(packet, separators=(",", ":")))
    else:
        s = packet.get("summary", {})
        print(f"{packet.get('runtime_status')}: {s.get('finalized_case_count')} finalized, {s.get('held_case_count')} held")
        for out in packet.get("case_decision_outputs", [])[:8]:
            print(f"{out.get('case_id')}: {out.get('decision_output_status')}")


if __name__ == "__main__":
    main()
