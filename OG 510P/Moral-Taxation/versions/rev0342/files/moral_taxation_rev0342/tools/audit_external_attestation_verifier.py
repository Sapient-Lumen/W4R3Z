#!/usr/bin/env python3
"""Audit the external-attestation verifier and adapter-binding boundary.

A producer cannot satisfy promotion by writing `verified_external_attestation`;
it must sign the exact evidence payload. Rev0339 adds the next hard edge: that
signed payload must also be bound to the consuming adapter/case scope, and trust
keys can be revoked or held behind a future transparency-log policy.
"""
from __future__ import annotations

import base64
import copy
import importlib.util
import json
import pathlib
import sys
from typing import Any, Dict, List, Mapping

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
RUNTIME_STATUS = "external_attestation_verifier_checked"
PROFILE = "ed25519_canonical_json_v1"


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


verifier = load_module("verify_external_attestation", root / "tools/verify_external_attestation.py")
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except Exception as exc:  # pragma: no cover - this archive must fail closed if missing.
    raise SystemExit(f"cryptography dependency unavailable for verifier audit: {exc.__class__.__name__}")


def sign_attestation(evidence: Mapping[str, Any], private_key: Any, key_id: str, not_after: str = "2026-12-31") -> Dict[str, Any]:
    payload = verifier.signed_payload_for_evidence(evidence, not_before="2026-01-01", not_after=not_after)
    signature = private_key.sign(verifier.canonical_bytes(payload))
    return {
        "profile": PROFILE,
        "key_id": key_id,
        "signed_payload": payload,
        "signature": base64.b64encode(signature).decode("ascii"),
    }


test_packet: Dict[str, Any] = {
    "case_id": "GC-ATTESTATION-BINDING-TEST",
    "adapter_id": "rev0339-current-law-adapter-binding-test",
    "adapter_type": "current_law_refresh_adapter",
    "route_id": "rev0339_adapter_binding_route",
    "source_id": "S681",
    "required_outputs": ["claim_supported"],
}
replay_packet = dict(test_packet)
replay_packet["route_id"] = "rev0339_wrong_route_replay_target"

key_id = "rev0339-test-trusted-producer-key"
private_key = Ed25519PrivateKey.generate()
public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode("utf-8")

base_evidence: Dict[str, Any] = {
    "producer_id": "rev0339_external_test_producer",
    "producer_contract_version": "2026-06-18",
    "evidence_kind": "current_law_refresh_adapter",
    "created_at": "2026-06-18",
    "checked_at": "2026-06-18",
    "producer_mode": "external_observed_signed_bundle",
    "evidence_origin": "external_observed",
    "external_source_attestation_status": "verified_external_attestation",
    "promotion_eligible": True,
    "case_id": test_packet["case_id"],
    "adapter_id": test_packet["adapter_id"],
    "route_id": test_packet["route_id"],
    "source_id": "S681",
    "adapter_binding_hash": executor.adapter_binding_hash(test_packet),
    "authority_locator": "https://example.invalid/authoritative-record/1",
    "jurisdiction": "test-jurisdiction",
    "effective_date": "2026-06-18",
    "result_status": "unchanged",
    "reviewer_or_system": "rev0339-verifier-audit",
    "claim_supported": True,
}
base_evidence["external_attestation"] = sign_attestation(base_evidence, private_key, key_id)
trusted_bundle = {
    "execution_context": {"as_of_date": "2026-06-18"},
    "trusted_external_attestation_verifier": {
        "profile": PROFILE,
        "policy": {"require_active_key_status": True, "require_transparency_log_entry": False},
        "trust_store": [
            {
                "key_id": key_id,
                "issuer": "rev0339 verifier audit",
                "status": "active",
                "public_key_pem": public_pem,
                "allowed_producer_ids": ["rev0339_external_test_producer"],
                "allowed_evidence_kinds": ["current_law_refresh_adapter"],
                "allowed_adapter_binding_hashes": [executor.adapter_binding_hash(test_packet)],
                "not_before": "2026-01-01",
                "not_after": "2026-12-31",
            }
        ],
    },
}

valid = verifier.verification_for_evidence(base_evidence, trusted_bundle)
no_trust = verifier.verification_for_evidence(base_evidence, {"execution_context": {"as_of_date": "2026-06-18"}})
tampered = copy.deepcopy(base_evidence)
tampered["jurisdiction"] = "tampered-jurisdiction"
tampered_result = verifier.verification_for_evidence(tampered, trusted_bundle)
forged_status = copy.deepcopy(base_evidence)
forged_status.pop("external_attestation", None)
forged_result = verifier.verification_for_evidence(forged_status, trusted_bundle)
expired_bundle = copy.deepcopy(trusted_bundle)
expired_bundle["execution_context"]["as_of_date"] = "2027-01-02"
expired_result = verifier.verification_for_evidence(base_evidence, expired_bundle)
revoked_bundle = copy.deepcopy(trusted_bundle)
revoked_bundle["trusted_external_attestation_verifier"]["trust_store"][0]["revoked_at"] = "2026-06-17"
revoked_result = verifier.verification_for_evidence(base_evidence, revoked_bundle)
transparency_required_bundle = copy.deepcopy(trusted_bundle)
transparency_required_bundle["trusted_external_attestation_verifier"]["policy"]["require_transparency_log_entry"] = True
transparency_result = verifier.verification_for_evidence(base_evidence, transparency_required_bundle)
executor_valid_errors = executor.external_attestation_validation_errors(base_evidence, trusted_bundle, test_packet)
executor_forged_errors = executor.external_attestation_validation_errors(forged_status, trusted_bundle, test_packet)
executor_replay_errors = executor.external_attestation_validation_errors(base_evidence, trusted_bundle, replay_packet)

