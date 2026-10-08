#!/usr/bin/env python3
"""Fail-closed verifier for external evidence attestations.

The archive can exercise schemas with internal fixtures, but implementation-grade
adapter evidence needs a different boundary: a trusted issuer must sign the exact
evidence payload that the adapter consumed. This module is deliberately small and
offline. It verifies Ed25519 signatures over canonical JSON claims against a
bundle-supplied trust store; it does not fetch law, trust roots, transparency-log
entries, or revocation state by itself.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import pathlib
from typing import Any, Dict, Iterable, List, Mapping

RUNTIME_STATUS = "external_attestation_verifier_checked"
PROFILE = "ed25519_canonical_json_v1"
REQUIRED_SIGNED_PAYLOAD_FIELDS = [
    "attestation_profile",
    "evidence_payload_hash",
    "producer_id",
    "producer_contract_version",
    "evidence_kind",
    "evidence_origin",
    "created_at",
    "adapter_binding_hash",
]
EXCLUDED_EVIDENCE_KEYS = {
    "external_attestation",
    "external_attestation_verification",
}
STATUS_VERIFIED = "verified_external_attestation"
STATUS_NOT_CONFIGURED = "not_configured_fail_closed"
STATUS_NOT_REQUIRED = "not_required_for_fixture_or_non_external_evidence"
STATUS_MISSING_ATTESTATION = "missing_external_attestation"
STATUS_UNTRUSTED_KEY = "untrusted_attestation_key"
STATUS_BAD_SIGNATURE = "bad_attestation_signature"
STATUS_PAYLOAD_MISMATCH = "attestation_payload_mismatch"
STATUS_EXPIRED = "attestation_or_trust_entry_expired"
STATUS_DEPENDENCY_UNAVAILABLE = "cryptography_dependency_unavailable"
STATUS_UNSUPPORTED_PROFILE = "unsupported_attestation_profile"
STATUS_KEY_REVOKED = "attestation_key_revoked"
STATUS_TRANSPARENCY_REQUIRED = "attestation_transparency_log_missing_or_unverified"
STATUS_TRUST_POLICY_VIOLATION = "attestation_trust_policy_violation"
CONFIGURED_STATUS = "configured_trust_store_present"

try:  # pragma: no cover - exercised by runtime audit when dependency exists.
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except Exception:  # pragma: no cover - fail-closed fallback.
    InvalidSignature = Exception  # type: ignore[assignment]
    serialization = None  # type: ignore[assignment]
    Ed25519PublicKey = None  # type: ignore[assignment]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compact_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _b64decode(value: str) -> bytes:
    text = str(value).strip()
    padding = "=" * (-len(text) % 4)
    try:
        return base64.b64decode(text + padding, validate=True)
    except Exception:
        return base64.urlsafe_b64decode(text + padding)


def parse_date(value: Any) -> dt.date | None:
    if value in (None, "", [], {}):
        return None
    text = str(value)
    if "T" in text:
        text = text.split("T", 1)[0]
    try:
        return dt.date.fromisoformat(text[:10])
    except ValueError:
        return None


def bundle_as_of_date(bundle: Mapping[str, Any], evidence: Mapping[str, Any]) -> dt.date | None:
    context = bundle.get("execution_context", {}) if isinstance(bundle, Mapping) else {}
    if isinstance(context, Mapping):
        parsed = parse_date(context.get("as_of_date"))
        if parsed:
            return parsed
    return parse_date(bundle.get("as_of_date")) or parse_date(evidence.get("checked_at")) or parse_date(evidence.get("run_at")) or parse_date(evidence.get("created_at"))


def verifier_config(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(bundle, Mapping):
        return {}
    for key in [
        "trusted_external_attestation_verifier",
        "trusted_attestation_verifier_config",
        "external_attestation_verifier_config",
    ]:
        value = bundle.get(key)
        if isinstance(value, Mapping):
            return dict(value)
    context = bundle.get("execution_context", {})
    if isinstance(context, Mapping):
        value = context.get("trusted_external_attestation_verifier")
        if isinstance(value, Mapping):
            return dict(value)
    return {}


def trust_store_entries(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    config = verifier_config(bundle)
    raw = config.get("trust_store") or config.get("trusted_keys") or []
    if isinstance(raw, list):
        return [dict(x) for x in raw if isinstance(x, Mapping)]
    if isinstance(raw, Mapping):
        return [dict(x) for x in raw.values() if isinstance(x, Mapping)]
    return []


def verifier_policy(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    config = verifier_config(bundle)
    value = config.get("policy")
    return dict(value) if isinstance(value, Mapping) else {}


def trust_policy_hash(bundle: Mapping[str, Any]) -> str:
    """Hash the configured verification policy and trust anchors.

    This is not a public transparency log proof. It is a replay binding that
    makes key, policy, and trust-store drift visible to later promotion gates.
    """
    return compact_hash({
        "profile": PROFILE,
        "policy": verifier_policy(bundle),
        "trust_store": trust_store_entries(bundle),
    })


def configured_verifier_status(bundle: Mapping[str, Any]) -> str:
    if serialization is None or Ed25519PublicKey is None:
        return STATUS_DEPENDENCY_UNAVAILABLE
    config = verifier_config(bundle)
    profile = str(config.get("profile") or PROFILE)
    if profile != PROFILE:
        return STATUS_UNSUPPORTED_PROFILE
    return CONFIGURED_STATUS if trust_store_entries(bundle) else STATUS_NOT_CONFIGURED


def evidence_payload(evidence: Mapping[str, Any]) -> Dict[str, Any]:
    return {str(k): v for k, v in evidence.items() if str(k) not in EXCLUDED_EVIDENCE_KEYS}


def evidence_payload_hash(evidence: Mapping[str, Any]) -> str:
    return compact_hash(evidence_payload(evidence))


def attestation_for_evidence(evidence: Mapping[str, Any]) -> Dict[str, Any]:
    value = evidence.get("external_attestation") or evidence.get("attestation") or {}
    return dict(value) if isinstance(value, Mapping) else {}


def trust_entry_for_key(bundle: Mapping[str, Any], key_id: str) -> Dict[str, Any]:
    for entry in trust_store_entries(bundle):
        if str(entry.get("key_id") or "") == key_id:
            return entry
    return {}


def _list_allows(value: Iterable[Any] | None, candidate: Any) -> bool:
    values = [str(x) for x in (value or [])]
    return not values or str(candidate) in values or "*" in values


def _date_in_range(target: dt.date | None, not_before: Any, not_after: Any) -> bool:
    if target is None:
        return True
    start = parse_date(not_before)
    end = parse_date(not_after)
    if start and target < start:
        return False
    if end and target > end:
        return False
    return True


def _load_public_key(entry: Mapping[str, Any]) -> Any:
    if serialization is None or Ed25519PublicKey is None:
        return None
    pem = entry.get("public_key_pem") or entry.get("public_key")
    if pem:
        return serialization.load_pem_public_key(str(pem).encode("utf-8"))
    raw = entry.get("public_key_base64") or entry.get("public_key_multibase")
    if raw:
        raw_text = str(raw)
        if raw_text.startswith("z"):
            raise ValueError("multibase base58 keys are not supported by this offline verifier")
        return Ed25519PublicKey.from_public_bytes(_b64decode(raw_text))
    return None


def _base_result(
    status: str,
    errors: List[str],
    evidence: Mapping[str, Any],
    attestation: Mapping[str, Any] | None = None,
    signed_payload: Mapping[str, Any] | None = None,
    key_id: str | None = None,
    bundle: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "runtime_status": RUNTIME_STATUS,
        "verifier_profile": PROFILE,
        "verifier_status": status,
        "trusted_external_attestation": status == STATUS_VERIFIED,
        "errors": errors,
        "key_id": key_id,
        "evidence_payload_hash": evidence_payload_hash(evidence),
        "adapter_binding_hash": evidence.get("adapter_binding_hash"),
        "attestation_hash": compact_hash(attestation) if attestation else None,
        "signed_payload_hash": compact_hash(signed_payload) if signed_payload else None,
        "trust_policy_hash": trust_policy_hash(bundle) if bundle is not None else None,
    }


def verification_for_evidence(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> Dict[str, Any]:
    """Verify the external attestation on one evidence record.

    Returns a compact, non-throwing packet. Any verification problem is a
    non-verified status, so callers can block finalization without guessing.
    """
    if configured_verifier_status(bundle) != CONFIGURED_STATUS:
        status = configured_verifier_status(bundle)
        return _base_result(status, [status], evidence, bundle=bundle)

    attestation = attestation_for_evidence(evidence)
    if not attestation:
        return _base_result(STATUS_MISSING_ATTESTATION, [STATUS_MISSING_ATTESTATION], evidence, bundle=bundle)

    profile = str(attestation.get("profile") or attestation.get("type") or "")
    key_id = str(attestation.get("key_id") or "")
    signed_payload = attestation.get("signed_payload")
    signature = attestation.get("signature")
    errors: List[str] = []
    if profile != PROFILE:
        errors.append(STATUS_UNSUPPORTED_PROFILE)
    if not key_id:
        errors.append("missing_key_id")
    if not isinstance(signed_payload, Mapping):
        errors.append("missing_signed_payload")
        signed_payload = {}
    if not signature:
        errors.append("missing_signature")
    signed_payload = dict(signed_payload or {})
    for field in REQUIRED_SIGNED_PAYLOAD_FIELDS:
        if signed_payload.get(field) in (None, "", [], {}):
            errors.append(f"missing_signed_payload_field:{field}")
    if signed_payload.get("attestation_profile") != PROFILE:
        errors.append("signed_payload_profile_mismatch")
    if signed_payload.get("evidence_payload_hash") != evidence_payload_hash(evidence):
        errors.append("evidence_payload_hash_mismatch")
    for field in ["producer_id", "producer_contract_version", "evidence_kind", "evidence_origin", "created_at", "adapter_binding_hash"]:
        if str(signed_payload.get(field) or "") != str(evidence.get(field) or ""):
            errors.append(f"signed_payload_{field}_mismatch")

    entry = trust_entry_for_key(bundle, key_id)
    if not entry:
        errors.append(STATUS_UNTRUSTED_KEY)
    else:
        if not _list_allows(entry.get("allowed_producer_ids"), evidence.get("producer_id")):
            errors.append("trusted_key_not_allowed_for_producer")
        if not _list_allows(entry.get("allowed_evidence_kinds"), evidence.get("evidence_kind")):
            errors.append("trusted_key_not_allowed_for_evidence_kind")
        as_of = bundle_as_of_date(bundle, evidence)
        if not _date_in_range(as_of, entry.get("not_before"), entry.get("not_after")):
            errors.append(STATUS_EXPIRED)
        if signed_payload.get("not_after") and as_of and parse_date(signed_payload.get("not_after")) and as_of > parse_date(signed_payload.get("not_after")):
            errors.append(STATUS_EXPIRED)
        if signed_payload.get("not_before") and as_of and parse_date(signed_payload.get("not_before")) and as_of < parse_date(signed_payload.get("not_before")):
            errors.append(STATUS_EXPIRED)
        if entry.get("revoked") is True or str(entry.get("status") or "active") == "revoked":
            errors.append(STATUS_KEY_REVOKED)
        revoked_at = parse_date(entry.get("revoked_at"))
        if revoked_at and (as_of is None or as_of >= revoked_at):
            errors.append(STATUS_KEY_REVOKED)
        if not _list_allows(entry.get("allowed_adapter_binding_hashes"), evidence.get("adapter_binding_hash")):
            errors.append("trusted_key_not_allowed_for_adapter_binding_hash")

    policy = verifier_policy(bundle)
    if policy.get("require_transparency_log_entry") is True:
        tlog = attestation.get("transparency_log") if isinstance(attestation, Mapping) else None
        required_tlog_fields = ["log_id", "entry_hash", "integrated_time", "checkpoint_hash"]
        if not isinstance(tlog, Mapping) or any(tlog.get(field) in (None, "", [], {}) for field in required_tlog_fields):
            errors.append(STATUS_TRANSPARENCY_REQUIRED)
    if policy.get("require_active_key_status", True) is True and entry and str(entry.get("status") or "active") not in {"active"}:
        errors.append(STATUS_TRUST_POLICY_VIOLATION)

    if not errors:
        try:
            public_key = _load_public_key(entry)
            if public_key is None:
                errors.append("trusted_key_material_missing")
            else:
                public_key.verify(_b64decode(str(signature)), canonical_bytes(signed_payload))
        except InvalidSignature:
            errors.append(STATUS_BAD_SIGNATURE)
        except Exception as exc:
            errors.append(f"signature_verification_error:{exc.__class__.__name__}")

    if errors:
        if STATUS_KEY_REVOKED in errors:
            status = STATUS_KEY_REVOKED
        elif STATUS_EXPIRED in errors:
            status = STATUS_EXPIRED
        elif STATUS_UNTRUSTED_KEY in errors:
            status = STATUS_UNTRUSTED_KEY
        elif STATUS_TRANSPARENCY_REQUIRED in errors:
            status = STATUS_TRANSPARENCY_REQUIRED
        elif STATUS_TRUST_POLICY_VIOLATION in errors:
            status = STATUS_TRUST_POLICY_VIOLATION
        elif STATUS_BAD_SIGNATURE in errors or any(e.startswith("signature_verification_error") for e in errors):
            status = STATUS_BAD_SIGNATURE
        elif STATUS_UNSUPPORTED_PROFILE in errors:
            status = STATUS_UNSUPPORTED_PROFILE
        elif any("mismatch" in e for e in errors):
            status = STATUS_PAYLOAD_MISMATCH
        else:
            status = STATUS_MISSING_ATTESTATION
        return _base_result(status, sorted(set(errors)), evidence, attestation, signed_payload, key_id, bundle=bundle)

    return _base_result(STATUS_VERIFIED, [], evidence, attestation, signed_payload, key_id, bundle=bundle)


def signed_payload_for_evidence(evidence: Mapping[str, Any], not_after: str | None = None, not_before: str | None = None) -> Dict[str, Any]:
    """Build the canonical claim a trusted external producer signs.

    This helper is used by the audit harness and by real producers that want a
    deterministic signing target; it does not sign anything by itself.
    """
    payload: Dict[str, Any] = {
        "attestation_profile": PROFILE,
        "evidence_payload_hash": evidence_payload_hash(evidence),
        "producer_id": evidence.get("producer_id"),
        "producer_contract_version": evidence.get("producer_contract_version"),
        "evidence_kind": evidence.get("evidence_kind"),
        "evidence_origin": evidence.get("evidence_origin"),
        "created_at": evidence.get("created_at"),
        "adapter_binding_hash": evidence.get("adapter_binding_hash"),
    }
    if not_before:
        payload["not_before"] = not_before
    if not_after:
        payload["not_after"] = not_after
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify one external evidence attestation against a bundle trust store.")
    parser.add_argument("--evidence", required=True, help="Evidence JSON file")
    parser.add_argument("--bundle", required=True, help="Evidence bundle / verifier-config JSON file")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()
    evidence = json.loads(pathlib.Path(args.evidence).read_text(encoding="utf-8"))
    bundle = json.loads(pathlib.Path(args.bundle).read_text(encoding="utf-8"))
    packet = verification_for_evidence(evidence, bundle)
    print(json.dumps(packet, separators=(",", ":") if args.json else (", ", ": ")))


if __name__ == "__main__":
    main()
