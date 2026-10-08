#!/usr/bin/env python3
"""Build a signed positive-path evidence bundle for verifier/promotion smoke tests.

This is intentionally not a production evidence producer. It creates a small,
self-contained bundle for one bounded answer packet so audits can prove that the
external-attestation, adapter-binding, replay, and promotion mechanics work when
all cryptographic and schema conditions are satisfied. The bundle sets
execution_context.promotion_mode=sandbox_positive_path_test so promotion may
exercise the positive path without certifying a final legal/model disposition.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import pathlib
import sys
from typing import Any, Dict, Mapping

sys.dont_write_bytecode = True
TOOLS_DIR = pathlib.Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
import execute_decision_adapters as executor
import verify_external_attestation as verifier

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except Exception as exc:  # pragma: no cover - fail loudly; this is only a test tool.
    raise SystemExit(f"cryptography dependency unavailable for smoke bundle: {exc.__class__.__name__}")

PRODUCER_ID = "rev0342_signed_strict_smoke_evidence_producer"
CONTRACT_VERSION = "2026-06-18-rev0342"
KEY_ID = "rev0342-strict-smoke-ed25519-key"
DEFAULT_AS_OF_DATE = "2026-06-18"


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def deterministic_private_key() -> Any:
    """Return a public, deterministic test-vector key for reproducible sandbox audits.

    The generated bundle is explicitly non-certifying; using a deterministic key
    prevents the smoke path from hiding runtime drift behind fresh random keys.
    """
    seed = hashlib.sha256(b"moral-taxation-rev0342-strict-positive-path-smoke-key").digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def smoke_hash(value: Any) -> str:
    return executor.compact_hash(value)


def public_key_pem(private_key: Any) -> str:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def sign_evidence(evidence: Dict[str, Any], private_key: Any) -> Dict[str, Any]:
    payload = verifier.signed_payload_for_evidence(evidence, not_before="2026-01-01", not_after="2026-12-31")
    signature = private_key.sign(verifier.canonical_bytes(payload))
    return {
        "profile": verifier.PROFILE,
        "key_id": KEY_ID,
        "signed_payload": payload,
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def common_evidence(packet: Mapping[str, Any], as_of_date: str) -> Dict[str, Any]:
    return {
        "producer_id": PRODUCER_ID,
        "producer_contract_version": CONTRACT_VERSION,
        "evidence_kind": packet.get("adapter_type"),
        "created_at": as_of_date,
        "checked_at": as_of_date,
        "run_at": as_of_date,
        "producer_mode": "external_observed_signed_bundle",
        "evidence_origin": "external_observed",
        "external_source_attestation_status": "verified_external_attestation",
        "promotion_eligible": True,
        "strict_schema_test_fixture": False,
        "sandbox_positive_path_test": True,
        "case_id": packet.get("case_id"),
        "adapter_id": packet.get("adapter_id"),
        "adapter_type": packet.get("adapter_type"),
        "route_id": packet.get("route_id"),
        "source_id": packet.get("source_id"),
        "model_class": packet.get("model_class"),
        "scope": packet.get("scope"),
        "adapter_binding_hash": executor.adapter_binding_hash(packet),
        "evidence_locator": f"sandbox-smoke://rev0342/{packet.get('case_id')}/{packet.get('adapter_id')}",
    }


def authority_strict_proof_fields(packet: Mapping[str, Any], as_of_date: str) -> Dict[str, Any]:
    basis = {
        "case_id": packet.get("case_id"),
        "adapter_id": packet.get("adapter_id"),
        "source_id": packet.get("source_id"),
        "route_id": packet.get("route_id"),
        "as_of_date": as_of_date,
        "proof": "strict-authority-sandbox-smoke",
    }
    record_hash = smoke_hash({**basis, "record": "authority-evidence"})
    intake_hash = smoke_hash({**basis, "record": "authority-intake"})
    source_hash = smoke_hash({**basis, "record": "authority-source"})
    bundle_hash = smoke_hash({"bundle": "rev0342-strict-authority-smoke", "record_hash": record_hash})
    intake_bundle_hash = smoke_hash({"bundle": "rev0342-strict-authority-intake-smoke", "record_hash": intake_hash})
    source_manifest_hash = smoke_hash({"manifest": "rev0342-strict-authority-source-smoke", "record_hash": source_hash})
    locator_tail = f"{packet.get('case_id')}/{packet.get('adapter_id')}"
    return {
        "authority_evidence_bundle_id": "rev0342-strict-smoke-authority-evidence-bundle",
        "authority_evidence_record_hash": record_hash,
        "authority_evidence_bundle_hash": bundle_hash,
        "authority_certification_level": "implementation_grade",
        "implementation_grade_authority_evidence": True,
        "authority_source_contract_id": "rev0342-strict-smoke-authority-source-contract",
        "authority_source_locator": f"sandbox-authority-source://rev0342/{locator_tail}",
        "authority_checked_at": as_of_date,
        "authority_coverage_period": {"start": as_of_date, "end": as_of_date},
        "authority_freshness_status": "fresh",
        "authority_provenance_hash": smoke_hash({**basis, "proof": "authority-provenance"}),
        "external_authority_claim_hash": smoke_hash({**basis, "claim": "supported"}),
        "authority_intake_bundle_id": "rev0342-strict-smoke-authority-intake-bundle",
        "authority_intake_record_hash": intake_hash,
        "authority_intake_bundle_hash": intake_bundle_hash,
        "authority_raw_locator": f"sandbox-authority-raw://rev0342/{locator_tail}",
        "authority_raw_record_hash": smoke_hash({**basis, "raw": "observed"}),
        "authority_claim_locator": f"sandbox-authority-claim://rev0342/{locator_tail}",
        "authority_claim_support_map_hash": smoke_hash({**basis, "support-map": True}),
        "authority_reviewer_attestation_hash": smoke_hash({**basis, "reviewer": "strict-smoke"}),
        "authority_conflict_search_hash": smoke_hash({**basis, "conflict-search": "none"}),
        "authority_intake_certification_level": "implementation_grade",
        "implementation_grade_authority_intake": True,
        "authority_source_type": "primary_authority_observation_record",
        "authority_primary_authority": True,
        "authority_retrieved_at": as_of_date,
        "authority_intake_freshness_status": "fresh",
        "authority_record_claim_supported": True,
        "authority_source_manifest_id": "rev0342-strict-smoke-authority-source-manifest",
        "authority_source_record_hash": source_hash,
        "authority_source_manifest_hash": source_manifest_hash,
        "authority_source_certification_level": "implementation_grade",
        "implementation_grade_authority_source": True,
        "authority_retrieval_source_locator": f"sandbox-authority-retrieval-source://rev0342/{locator_tail}",
        "authority_retrieval_claim_locator": f"sandbox-authority-retrieval-claim://rev0342/{locator_tail}",
        "authority_retrieval_source_type": "primary_authority_repository",
        "authority_source_retrieval_date": as_of_date,
        "authority_source_freshness_status": "fresh",
        "authority_source_primary_authority": True,
        "authority_source_claim_support_hash": smoke_hash({**basis, "source-claim": "supported"}),
        "authority_source_conflict_review_hash": smoke_hash({**basis, "source-conflict-review": "none"}),
        "authority_source_provenance_hash": smoke_hash({**basis, "source-provenance": True}),
    }


def model_input_source_strict_proof_fields(packet: Mapping[str, Any], as_of_date: str, input_record_hash: str) -> Dict[str, Any]:
    basis = {
        "case_id": packet.get("case_id"),
        "adapter_id": packet.get("adapter_id"),
        "route_id": packet.get("route_id"),
        "model_class": packet.get("model_class"),
        "input_record_hash": input_record_hash,
        "as_of_date": as_of_date,
        "proof": "strict-model-input-source-sandbox-smoke",
    }
    source_record_hash = smoke_hash({**basis, "record": "input-source"})
    manifest_hash = smoke_hash({"manifest": "rev0342-strict-model-input-source-smoke", "record_hash": source_record_hash})
    locator_tail = f"{packet.get('case_id')}/{packet.get('adapter_id')}"
    return {
        "model_input_source_manifest_id": "rev0342-strict-smoke-model-input-source-manifest",
        "model_input_source_runtime_status": "strict_sandbox_external_source_manifest",
        "input_source_record_hash": source_record_hash,
        "input_source_manifest_hash": manifest_hash,
        "input_certification_level": "implementation_grade",
        "implementation_grade_input_source": True,
        "source_contract_id": "rev0342-strict-smoke-model-input-source-contract",
        "source_locator": f"sandbox-model-input-source://rev0342/{locator_tail}",
        "source_coverage_period": {"start": as_of_date, "end": as_of_date},
        "source_extraction_date": as_of_date,
        "source_freshness_status": "fresh",
        "source_freshness_policy_days": 366,
        "units_verified": True,
        "provenance_hash": smoke_hash({**basis, "provenance": True}),
    }


def evidence_for_packet(packet: Mapping[str, Any], as_of_date: str) -> Dict[str, Any]:
    typ = str(packet.get("adapter_type") or "")
    evidence = common_evidence(packet, as_of_date)
    if typ == "jurisdiction_scope_adapter":
        evidence.update(authority_strict_proof_fields(packet, as_of_date))
        evidence.update({
            "jurisdiction": "bounded-smoke-test-jurisdiction",
            "effective_date": as_of_date,
            "authority_level": "sandbox_verified_authority_level",
            "preemption_or_treaty_conflict": "none_identified",
            "implementation_status": "in_force",
            "conflict_resolution": "resolved_no_conflict",
            "result_status": "unchanged",
            "reviewer_or_system": "rev0342-strict-positive-path-smoke-audit",
            "claim_supported": True,
            "authority_locator": evidence["evidence_locator"],
        })
    elif typ in {"floor_delivery_adapter", "quantitative_model_adapter", "no_go_threshold_adapter"}:
        required_outputs = [str(x) for x in packet.get("required_outputs", [])]
        outputs = {name: f"sandbox-smoke-{name}-verified" for name in required_outputs}
        outputs.setdefault("smoke_result", "verified")
        input_record_hash = executor.compact_hash({
            "case_id": packet.get("case_id"),
            "adapter_id": packet.get("adapter_id"),
            "required_outputs": required_outputs,
            "as_of_date": as_of_date,
            "purpose": "sandbox_positive_path_test",
        })
        evidence.update(model_input_source_strict_proof_fields(packet, as_of_date, input_record_hash))
        evidence.update({
            "model_name": f"rev0342-strict-smoke-{packet.get('model_class') or typ}",
            "model_version": "sandbox-strict-smoke-v2",
            "inputs_hash": input_record_hash,
            "assumptions": {"purpose": "positive-path smoke test only", "not_current_law": True},
            "uncertainty_method": "not_applicable_sandbox_smoke_test",
            "outputs": outputs,
            "result_status": "executed",
            "model_input_bundle_id": "rev0342-strict-smoke-input-bundle",
            "model_input_record_hash": input_record_hash,
            "input_hash_basis": "explicit_model_input_bundle",
            "input_locator": f"sandbox-smoke://rev0342/model-input/{packet.get('adapter_id')}",
            "assumption_set_id": "rev0342-strict-smoke-assumption-set",
            "input_values_hash": input_record_hash,
            "run_locator": evidence["evidence_locator"],
        })
        if typ == "no_go_threshold_adapter":
            evidence.update({"threshold_result": "not_triggered", "reviewer_or_system": "rev0342-strict-positive-path-smoke-audit"})
    elif typ == "current_law_refresh_adapter":
        evidence.update(authority_strict_proof_fields(packet, as_of_date))
        evidence.update({
            "source_id": packet.get("source_id"),
            "retrieval_method": "sandbox_smoke_no_network",
            "authority_locator": evidence["evidence_locator"],
            "jurisdiction": packet.get("jurisdiction") or "bounded-smoke-test-jurisdiction",
            "effective_date": packet.get("effective_date") or as_of_date,
            "result_status": "unchanged",
            "reviewer_or_system": "rev0342-strict-positive-path-smoke-audit",
            "claim_supported": True,
        })
    else:
        raise ValueError(f"unsupported adapter type for smoke bundle: {typ}")
    return evidence


def producer_contract() -> Dict[str, Any]:
    return {
        "producer_id": PRODUCER_ID,
        "contract_version": CONTRACT_VERSION,
        "adapter_types": [
            "current_law_refresh_adapter",
            "jurisdiction_scope_adapter",
            "floor_delivery_adapter",
            "quantitative_model_adapter",
            "no_go_threshold_adapter",
        ],
        "permitted_execution_modes": ["external_observed_signed_bundle"],
        "freshness_policy_days": 366,
        "blocking_statuses": ["changed", "superseded", "uncertain", "not_found", "triggered"],
        "stores_doctrine": False,
        "output_retention": "external_evidence_bundle_only",
        "non_doctrine_warning": "This strict smoke producer exercises evidence mechanics only; it is not a source of current law or empirical model truth.",
    }


def build_bundle(root: pathlib.Path, case_id: str = "GC-001", route_limit: int = 5, facts_only_limit: int = 8, as_of_date: str = DEFAULT_AS_OF_DATE) -> Dict[str, Any]:
    answer_case = load_module("answer_case", root / "tools/answer_case.py")
    golden = json.loads((root / "docs/00-meta/golden-cases.json").read_text(encoding="utf-8"))
    cases = [case for case in golden.get("cases", []) if case.get("case_id") == case_id]
    if not cases:
        raise SystemExit(f"unknown case id: {case_id}")
    runtime = answer_case.AnswerRuntime(root, route_limit, facts_only_limit)
    answer = runtime.answer_case(cases[0])
    packets = []
    for packet in answer.get("disposition", {}).get("adapter_checks", []):
        item = dict(packet)
        item.setdefault("case_id", answer.get("case_id"))
        packets.append(item)
    private_key = deterministic_private_key()
    adapter_evidence: Dict[str, Dict[str, Any]] = {}
    binding_hashes = []
    for packet in packets:
        evidence = evidence_for_packet(packet, as_of_date)
        evidence["external_attestation"] = sign_evidence(evidence, private_key)
        adapter_evidence[f"{packet.get('case_id')}:{packet.get('adapter_id')}"] = evidence
        binding_hashes.append(executor.adapter_binding_hash(packet))
    return {
        "kind": "signed_external_evidence_smoke_bundle",
        "runtime_status": "signed_external_evidence_smoke_bundle_generated",
        "rule_version": 2,
        "case_id": case_id,
        "route_limit": route_limit,
        "facts_only_candidate_limit": facts_only_limit,
        "adapter_record_count": len(adapter_evidence),
        "execution_context": {
            "as_of_date": as_of_date,
            "promotion_mode": "sandbox_positive_path_test",
            "sandbox_smoke_test_only": True,
            "deterministic_public_test_vector_key": True,
            "strict_model_input_source_certification_required": True,
            "strict_authority_evidence_required": True,
            "non_doctrine_warning": "Positive-path strict smoke bundle only; do not treat as current law, jurisdiction clearance, model truth, or final advice.",
        },
        "trusted_external_attestation_verifier": {
            "profile": verifier.PROFILE,
            "policy": {"require_active_key_status": True, "require_transparency_log_entry": False},
            "trust_store": [
                {
                    "key_id": KEY_ID,
                    "issuer": "rev0342 strict positive-path smoke harness",
                    "status": "active",
                    "public_key_pem": public_key_pem(private_key),
                    "allowed_producer_ids": [PRODUCER_ID],
                    "allowed_evidence_kinds": producer_contract()["adapter_types"],
                    "allowed_adapter_binding_hashes": binding_hashes,
                    "not_before": "2026-01-01",
                    "not_after": "2026-12-31",
                }
            ],
        },
        "producer_contracts": [producer_contract()],
        "adapter_evidence": adapter_evidence,
        "non_doctrine_warning": "This generated strict bundle is for verifier/replay/promotion smoke testing only and must not be packaged as an external factual record.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a signed sandbox evidence bundle that exercises the positive verifier path.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--case-id", default="GC-001")
    parser.add_argument("--route-limit", type=int, default=5)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=8)
    parser.add_argument("--as-of-date", default=DEFAULT_AS_OF_DATE)
    parser.add_argument("--output", help="Write JSON bundle to this path instead of stdout")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    bundle = build_bundle(root, args.case_id, args.route_limit, args.facts_only_candidate_limit, args.as_of_date)
    text = json.dumps(bundle, separators=(",", ":") if args.json else (", ", ": ")) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
