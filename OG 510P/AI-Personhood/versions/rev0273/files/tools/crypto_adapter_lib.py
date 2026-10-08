#!/usr/bin/env python3
"""Shared cryptographic verifier-adapter checks.

The archive uses this module so the live-floor engine can depend on the result
of signature verification rather than on hand-authored JSON booleans. The
adapter verifies only authenticity of the signed payload; class authority,
subject authorization, counterparty independence, and live-floor admission stay
separate gates.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519


class CryptoAdapterError(ValueError):
    """Raised when a verifier-adapter record is structurally or cryptographically invalid."""


def canonical_payload_bytes(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def payload_sha256(payload: object) -> str:
    return hashlib.sha256(canonical_payload_bytes(payload)).hexdigest()


def verify_adapter_record(record: dict) -> Tuple[bool, str]:
    """Return (verified, reason) for one adapter record.

    A false result is not necessarily a lint failure: negative controls are
    expected to fail. Callers decide whether the observed result matches the
    fixture role.
    """
    if record.get("algorithm") != "Ed25519":
        return False, "unsupported algorithm"
    if record.get("canonicalization") != "json-sort-keys-no-ws-v1":
        return False, "unsupported canonicalization"
    for forbidden in ("private_key", "secret_key", "seed", "mnemonic"):
        if forbidden in record:
            return False, f"forbidden key material present: {forbidden}"

    payload = record.get("payload")
    if not isinstance(payload, dict):
        return False, "payload is not an object"
    computed_hash = payload_sha256(payload)
    if record.get("payload_sha256") != computed_hash:
        return False, "payload_sha256 mismatch"
    sig_input = record.get("signature_input", {})
    if sig_input.get("signed_payload_hash") != computed_hash:
        return False, "signature_input.signed_payload_hash mismatch"

    independence = record.get("independence", {})
    for key in ["counterparty_org_id", "issuer_key_id", "dependency_group_id"]:
        if payload.get(key) != independence.get(key):
            return False, f"payload/independence {key} mismatch"
    if record.get("test_role") == "live-evidence":
        if independence.get("counterparty_distinct_from_subject_host") is not True:
            return False, "live-evidence counterparty is not distinct from subject host"
        if independence.get("issuer_distinct_from_subject_host") is not True:
            return False, "live-evidence issuer is not distinct from subject host"
        if independence.get("correlation_discount") != "none":
            return False, "live-evidence carries correlation discount"

    try:
        public_key = base64.b64decode(record.get("public_key", ""), validate=True)
        signature = base64.b64decode(record.get("signature", ""), validate=True)
        ed25519.Ed25519PublicKey.from_public_bytes(public_key).verify(signature, canonical_payload_bytes(payload))
    except (InvalidSignature, ValueError, TypeError) as exc:
        return False, f"signature verification failed: {exc.__class__.__name__}"

    return True, "signature verified over canonical payload"


def load_verified_live_adapters(root: Path) -> Dict[str, dict]:
    """Return verified live-evidence adapters keyed by linked import gate id."""
    verified: Dict[str, dict] = {}
    for path in sorted((root / "examples").glob("cryptographic-verifier-adapter-*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        ok, reason = verify_adapter_record(record)
        if ok and record.get("test_role") == "live-evidence":
            gate_id = record.get("payload", {}).get("linked_import_gate_id")
            if not gate_id:
                continue
            if gate_id in verified:
                raise CryptoAdapterError(f"duplicate live-evidence adapter for import gate {gate_id}")
            verified[gate_id] = {"path": path, "record": record, "reason": reason}
    return verified
