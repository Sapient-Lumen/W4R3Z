#!/usr/bin/env python3
"""tools/envelope_common.py

Shared helpers for EvidenceEnvelope digest computation.

Centralizing these rules reduces the risk of subtle drift across tools.

Normative reference: docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md

This module is stdlib-only and is NOT a production crypto library.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Tuple

from jcs import dumps as jcs_dumps, dump_bytes as jcs_bytes


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def payload_digest_for_json_value(value: Any) -> str:
    """Compute payload_digest for a JSON value using RFC8785-JCS."""
    return f"sha256:{sha256_hex(jcs_bytes(value))}"


def canonicalize_payload_bytes_for_digest(payload_bytes: bytes, media_type: str, canonicalization: str) -> Tuple[bytes, str]:
    """Return the bytes that MUST be hashed for payload_digest.

    Rules:
    - If canonicalization is RFC8785-JCS, verifiers SHOULD treat the payload as JSON and apply JCS.
      * If media_type is present and not JSON, verifiers treat this as a schema violation and hash raw bytes.
    - Otherwise: treat bytes as opaque.

    Returns: (bytes_to_hash, note)
    """
    if canonicalization == "RFC8785-JCS":
        # Best-effort JSON detection: allow missing media_type, but flag explicit non-JSON.
        if media_type and not media_type.startswith("application/json"):
            return payload_bytes, "raw_non_json_media_type"
        try:
            obj = json.loads(payload_bytes.decode("utf-8"))
            return jcs_dumps(obj).encode("utf-8"), "jcs"
        except Exception:
            return payload_bytes, "raw_json_parse_failed"
    return payload_bytes, "raw"


TBS_FIELDS = [
    "envelope_version",
    "kind",
    "track",
    "issued_at",
    "issuer",
    "subject",
    "payload_schema",
    "payload_digest",
    "canonicalization",
]


def build_tbs(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Build the to-be-signed object per docs/176."""
    t = {k: envelope[k] for k in TBS_FIELDS}
    if "attachments" in envelope:
        t["attachments"] = envelope["attachments"]
    return t


def tbs_digest_for_envelope(envelope: Dict[str, Any]) -> str:
    """Compute tbs_digest for an envelope (sha256 of JCS(TBS(envelope)))."""
    tbs = build_tbs(envelope)
    tbs_bytes = jcs_dumps(tbs).encode("utf-8")
    return f"sha256:{sha256_hex(tbs_bytes)}"