if valid.get("runtime_status") != RUNTIME_STATUS:
    errors.append("valid verifier packet has stale runtime status")
if valid.get("verifier_status") != verifier.STATUS_VERIFIED or valid.get("trusted_external_attestation") is not True:
    errors.append("valid signed evidence was not verified")
if valid.get("adapter_binding_hash") != executor.adapter_binding_hash(test_packet):
    errors.append("valid verifier packet does not bind adapter scope")
if not valid.get("trust_policy_hash"):
    errors.append("valid verifier packet missing trust policy hash")
if no_trust.get("verifier_status") != verifier.STATUS_NOT_CONFIGURED:
    errors.append("verifier must fail closed without a trust store")
if tampered_result.get("verifier_status") != verifier.STATUS_PAYLOAD_MISMATCH:
    errors.append("tampered evidence payload hash was not blocked")
if forged_result.get("verifier_status") != verifier.STATUS_MISSING_ATTESTATION:
    errors.append("producer-declared verified status without proof was not blocked")
if expired_result.get("verifier_status") != verifier.STATUS_EXPIRED:
    errors.append("expired trust/attestation window was not blocked")
if revoked_result.get("verifier_status") != verifier.STATUS_KEY_REVOKED:
    errors.append("revoked trust key was not blocked")
if transparency_result.get("verifier_status") != verifier.STATUS_TRANSPARENCY_REQUIRED:
    errors.append("missing transparency-log proof did not fail closed when policy required it")
if executor_valid_errors:
    errors.append(f"executor rejected a valid verifier packet: {executor_valid_errors}")
if not executor_forged_errors or "external_attestation_verifier_not_verified:missing_external_attestation" not in executor_forged_errors:
    errors.append("executor did not reject forged external-attestation status")
if not executor_replay_errors or "adapter_binding_hash_mismatch" not in executor_replay_errors:
    errors.append("executor did not reject signed evidence replayed into the wrong adapter binding")
if valid.get("evidence_payload_hash") == tampered_result.get("evidence_payload_hash"):
    errors.append("tamper probe did not alter the evidence payload hash")

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
expected = {
    "external_attestation_verifier_required": True,
    "external_attestation_verifier_runtime_status": RUNTIME_STATUS,
    "external_attestation_verifier_profile": PROFILE,
    "external_attestation_valid_signature_status": valid.get("verifier_status"),
    "external_attestation_adapter_binding_required": True,
    "external_attestation_adapter_binding_replay_blocked": "adapter_binding_hash_mismatch" in executor_replay_errors,
    "external_attestation_fail_closed_without_trust_store": no_trust.get("verifier_status") == verifier.STATUS_NOT_CONFIGURED,
    "external_attestation_tamper_blocked": tampered_result.get("verifier_status") == verifier.STATUS_PAYLOAD_MISMATCH,
    "external_attestation_forged_status_blocked": forged_result.get("verifier_status") == verifier.STATUS_MISSING_ATTESTATION,
    "external_attestation_expired_blocked": expired_result.get("verifier_status") == verifier.STATUS_EXPIRED,
    "external_attestation_revoked_key_blocked": revoked_result.get("verifier_status") == verifier.STATUS_KEY_REVOKED,
    "external_attestation_transparency_policy_fail_closed": transparency_result.get("verifier_status") == verifier.STATUS_TRANSPARENCY_REQUIRED,
}
for key, value in expected.items():
    if cube.get("audit_summary", {}).get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("external_attestation_verifier_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json external_attestation_verifier_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    lines = [
        f"External attestation verifier runtime status: {RUNTIME_STATUS}",
        f"Verifier profile: {PROFILE}",
        f"Valid signed evidence status: {valid.get('verifier_status')}",
        f"Adapter binding replay blocked: {'yes' if 'adapter_binding_hash_mismatch' in executor_replay_errors else 'no'}",
        f"No trust store status: {no_trust.get('verifier_status')}",
        f"Tampered payload status: {tampered_result.get('verifier_status')}",
        f"Forged status without proof: {forged_result.get('verifier_status')}",
        f"Expired attestation status: {expired_result.get('verifier_status')}",
        f"Revoked key status: {revoked_result.get('verifier_status')}",
        f"Transparency-required status: {transparency_result.get('verifier_status')}",
    ]
    for line in lines:
        if line not in report:
            errors.append(f"external attestation verifier report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("external attestation verifier audit ok")
