#!/usr/bin/env python3
"""Export a reviewable, non-certifying decision evidence bundle.

The positive-path smoke harness proves that adapter-bound, signed evidence can
satisfy the verifier/replay/promotion mechanics. This exporter turns that into
a bounded review packet: enough material for a reviewer to re-check signatures,
adapter bindings, replay hashes, strict proof gates, and decision-output status
without mistaking the packet for final public advice.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
from typing import Any, Dict, Iterable, List, Mapping, Sequence

sys.dont_write_bytecode = True
TOOLS_DIR = pathlib.Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import execute_decision_adapters as executor
import verify_external_attestation as verifier

RUNTIME_STATUS = "decision_review_bundle_exported"
RULE_VERSION = 1
BUNDLE_KIND_SANDBOX = "sandbox_positive_path_decision_review_bundle"
NON_DOCTRINE_WARNING = (
    "This review bundle is a bounded verifier/replay packet. It may contain a "
    "sandbox positive-path test vector, but it is not current law, not legal "
    "advice, not empirical model truth, and not a final determination."
)


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def compact_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


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


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_case_answer(root: pathlib.Path, case_id: str, route_limit: int, facts_only_limit: int) -> Dict[str, Any]:
    answer_case = load_module("answer_case", root / "tools/answer_case.py")
    golden = load_json(root / "docs/00-meta/golden-cases.json")
    cases = [case for case in golden.get("cases", []) if case.get("case_id") == case_id]
    if not cases:
        raise SystemExit(f"unknown case id: {case_id}")
    runtime = answer_case.AnswerRuntime(root, route_limit, facts_only_limit)
    return runtime.answer_case(cases[0])


def scrub_private_material(value: Any) -> Any:
    """Remove accidental private-key material before export.

    The smoke bundle should only contain public keys, but review packets are a
    human-facing handoff surface, so enforce the boundary defensively.
    """
    if isinstance(value, Mapping):
        out: Dict[str, Any] = {}
        for key, child in value.items():
            lowered = str(key).lower()
            if "private" in lowered or lowered in {"seed", "secret", "secret_key"}:
                out[str(key)] = "<redacted-private-material>"
            else:
                out[str(key)] = scrub_private_material(child)
        return out
    if isinstance(value, list):
        return [scrub_private_material(child) for child in value]
    if isinstance(value, str) and "PRIVATE KEY" in value:
        return "<redacted-private-material>"
    return value


def trust_store_public_view(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    config = verifier.verifier_config(bundle)
    if not config:
        return {}
    return scrub_private_material(config)


def _evidence_items(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    pool = bundle.get("adapter_evidence", {}) if isinstance(bundle, Mapping) else {}
    items = []
    if isinstance(pool, Mapping):
        for lookup_key, evidence in sorted(pool.items()):
            if isinstance(evidence, Mapping):
                payload = verifier.evidence_payload(evidence)
                attestation = verifier.attestation_for_evidence(evidence)
                verification = verifier.verification_for_evidence(evidence, bundle)
                items.append({
                    "lookup_key": str(lookup_key),
                    "case_id": evidence.get("case_id"),
                    "adapter_id": evidence.get("adapter_id"),
                    "adapter_type": evidence.get("adapter_type"),
                    "route_id": evidence.get("route_id"),
                    "source_id": evidence.get("source_id"),
                    "model_class": evidence.get("model_class"),
                    "scope": evidence.get("scope"),
                    "evidence_kind": evidence.get("evidence_kind"),
                    "evidence_origin": evidence.get("evidence_origin"),
                    "promotion_eligible": evidence.get("promotion_eligible") is True,
                    "strict_schema_test_fixture": evidence.get("strict_schema_test_fixture") is True,
                    "adapter_binding_hash": evidence.get("adapter_binding_hash"),
                    "evidence_payload_hash": verifier.evidence_payload_hash(evidence),
                    "external_attestation": scrub_private_material(attestation),
                    "external_attestation_verification": verification,
                    "evidence_payload": scrub_private_material(payload),
                })
    return items


def _record_index(ledger: Mapping[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for record in ledger.get("ledger_records", []):
        if not isinstance(record, Mapping):
            continue
        out.append({
            "record_key": record.get("record_key"),
            "case_id": record.get("case_id"),
            "adapter_id": record.get("adapter_id"),
            "adapter_type": record.get("adapter_type"),
            "route_id": record.get("route_id"),
            "finalization_status": record.get("finalization_status"),
            "promotion_eligible": record.get("promotion_eligible") is True,
            "trusted_external_attestation": record.get("trusted_external_attestation") is True,
            "external_attestation_verifier_status": record.get("external_attestation_verifier_status"),
            "adapter_binding_hash": record.get("adapter_binding_hash"),
            "evidence_adapter_binding_hash": record.get("evidence_adapter_binding_hash"),
            "strict_model_input_source_certification_required": record.get("strict_model_input_source_certification_required") is True,
            "strict_authority_evidence_required": record.get("strict_authority_evidence_required") is True,
            "input_source_record_hash": record.get("input_source_record_hash"),
            "input_source_manifest_hash": record.get("input_source_manifest_hash"),
            "authority_evidence_record_hash": record.get("authority_evidence_record_hash"),
            "authority_source_record_hash": record.get("authority_source_record_hash"),
            "authority_source_manifest_hash": record.get("authority_source_manifest_hash"),
            "evidence_truth_boundary_hash": record.get("evidence_truth_boundary_hash"),
            "external_attestation_verification_hash": record.get("external_attestation_verification_hash"),
            "result_hash": record.get("result_hash"),
        })
    return out


def _review_gates(
    evidence_items: Sequence[Mapping[str, Any]],
    ledger: Mapping[str, Any],
    comparison: Mapping[str, Any],
    promotion: Mapping[str, Any],
    outputs: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    summary = ledger.get("summary", {}) if isinstance(ledger.get("summary"), Mapping) else {}
    promo_summary = promotion.get("summary", {}) if isinstance(promotion.get("summary"), Mapping) else {}
    output_summary = outputs.get("summary", {}) if isinstance(outputs.get("summary"), Mapping) else {}
    expected_count = int(summary.get("record_count") or 0)
    verified_count = sum(1 for item in evidence_items if item.get("external_attestation_verification", {}).get("trusted_external_attestation") is True)
    gates = [
        {
            "gate": "external_attestations_recompute",
            "passed": verified_count == expected_count and expected_count > 0,
            "verified_count": verified_count,
            "expected_count": expected_count,
        },
        {
            "gate": "adapter_bindings_match",
            "passed": int(summary.get("adapter_binding_mismatch_count") or 0) == 0,
            "mismatch_count": int(summary.get("adapter_binding_mismatch_count") or 0),
        },
        {
            "gate": "strict_model_input_source_proofs_present",
            "passed": summary.get("strict_model_input_source_proof_record_count") == summary.get("strict_model_input_source_required_record_count"),
            "proof_count": summary.get("strict_model_input_source_proof_record_count"),
            "required_count": summary.get("strict_model_input_source_required_record_count"),
        },
        {
            "gate": "strict_authority_source_proofs_present",
            "passed": summary.get("strict_authority_evidence_proof_record_count") == summary.get("strict_authority_evidence_required_record_count"),
            "proof_count": summary.get("strict_authority_evidence_proof_record_count"),
            "required_count": summary.get("strict_authority_evidence_required_record_count"),
        },
        {
            "gate": "replay_clean",
            "passed": comparison.get("mismatch_count") == 0,
            "mismatch_count": comparison.get("mismatch_count"),
        },
        {
            "gate": "sandbox_does_not_promote_final_cases",
            "passed": promo_summary.get("promoted_case_count") == 0 and promo_summary.get("sandbox_positive_path_case_count") == 1,
            "promoted_case_count": promo_summary.get("promoted_case_count"),
            "sandbox_positive_path_case_count": promo_summary.get("sandbox_positive_path_case_count"),
        },
        {
            "gate": "decision_outputs_remain_held",
            "passed": output_summary.get("finalized_case_count") == 0 and output_summary.get("held_case_count") == 1,
            "finalized_case_count": output_summary.get("finalized_case_count"),
            "held_case_count": output_summary.get("held_case_count"),
        },
    ]
    return gates


def build_review_bundle(
    root: pathlib.Path,
    case_id: str = "GC-001",
    route_limit: int = 5,
    facts_only_limit: int = 8,
    as_of_date: str = "2026-06-18",
    evidence_bundle: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    smoke_builder = load_module("build_signed_external_evidence_smoke_bundle", root / "tools/build_signed_external_evidence_smoke_bundle.py")
    ledger_builder = load_module("build_evidence_replay_ledger", root / "tools/build_evidence_replay_ledger.py")
    promoter = load_module("promote_decision_release", root / "tools/promote_decision_release.py")
    materializer = load_module("materialize_decision_outputs", root / "tools/materialize_decision_outputs.py")

    bundle = copy.deepcopy(dict(evidence_bundle)) if evidence_bundle is not None else smoke_builder.build_bundle(root, case_id, route_limit, facts_only_limit, as_of_date)
    answer = load_case_answer(root, case_id, route_limit, facts_only_limit)
    answers = [answer]
    ledger = ledger_builder.ledger_for_answers(root, answers, bundle)
    replayed = ledger_builder.ledger_for_answers(root, answers, bundle)
    comparison = ledger_builder.replay_compare(ledger, replayed)
    promotion = promoter.promotion_from_ledger(ledger, comparison)
    outputs = materializer.materialize_outputs_from_promotion(answers, ledger, promotion)
    evidence_items = _evidence_items(bundle)
    record_index = _record_index(ledger)
    gates = _review_gates(evidence_items, ledger, comparison, promotion, outputs)
    case_outputs = outputs.get("case_decision_outputs", []) if isinstance(outputs.get("case_decision_outputs"), list) else []
    packet: Dict[str, Any] = {
        "kind": BUNDLE_KIND_SANDBOX,
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "case_id": case_id,
        "title": answer.get("title"),
        "production_finalization_allowed": False,
        "review_scope": {
            "route_limit": route_limit,
            "facts_only_candidate_limit": facts_only_limit,
            "as_of_date": as_of_date,
            "promotion_mode": promotion.get("promotion_mode"),
            "promotion_scope": ledger.get("promotion_scope", {}),
            "selected_route_ids": answer.get("disposition", {}).get("ordered_route_ids", []),
            "adapter_record_count": ledger.get("summary", {}).get("record_count"),
            "sandbox_smoke_test_only": True,
        },
        "hashes": {
            "answer_hash": compact_hash(answer),
            "evidence_bundle_hash": ledger.get("evidence_bundle_hash"),
            "ledger_hash": ledger.get("ledger_hash"),
            "replay_comparison_hash": compact_hash(comparison),
            "promotion_packet_hash": promotion.get("promotion_packet_hash"),
            "decision_output_packet_hash": outputs.get("decision_output_packet_hash"),
            "trust_policy_hash": verifier.trust_policy_hash(bundle),
        },
        "trust_store_public_view": trust_store_public_view(bundle),
        "producer_contracts": scrub_private_material(bundle.get("producer_contracts") or bundle.get("evidence_producer_contracts") or []),
        "review_gates": gates,
        "all_review_gates_passed": all(gate.get("passed") is True for gate in gates),
        "ledger_summary": ledger.get("summary", {}),
        "replay_summary": {
            "runtime_status": comparison.get("runtime_status"),
            "mismatch_count": comparison.get("mismatch_count"),
            "mismatches": comparison.get("mismatches", [])[:20],
        },
        "promotion_summary": promotion.get("summary", {}),
        "decision_output_summary": outputs.get("summary", {}),
        "case_decision_output": scrub_private_material(case_outputs[0]) if case_outputs else {},
        "ledger_record_index": record_index,
        "evidence_review_records": evidence_items,
        "external_attestation_profile": verifier.PROFILE,
        "reviewer_actions": [
            "Recompute each evidence_payload_hash from evidence_payload and compare it to the signed payload.",
            "Verify every Ed25519 signature against the public trust-store key and policy.",
            "Recompute adapter_binding_hash for each consumed adapter packet; do not accept cross-case or cross-route substitution.",
            "Rebuild the replay ledger and require zero mismatches before considering any production path.",
            "Confirm promotion_mode is production and production evidence is non-sandbox before any final determination; this bundle deliberately fails that finality condition.",
        ],
        "non_doctrine_warning": NON_DOCTRINE_WARNING,
    }
    packet["review_bundle_hash"] = compact_hash({k: v for k, v in packet.items() if k != "review_bundle_hash"})
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a non-certifying decision review bundle for one case.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--case-id", default="GC-001")
    parser.add_argument("--route-limit", type=int, default=5)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=8)
    parser.add_argument("--as-of-date", default="2026-06-18")
    parser.add_argument("--evidence", help="Use an existing evidence bundle JSON instead of the sandbox smoke builder")
    parser.add_argument("--output", help="Write JSON bundle to this path instead of stdout")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    evidence = load_json(pathlib.Path(args.evidence).resolve()) if args.evidence else None
    packet = build_review_bundle(root, args.case_id, args.route_limit, args.facts_only_candidate_limit, args.as_of_date, evidence)
    text = json.dumps(packet, sort_keys=True, separators=(",", ":") if args.json else (", ", ": ")) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
