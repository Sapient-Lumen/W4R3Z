#!/usr/bin/env python3
"""tools/observer_verify_packet.py

Offline integrity checks for an evidence packet directory.

Checks:
- content-addressed objects: sha256 matches filename (sha256-<hex>.*)
- envelopes: payload_digest and tbs_digest recompute cleanly (docs/176)
- payload pointers: referenced object exists, hash/size match pointer
- attachments: referenced objects exist and hash/size match; optional receipt profile validation
- manifest: referenced digests/urls exist and hash/size match (best effort)

Default reports are hash-only and explicitly emit authentication_status=HASH_ONLY_NOT_AUTHENTICATED.
Optional Ed25519 authentication can be enabled with --trust-keyset (alias: --auth-keyring); that bounded profile verifies EvidenceEnvelope signatures over RFC8785-JCS TBS bytes. The profile can also require a local trust-keyset byte pin, an external trust-keyset publication receipt, and an external synthetic governance bundle that binds the keyset/receipt to ceremony + lifecycle evidence, plus an external governance-bundle publication receipt. When a strict verification-policy lockfile is used, the verifier can also require an external publication receipt for the policy lockfile itself. It still does not prove legal authority, live-pilot authorization, live online revocation status, or production key ceremony sufficiency.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import csv
import json
import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jcs import dump_bytes as jcs_bytes

from envelope_common import (
    canonicalize_payload_bytes_for_digest,
    payload_digest_for_json_value,
    sha256_hex,
    tbs_bytes_for_envelope,
    tbs_digest_for_envelope,
)

from path_safety import safe_join

from verifier_problem_codes import code_of, is_known, severity as severity_for_code, all_codes_sorted, CODES

try:
    # Optional authenticated profile (docs/841). The default verifier path remains hash-only.
    from cryptography.exceptions import InvalidSignature  # type: ignore
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # type: ignore

    CRYPTOGRAPHY_AVAILABLE = True
except Exception:  # pragma: no cover - dependency-light environments exercise fail-closed behavior
    InvalidSignature = Exception  # type: ignore
    Ed25519PublicKey = None  # type: ignore
    CRYPTOGRAPHY_AVAILABLE = False

try:
    # Optional publishable artifact lint integration (docs/173).
    from tools.public_artifact_lint import lint_packet as lint_public_packet
except Exception:
    try:
        from public_artifact_lint import lint_packet as lint_public_packet
    except Exception:
        lint_public_packet = None  # type: ignore

try:
    from tools.publication_policy import DEFAULT_MAX_STRING as PUBLIC_LINT_DEFAULT_MAX_STRING
except Exception:
    try:
        from publication_policy import DEFAULT_MAX_STRING as PUBLIC_LINT_DEFAULT_MAX_STRING
    except Exception:
        PUBLIC_LINT_DEFAULT_MAX_STRING = 8192

try:
    # Optional public fingerprint integration (docs/226).
    from tools.public_fingerprint_report import (
        compute_public_fingerprint as compute_public_fingerprint,
        MAX_INCLUDE_BYTES_DEFAULT as PUBLIC_FP_DEFAULT_MAX_BYTES,
        REPORT_FORMAT_VERSION as PUBLIC_FP_REPORT_FORMAT_VERSION,
        ROOT_TEXT_NAMES as PUBLIC_FP_ROOT_TEXT_NAMES,
        ROOT_JSON_NAMES as PUBLIC_FP_ROOT_JSON_NAMES,
        EXCLUDE_ROOT_NAMES as PUBLIC_FP_EXCLUDE_ROOT_NAMES,
    )
except Exception:
    try:
        from public_fingerprint_report import (
            compute_public_fingerprint as compute_public_fingerprint,
            MAX_INCLUDE_BYTES_DEFAULT as PUBLIC_FP_DEFAULT_MAX_BYTES,
            REPORT_FORMAT_VERSION as PUBLIC_FP_REPORT_FORMAT_VERSION,
            ROOT_TEXT_NAMES as PUBLIC_FP_ROOT_TEXT_NAMES,
            ROOT_JSON_NAMES as PUBLIC_FP_ROOT_JSON_NAMES,
            EXCLUDE_ROOT_NAMES as PUBLIC_FP_EXCLUDE_ROOT_NAMES,
        )
    except Exception:
        compute_public_fingerprint = None  # type: ignore
        PUBLIC_FP_DEFAULT_MAX_BYTES = 512 * 1024
        PUBLIC_FP_REPORT_FORMAT_VERSION = "unknown"
        PUBLIC_FP_ROOT_TEXT_NAMES = set()  # type: ignore
        PUBLIC_FP_ROOT_JSON_NAMES = set()  # type: ignore
        PUBLIC_FP_EXCLUDE_ROOT_NAMES = set()  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PROFILE_REGISTRY = ROOT / "artifacts" / "registries" / "receipt-profiles.csv"
KIND_REGISTRY = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
ATTACHMENT_REQUIREMENTS = ROOT / "artifacts" / "registries" / "envelope-attachment-requirements.csv"
VERIFIER_PROBLEM_CODES_REGISTRY = ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv"
VERIFIER_PROFILES_REGISTRY = ROOT / "artifacts" / "registries" / "verifier-profiles.csv"
ARCHIVE_VERSION_FILE = ROOT / "VERSION"

SUPPORTED_ENVELOPE_MAJORS = {1}
REPORT_VERSION = "1.26.0"  # schemas/PacketVerificationReport.json


def iso_utc_now_seconds() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def normalize_sha256_pin(value: str) -> str | None:
    """Normalize a caller-supplied sha256 pin to lowercase hex without prefix."""

    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    if v.startswith("sha256:"):
        v = v.split(":", 1)[1]
    if re.fullmatch(r"[0-9a-f]{64}", v):
        return v
    return None


def load_archive_version() -> str:
    try:
        return ARCHIVE_VERSION_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return "unknown"


def load_kind_registry() -> dict[str, dict[str, str]]:
    """Load artifacts/registries/envelope-kinds.csv into a kind->row map."""
    if not KIND_REGISTRY.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with KIND_REGISTRY.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            k = (row.get("kind") or "").strip()
            if k:
                out[k] = {kk: (row.get(kk) or "").strip() for kk in (r.fieldnames or [])}
    return out


def load_attachment_requirements() -> dict[str, list[dict[str, str]]]:
    """Load required attachment rels per kind (yes-only)."""
    if not ATTACHMENT_REQUIREMENTS.exists():
        return {}
    out: dict[str, list[dict[str, str]]] = {}
    with ATTACHMENT_REQUIREMENTS.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            kind = (row.get("kind") or "").strip()
            if not kind:
                continue
            if (row.get("required") or "").strip().lower() != "yes":
                continue
            out.setdefault(kind, []).append(
                {
                    "rel": (row.get("rel") or "").strip(),
                    "media_type": (row.get("media_type") or "").strip(),
                    "attachment_schema": (row.get("attachment_schema") or "").strip(),
                }
            )
    return out


def load_receipt_profiles() -> set[str]:
    if not RECEIPT_PROFILE_REGISTRY.exists():
        return set()
    profiles = set()
    try:
        with RECEIPT_PROFILE_REGISTRY.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                p = row.get("profile")
                if p:
                    profiles.add(p)
    except Exception:
        return set()
    return profiles


RECEIPT_PROFILES = load_receipt_profiles()
KIND_ROWS = load_kind_registry()
ATT_REQS = load_attachment_requirements()
ARCHIVE_VERSION = load_archive_version()


def parse_semver_major(v: str) -> int | None:
    try:
        parts = v.split(".")
        if len(parts) != 3:
            return None
        return int(parts[0])
    except Exception:
        return None




def _path_inside_dir(candidate: Path, parent: Path) -> bool:
    """Return True if candidate is packet-contained by lexical or resolved route.

    Trust roots must be supplied from outside the packet they authenticate.  Check both
    the lexical path (to catch packet-local symlink routes) and the resolved path (to
    catch outside symlinks that point back into the packet).
    """

    def norm_abs(x: Path) -> Path:
        raw = x if x.is_absolute() else (Path.cwd() / x)
        return Path(os.path.abspath(os.fspath(raw)))

    def is_child(child: Path, root: Path) -> bool:
        try:
            child.relative_to(root)
            return True
        except ValueError:
            return False

    parent_lex = norm_abs(parent)
    cand_lex = norm_abs(candidate)
    if is_child(cand_lex, parent_lex):
        return True

    try:
        parent_res = parent_lex.resolve(strict=False)
        cand_res = cand_lex.resolve(strict=False)
    except Exception:
        return False
    return is_child(cand_res, parent_res)

AUTH_ALG_ED25519_JCS_TBS_V1 = "Ed25519-JCS-TBS-v1"
SUPPORTED_AUTH_ALGS = {AUTH_ALG_ED25519_JCS_TBS_V1, "Ed25519", "ed25519", "ed25519-jcs-tbs-v1"}
TRUST_KEYSET_RECEIPT_PROFILE = "tes.trust_keyset_publication_receipt.v1"
DEFAULT_REQUIRED_GOVERNANCE_EVENTS = ["key_ceremony", "publication", "rotation_or_revocation_drill"]
TRUST_GOVERNANCE_BUNDLE_PROFILE = "tes.trust_key_governance_bundle.v1"
TRUST_GOVERNANCE_BUNDLE_RECEIPT_PROFILE = "tes.trust_governance_bundle_publication_receipt.v1"
TRUST_STATUS_SNAPSHOT_PROFILE = "tes.trust_status_snapshot.v1"
TRUST_STATUS_SNAPSHOT_RECEIPT_PROFILE = "tes.trust_status_snapshot_publication_receipt.v1"
SIGNER_AUTHORIZATION_ROSTER_PROFILE = "tes.signer_authorization_roster.v1"
SIGNER_AUTHORIZATION_ROSTER_RECEIPT_PROFILE = "tes.signer_authorization_roster_publication_receipt.v1"
VERIFICATION_POLICY_LOCKFILE_PROFILE = "tes.verification_policy_lockfile.v1"
VERIFICATION_POLICY_LOCKFILE_RECEIPT_PROFILE = "tes.verification_policy_lockfile_publication_receipt.v1"
STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE = "strict-local-trust-chain-v1"
STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE = "strict-local-authorized-trust-chain-v1"
DEFAULT_AUTH_PROFILE = "bounded-ed25519-jcs-tbs-v1"
MAX_STRICT_POLICY_VALIDITY_WINDOW_SECONDS = 14 * 24 * 60 * 60


def _parse_rfc3339_utc(value: str) -> datetime | None:
    """Parse a bounded RFC3339 timestamp for key-validity checks."""

    if not isinstance(value, str) or not value.strip():
        return None
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)




def _first_nonempty_channel_digest(ch: dict[str, Any], names: tuple[str, ...]) -> str:
    """Return a channel-level digest string without falling back to top-level receipt fields.

    Publication receipts are only meaningful as independent-channel evidence when each
    channel states the digest it observed.  Falling back to the receipt-level digest
    would let a channel entry look bound without carrying its own observation.
    """

    for name in names:
        v = ch.get(name)
        if isinstance(v, str) and v.strip():
            return v.strip().lower()
    return ""

def _decode_multibase_bytes(value: str, encoding: str) -> bytes | None:
    """Decode base64/base64url/hex with strict-ish padding handling."""

    if not isinstance(value, str):
        return None
    raw = value.strip()
    enc = (encoding or "base64").strip().lower()
    try:
        if enc == "hex":
            return bytes.fromhex(raw)
        if enc == "base64url":
            pad = "=" * (-len(raw) % 4)
            return base64.urlsafe_b64decode((raw + pad).encode("ascii"))
        if enc == "base64":
            return base64.b64decode(raw.encode("ascii"), validate=True)
    except (ValueError, binascii.Error, UnicodeEncodeError):
        return None
    return None


def _keyring_bytes_and_obj(keyring_path: Path) -> tuple[bytes | None, dict[str, Any] | None, list[str]]:
    try:
        b = keyring_path.read_bytes()
    except Exception as e:
        return None, None, [f"signature_trust_keyset_invalid:read_failed:{type(e).__name__}"]
    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        return b, None, [f"signature_trust_keyset_invalid:json_parse_failed:{type(e).__name__}"]
    if not isinstance(obj, dict):
        return b, None, ["signature_trust_keyset_invalid:not_object"]
    return b, obj, []


def _normalized_key_rows(keyring: dict[str, Any]) -> tuple[list[dict[str, Any]], int, list[str]]:
    raw_keys = keyring.get("keys")
    if not isinstance(raw_keys, list):
        return [], 0, ["signature_trust_keyset_invalid:missing_keys_array"]
    out: list[dict[str, Any]] = []
    problems: list[str] = []
    for i, k in enumerate(raw_keys):
        if not isinstance(k, dict):
            problems.append(f"signature_trust_keyset_invalid:key_not_object:{i}")
            continue
        kid = str(k.get("kid") or "").strip()
        signer_id = str(k.get("signer_id") or "").strip()
        alg = str(k.get("alg") or AUTH_ALG_ED25519_JCS_TBS_V1).strip()
        public_key = str(k.get("public_key") or k.get("public_key_ed25519") or "").strip()
        encoding = str(k.get("encoding") or k.get("public_key_encoding") or "base64").strip()
        if not kid and not signer_id:
            problems.append(f"signature_trust_keyset_invalid:key_missing_kid_and_signer:{i}")
            continue
        if alg not in SUPPORTED_AUTH_ALGS:
            problems.append(f"signature_alg_unsupported:keyring:{kid or signer_id}:{alg or 'missing'}")
            continue
        pk_bytes = _decode_multibase_bytes(public_key, encoding)
        if pk_bytes is None or len(pk_bytes) != 32:
            problems.append(f"signature_trust_keyset_invalid:public_key_decode:{kid or signer_id}")
            continue
        row = dict(k)
        row["kid"] = kid
        row["signer_id"] = signer_id
        row["alg"] = AUTH_ALG_ED25519_JCS_TBS_V1
        row["_public_key_bytes"] = pk_bytes
        out.append(row)
    return out, len(raw_keys), problems


def _signature_candidates(sig: dict[str, Any], keys: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kid = str(sig.get("kid") or "").strip()
    signer_id = str(sig.get("signer_id") or "").strip()
    if kid:
        return [k for k in keys if str(k.get("kid") or "").strip() == kid]
    if signer_id:
        return [k for k in keys if str(k.get("signer_id") or "").strip() == signer_id]
    return []


def _key_allowed_for_envelope(key: dict[str, Any], env: dict[str, Any], env_name: str) -> list[str]:
    problems: list[str] = []
    status = str(key.get("status") or "active").strip().lower()
    kid = str(key.get("kid") or key.get("signer_id") or "unknown")
    if status == "revoked":
        problems.append(f"signature_key_revoked:{env_name}:{kid}")
    elif status not in {"active", "valid", "retired"}:
        problems.append(f"signature_key_not_active:{env_name}:{kid}:{status or 'missing'}")

    issued_at = _parse_rfc3339_utc(str(env.get("issued_at") or ""))
    nb_raw = str(key.get("valid_from") or key.get("not_before") or "").strip()
    na_raw = str(key.get("valid_to") or key.get("not_after") or "").strip()
    retired_raw = str(key.get("retired_at") or "").strip()
    if issued_at is not None:
        nb = _parse_rfc3339_utc(nb_raw) if nb_raw else None
        na = _parse_rfc3339_utc(na_raw) if na_raw else None
        retired_at = _parse_rfc3339_utc(retired_raw) if retired_raw else None
        if nb_raw and nb is None:
            problems.append(f"signature_issued_at_invalid:{env_name}:{kid}:valid_from_unparseable")
        if na_raw and na is None:
            problems.append(f"signature_issued_at_invalid:{env_name}:{kid}:valid_to_unparseable")
        if retired_raw and retired_at is None:
            problems.append(f"signature_issued_at_invalid:{env_name}:{kid}:retired_at_unparseable")
        if nb is not None and issued_at < nb:
            problems.append(f"signature_key_not_yet_valid:{env_name}:{kid}")
        if na is not None and issued_at > na:
            problems.append(f"signature_key_expired:{env_name}:{kid}")
        if status == "retired" and retired_at is not None and issued_at > retired_at:
            problems.append(f"signature_key_expired:{env_name}:{kid}:retired_at")
        if status == "retired" and retired_at is None and na is None:
            problems.append(f"signature_issued_at_invalid:{env_name}:{kid}:retired_without_retired_at_or_valid_to")
    elif nb_raw or na_raw or retired_raw or status == "retired":
        problems.append(f"signature_issued_at_invalid:{env_name}:{kid}:issued_at_missing_or_unparseable")

    allowed_raw = key.get("allowed_kinds", key.get("trust_scope"))
    if allowed_raw is not None:
        if isinstance(allowed_raw, str):
            allowed = {x.strip() for x in allowed_raw.replace(",", ";").split(";") if x.strip()}
        elif isinstance(allowed_raw, list):
            allowed = {str(x).strip() for x in allowed_raw if str(x).strip()}
        else:
            allowed = set()
        kind = str(env.get("kind") or "").strip()
        if allowed and "*" not in allowed and kind not in allowed:
            problems.append(f"signature_kind_not_allowed:{env_name}:{kid}:{kind or 'missing_kind'}")
    return problems


def _verify_one_signature(sig: dict[str, Any], key: dict[str, Any], env: dict[str, Any]) -> bool:
    if Ed25519PublicKey is None:
        return False
    enc = str(sig.get("sig_encoding") or "base64").strip().lower()
    sig_bytes = _decode_multibase_bytes(str(sig.get("sig") or ""), enc)
    if sig_bytes is None or len(sig_bytes) != 64:
        return False
    pk = Ed25519PublicKey.from_public_bytes(key["_public_key_bytes"])
    msg = tbs_bytes_for_envelope(env)
    pk.verify(sig_bytes, msg)
    return True



def _trust_keyset_signature_policy(keyring: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Return bounded signature-threshold policy from the trust keyset.

    Default threshold remains 1 for compatibility.  A keyset may raise the
    threshold using signature_policy.minimum_distinct_valid_signatures_per_envelope.
    The verifier counts distinct key material, so repeated signatures from the same
    key or duplicate key records cannot create a fake quorum.
    """

    problems: list[str] = []
    raw = keyring.get("signature_policy") or keyring.get("policy") or {}
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        problems.append("signature_trust_keyset_invalid:signature_policy_not_object")
        raw = {}

    threshold = raw.get("minimum_distinct_valid_signatures_per_envelope")
    if threshold is None:
        threshold = raw.get("minimum_valid_signatures_per_envelope", 1)
    try:
        threshold_int = int(threshold)
    except Exception:
        problems.append("signature_trust_keyset_invalid:signature_threshold_unparseable")
        threshold_int = 1
    if threshold_int < 1:
        problems.append("signature_trust_keyset_invalid:signature_threshold_lt_1")
        threshold_int = 1
    if threshold_int > 50:
        problems.append("signature_trust_keyset_invalid:signature_threshold_gt_50")
        threshold_int = 50

    return {
        "minimum_valid_signatures_per_envelope": int(threshold_int),
        "minimum_distinct_valid_signatures_per_envelope": int(threshold_int),
        "require_distinct_key_material": bool(raw.get("require_distinct_key_material", True)),
        "require_distinct_kids": bool(raw.get("require_distinct_kids", True)),
        "require_all_envelopes_authenticated": bool(raw.get("require_all_envelopes_authenticated", True)),
    }, problems


def validate_trust_keyset_publication_receipt(
    packet_dir: Path,
    receipt_path: Path | None,
    expected_keyset_sha256: str,
    require_receipt: bool,
    expected_receipt_sha256: str | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate an optional external publication receipt for the trust-keyset digest.

    The receipt is intentionally modest. It proves only that the verifier was given
    a separate JSON object, outside the packet boundary, whose bytes bind the trust
    keyset digest to named publication channels. It does not fetch those channels,
    prove real-world office authority, or check online revocation freshness.
    """

    summary: dict[str, Any] = {
        "trust_keyset_receipt_required": bool(require_receipt),
        "trust_keyset_receipt_status": "not_supplied",
        "trust_keyset_receipt_sha256": "",
        "trust_keyset_receipt_pin_required": bool((expected_receipt_sha256 or "").strip()),
        "trust_keyset_receipt_pin_status": "not_supplied",
        "trust_keyset_receipt_pin_sha256": "",
        "trust_keyset_receipt_id": "",
        "trust_keyset_receipt_profile": "",
        "trust_keyset_receipt_channel_count": 0,
        "trust_keyset_receipt_independent_channel_count": 0,
        "trust_keyset_receipt_required_independent_channels": 0,
    }
    problems: list[str] = []

    expected_receipt_pin_hex: str | None = None
    if (expected_receipt_sha256 or "").strip():
        expected_receipt_pin_hex = normalize_sha256_pin(str(expected_receipt_sha256))
        if expected_receipt_pin_hex is None:
            summary["trust_keyset_receipt_pin_status"] = "invalid"
            summary["trust_keyset_receipt_status"] = "invalid"
            problems.append("signature_trust_keyset_receipt_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["trust_keyset_receipt_pin_sha256"] = "sha256:" + expected_receipt_pin_hex

    if receipt_path is None or not str(receipt_path).strip():
        if require_receipt:
            summary["trust_keyset_receipt_status"] = "missing"
            problems.append("signature_trust_keyset_receipt_invalid:required_receipt_not_supplied")
        return problems, summary

    if _path_inside_dir(receipt_path, packet_dir):
        summary["trust_keyset_receipt_status"] = "packet_contained_rejected"
        problems.append("signature_trust_keyset_receipt_untrusted_location:packet_contained")
        return problems, summary

    try:
        b = receipt_path.read_bytes()
    except Exception as e:
        summary["trust_keyset_receipt_status"] = "invalid"
        problems.append(f"signature_trust_keyset_receipt_invalid:read_failed:{type(e).__name__}")
        return problems, summary

    actual_receipt_hex = sha256_hex_bytes(b)
    summary["trust_keyset_receipt_sha256"] = "sha256:" + actual_receipt_hex
    if expected_receipt_pin_hex is not None:
        if actual_receipt_hex.lower() != expected_receipt_pin_hex.lower():
            summary["trust_keyset_receipt_pin_status"] = "mismatched"
            summary["trust_keyset_receipt_status"] = "mismatched"
            problems.append(
                f"signature_trust_keyset_receipt_pin_mismatch:expected=sha256:{expected_receipt_pin_hex}:got=sha256:{actual_receipt_hex}"
            )
            return problems, summary
        summary["trust_keyset_receipt_pin_status"] = "matched"
    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["trust_keyset_receipt_status"] = "invalid"
        problems.append(f"signature_trust_keyset_receipt_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary
    if not isinstance(obj, dict):
        summary["trust_keyset_receipt_status"] = "invalid"
        problems.append("signature_trust_keyset_receipt_invalid:not_object")
        return problems, summary

    summary["trust_keyset_receipt_id"] = str(obj.get("receipt_id") or "")[:200]
    profile = str(obj.get("profile") or obj.get("receipt_profile") or "").strip()
    summary["trust_keyset_receipt_profile"] = profile
    if not profile:
        problems.append("signature_trust_keyset_receipt_invalid:missing_profile")
    elif profile != TRUST_KEYSET_RECEIPT_PROFILE:
        problems.append(f"signature_trust_keyset_receipt_invalid:unsupported_profile:{profile}")

    got_digest = str(obj.get("trust_keyset_sha256") or obj.get("keyset_sha256") or "").strip().lower()
    want_digest = str(expected_keyset_sha256 or "").strip().lower()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_digest):
        problems.append("signature_trust_keyset_receipt_invalid:missing_or_bad_trust_keyset_sha256")
    elif got_digest != want_digest:
        summary["trust_keyset_receipt_status"] = "mismatched"
        problems.append(f"signature_trust_keyset_receipt_digest_mismatch:expected={want_digest}:got={got_digest}")
        return problems, summary

    channels = obj.get("publication_channels") or obj.get("channels") or []
    if not isinstance(channels, list):
        channels = []
        problems.append("signature_trust_keyset_receipt_invalid:channels_not_array")
    channel_keys: set[tuple[str, str]] = set()
    for i, ch in enumerate(channels):
        if not isinstance(ch, dict):
            problems.append(f"signature_trust_keyset_receipt_invalid:channel_not_object:{i}")
            continue
        cid = str(ch.get("channel_id") or "").strip()
        ctype = str(ch.get("channel_type") or "").strip()
        observed_digest = _first_nonempty_channel_digest(ch, ("observed_trust_keyset_sha256", "trust_keyset_sha256"))
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", observed_digest):
            problems.append(f"signature_trust_keyset_receipt_digest_mismatch:channel_missing_or_bad_observed_digest:{cid or i}")
        elif observed_digest != want_digest:
            problems.append(f"signature_trust_keyset_receipt_digest_mismatch:channel={cid or i}")
        if not cid or not ctype:
            problems.append(f"signature_trust_keyset_receipt_invalid:channel_missing_id_or_type:{i}")
            continue
        channel_keys.add((ctype, cid))
    summary["trust_keyset_receipt_channel_count"] = len(channels)
    summary["trust_keyset_receipt_independent_channel_count"] = len(channel_keys)

    min_raw = obj.get("minimum_independent_channels", 2)
    try:
        min_channels = int(min_raw)
    except Exception:
        min_channels = 2
        problems.append("signature_trust_keyset_receipt_invalid:minimum_independent_channels_unparseable")
    if min_channels < 1:
        min_channels = 1
    if min_channels > 10:
        min_channels = 10
    summary["trust_keyset_receipt_required_independent_channels"] = min_channels

    if len(channel_keys) < min_channels:
        summary["trust_keyset_receipt_status"] = "channel_quorum_not_met"
        problems.append(f"signature_trust_keyset_receipt_channel_quorum_not_met:valid={len(channel_keys)}:required={min_channels}")
        return problems, summary
    if not _record_publication_channel_diversity(
        summary=summary,
        problems=problems,
        field_prefix="trust_keyset_receipt",
        problem_code="signature_trust_keyset_receipt_channel_diversity_not_met",
        channels=channels,
        channel_keys=channel_keys,
        min_channels=min_channels,
        status_field="trust_keyset_receipt_status",
    ):
        return problems, summary

    summary["trust_keyset_receipt_status"] = "invalid" if problems else "matched"
    return problems, summary





def _publication_channel_route_key(ch: dict[str, Any]) -> tuple[str, ...]:
    """Return a normalized route key for a publication channel row.

    Distinct channel IDs are not enough for a trust-chain quorum: two labels can
    still point at the same publication route. Prefer locator-like fields when
    present; fall back to (channel_type, channel_id) only when no route locator
    is available. The value is intentionally local and synthetic; it does not
    fetch or validate any external channel.
    """

    for key in (
        "locator_ref",
        "url",
        "uri",
        "href",
        "channel_url",
        "location",
        "ref",
    ):
        value = str(ch.get(key) or "").strip().lower()
        if value:
            return ("locator", value)
    ctype = str(ch.get("channel_type") or "").strip().lower()
    cid = str(ch.get("channel_id") or "").strip().lower()
    if ctype or cid:
        return ("id", ctype, cid)
    return ()


def _record_publication_channel_diversity(
    *,
    summary: dict[str, Any],
    problems: list[str],
    field_prefix: str,
    problem_code: str,
    channels: list[Any],
    channel_keys: set[tuple[str, str]],
    min_channels: int,
    status_field: str,
) -> bool:
    """Require a quorum to span distinct channel types and routes.

    Earlier verifier revisions counted distinct (channel_type, channel_id)
    pairs. That could be gamed by minting two channel IDs under one channel
    class, or by giving the same route two labels. This helper records the
    receipt-surface counts and fails closed for same-type or duplicate-route
    quorum inflation.
    """

    channel_types = {ctype for ctype, _cid in channel_keys if ctype}
    route_keys: list[tuple[str, ...]] = []
    for ch in channels:
        if isinstance(ch, dict):
            route_key = _publication_channel_route_key(ch)
            if route_key:
                route_keys.append(route_key)
    duplicate_route_count = len(route_keys) - len(set(route_keys))
    required_type_count = 2 if min_channels >= 2 else 1

    summary[f"{field_prefix}_independent_channel_type_count"] = len(channel_types)
    summary[f"{field_prefix}_required_independent_channel_types"] = required_type_count
    summary[f"{field_prefix}_duplicate_channel_route_count"] = max(0, duplicate_route_count)

    if duplicate_route_count > 0:
        summary[f"{field_prefix}_channel_diversity_status"] = "duplicate_route"
        summary[status_field] = "channel_diversity_not_met"
        problems.append(f"{problem_code}:duplicate_route")
        return False
    if len(channel_types) < required_type_count:
        summary[f"{field_prefix}_channel_diversity_status"] = "type_quorum_not_met"
        summary[status_field] = "channel_diversity_not_met"
        problems.append(f"{problem_code}:types={len(channel_types)}:required={required_type_count}")
        return False

    summary[f"{field_prefix}_channel_diversity_status"] = "distinct_types_met"
    return True

def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [x for x in value if isinstance(x, dict)]


def _public_key_material_sha256_from_key(key: dict[str, Any]) -> str:
    raw = key.get("_public_key_bytes")
    if not isinstance(raw, (bytes, bytearray)):
        return ""
    return "sha256:" + hashlib.sha256(bytes(raw)).hexdigest()


def validate_trust_governance_bundle(
    packet_dir: Path,
    bundle_path: Path | None,
    expected_bundle_sha256: str | None,
    expected_keyset_sha256: str,
    expected_receipt_sha256: str,
    keys: list[dict[str, Any]],
    keyring: dict[str, Any],
    require_bundle: bool,
) -> tuple[list[str], dict[str, Any]]:
    """Validate optional external synthetic trust-governance evidence.

    This is a bounded local governance guard, not a production ceremony verifier.
    It proves only that the operator supplied a separate public JSON bundle whose
    bytes, digest pins, witness quorum, key-event references, and receipt/keyset
    bindings are internally coherent and external to the packet being verified.
    """

    summary: dict[str, Any] = {
        "trust_governance_bundle_required": bool(require_bundle),
        "trust_governance_bundle_status": "not_supplied",
        "trust_governance_bundle_sha256": "",
        "trust_governance_bundle_pin_required": bool((expected_bundle_sha256 or "").strip()),
        "trust_governance_bundle_pin_status": "not_supplied",
        "trust_governance_bundle_pin_sha256": "",
        "trust_governance_bundle_id": "",
        "trust_governance_bundle_profile": "",
        "trust_governance_witness_count": 0,
        "trust_governance_required_witness_count": 0,
        "trust_governance_event_count": 0,
        "trust_governance_rotation_or_revocation_event_count": 0,
    }
    problems: list[str] = []

    expected_pin_hex: str | None = None
    if (expected_bundle_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_bundle_sha256))
        if expected_pin_hex is None:
            summary["trust_governance_bundle_pin_status"] = "invalid"
            summary["trust_governance_bundle_status"] = "invalid"
            problems.append("signature_trust_governance_bundle_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["trust_governance_bundle_pin_sha256"] = "sha256:" + expected_pin_hex

    if bundle_path is None or not str(bundle_path).strip():
        if require_bundle:
            summary["trust_governance_bundle_status"] = "missing"
            problems.append("signature_trust_governance_bundle_invalid:required_bundle_not_supplied")
        return problems, summary

    if _path_inside_dir(bundle_path, packet_dir):
        summary["trust_governance_bundle_status"] = "packet_contained_rejected"
        problems.append("signature_trust_governance_bundle_untrusted_location:packet_contained")
        return problems, summary

    try:
        b = bundle_path.read_bytes()
    except Exception as e:
        summary["trust_governance_bundle_status"] = "invalid"
        problems.append(f"signature_trust_governance_bundle_invalid:read_failed:{type(e).__name__}")
        return problems, summary

    actual_hex = sha256_hex_bytes(b)
    summary["trust_governance_bundle_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["trust_governance_bundle_status"] = "mismatched"
            summary["trust_governance_bundle_pin_status"] = "mismatched"
            problems.append(f"signature_trust_governance_bundle_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}")
            return problems, summary
        summary["trust_governance_bundle_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["trust_governance_bundle_status"] = "invalid"
        problems.append(f"signature_trust_governance_bundle_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary
    if not isinstance(obj, dict):
        summary["trust_governance_bundle_status"] = "invalid"
        problems.append("signature_trust_governance_bundle_invalid:not_object")
        return problems, summary

    bundle_id = str(obj.get("governance_bundle_id") or obj.get("bundle_id") or "").strip()
    profile = str(obj.get("profile") or "").strip()
    status = str(obj.get("status") or "active").strip().lower()
    summary["trust_governance_bundle_id"] = bundle_id[:200]
    summary["trust_governance_bundle_profile"] = profile

    if profile != TRUST_GOVERNANCE_BUNDLE_PROFILE:
        problems.append(f"signature_trust_governance_bundle_invalid:unsupported_profile:{profile or 'missing'}")
    if status not in {"active", "current"}:
        summary["trust_governance_bundle_status"] = "stale_superseded"
        problems.append(f"signature_trust_governance_bundle_stale:status={status or 'missing'}")
    if obj.get("superseded_by") or obj.get("superseded_at"):
        summary["trust_governance_bundle_status"] = "stale_superseded"
        problems.append("signature_trust_governance_bundle_stale:superseded_marker_present")

    got_keyset = str(obj.get("trust_keyset_sha256") or "").strip().lower()
    want_keyset = str(expected_keyset_sha256 or "").strip().lower()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_keyset):
        problems.append("signature_trust_governance_bundle_keyset_mismatch:missing_or_bad_trust_keyset_sha256")
    elif got_keyset != want_keyset:
        summary["trust_governance_bundle_status"] = "keyset_mismatch"
        problems.append(f"signature_trust_governance_bundle_keyset_mismatch:expected={want_keyset}:got={got_keyset}")

    wants_receipt = bool(obj.get("requires_external_publication_receipt", True))
    got_receipt = str(obj.get("publication_receipt_sha256") or obj.get("trust_keyset_receipt_sha256") or "").strip().lower()
    want_receipt = str(expected_receipt_sha256 or "").strip().lower()
    if wants_receipt:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_receipt):
            problems.append("signature_trust_governance_bundle_receipt_mismatch:missing_or_bad_publication_receipt_sha256")
        elif not re.fullmatch(r"sha256:[0-9a-f]{64}", want_receipt):
            problems.append("signature_trust_governance_bundle_receipt_mismatch:no_valid_external_receipt_was_verified")
        elif got_receipt != want_receipt:
            summary["trust_governance_bundle_status"] = "receipt_mismatch"
            problems.append(f"signature_trust_governance_bundle_receipt_mismatch:expected={want_receipt}:got={got_receipt}")

    ceremony = obj.get("key_ceremony") if isinstance(obj.get("key_ceremony"), dict) else {}
    witnesses = _as_list_of_dicts(ceremony.get("witnesses") if isinstance(ceremony, dict) else [])
    witness_ids = {
        str(w.get("witness_id") or w.get("id") or w.get("name") or "").strip()
        for w in witnesses
        if str(w.get("witness_id") or w.get("id") or w.get("name") or "").strip()
    }
    min_witnesses_raw = obj.get("minimum_witnesses", ceremony.get("minimum_witnesses", 2) if isinstance(ceremony, dict) else 2)
    try:
        min_witnesses = int(min_witnesses_raw)
    except Exception:
        min_witnesses = 2
        problems.append("signature_trust_governance_bundle_invalid:minimum_witnesses_unparseable")
    if min_witnesses < 1:
        min_witnesses = 1
    if min_witnesses > 25:
        min_witnesses = 25
    summary["trust_governance_witness_count"] = len(witness_ids)
    summary["trust_governance_required_witness_count"] = min_witnesses
    if len(witness_ids) < min_witnesses:
        summary["trust_governance_bundle_status"] = "witness_quorum_not_met"
        problems.append(f"signature_trust_governance_bundle_witness_quorum_not_met:valid={len(witness_ids)}:required={min_witnesses}")

    raw_events = obj.get("key_events") or obj.get("key_lifecycle_events") or []
    events = _as_list_of_dicts(raw_events)
    summary["trust_governance_event_count"] = len(events)
    rotation_types = {"rotated", "retired", "revoked", "revocation", "rotation", "replaced"}
    rotation_count = sum(1 for ev in events if str(ev.get("event_type") or "").strip().lower() in rotation_types)
    summary["trust_governance_rotation_or_revocation_event_count"] = int(rotation_count)
    if bool(obj.get("requires_rotation_or_revocation_event", True)) and rotation_count < 1:
        problems.append("signature_trust_governance_bundle_event_missing:rotation_or_revocation_event_required")

    events_by_key: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        kid = str(ev.get("kid") or ev.get("key_id") or "").strip()
        if kid:
            events_by_key.setdefault(kid, []).append(ev)

    for key in keys:
        kid = str(key.get("kid") or "").strip()
        if not kid:
            continue
        expected_pk_sha = _public_key_material_sha256_from_key(key)
        matches = []
        for ev in events_by_key.get(kid, []):
            ev_type = str(ev.get("event_type") or "").strip().lower()
            pk_sha = str(ev.get("public_key_sha256") or "").strip().lower()
            if ev_type in {"generated", "activated", "published", "rotated_in"} and pk_sha == expected_pk_sha:
                matches.append(ev)
        if not matches:
            problems.append(f"signature_trust_governance_bundle_event_missing:active_key_activation:{kid}")

    # Optional scope sanity: if the keyset declares scope, the governance bundle should not contradict it.
    kr_scope = keyring.get("scope") if isinstance(keyring.get("scope"), dict) else {}
    gb_scope = obj.get("scope") if isinstance(obj.get("scope"), dict) else {}
    for field in ("election_id", "jurisdiction"):
        kr_v = str(kr_scope.get(field) or "").strip() if isinstance(kr_scope, dict) else ""
        gb_v = str(gb_scope.get(field) or "").strip() if isinstance(gb_scope, dict) else ""
        if kr_v and gb_v and kr_v != gb_v:
            problems.append(f"signature_trust_governance_bundle_invalid:scope_mismatch:{field}")

    if problems and summary["trust_governance_bundle_status"] == "not_supplied":
        summary["trust_governance_bundle_status"] = "invalid"
    elif not problems:
        summary["trust_governance_bundle_status"] = "matched"

    return problems, summary


def validate_trust_governance_bundle_publication_receipt(
    packet_dir: Path,
    receipt_path: Path | None,
    expected_bundle_sha256: str,
    require_receipt: bool,
    expected_receipt_sha256: str | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate an optional external publication receipt for governance-bundle bytes.

    This is a bounded local guard.  It proves only that the verifier was given a
    separate JSON object, external to the packet, whose bytes bind the governance
    bundle digest to named publication channels. It does not fetch those channels,
    prove election-office authority, or establish production revocation freshness.
    """

    summary: dict[str, Any] = {
        "trust_governance_bundle_receipt_required": bool(require_receipt),
        "trust_governance_bundle_receipt_status": "not_supplied",
        "trust_governance_bundle_receipt_sha256": "",
        "trust_governance_bundle_receipt_pin_required": bool((expected_receipt_sha256 or "").strip()),
        "trust_governance_bundle_receipt_pin_status": "not_supplied",
        "trust_governance_bundle_receipt_pin_sha256": "",
        "trust_governance_bundle_receipt_id": "",
        "trust_governance_bundle_receipt_profile": "",
        "trust_governance_bundle_receipt_channel_count": 0,
        "trust_governance_bundle_receipt_independent_channel_count": 0,
        "trust_governance_bundle_receipt_required_independent_channels": 0,
    }
    problems: list[str] = []

    expected_pin_hex: str | None = None
    if (expected_receipt_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_receipt_sha256))
        if expected_pin_hex is None:
            summary["trust_governance_bundle_receipt_pin_status"] = "invalid"
            summary["trust_governance_bundle_receipt_status"] = "invalid"
            problems.append("signature_trust_governance_bundle_receipt_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["trust_governance_bundle_receipt_pin_sha256"] = "sha256:" + expected_pin_hex

    want_digest = str(expected_bundle_sha256 or "").strip().lower()
    if require_receipt and not re.fullmatch(r"sha256:[0-9a-f]{64}", want_digest):
        summary["trust_governance_bundle_receipt_status"] = "invalid"
        problems.append("signature_trust_governance_bundle_receipt_invalid:governance_bundle_digest_not_available")
        return problems, summary

    if receipt_path is None or not str(receipt_path).strip():
        if require_receipt:
            summary["trust_governance_bundle_receipt_status"] = "missing"
            problems.append("signature_trust_governance_bundle_receipt_invalid:required_receipt_not_supplied")
        return problems, summary

    if _path_inside_dir(receipt_path, packet_dir):
        summary["trust_governance_bundle_receipt_status"] = "packet_contained_rejected"
        problems.append("signature_trust_governance_bundle_receipt_untrusted_location:packet_contained")
        return problems, summary

    try:
        b = receipt_path.read_bytes()
    except Exception as e:
        summary["trust_governance_bundle_receipt_status"] = "invalid"
        problems.append(f"signature_trust_governance_bundle_receipt_invalid:read_failed:{type(e).__name__}")
        return problems, summary

    actual_hex = sha256_hex_bytes(b)
    summary["trust_governance_bundle_receipt_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["trust_governance_bundle_receipt_pin_status"] = "mismatched"
            summary["trust_governance_bundle_receipt_status"] = "mismatched"
            problems.append(f"signature_trust_governance_bundle_receipt_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}")
            return problems, summary
        summary["trust_governance_bundle_receipt_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["trust_governance_bundle_receipt_status"] = "invalid"
        problems.append(f"signature_trust_governance_bundle_receipt_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary
    if not isinstance(obj, dict):
        summary["trust_governance_bundle_receipt_status"] = "invalid"
        problems.append("signature_trust_governance_bundle_receipt_invalid:not_object")
        return problems, summary

    summary["trust_governance_bundle_receipt_id"] = str(obj.get("receipt_id") or "")[:200]
    profile = str(obj.get("profile") or obj.get("receipt_profile") or "").strip()
    summary["trust_governance_bundle_receipt_profile"] = profile
    if not profile:
        problems.append("signature_trust_governance_bundle_receipt_invalid:missing_profile")
    elif profile != TRUST_GOVERNANCE_BUNDLE_RECEIPT_PROFILE:
        problems.append(f"signature_trust_governance_bundle_receipt_invalid:unsupported_profile:{profile}")

    got_digest = str(
        obj.get("trust_governance_bundle_sha256")
        or obj.get("governance_bundle_sha256")
        or obj.get("trust_key_governance_bundle_sha256")
        or ""
    ).strip().lower()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_digest):
        problems.append("signature_trust_governance_bundle_receipt_invalid:missing_or_bad_governance_bundle_sha256")
    elif want_digest and got_digest != want_digest:
        summary["trust_governance_bundle_receipt_status"] = "mismatched"
        problems.append(f"signature_trust_governance_bundle_receipt_digest_mismatch:expected={want_digest}:got={got_digest}")
        return problems, summary

    channels = obj.get("publication_channels") or obj.get("channels") or []
    if not isinstance(channels, list):
        channels = []
        problems.append("signature_trust_governance_bundle_receipt_invalid:channels_not_array")
    channel_keys: set[tuple[str, str]] = set()
    for i, ch in enumerate(channels):
        if not isinstance(ch, dict):
            problems.append(f"signature_trust_governance_bundle_receipt_invalid:channel_not_object:{i}")
            continue
        cid = str(ch.get("channel_id") or "").strip()
        ctype = str(ch.get("channel_type") or "").strip()
        observed_digest = _first_nonempty_channel_digest(
            ch,
            ("observed_trust_governance_bundle_sha256", "trust_governance_bundle_sha256", "governance_bundle_sha256"),
        )
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", observed_digest):
            problems.append(f"signature_trust_governance_bundle_receipt_digest_mismatch:channel_missing_or_bad_observed_digest:{cid or i}")
        elif observed_digest != got_digest:
            problems.append(f"signature_trust_governance_bundle_receipt_digest_mismatch:channel={cid or i}")
        if not cid or not ctype:
            problems.append(f"signature_trust_governance_bundle_receipt_invalid:channel_missing_id_or_type:{i}")
            continue
        channel_keys.add((ctype, cid))
    summary["trust_governance_bundle_receipt_channel_count"] = len(channels)
    summary["trust_governance_bundle_receipt_independent_channel_count"] = len(channel_keys)

    min_raw = obj.get("minimum_independent_channels", 2)
    try:
        min_channels = int(min_raw)
    except Exception:
        min_channels = 2
        problems.append("signature_trust_governance_bundle_receipt_invalid:minimum_independent_channels_unparseable")
    if min_channels < 1:
        min_channels = 1
    if min_channels > 10:
        min_channels = 10
    summary["trust_governance_bundle_receipt_required_independent_channels"] = min_channels

    if len(channel_keys) < min_channels:
        summary["trust_governance_bundle_receipt_status"] = "channel_quorum_not_met"
        problems.append(f"signature_trust_governance_bundle_receipt_channel_quorum_not_met:valid={len(channel_keys)}:required={min_channels}")
        return problems, summary
    if not _record_publication_channel_diversity(
        summary=summary,
        problems=problems,
        field_prefix="trust_governance_bundle_receipt",
        problem_code="signature_trust_governance_bundle_receipt_channel_diversity_not_met",
        channels=channels,
        channel_keys=channel_keys,
        min_channels=min_channels,
        status_field="trust_governance_bundle_receipt_status",
    ):
        return problems, summary

    summary["trust_governance_bundle_receipt_status"] = "invalid" if problems else "matched"
    return problems, summary


def validate_trust_status_snapshot(
    packet_dir: Path,
    snapshot_path: Path | None,
    expected_snapshot_sha256: str | None,
    expected_keyset_sha256: str,
    expected_governance_bundle_sha256: str,
    expected_governance_bundle_receipt_sha256: str,
    keys: list[dict[str, Any]],
    require_snapshot: bool,
    verification_time: datetime | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate an optional external trust-status snapshot.

    This is a bounded local freshness/revocation guard. It proves only that the
    operator supplied a separate JSON status snapshot, outside the packet, whose
    bytes are optionally pinned, whose update window covers verification_time,
    and whose key-status entries do not revoke or omit the trusted key material
    used by the local trust keyset. It does not fetch an online revocation feed
    or prove production authority for the status publisher.
    """

    if verification_time is None:
        verification_time = datetime.now(timezone.utc)
    if verification_time.tzinfo is None:
        verification_time = verification_time.replace(tzinfo=timezone.utc)
    verification_time = verification_time.astimezone(timezone.utc)
    verification_time_s = verification_time.isoformat(timespec="seconds").replace("+00:00", "Z")

    summary: dict[str, Any] = {
        "trust_status_snapshot_required": bool(require_snapshot),
        "trust_status_snapshot_status": "not_supplied",
        "trust_status_snapshot_sha256": "",
        "trust_status_snapshot_pin_required": bool((expected_snapshot_sha256 or "").strip()),
        "trust_status_snapshot_pin_status": "not_supplied",
        "trust_status_snapshot_pin_sha256": "",
        "trust_status_snapshot_id": "",
        "trust_status_snapshot_profile": "",
        "trust_status_snapshot_this_update": "",
        "trust_status_snapshot_next_update": "",
        "trust_status_snapshot_verification_time": verification_time_s,
        "trust_status_snapshot_key_status_count": 0,
        "trust_status_snapshot_revoked_key_count": 0,
        "trust_status_snapshot_authority_count": 0,
        "trust_status_snapshot_required_authority_count": 0,
    }
    problems: list[str] = []

    expected_pin_hex: str | None = None
    if (expected_snapshot_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_snapshot_sha256))
        if expected_pin_hex is None:
            summary["trust_status_snapshot_pin_status"] = "invalid"
            summary["trust_status_snapshot_status"] = "invalid"
            problems.append("signature_trust_status_snapshot_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["trust_status_snapshot_pin_sha256"] = "sha256:" + expected_pin_hex

    if snapshot_path is None or not str(snapshot_path).strip():
        if require_snapshot:
            summary["trust_status_snapshot_status"] = "missing"
            problems.append("signature_trust_status_snapshot_invalid:required_snapshot_not_supplied")
        return problems, summary

    if _path_inside_dir(snapshot_path, packet_dir):
        summary["trust_status_snapshot_status"] = "packet_contained_rejected"
        problems.append("signature_trust_status_snapshot_untrusted_location:packet_contained")
        return problems, summary

    try:
        b = snapshot_path.read_bytes()
    except Exception as e:
        summary["trust_status_snapshot_status"] = "invalid"
        problems.append(f"signature_trust_status_snapshot_invalid:read_failed:{type(e).__name__}")
        return problems, summary

    actual_hex = sha256_hex_bytes(b)
    summary["trust_status_snapshot_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["trust_status_snapshot_pin_status"] = "mismatched"
            summary["trust_status_snapshot_status"] = "mismatched"
            problems.append(f"signature_trust_status_snapshot_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}")
            return problems, summary
        summary["trust_status_snapshot_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["trust_status_snapshot_status"] = "invalid"
        problems.append(f"signature_trust_status_snapshot_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary
    if not isinstance(obj, dict):
        summary["trust_status_snapshot_status"] = "invalid"
        problems.append("signature_trust_status_snapshot_invalid:not_object")
        return problems, summary

    snapshot_id = str(obj.get("snapshot_id") or obj.get("status_snapshot_id") or "").strip()
    profile = str(obj.get("profile") or "").strip()
    status = str(obj.get("status") or "current").strip().lower()
    summary["trust_status_snapshot_id"] = snapshot_id[:200]
    summary["trust_status_snapshot_profile"] = profile
    if profile != TRUST_STATUS_SNAPSHOT_PROFILE:
        problems.append(f"signature_trust_status_snapshot_invalid:unsupported_profile:{profile or 'missing'}")
    if status not in {"active", "current"}:
        summary["trust_status_snapshot_status"] = "stale_expired"
        problems.append(f"signature_trust_status_snapshot_stale:status={status or 'missing'}")
    if obj.get("superseded_by") or obj.get("superseded_at"):
        summary["trust_status_snapshot_status"] = "stale_expired"
        problems.append("signature_trust_status_snapshot_stale:superseded_marker_present")

    want_keyset = str(expected_keyset_sha256 or "").strip().lower()
    got_keyset = str(obj.get("trust_keyset_sha256") or obj.get("keyset_sha256") or "").strip().lower()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_keyset):
        problems.append("signature_trust_status_snapshot_keyset_mismatch:missing_or_bad_trust_keyset_sha256")
    elif got_keyset != want_keyset:
        summary["trust_status_snapshot_status"] = "keyset_mismatch"
        problems.append(f"signature_trust_status_snapshot_keyset_mismatch:expected={want_keyset}:got={got_keyset}")

    want_gov = str(expected_governance_bundle_sha256 or "").strip().lower()
    got_gov = str(obj.get("trust_governance_bundle_sha256") or obj.get("governance_bundle_sha256") or "").strip().lower()
    if got_gov or want_gov:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_gov):
            problems.append("signature_trust_status_snapshot_governance_mismatch:missing_or_bad_governance_bundle_sha256")
        elif want_gov and got_gov != want_gov:
            summary["trust_status_snapshot_status"] = "governance_mismatch"
            problems.append(f"signature_trust_status_snapshot_governance_mismatch:bundle_expected={want_gov}:got={got_gov}")

    want_gov_receipt = str(expected_governance_bundle_receipt_sha256 or "").strip().lower()
    got_gov_receipt = str(
        obj.get("trust_governance_bundle_receipt_sha256")
        or obj.get("governance_bundle_receipt_sha256")
        or ""
    ).strip().lower()
    if got_gov_receipt or want_gov_receipt:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_gov_receipt):
            problems.append("signature_trust_status_snapshot_governance_mismatch:missing_or_bad_governance_bundle_receipt_sha256")
        elif want_gov_receipt and got_gov_receipt != want_gov_receipt:
            summary["trust_status_snapshot_status"] = "governance_mismatch"
            problems.append(f"signature_trust_status_snapshot_governance_mismatch:receipt_expected={want_gov_receipt}:got={got_gov_receipt}")

    this_update_raw = str(obj.get("this_update") or obj.get("issued_at") or "").strip()
    next_update_raw = str(obj.get("next_update") or "").strip()
    summary["trust_status_snapshot_this_update"] = this_update_raw[:80]
    summary["trust_status_snapshot_next_update"] = next_update_raw[:80]
    this_update = _parse_rfc3339_utc(this_update_raw)
    next_update = _parse_rfc3339_utc(next_update_raw)
    if this_update is None:
        problems.append("signature_trust_status_snapshot_invalid:this_update_missing_or_unparseable")
    if next_update is None:
        problems.append("signature_trust_status_snapshot_invalid:next_update_missing_or_unparseable")
    if this_update is not None and verification_time < this_update:
        summary["trust_status_snapshot_status"] = "stale_expired"
        problems.append("signature_trust_status_snapshot_stale:verification_time_before_this_update")
    if next_update is not None and verification_time > next_update:
        summary["trust_status_snapshot_status"] = "stale_expired"
        problems.append("signature_trust_status_snapshot_stale:next_update_elapsed")
    if this_update is not None and next_update is not None and next_update <= this_update:
        summary["trust_status_snapshot_status"] = "invalid"
        problems.append("signature_trust_status_snapshot_invalid:next_update_not_after_this_update")

    authorities = _as_list_of_dicts(obj.get("status_authorities") or obj.get("authorities") or [])
    authority_keys: set[tuple[str, str]] = set()
    for i, auth in enumerate(authorities):
        aid = str(auth.get("authority_id") or auth.get("id") or "").strip()
        atype = str(auth.get("authority_type") or auth.get("type") or "").strip()
        if not aid or not atype:
            problems.append(f"signature_trust_status_snapshot_invalid:authority_missing_id_or_type:{i}")
            continue
        authority_keys.add((atype, aid))
    min_auth_raw = obj.get("minimum_status_authorities", 1)
    try:
        min_auth = int(min_auth_raw)
    except Exception:
        min_auth = 1
        problems.append("signature_trust_status_snapshot_invalid:minimum_status_authorities_unparseable")
    if min_auth < 1:
        min_auth = 1
    if min_auth > 10:
        min_auth = 10
    summary["trust_status_snapshot_authority_count"] = len(authority_keys)
    summary["trust_status_snapshot_required_authority_count"] = min_auth
    if len(authority_keys) < min_auth:
        summary["trust_status_snapshot_status"] = "authority_quorum_not_met"
        problems.append(f"signature_trust_status_snapshot_authority_quorum_not_met:valid={len(authority_keys)}:required={min_auth}")

    key_statuses = _as_list_of_dicts(obj.get("key_statuses") or obj.get("keys") or [])
    summary["trust_status_snapshot_key_status_count"] = len(key_statuses)
    revoked_statuses = {"revoked", "suspended", "compromised", "disabled"}
    retired_statuses = {"retired", "expired"}
    active_statuses = {"active", "valid", "current", "trusted"}
    summary["trust_status_snapshot_revoked_key_count"] = sum(
        1 for row in key_statuses if str(row.get("status") or "").strip().lower() in revoked_statuses
    )
    status_by_kid: dict[str, list[dict[str, Any]]] = {}
    for row in key_statuses:
        kid = str(row.get("kid") or row.get("key_id") or "").strip()
        if kid:
            status_by_kid.setdefault(kid, []).append(row)

    for key in keys:
        kid = str(key.get("kid") or "").strip()
        if not kid:
            continue
        expected_pk_sha = _public_key_material_sha256_from_key(key)
        entries = status_by_kid.get(kid, [])
        if not entries:
            problems.append(f"signature_trust_status_snapshot_key_missing:{kid}")
            continue
        matching_entries: list[dict[str, Any]] = []
        for row in entries:
            pk_sha = str(row.get("public_key_sha256") or "").strip().lower()
            if not pk_sha or pk_sha == expected_pk_sha:
                matching_entries.append(row)
        if not matching_entries:
            problems.append(f"signature_trust_status_snapshot_key_status_mismatch:{kid}:public_key_sha256")
            continue
        row_statuses = {str(row.get("status") or "").strip().lower() for row in matching_entries}
        if row_statuses & revoked_statuses:
            problems.append(f"signature_trust_status_snapshot_key_revoked:{kid}:{sorted(row_statuses & revoked_statuses)[0]}")
            continue
        key_status = str(key.get("status") or "active").strip().lower()
        if key_status in {"active", "valid"} and not (row_statuses & active_statuses):
            problems.append(f"signature_trust_status_snapshot_key_status_mismatch:{kid}:expected_active")
        if key_status == "retired" and not (row_statuses & (active_statuses | retired_statuses)):
            problems.append(f"signature_trust_status_snapshot_key_status_mismatch:{kid}:expected_retired_or_historical")

    if problems and summary["trust_status_snapshot_status"] == "not_supplied":
        summary["trust_status_snapshot_status"] = "invalid"
    elif not problems:
        summary["trust_status_snapshot_status"] = "matched"
    return problems, summary



def validate_trust_status_snapshot_publication_receipt(
    packet_dir: Path,
    receipt_path: Path | None,
    expected_status_snapshot_sha256: str,
    require_receipt: bool,
    expected_receipt_sha256: str | None = None,
    verification_time: datetime | None = None,
    status_snapshot_summary: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate an optional external publication receipt for status-snapshot bytes.

    This is a bounded local guard. It proves only that the verifier was given a
    separate JSON object, outside the packet being authenticated, whose bytes
    bind the supplied trust-status snapshot digest to named publication
    channels. It also checks synthetic receipt/update temporal order so a stale
    or pre-snapshot publication receipt cannot be replayed as current status
    evidence. It does not fetch those channels, prove election-office authority,
    implement trusted timestamping, or establish production online revocation
    freshness.
    """

    if verification_time is not None:
        if verification_time.tzinfo is None:
            verification_time = verification_time.replace(tzinfo=timezone.utc)
        verification_time = verification_time.astimezone(timezone.utc)
    verification_time_s = verification_time.isoformat(timespec="seconds").replace("+00:00", "Z") if verification_time else ""
    status_summary = status_snapshot_summary if isinstance(status_snapshot_summary, dict) else {}
    snapshot_this_update_text = str(status_summary.get("trust_status_snapshot_this_update") or "").strip()
    snapshot_next_update_text = str(status_summary.get("trust_status_snapshot_next_update") or "").strip()

    summary: dict[str, Any] = {
        "trust_status_snapshot_receipt_required": bool(require_receipt),
        "trust_status_snapshot_receipt_status": "not_supplied",
        "trust_status_snapshot_receipt_sha256": "",
        "trust_status_snapshot_receipt_pin_required": bool((expected_receipt_sha256 or "").strip()),
        "trust_status_snapshot_receipt_pin_status": "not_supplied",
        "trust_status_snapshot_receipt_pin_sha256": "",
        "trust_status_snapshot_receipt_id": "",
        "trust_status_snapshot_receipt_profile": "",
        "trust_status_snapshot_receipt_channel_count": 0,
        "trust_status_snapshot_receipt_independent_channel_count": 0,
        "trust_status_snapshot_receipt_required_independent_channels": 0,
        "trust_status_snapshot_receipt_validity_status": "not_checked",
        "trust_status_snapshot_receipt_valid_from": "",
        "trust_status_snapshot_receipt_valid_until": "",
        "trust_status_snapshot_receipt_issued_at": "",
        "trust_status_snapshot_receipt_issued_at_status": "not_checked",
        "trust_status_snapshot_receipt_channel_time_status": "not_checked",
        "trust_status_snapshot_receipt_temporal_status": "not_checked",
        "trust_status_snapshot_receipt_temporal_snapshot_this_update": snapshot_this_update_text[:80],
        "trust_status_snapshot_receipt_temporal_snapshot_next_update": snapshot_next_update_text[:80],
        "trust_status_snapshot_receipt_published_at_min": "",
        "trust_status_snapshot_receipt_published_at_max": "",
        "trust_status_snapshot_receipt_earliest_published_at": "",
        "trust_status_snapshot_receipt_latest_published_at": "",
        "trust_status_snapshot_receipt_external_verification_time": verification_time_s,
    }
    problems: list[str] = []

    expected_pin_hex: str | None = None
    if (expected_receipt_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_receipt_sha256))
        if expected_pin_hex is None:
            summary["trust_status_snapshot_receipt_pin_status"] = "invalid"
            summary["trust_status_snapshot_receipt_status"] = "invalid"
            problems.append("signature_trust_status_snapshot_receipt_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["trust_status_snapshot_receipt_pin_sha256"] = "sha256:" + expected_pin_hex

    want_digest = str(expected_status_snapshot_sha256 or "").strip().lower()
    receipt_requested = bool(require_receipt or receipt_path is not None or expected_pin_hex is not None)
    if receipt_requested and not re.fullmatch(r"sha256:[0-9a-f]{64}", want_digest):
        summary["trust_status_snapshot_receipt_status"] = "invalid"
        problems.append("signature_trust_status_snapshot_receipt_invalid:status_snapshot_digest_not_available")
        return problems, summary

    if receipt_path is None or not str(receipt_path).strip():
        if require_receipt:
            summary["trust_status_snapshot_receipt_status"] = "missing"
            problems.append("signature_trust_status_snapshot_receipt_invalid:required_receipt_not_supplied")
        return problems, summary

    if _path_inside_dir(receipt_path, packet_dir):
        summary["trust_status_snapshot_receipt_status"] = "packet_contained_rejected"
        problems.append("signature_trust_status_snapshot_receipt_untrusted_location:packet_contained")
        return problems, summary

    try:
        b = receipt_path.read_bytes()
    except Exception as e:
        summary["trust_status_snapshot_receipt_status"] = "invalid"
        problems.append(f"signature_trust_status_snapshot_receipt_invalid:read_failed:{type(e).__name__}")
        return problems, summary

    actual_hex = sha256_hex_bytes(b)
    summary["trust_status_snapshot_receipt_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["trust_status_snapshot_receipt_pin_status"] = "mismatched"
            summary["trust_status_snapshot_receipt_status"] = "mismatched"
            problems.append(f"signature_trust_status_snapshot_receipt_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}")
            return problems, summary
        summary["trust_status_snapshot_receipt_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["trust_status_snapshot_receipt_status"] = "invalid"
        problems.append(f"signature_trust_status_snapshot_receipt_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary
    if not isinstance(obj, dict):
        summary["trust_status_snapshot_receipt_status"] = "invalid"
        problems.append("signature_trust_status_snapshot_receipt_invalid:not_object")
        return problems, summary

    profile = str(obj.get("profile") or "").strip()
    receipt_id = str(obj.get("receipt_id") or "").strip()
    summary["trust_status_snapshot_receipt_profile"] = profile
    summary["trust_status_snapshot_receipt_id"] = receipt_id[:200]
    if profile != TRUST_STATUS_SNAPSHOT_RECEIPT_PROFILE:
        problems.append(f"signature_trust_status_snapshot_receipt_invalid:unsupported_profile:{profile or 'missing'}")

    got_digest = str(
        obj.get("trust_status_snapshot_sha256")
        or obj.get("status_snapshot_sha256")
        or obj.get("snapshot_sha256")
        or ""
    ).strip().lower()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_digest):
        problems.append("signature_trust_status_snapshot_receipt_digest_mismatch:missing_or_bad_trust_status_snapshot_sha256")
    elif want_digest and got_digest != want_digest:
        summary["trust_status_snapshot_receipt_status"] = "digest_mismatch"
        problems.append(f"signature_trust_status_snapshot_receipt_digest_mismatch:expected={want_digest}:got={got_digest}")

    channels = _as_list_of_dicts(obj.get("publication_channels") or obj.get("channels") or [])
    channel_keys: set[tuple[str, str]] = set()
    published_times: list[datetime] = []
    for i, ch in enumerate(channels):
        if not isinstance(ch, dict):
            problems.append(f"signature_trust_status_snapshot_receipt_invalid:channel_not_object:{i}")
            continue
        cid = str(ch.get("channel_id") or "").strip()
        ctype = str(ch.get("channel_type") or "").strip()
        observed_digest = _first_nonempty_channel_digest(
            ch,
            (
                "observed_trust_status_snapshot_sha256",
                "observed_status_snapshot_sha256",
                "trust_status_snapshot_sha256",
                "status_snapshot_sha256",
            ),
        )
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", observed_digest):
            problems.append(f"signature_trust_status_snapshot_receipt_digest_mismatch:channel_missing_or_bad_observed_digest:{cid or i}")
        elif observed_digest != got_digest:
            problems.append(f"signature_trust_status_snapshot_receipt_digest_mismatch:channel={cid or i}")
        if not cid or not ctype:
            problems.append(f"signature_trust_status_snapshot_receipt_invalid:channel_missing_id_or_type:{i}")
            continue
        channel_keys.add((ctype, cid))
        published_text = str(ch.get("published_at") or ch.get("observed_at") or "").strip()
        if not published_text:
            problems.append(f"signature_trust_status_snapshot_receipt_temporal_invalid:channel_missing_published_at:{cid or i}")
            continue
        published_at = _parse_rfc3339_utc(published_text)
        if published_at is None:
            problems.append(f"signature_trust_status_snapshot_receipt_temporal_invalid:channel_published_at_unparseable:{cid or i}")
            continue
        published_times.append(published_at)
    summary["trust_status_snapshot_receipt_channel_count"] = len(channels)
    summary["trust_status_snapshot_receipt_independent_channel_count"] = len(channel_keys)

    min_raw = obj.get("minimum_independent_channels", 2)
    try:
        min_channels = int(min_raw)
    except Exception:
        min_channels = 2
        problems.append("signature_trust_status_snapshot_receipt_invalid:minimum_independent_channels_unparseable")
    if min_channels < 1:
        min_channels = 1
    if min_channels > 10:
        min_channels = 10
    summary["trust_status_snapshot_receipt_required_independent_channels"] = min_channels

    if len(channel_keys) < min_channels:
        summary["trust_status_snapshot_receipt_status"] = "channel_quorum_not_met"
        problems.append(f"signature_trust_status_snapshot_receipt_channel_quorum_not_met:valid={len(channel_keys)}:required={min_channels}")
        return problems, summary
    if not _record_publication_channel_diversity(
        summary=summary,
        problems=problems,
        field_prefix="trust_status_snapshot_receipt",
        problem_code="signature_trust_status_snapshot_receipt_channel_diversity_not_met",
        channels=channels,
        channel_keys=channel_keys,
        min_channels=min_channels,
        status_field="trust_status_snapshot_receipt_status",
    ):
        return problems, summary

    issued_at_text = str(obj.get("issued_at") or "").strip()
    valid_from_text = str(obj.get("valid_from") or "").strip()
    valid_until_text = str(obj.get("valid_until") or "").strip()
    summary["trust_status_snapshot_receipt_issued_at"] = issued_at_text[:80]
    summary["trust_status_snapshot_receipt_valid_from"] = valid_from_text[:80]
    summary["trust_status_snapshot_receipt_valid_until"] = valid_until_text[:80]

    issued_at = _parse_rfc3339_utc(issued_at_text)
    valid_from = _parse_rfc3339_utc(valid_from_text)
    valid_until = _parse_rfc3339_utc(valid_until_text)
    snapshot_this_update = _parse_rfc3339_utc(snapshot_this_update_text)
    snapshot_next_update = _parse_rfc3339_utc(snapshot_next_update_text) if snapshot_next_update_text else None

    temporal_checks_required = bool(require_receipt or verification_time is not None)
    temporal_problems_before = len(problems)
    if temporal_checks_required:
        if verification_time is None:
            problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:external_verification_time_required")
        if issued_at is None:
            summary["trust_status_snapshot_receipt_issued_at_status"] = "missing_or_invalid"
            problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:issued_at_missing_or_unparseable")
        if not valid_from_text or not valid_until_text:
            summary["trust_status_snapshot_receipt_validity_status"] = "missing"
            problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:missing_validity_window")
        elif valid_from is None or valid_until is None:
            summary["trust_status_snapshot_receipt_validity_status"] = "invalid"
            problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:validity_window_unparseable")
        if snapshot_this_update is None:
            problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:snapshot_this_update_missing_or_unparseable")

        if valid_from is not None and valid_until is not None:
            if valid_from > valid_until:
                summary["trust_status_snapshot_receipt_validity_status"] = "invalid"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:reversed_validity_window")
            elif verification_time is not None and verification_time < valid_from:
                summary["trust_status_snapshot_receipt_validity_status"] = "not_yet_valid"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:not_yet_valid")
            elif verification_time is not None and verification_time > valid_until:
                summary["trust_status_snapshot_receipt_validity_status"] = "expired"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:expired")
            else:
                summary["trust_status_snapshot_receipt_validity_status"] = "within_window"

        if issued_at is not None:
            if snapshot_this_update is not None and issued_at < snapshot_this_update:
                summary["trust_status_snapshot_receipt_issued_at_status"] = "before_snapshot_update"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:issued_before_snapshot_this_update")
            elif verification_time is not None and issued_at > verification_time:
                summary["trust_status_snapshot_receipt_issued_at_status"] = "after_verification_time"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:issued_after_verification_time")
            elif valid_from is not None and valid_until is not None and (issued_at < valid_from or issued_at > valid_until):
                summary["trust_status_snapshot_receipt_issued_at_status"] = "outside_window"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:issued_at_outside_validity_window")
            else:
                summary["trust_status_snapshot_receipt_issued_at_status"] = "coherent"

        if published_times:
            earliest = min(published_times)
            latest = max(published_times)
            earliest_s = earliest.isoformat(timespec="seconds").replace("+00:00", "Z")
            latest_s = latest.isoformat(timespec="seconds").replace("+00:00", "Z")
            summary["trust_status_snapshot_receipt_published_at_min"] = earliest_s
            summary["trust_status_snapshot_receipt_published_at_max"] = latest_s
            summary["trust_status_snapshot_receipt_earliest_published_at"] = earliest_s
            summary["trust_status_snapshot_receipt_latest_published_at"] = latest_s
            if snapshot_this_update is not None and earliest < snapshot_this_update:
                summary["trust_status_snapshot_receipt_channel_time_status"] = "before_snapshot_update"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:channel_before_snapshot_this_update")
            elif verification_time is not None and latest > verification_time:
                summary["trust_status_snapshot_receipt_channel_time_status"] = "after_verification_time"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:channel_after_verification_time")
            elif issued_at is not None and issued_at < latest:
                summary["trust_status_snapshot_receipt_channel_time_status"] = "receipt_before_latest_channel"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:receipt_issued_before_latest_channel")
            elif snapshot_next_update is not None and latest > snapshot_next_update:
                summary["trust_status_snapshot_receipt_channel_time_status"] = "after_snapshot_next_update"
                problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:channel_after_snapshot_next_update")
            else:
                summary["trust_status_snapshot_receipt_channel_time_status"] = "within_window"
        elif channels:
            summary["trust_status_snapshot_receipt_channel_time_status"] = "missing_or_invalid"
        else:
            summary["trust_status_snapshot_receipt_channel_time_status"] = "missing"
            problems.append("signature_trust_status_snapshot_receipt_temporal_invalid:no_publication_channels")

        if len(problems) == temporal_problems_before:
            summary["trust_status_snapshot_receipt_temporal_status"] = "coherent"
        else:
            summary["trust_status_snapshot_receipt_temporal_status"] = "invalid"

    summary["trust_status_snapshot_receipt_status"] = "invalid" if problems else "matched"
    return problems, summary


def _string_set(value: Any) -> set[str]:
    """Normalize a string/list field to a set of non-empty strings."""

    if isinstance(value, str):
        return {x.strip() for x in value.replace(",", ";").split(";") if x.strip()}
    if isinstance(value, list):
        return {str(x).strip() for x in value if str(x).strip()}
    return set()


def _packet_scope(packet_dir: Path) -> dict[str, str]:
    """Best-effort packet scope pulled from manifest.json."""

    out = {"election_id": "", "jurisdiction": ""}
    try:
        obj = json.loads((packet_dir / "manifest.json").read_text(encoding="utf-8"))
    except Exception:
        return out
    if not isinstance(obj, dict):
        return out
    out["election_id"] = str(obj.get("election_id") or "").strip()
    out["jurisdiction"] = str(obj.get("jurisdiction") or "").strip()
    scope = obj.get("scope") if isinstance(obj.get("scope"), dict) else {}
    if not out["election_id"] and isinstance(scope, dict):
        out["election_id"] = str(scope.get("election_id") or "").strip()
    if not out["jurisdiction"] and isinstance(scope, dict):
        out["jurisdiction"] = str(scope.get("jurisdiction") or "").strip()
    return out


def validate_signer_authorization_roster(
    packet_dir: Path,
    roster_path: Path | None,
    expected_roster_sha256: str | None,
    expected_keyset_sha256: str,
    expected_status_snapshot_sha256: str,
    keyring: dict[str, Any],
    keys: list[dict[str, Any]],
    require_roster: bool,
    verification_time: datetime | None = None,
) -> tuple[list[str], dict[str, Any], dict[str, list[dict[str, Any]]]]:
    """Validate optional external signer-role authorization evidence.

    This bounded guard answers a narrower question than signature verification:
    did the operator supply a separate, byte-pinned roster saying that the public
    keys/signers in the local trust keyset were authorized for the envelope kinds
    and roles being checked?  It does not prove employment, HR records, legal
    authority, identity-proofing adequacy, or production authorization.
    """

    summary: dict[str, Any] = {
        "signer_authorization_roster_required": bool(require_roster),
        "signer_authorization_roster_status": "not_supplied",
        "signer_authorization_roster_sha256": "",
        "signer_authorization_roster_pin_required": bool((expected_roster_sha256 or "").strip()),
        "signer_authorization_roster_pin_status": "not_supplied",
        "signer_authorization_roster_pin_sha256": "",
        "signer_authorization_roster_id": "",
        "signer_authorization_roster_profile": "",
        "signer_authorization_authority_count": 0,
        "signer_authorization_required_authority_count": 0,
        "signer_authorization_entry_count": 0,
        "signer_authorization_active_entry_count": 0,
        "signer_authorization_scope_election_id": "",
        "signer_authorization_scope_jurisdiction": "",
        "signer_authorization_roster_issued_at": "",
        "signer_authorization_roster_valid_from": "",
        "signer_authorization_roster_valid_until": "",
        "signer_authorization_roster_verification_time": (verification_time.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if isinstance(verification_time, datetime) else ""),
        "signer_authorization_roster_temporal_status": "not_checked",
        "signer_authorization_authority_observed_at_min": "",
        "signer_authorization_authority_observed_at_max": "",
        "signer_authorization_authority_observed_at_status": "not_checked",
        "signer_authorization_row_validity_status": "not_checked",
    }
    problems: list[str] = []
    index: dict[str, list[dict[str, Any]]] = {}

    expected_pin_hex: str | None = None
    if (expected_roster_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_roster_sha256))
        if expected_pin_hex is None:
            summary["signer_authorization_roster_pin_status"] = "invalid"
            summary["signer_authorization_roster_status"] = "invalid"
            problems.append("signature_signer_authorization_roster_pin_invalid:expected_sha256_malformed")
            return problems, summary, index
        summary["signer_authorization_roster_pin_sha256"] = "sha256:" + expected_pin_hex

    if roster_path is None or not str(roster_path).strip():
        if require_roster:
            summary["signer_authorization_roster_status"] = "missing"
            problems.append("signature_signer_authorization_roster_invalid:required_roster_not_supplied")
        return problems, summary, index

    if _path_inside_dir(roster_path, packet_dir):
        summary["signer_authorization_roster_status"] = "packet_contained_rejected"
        problems.append("signature_signer_authorization_roster_untrusted_location:packet_contained")
        return problems, summary, index

    try:
        b = roster_path.read_bytes()
    except Exception as e:
        summary["signer_authorization_roster_status"] = "invalid"
        problems.append(f"signature_signer_authorization_roster_invalid:read_failed:{type(e).__name__}")
        return problems, summary, index

    actual_hex = sha256_hex_bytes(b)
    summary["signer_authorization_roster_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["signer_authorization_roster_pin_status"] = "mismatched"
            summary["signer_authorization_roster_status"] = "mismatched"
            problems.append(f"signature_signer_authorization_roster_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}")
            return problems, summary, index
        summary["signer_authorization_roster_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["signer_authorization_roster_status"] = "invalid"
        problems.append(f"signature_signer_authorization_roster_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary, index
    if not isinstance(obj, dict):
        summary["signer_authorization_roster_status"] = "invalid"
        problems.append("signature_signer_authorization_roster_invalid:not_object")
        return problems, summary, index

    roster_id = str(obj.get("roster_id") or obj.get("authorization_roster_id") or "").strip()
    profile = str(obj.get("profile") or "").strip()
    status = str(obj.get("status") or "current").strip().lower()
    summary["signer_authorization_roster_id"] = roster_id[:200]
    summary["signer_authorization_roster_profile"] = profile
    if profile != SIGNER_AUTHORIZATION_ROSTER_PROFILE:
        problems.append(f"signature_signer_authorization_roster_invalid:unsupported_profile:{profile or 'missing'}")
    if status not in {"active", "current"}:
        summary["signer_authorization_roster_status"] = "stale_superseded"
        problems.append(f"signature_signer_authorization_not_active:roster_status={status or 'missing'}")
    if obj.get("superseded_by") or obj.get("superseded_at"):
        summary["signer_authorization_roster_status"] = "stale_superseded"
        problems.append("signature_signer_authorization_not_active:superseded_marker_present")

    # A byte-pinned authorization roster is still unsafe if it can silently act as
    # a stale, future-dated, or open-ended authorization record.  The stricter
    # profile therefore treats the roster as temporal evidence: its own issuance
    # and validity window must be coherent with the externally supplied verifier
    # time.  This does not prove real employment or legal authority; it merely
    # prevents a local synthetic roster from time-traveling.
    issue_raw = str(obj.get("issued_at") or "").strip()
    valid_from_raw = str(obj.get("valid_from") or "").strip()
    valid_until_raw = str(obj.get("valid_until") or "").strip()
    summary["signer_authorization_roster_issued_at"] = issue_raw[:64]
    summary["signer_authorization_roster_valid_from"] = valid_from_raw[:64]
    summary["signer_authorization_roster_valid_until"] = valid_until_raw[:64]
    vt = verification_time.astimezone(timezone.utc) if isinstance(verification_time, datetime) else None
    issue_dt = _parse_rfc3339_utc(issue_raw) if issue_raw else None
    valid_from_dt = _parse_rfc3339_utc(valid_from_raw) if valid_from_raw else None
    valid_until_dt = _parse_rfc3339_utc(valid_until_raw) if valid_until_raw else None
    temporal_problem_count = 0
    if require_roster:
        if vt is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:verification_time_required")
        if not issue_raw or issue_dt is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:issued_at_missing_or_unparseable")
        if not valid_from_raw or valid_from_dt is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:valid_from_missing_or_unparseable")
        if not valid_until_raw or valid_until_dt is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:valid_until_missing_or_unparseable")
        if valid_from_dt is not None and valid_until_dt is not None and valid_from_dt > valid_until_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:valid_from_after_valid_until")
        if issue_dt is not None and valid_until_dt is not None and issue_dt > valid_until_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:issued_after_valid_until")
        if vt is not None and issue_dt is not None and issue_dt > vt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:issued_at_after_verification_time")
        if vt is not None and valid_from_dt is not None and vt < valid_from_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:verification_time_before_valid_from")
        if vt is not None and valid_until_dt is not None and vt > valid_until_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_temporal_invalid:verification_time_after_valid_until")
        if temporal_problem_count:
            summary["signer_authorization_roster_temporal_status"] = "invalid"
            summary["signer_authorization_roster_status"] = "temporal_invalid"
        else:
            summary["signer_authorization_roster_temporal_status"] = "within_window"

    want_keyset = str(expected_keyset_sha256 or "").strip().lower()
    got_keyset = str(obj.get("trust_keyset_sha256") or obj.get("keyset_sha256") or "").strip().lower()
    if want_keyset:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_keyset):
            problems.append("signature_signer_authorization_key_mismatch:missing_or_bad_trust_keyset_sha256")
        elif got_keyset != want_keyset:
            summary["signer_authorization_roster_status"] = "keyset_mismatch"
            problems.append(f"signature_signer_authorization_key_mismatch:expected_keyset={want_keyset}:got={got_keyset}")

    want_status = str(expected_status_snapshot_sha256 or "").strip().lower()
    got_status = str(obj.get("trust_status_snapshot_sha256") or obj.get("status_snapshot_sha256") or "").strip().lower()
    if want_status or got_status:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_status):
            problems.append("signature_signer_authorization_key_mismatch:missing_or_bad_trust_status_snapshot_sha256")
        elif want_status and got_status != want_status:
            summary["signer_authorization_roster_status"] = "status_snapshot_mismatch"
            problems.append(f"signature_signer_authorization_key_mismatch:expected_status_snapshot={want_status}:got={got_status}")

    scope = obj.get("scope") if isinstance(obj.get("scope"), dict) else {}
    roster_election = str(scope.get("election_id") or obj.get("election_id") or "").strip()
    roster_jurisdiction = str(scope.get("jurisdiction") or obj.get("jurisdiction") or "").strip()
    summary["signer_authorization_scope_election_id"] = roster_election[:120]
    summary["signer_authorization_scope_jurisdiction"] = roster_jurisdiction[:120]
    keyring_scope = keyring.get("scope") if isinstance(keyring.get("scope"), dict) else {}
    packet_scope = _packet_scope(packet_dir)
    for field, roster_v in (("election_id", roster_election), ("jurisdiction", roster_jurisdiction)):
        kr_v = str(keyring_scope.get(field) or "").strip() if isinstance(keyring_scope, dict) else ""
        pkt_v = str(packet_scope.get(field) or "").strip()
        if kr_v and roster_v and kr_v != roster_v:
            problems.append(f"signature_signer_authorization_scope_mismatch:keyring:{field}")
        if pkt_v and roster_v and pkt_v != roster_v:
            problems.append(f"signature_signer_authorization_scope_mismatch:packet:{field}")

    authorities = _as_list_of_dicts(obj.get("authorities") or obj.get("authorization_authorities") or [])
    authority_keys: set[tuple[str, str]] = set()
    authority_observation_times: list[datetime] = []
    authority_temporal_problem_count = 0
    for i, auth in enumerate(authorities):
        aid = str(auth.get("authority_id") or auth.get("id") or "").strip()
        atype = str(auth.get("authority_type") or auth.get("type") or "").strip()
        if not aid or not atype:
            problems.append(f"signature_signer_authorization_roster_invalid:authority_missing_id_or_type:{i}")
            continue
        observed_raw = str(auth.get("observed_at") or auth.get("attested_at") or "").strip()
        observed_dt = _parse_rfc3339_utc(observed_raw) if observed_raw else None
        if require_roster:
            if not observed_raw or observed_dt is None:
                authority_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_temporal_invalid:authority_observed_at_missing_or_unparseable:{i}")
            else:
                authority_observation_times.append(observed_dt)
                if issue_dt is not None and observed_dt > issue_dt:
                    authority_temporal_problem_count += 1
                    problems.append(f"signature_signer_authorization_roster_temporal_invalid:authority_observed_after_roster_issued:{i}")
                if vt is not None and observed_dt > vt:
                    authority_temporal_problem_count += 1
                    problems.append(f"signature_signer_authorization_roster_temporal_invalid:authority_observed_after_verification_time:{i}")
        authority_keys.add((atype, aid))
    if authority_observation_times:
        summary["signer_authorization_authority_observed_at_min"] = min(authority_observation_times).isoformat(timespec="seconds").replace("+00:00", "Z")
        summary["signer_authorization_authority_observed_at_max"] = max(authority_observation_times).isoformat(timespec="seconds").replace("+00:00", "Z")
    if require_roster:
        if authority_temporal_problem_count:
            summary["signer_authorization_authority_observed_at_status"] = "invalid"
            if summary.get("signer_authorization_roster_status") == "not_supplied":
                summary["signer_authorization_roster_status"] = "temporal_invalid"
        else:
            summary["signer_authorization_authority_observed_at_status"] = "coherent"
    min_auth_raw = obj.get("minimum_authorities", obj.get("minimum_authorization_authorities", 2))
    try:
        min_auth = int(min_auth_raw)
    except Exception:
        min_auth = 2
        problems.append("signature_signer_authorization_roster_invalid:minimum_authorities_unparseable")
    if min_auth < 1:
        min_auth = 1
    if min_auth > 10:
        min_auth = 10
    summary["signer_authorization_authority_count"] = len(authority_keys)
    summary["signer_authorization_required_authority_count"] = min_auth
    if len(authority_keys) < min_auth:
        summary["signer_authorization_roster_status"] = "authority_quorum_not_met"
        problems.append(f"signature_signer_authorization_authority_quorum_not_met:valid={len(authority_keys)}:required={min_auth}")

    auth_rows = _as_list_of_dicts(obj.get("authorizations") or obj.get("signer_authorizations") or [])
    summary["signer_authorization_entry_count"] = len(auth_rows)
    active_statuses = {"active", "current", "authorized", "valid"}
    inactive_statuses = {"revoked", "suspended", "disabled", "expired", "retired", "superseded"}
    active_count = 0
    for i, row in enumerate(auth_rows):
        kid = str(row.get("kid") or row.get("key_id") or "").strip()
        signer_id = str(row.get("signer_id") or row.get("subject_id") or "").strip()
        row_status = str(row.get("status") or "active").strip().lower()
        row_scope = row.get("scope") if isinstance(row.get("scope"), dict) else {}
        row_election = str(row_scope.get("election_id") or row.get("election_id") or roster_election or "").strip()
        row_jurisdiction = str(row_scope.get("jurisdiction") or row.get("jurisdiction") or roster_jurisdiction or "").strip()
        if not kid:
            problems.append(f"signature_signer_authorization_roster_invalid:authorization_missing_kid:{i}")
            continue
        if row_status not in active_statuses and row_status not in inactive_statuses:
            problems.append(f"signature_signer_authorization_not_active:{kid}:{row_status or 'missing'}")
            continue
        if row_election and roster_election and row_election != roster_election:
            problems.append(f"signature_signer_authorization_scope_mismatch:authorization:{kid}:election_id")
        if row_jurisdiction and roster_jurisdiction and row_jurisdiction != roster_jurisdiction:
            problems.append(f"signature_signer_authorization_scope_mismatch:authorization:{kid}:jurisdiction")
        if row_status in active_statuses and require_roster:
            row_from_raw = str(row.get("authorized_from") or row.get("valid_from") or "").strip()
            row_until_raw = str(row.get("authorized_until") or row.get("valid_to") or "").strip()
            row_from_dt = _parse_rfc3339_utc(row_from_raw) if row_from_raw else None
            row_until_dt = _parse_rfc3339_utc(row_until_raw) if row_until_raw else None
            if not row_from_raw or row_from_dt is None:
                problems.append(f"signature_signer_authorization_time_invalid:{kid}:authorization_valid_from_missing_or_unparseable")
            if not row_until_raw or row_until_dt is None:
                problems.append(f"signature_signer_authorization_time_invalid:{kid}:authorization_valid_until_missing_or_unparseable")
            if row_from_dt is not None and row_until_dt is not None and row_from_dt > row_until_dt:
                problems.append(f"signature_signer_authorization_time_invalid:{kid}:authorization_valid_from_after_valid_until")
        normalized = dict(row)
        normalized["kid"] = kid
        normalized["signer_id"] = signer_id
        normalized["_row_status"] = row_status
        normalized["_election_id"] = row_election
        normalized["_jurisdiction"] = row_jurisdiction
        normalized["_authorization_id"] = str(row.get("authorization_id") or row.get("id") or kid).strip()
        normalized["_authorized_kinds"] = _string_set(row.get("authorized_kinds") or row.get("allowed_kinds") or row.get("kinds"))
        normalized["_authorized_roles"] = _string_set(row.get("authorized_roles") or row.get("roles") or row.get("role"))
        normalized["_public_key_sha256"] = str(row.get("public_key_sha256") or "").strip().lower()
        index.setdefault(kid, []).append(normalized)
        if row_status in active_statuses:
            active_count += 1
    summary["signer_authorization_active_entry_count"] = active_count
    if require_roster:
        if any(str(p).startswith("signature_signer_authorization_time_invalid:") for p in problems):
            summary["signer_authorization_row_validity_status"] = "invalid"
        else:
            summary["signer_authorization_row_validity_status"] = "coherent"

    for key in keys:
        key_status = str(key.get("status") or "active").strip().lower()
        if key_status not in {"active", "valid"}:
            continue
        kid = str(key.get("kid") or "").strip()
        signer_id = str(key.get("signer_id") or "").strip()
        expected_pk_sha = _public_key_material_sha256_from_key(key)
        candidate_rows = [r for r in index.get(kid, []) if str(r.get("_row_status") or "").lower() in active_statuses]
        if not candidate_rows:
            problems.append(f"signature_signer_authorization_missing:{kid}")
            continue
        if signer_id and not any((not r.get("signer_id") or r.get("signer_id") == signer_id) for r in candidate_rows):
            problems.append(f"signature_signer_authorization_key_mismatch:{kid}:signer_id")
        if expected_pk_sha and not any((not r.get("_public_key_sha256") or r.get("_public_key_sha256") == expected_pk_sha) for r in candidate_rows):
            problems.append(f"signature_signer_authorization_key_mismatch:{kid}:public_key_sha256")

    if problems and summary["signer_authorization_roster_status"] == "not_supplied":
        summary["signer_authorization_roster_status"] = "invalid"
    elif not problems:
        summary["signer_authorization_roster_status"] = "matched"
    return problems, summary, index


def validate_signer_authorization_roster_publication_receipt(
    packet_dir: Path,
    receipt_path: Path | None,
    expected_roster_sha256: str,
    require_receipt: bool,
    expected_receipt_sha256: str | None = None,
    verification_time: datetime | None = None,
    roster_summary: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate an optional external publication receipt for signer-authorization roster bytes.

    This bounded local guard proves only that the verifier was given a separate
    JSON receipt, outside the packet being authenticated, whose bytes bind the
    supplied signer-authorization roster digest to distinct synthetic publication
    channels.  In the strict synthetic profile it also checks identity and
    temporal coherence against the already-validated roster summary so an old or
    mismatched roster-publication receipt cannot be replayed as current
    authorization evidence. It does not prove signer employment, legal delegation,
    HR identity proofing, trusted timestamping, or production authorization.
    """

    if verification_time is not None:
        if verification_time.tzinfo is None:
            verification_time = verification_time.replace(tzinfo=timezone.utc)
        verification_time = verification_time.astimezone(timezone.utc)
    verification_time_s = verification_time.isoformat(timespec="seconds").replace("+00:00", "Z") if verification_time else ""
    roster_s = roster_summary if isinstance(roster_summary, dict) else {}
    expected_roster_id = str(roster_s.get("signer_authorization_roster_id") or "").strip()
    expected_roster_issued_at = str(roster_s.get("signer_authorization_roster_issued_at") or "").strip()
    expected_roster_valid_from = str(roster_s.get("signer_authorization_roster_valid_from") or "").strip()
    expected_roster_valid_until = str(roster_s.get("signer_authorization_roster_valid_until") or "").strip()

    summary: dict[str, Any] = {
        "signer_authorization_roster_receipt_required": bool(require_receipt),
        "signer_authorization_roster_receipt_status": "not_supplied",
        "signer_authorization_roster_receipt_sha256": "",
        "signer_authorization_roster_receipt_pin_required": bool((expected_receipt_sha256 or "").strip()),
        "signer_authorization_roster_receipt_pin_status": "not_supplied",
        "signer_authorization_roster_receipt_pin_sha256": "",
        "signer_authorization_roster_receipt_id": "",
        "signer_authorization_roster_receipt_profile": "",
        "signer_authorization_roster_receipt_channel_count": 0,
        "signer_authorization_roster_receipt_independent_channel_count": 0,
        "signer_authorization_roster_receipt_required_independent_channels": 0,
        "signer_authorization_roster_receipt_roster_id_status": "not_checked",
        "signer_authorization_roster_receipt_roster_issued_at_status": "not_checked",
        "signer_authorization_roster_receipt_validity_status": "not_checked",
        "signer_authorization_roster_receipt_valid_from": "",
        "signer_authorization_roster_receipt_valid_until": "",
        "signer_authorization_roster_receipt_issued_at": "",
        "signer_authorization_roster_receipt_issued_at_status": "not_checked",
        "signer_authorization_roster_receipt_channel_time_status": "not_checked",
        "signer_authorization_roster_receipt_temporal_status": "not_checked",
        "signer_authorization_roster_receipt_temporal_roster_issued_at": expected_roster_issued_at[:80],
        "signer_authorization_roster_receipt_temporal_roster_valid_from": expected_roster_valid_from[:80],
        "signer_authorization_roster_receipt_temporal_roster_valid_until": expected_roster_valid_until[:80],
        "signer_authorization_roster_receipt_published_at_min": "",
        "signer_authorization_roster_receipt_published_at_max": "",
        "signer_authorization_roster_receipt_earliest_published_at": "",
        "signer_authorization_roster_receipt_latest_published_at": "",
        "signer_authorization_roster_receipt_external_verification_time": verification_time_s,
    }
    problems: list[str] = []

    expected_pin_hex: str | None = None
    if (expected_receipt_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_receipt_sha256))
        if expected_pin_hex is None:
            summary["signer_authorization_roster_receipt_pin_status"] = "invalid"
            summary["signer_authorization_roster_receipt_status"] = "invalid"
            problems.append("signature_signer_authorization_roster_receipt_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["signer_authorization_roster_receipt_pin_sha256"] = "sha256:" + expected_pin_hex

    want_digest = str(expected_roster_sha256 or "").strip().lower()
    receipt_requested = bool(require_receipt or receipt_path is not None or expected_pin_hex is not None)
    if receipt_requested and not re.fullmatch(r"sha256:[0-9a-f]{64}", want_digest):
        summary["signer_authorization_roster_receipt_status"] = "invalid"
        problems.append("signature_signer_authorization_roster_receipt_invalid:roster_digest_not_available")
        return problems, summary

    if receipt_path is None or not str(receipt_path).strip():
        if require_receipt:
            summary["signer_authorization_roster_receipt_status"] = "missing"
            problems.append("signature_signer_authorization_roster_receipt_invalid:required_receipt_not_supplied")
        return problems, summary

    if _path_inside_dir(receipt_path, packet_dir):
        summary["signer_authorization_roster_receipt_status"] = "packet_contained_rejected"
        problems.append("signature_signer_authorization_roster_receipt_untrusted_location:packet_contained")
        return problems, summary

    try:
        b = receipt_path.read_bytes()
    except Exception as e:
        summary["signer_authorization_roster_receipt_status"] = "invalid"
        problems.append(f"signature_signer_authorization_roster_receipt_invalid:read_failed:{type(e).__name__}")
        return problems, summary

    actual_hex = sha256_hex_bytes(b)
    summary["signer_authorization_roster_receipt_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["signer_authorization_roster_receipt_pin_status"] = "mismatched"
            summary["signer_authorization_roster_receipt_status"] = "mismatched"
            problems.append(f"signature_signer_authorization_roster_receipt_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}")
            return problems, summary
        summary["signer_authorization_roster_receipt_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["signer_authorization_roster_receipt_status"] = "invalid"
        problems.append(f"signature_signer_authorization_roster_receipt_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary
    if not isinstance(obj, dict):
        summary["signer_authorization_roster_receipt_status"] = "invalid"
        problems.append("signature_signer_authorization_roster_receipt_invalid:not_object")
        return problems, summary

    profile = str(obj.get("profile") or "").strip()
    receipt_id = str(obj.get("receipt_id") or "").strip()
    summary["signer_authorization_roster_receipt_profile"] = profile
    summary["signer_authorization_roster_receipt_id"] = receipt_id[:200]
    if profile != SIGNER_AUTHORIZATION_ROSTER_RECEIPT_PROFILE:
        problems.append(f"signature_signer_authorization_roster_receipt_invalid:unsupported_profile:{profile or 'missing'}")

    got_roster_id = str(obj.get("signer_authorization_roster_id") or obj.get("authorization_roster_id") or "").strip()
    if require_receipt or expected_roster_id:
        if not got_roster_id or not expected_roster_id:
            summary["signer_authorization_roster_receipt_roster_id_status"] = "missing"
            problems.append("signature_signer_authorization_roster_receipt_identity_mismatch:roster_id_missing")
        elif got_roster_id != expected_roster_id:
            summary["signer_authorization_roster_receipt_roster_id_status"] = "mismatched"
            problems.append(f"signature_signer_authorization_roster_receipt_identity_mismatch:expected_roster_id={expected_roster_id}:got={got_roster_id}")
        else:
            summary["signer_authorization_roster_receipt_roster_id_status"] = "matched"

    got_digest = str(
        obj.get("signer_authorization_roster_sha256")
        or obj.get("authorization_roster_sha256")
        or obj.get("roster_sha256")
        or ""
    ).strip().lower()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_digest):
        problems.append("signature_signer_authorization_roster_receipt_digest_mismatch:missing_or_bad_signer_authorization_roster_sha256")
    elif want_digest and got_digest != want_digest:
        summary["signer_authorization_roster_receipt_status"] = "digest_mismatch"
        problems.append(f"signature_signer_authorization_roster_receipt_digest_mismatch:expected={want_digest}:got={got_digest}")

    receipt_issued_raw = str(obj.get("issued_at") or "").strip()
    valid_from_raw = str(obj.get("valid_from") or "").strip()
    valid_until_raw = str(obj.get("valid_until") or "").strip()
    got_roster_issued_raw = str(obj.get("signer_authorization_roster_issued_at") or obj.get("authorization_roster_issued_at") or "").strip()
    summary["signer_authorization_roster_receipt_issued_at"] = receipt_issued_raw[:80]
    summary["signer_authorization_roster_receipt_valid_from"] = valid_from_raw[:80]
    summary["signer_authorization_roster_receipt_valid_until"] = valid_until_raw[:80]

    receipt_issued_dt = _parse_rfc3339_utc(receipt_issued_raw) if receipt_issued_raw else None
    valid_from_dt = _parse_rfc3339_utc(valid_from_raw) if valid_from_raw else None
    valid_until_dt = _parse_rfc3339_utc(valid_until_raw) if valid_until_raw else None
    expected_roster_issued_dt = _parse_rfc3339_utc(expected_roster_issued_at) if expected_roster_issued_at else None
    got_roster_issued_dt = _parse_rfc3339_utc(got_roster_issued_raw) if got_roster_issued_raw else None

    temporal_problem_count = 0
    if require_receipt:
        if verification_time is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:verification_time_required")
        if not receipt_issued_raw or receipt_issued_dt is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:issued_at_missing_or_unparseable")
        if not valid_from_raw or valid_from_dt is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:valid_from_missing_or_unparseable")
        if not valid_until_raw or valid_until_dt is None:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:valid_until_missing_or_unparseable")
        if valid_from_dt is not None and valid_until_dt is not None and valid_from_dt > valid_until_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:valid_from_after_valid_until")
        if verification_time is not None and valid_from_dt is not None and verification_time < valid_from_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:verification_time_before_valid_from")
        if verification_time is not None and valid_until_dt is not None and verification_time > valid_until_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:verification_time_after_valid_until")
        if verification_time is not None and receipt_issued_dt is not None and receipt_issued_dt > verification_time:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:issued_at_after_verification_time")
        if expected_roster_issued_at:
            if not got_roster_issued_raw or got_roster_issued_dt is None:
                temporal_problem_count += 1
                summary["signer_authorization_roster_receipt_roster_issued_at_status"] = "missing"
                problems.append("signature_signer_authorization_roster_receipt_identity_mismatch:roster_issued_at_missing_or_unparseable")
            elif got_roster_issued_raw != expected_roster_issued_at:
                temporal_problem_count += 1
                summary["signer_authorization_roster_receipt_roster_issued_at_status"] = "mismatched"
                problems.append("signature_signer_authorization_roster_receipt_identity_mismatch:roster_issued_at")
            else:
                summary["signer_authorization_roster_receipt_roster_issued_at_status"] = "matched"
        if expected_roster_issued_dt is not None and receipt_issued_dt is not None and receipt_issued_dt < expected_roster_issued_dt:
            temporal_problem_count += 1
            problems.append("signature_signer_authorization_roster_receipt_temporal_invalid:receipt_issued_before_roster_issued_at")

    channels = _as_list_of_dicts(obj.get("publication_channels") or obj.get("channels") or [])
    channel_keys: set[tuple[str, str]] = set()
    published_times: list[datetime] = []
    channel_temporal_problem_count = 0
    for i, ch in enumerate(channels):
        cid = str(ch.get("channel_id") or "").strip()
        ctype = str(ch.get("channel_type") or "").strip()
        observed_digest = _first_nonempty_channel_digest(
            ch,
            (
                "observed_signer_authorization_roster_sha256",
                "signer_authorization_roster_sha256",
                "authorization_roster_sha256",
                "roster_sha256",
            ),
        )
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", observed_digest):
            problems.append(f"signature_signer_authorization_roster_receipt_digest_mismatch:channel_missing_or_bad_observed_digest:{cid or i}")
        elif observed_digest != got_digest:
            problems.append(f"signature_signer_authorization_roster_receipt_digest_mismatch:channel={cid or i}")
        if not cid or not ctype:
            problems.append(f"signature_signer_authorization_roster_receipt_invalid:channel_missing_id_or_type:{i}")
            continue
        channel_keys.add((ctype, cid))
        if require_receipt:
            published_text = str(ch.get("published_at") or ch.get("observed_at") or "").strip()
            if not published_text:
                channel_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_receipt_temporal_invalid:channel_missing_published_at:{cid or i}")
                continue
            published_at = _parse_rfc3339_utc(published_text)
            if published_at is None:
                channel_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_receipt_temporal_invalid:channel_published_at_unparseable:{cid or i}")
                continue
            published_times.append(published_at)
            if expected_roster_issued_dt is not None and published_at < expected_roster_issued_dt:
                channel_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_receipt_temporal_invalid:channel_before_roster_issued_at:{cid or i}")
            if receipt_issued_dt is not None and published_at > receipt_issued_dt:
                channel_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_receipt_temporal_invalid:channel_after_receipt_issued_at:{cid or i}")
            if verification_time is not None and published_at > verification_time:
                channel_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_receipt_temporal_invalid:channel_after_verification_time:{cid or i}")
            if valid_from_dt is not None and published_at < valid_from_dt:
                channel_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_receipt_temporal_invalid:channel_before_receipt_valid_from:{cid or i}")
            if valid_until_dt is not None and published_at > valid_until_dt:
                channel_temporal_problem_count += 1
                problems.append(f"signature_signer_authorization_roster_receipt_temporal_invalid:channel_after_receipt_valid_until:{cid or i}")
    summary["signer_authorization_roster_receipt_channel_count"] = len(channels)
    summary["signer_authorization_roster_receipt_independent_channel_count"] = len(channel_keys)

    if require_receipt:
        summary["signer_authorization_roster_receipt_issued_at_status"] = "invalid" if any(str(p).startswith("signature_signer_authorization_roster_receipt_temporal_invalid:issued_at") for p in problems) else "coherent"
        if valid_from_dt is not None and valid_until_dt is not None and verification_time is not None and valid_from_dt <= verification_time <= valid_until_dt:
            summary["signer_authorization_roster_receipt_validity_status"] = "within_window"
        elif valid_from_raw or valid_until_raw:
            summary["signer_authorization_roster_receipt_validity_status"] = "outside_window"
        else:
            summary["signer_authorization_roster_receipt_validity_status"] = "invalid"
        if published_times:
            summary["signer_authorization_roster_receipt_published_at_min"] = min(published_times).isoformat(timespec="seconds").replace("+00:00", "Z")
            summary["signer_authorization_roster_receipt_published_at_max"] = max(published_times).isoformat(timespec="seconds").replace("+00:00", "Z")
            summary["signer_authorization_roster_receipt_earliest_published_at"] = summary["signer_authorization_roster_receipt_published_at_min"]
            summary["signer_authorization_roster_receipt_latest_published_at"] = summary["signer_authorization_roster_receipt_published_at_max"]
        summary["signer_authorization_roster_receipt_channel_time_status"] = "invalid" if channel_temporal_problem_count else "within_window"
        summary["signer_authorization_roster_receipt_temporal_status"] = "invalid" if temporal_problem_count or channel_temporal_problem_count else "coherent"

    min_raw = obj.get("minimum_independent_channels", 2)
    try:
        min_channels = int(min_raw)
    except Exception:
        min_channels = 2
        problems.append("signature_signer_authorization_roster_receipt_invalid:minimum_independent_channels_unparseable")
    if min_channels < 1:
        min_channels = 1
    if min_channels > 10:
        min_channels = 10
    summary["signer_authorization_roster_receipt_required_independent_channels"] = min_channels

    if len(channel_keys) < min_channels:
        summary["signer_authorization_roster_receipt_status"] = "channel_quorum_not_met"
        problems.append(f"signature_signer_authorization_roster_receipt_channel_quorum_not_met:valid={len(channel_keys)}:required={min_channels}")
        return problems, summary
    if not _record_publication_channel_diversity(
        summary=summary,
        problems=problems,
        field_prefix="signer_authorization_roster_receipt",
        problem_code="signature_signer_authorization_roster_receipt_channel_diversity_not_met",
        channels=channels,
        channel_keys=channel_keys,
        min_channels=min_channels,
        status_field="signer_authorization_roster_receipt_status",
    ):
        return problems, summary

    if any(str(p).startswith("signature_signer_authorization_roster_receipt_temporal_invalid:") for p in problems):
        summary["signer_authorization_roster_receipt_status"] = "temporal_invalid"
    elif any(str(p).startswith("signature_signer_authorization_roster_receipt_identity_mismatch:") for p in problems):
        summary["signer_authorization_roster_receipt_status"] = "identity_mismatch"
    else:
        summary["signer_authorization_roster_receipt_status"] = "invalid" if problems else "matched"
    return problems, summary

def _authorization_allows_key_for_envelope(
    authorization_index: dict[str, list[dict[str, Any]]] | None,
    key: dict[str, Any],
    env: dict[str, Any],
    env_name: str,
) -> list[str]:
    """Return fail-closed signer-authorization problems for one key/envelope."""

    if not authorization_index:
        return []
    kid = str(key.get("kid") or "").strip()
    signer_id = str(key.get("signer_id") or "").strip()
    if not kid:
        return [f"signature_signer_authorization_missing:{env_name}:kid_missing"]
    rows = authorization_index.get(kid) or []
    if not rows:
        return [f"signature_signer_authorization_missing:{env_name}:{kid}"]

    env_kind = str(env.get("kind") or "").strip()
    issued_at = _parse_rfc3339_utc(str(env.get("issued_at") or ""))
    env_subject = env.get("subject") if isinstance(env.get("subject"), dict) else {}
    env_election = str(env_subject.get("election_id") or "").strip() if isinstance(env_subject, dict) else ""
    env_jurisdiction = str(env_subject.get("jurisdiction") or "").strip() if isinstance(env_subject, dict) else ""
    key_roles = _string_set(key.get("roles") or key.get("role"))
    expected_pk_sha = _public_key_material_sha256_from_key(key)
    active_statuses = {"active", "current", "authorized", "valid"}
    inactive_statuses = {"revoked", "suspended", "disabled", "expired", "retired", "superseded"}

    saw_kind_problem = False
    saw_role_problem = False
    saw_key_problem = False
    saw_time_problem = False
    saw_scope_problem = False
    saw_inactive_problem = False
    for row in rows:
        row_status = str(row.get("_row_status") or row.get("status") or "active").strip().lower()
        if row_status in inactive_statuses or row_status not in active_statuses:
            saw_inactive_problem = True
            continue
        if signer_id and row.get("signer_id") and str(row.get("signer_id")) != signer_id:
            saw_key_problem = True
            continue
        row_pk_sha = str(row.get("_public_key_sha256") or "").strip().lower()
        if row_pk_sha and expected_pk_sha and row_pk_sha != expected_pk_sha:
            saw_key_problem = True
            continue
        authorized_kinds = row.get("_authorized_kinds") if isinstance(row.get("_authorized_kinds"), set) else _string_set(row.get("authorized_kinds") or row.get("allowed_kinds"))
        if authorized_kinds and "*" not in authorized_kinds and env_kind not in authorized_kinds:
            saw_kind_problem = True
            continue
        authorized_roles = row.get("_authorized_roles") if isinstance(row.get("_authorized_roles"), set) else _string_set(row.get("authorized_roles") or row.get("roles"))
        if authorized_roles and key_roles and not (authorized_roles & key_roles):
            saw_role_problem = True
            continue
        nb_raw = str(row.get("authorized_from") or row.get("valid_from") or "").strip()
        na_raw = str(row.get("authorized_until") or row.get("valid_to") or "").strip()
        nb = _parse_rfc3339_utc(nb_raw) if nb_raw else None
        na = _parse_rfc3339_utc(na_raw) if na_raw else None
        if nb_raw and nb is None:
            saw_time_problem = True
            continue
        if na_raw and na is None:
            saw_time_problem = True
            continue
        if issued_at is None and (nb or na):
            saw_time_problem = True
            continue
        if issued_at is not None and nb is not None and issued_at < nb:
            saw_time_problem = True
            continue
        if issued_at is not None and na is not None and issued_at > na:
            saw_time_problem = True
            continue
        row_election = str(row.get("_election_id") or "").strip()
        row_jurisdiction = str(row.get("_jurisdiction") or "").strip()
        if row_election and env_election and row_election != env_election:
            saw_scope_problem = True
            continue
        if row_jurisdiction and env_jurisdiction and row_jurisdiction != env_jurisdiction:
            saw_scope_problem = True
            continue
        return []

    out: list[str] = []
    if saw_inactive_problem:
        out.append(f"signature_signer_authorization_not_active:{env_name}:{kid}")
    if saw_key_problem:
        out.append(f"signature_signer_authorization_key_mismatch:{env_name}:{kid}")
    if saw_kind_problem:
        out.append(f"signature_signer_authorization_kind_not_allowed:{env_name}:{kid}:{env_kind or 'missing_kind'}")
    if saw_role_problem:
        out.append(f"signature_signer_authorization_role_mismatch:{env_name}:{kid}")
    if saw_time_problem:
        out.append(f"signature_signer_authorization_time_invalid:{env_name}:{kid}")
    if saw_scope_problem:
        out.append(f"signature_signer_authorization_scope_mismatch:{env_name}:{kid}")
    if not out:
        out.append(f"signature_signer_authorization_missing:{env_name}:{kid}")
    return out

def enforce_strict_local_trust_chain_profile(summary: dict[str, Any], require_signer_authorization: bool = False) -> list[str]:
    """Fail closed unless the local authenticated path has all strict-chain controls.

    This is not a production trust policy. It is a safer local profile for examples
    and operators who want to prevent a one-key or missing-status invocation from
    being confused with the full synthetic governance/status chain.
    """

    requirements = {
        "external_trust_keyset": summary.get("trust_keyset_location") == "external_to_packet",
        "trust_keyset_pin_matched": summary.get("trust_keyset_pin_status") == "matched",
        "trust_keyset_receipt_matched": summary.get("trust_keyset_receipt_status") == "matched",
        "trust_keyset_receipt_pin_matched": summary.get("trust_keyset_receipt_pin_status") == "matched",
        "trust_governance_bundle_matched": summary.get("trust_governance_bundle_status") == "matched",
        "trust_governance_bundle_pin_matched": summary.get("trust_governance_bundle_pin_status") == "matched",
        "trust_governance_bundle_receipt_matched": summary.get("trust_governance_bundle_receipt_status") == "matched",
        "trust_governance_bundle_receipt_pin_matched": summary.get("trust_governance_bundle_receipt_pin_status") == "matched",
        "trust_status_snapshot_matched": summary.get("trust_status_snapshot_status") == "matched",
        "trust_status_snapshot_pin_matched": summary.get("trust_status_snapshot_pin_status") == "matched",
        "trust_status_snapshot_receipt_matched": summary.get("trust_status_snapshot_receipt_status") == "matched",
        "trust_status_snapshot_receipt_pin_matched": summary.get("trust_status_snapshot_receipt_pin_status") == "matched",
        "trust_status_snapshot_receipt_temporal_coherent": summary.get("trust_status_snapshot_receipt_temporal_status") == "coherent",
        "signature_threshold_at_least_2": int((summary.get("policy") or {}).get("minimum_distinct_valid_signatures_per_envelope") or 0) >= 2,
        "governance_witness_quorum_at_least_3": int(summary.get("trust_governance_witness_count") or 0) >= 3,
        "status_authority_quorum_at_least_2": int(summary.get("trust_status_snapshot_authority_count") or 0) >= 2,
    }
    if require_signer_authorization:
        requirements.update({
            "signer_authorization_roster_matched": summary.get("signer_authorization_roster_status") == "matched",
            "signer_authorization_roster_pin_matched": summary.get("signer_authorization_roster_pin_status") == "matched",
            "signer_authorization_roster_receipt_matched": summary.get("signer_authorization_roster_receipt_status") == "matched",
            "signer_authorization_roster_receipt_pin_matched": summary.get("signer_authorization_roster_receipt_pin_status") == "matched",
            "signer_authorization_roster_receipt_quorum_at_least_2": int(summary.get("signer_authorization_roster_receipt_independent_channel_count") or 0) >= 2,
            "signer_authorization_roster_receipt_identity_matched": summary.get("signer_authorization_roster_receipt_roster_id_status") == "matched",
            "signer_authorization_roster_receipt_temporal_coherent": summary.get("signer_authorization_roster_receipt_temporal_status") == "coherent",
            "signer_authorization_authority_quorum_at_least_2": int(summary.get("signer_authorization_authority_count") or 0) >= 2,
            "signer_authorization_active_entries_at_least_threshold": int(summary.get("signer_authorization_active_entry_count") or 0) >= int((summary.get("policy") or {}).get("minimum_distinct_valid_signatures_per_envelope") or 1),
        })
    summary["auth_profile_required_controls"] = sorted(requirements)
    missing = [name for name, ok in sorted(requirements.items()) if not ok]
    if missing:
        summary["auth_profile_status"] = "not_met"
        summary["auth_profile_missing_controls"] = missing
        return [f"signature_auth_profile_not_met:{name}" for name in missing]
    summary["auth_profile_status"] = "requirements_met"
    summary["auth_profile_missing_controls"] = []
    return []


def verify_packet_signatures(
    packet_dir: Path,
    keyring_path: Path,
    expected_keyset_sha256: str | None = None,
    trust_keyset_receipt: Path | None = None,
    expected_trust_keyset_receipt_sha256: str | None = None,
    require_trust_keyset_receipt: bool = False,
    trust_governance_bundle: Path | None = None,
    expected_governance_bundle_sha256: str | None = None,
    require_trust_governance_bundle: bool = False,
    trust_governance_bundle_receipt: Path | None = None,
    expected_governance_bundle_receipt_sha256: str | None = None,
    require_trust_governance_bundle_receipt: bool = False,
    trust_status_snapshot: Path | None = None,
    expected_trust_status_snapshot_sha256: str | None = None,
    require_trust_status_snapshot: bool = False,
    trust_status_snapshot_receipt: Path | None = None,
    expected_trust_status_snapshot_receipt_sha256: str | None = None,
    require_trust_status_snapshot_receipt: bool = False,
    signer_authorization_roster: Path | None = None,
    expected_signer_authorization_roster_sha256: str | None = None,
    require_signer_authorization_roster: bool = False,
    signer_authorization_roster_receipt: Path | None = None,
    expected_signer_authorization_roster_receipt_sha256: str | None = None,
    require_signer_authorization_roster_receipt: bool = False,
    verification_time: datetime | None = None,
    auth_profile: str = DEFAULT_AUTH_PROFILE,
) -> tuple[list[str], dict[str, Any]]:
    """Verify Ed25519 signatures over EvidenceEnvelope TBS bytes using a local trust keyset."""

    requested_auth_profile = (auth_profile or DEFAULT_AUTH_PROFILE).strip()
    strict_local_trust_chain = requested_auth_profile == STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE
    strict_local_authorized_trust_chain = requested_auth_profile == STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE
    if strict_local_trust_chain or strict_local_authorized_trust_chain:
        require_trust_keyset_receipt = True
        require_trust_governance_bundle = True
        require_trust_governance_bundle_receipt = True
        require_trust_status_snapshot = True
        require_trust_status_snapshot_receipt = True
    if strict_local_authorized_trust_chain:
        require_signer_authorization_roster = True
        require_signer_authorization_roster_receipt = True

    problems: list[str] = []
    summary: dict[str, Any] = {
        "profile": "ed25519-jcs-tbs-v1",
        "auth_profile": requested_auth_profile,
        "auth_profile_status": "evaluating" if (strict_local_trust_chain or strict_local_authorized_trust_chain) else "not_requested",
        "auth_profile_required_controls": [],
        "auth_profile_missing_controls": [],
        "authentication_status": "SIGNATURE_FAILED",
        "envelopes_evaluated": 0,
        "envelopes_authenticated": 0,
        "trusted_signatures_valid": 0,
        "trusted_signatures_checked": 0,
        "trusted_key_count": 0,
        "trust_keyset_sha256": "",
        "trust_keyset_location": "external_to_packet",
        "trust_keyset_pin_required": bool((expected_keyset_sha256 or "").strip()),
        "trust_keyset_pin_status": "not_supplied",
        "trust_keyset_pin_sha256": "",
        "trust_keyset_receipt_required": bool(require_trust_keyset_receipt),
        "trust_keyset_receipt_status": "not_supplied",
        "trust_keyset_receipt_sha256": "",
        "trust_keyset_receipt_pin_required": bool((expected_trust_keyset_receipt_sha256 or "").strip()),
        "trust_keyset_receipt_pin_status": "not_supplied",
        "trust_keyset_receipt_pin_sha256": "",
        "trust_keyset_receipt_id": "",
        "trust_keyset_receipt_profile": "",
        "trust_keyset_receipt_channel_count": 0,
        "trust_keyset_receipt_independent_channel_count": 0,
        "trust_keyset_receipt_required_independent_channels": 0,
        "trust_governance_bundle_required": bool(require_trust_governance_bundle),
        "trust_governance_bundle_status": "not_supplied",
        "trust_governance_bundle_sha256": "",
        "trust_governance_bundle_pin_required": bool((expected_governance_bundle_sha256 or "").strip()),
        "trust_governance_bundle_pin_status": "not_supplied",
        "trust_governance_bundle_pin_sha256": "",
        "trust_governance_bundle_id": "",
        "trust_governance_bundle_profile": "",
        "trust_governance_witness_count": 0,
        "trust_governance_required_witness_count": 0,
        "trust_governance_event_count": 0,
        "trust_governance_rotation_or_revocation_event_count": 0,
        "trust_governance_bundle_receipt_required": bool(require_trust_governance_bundle_receipt),
        "trust_governance_bundle_receipt_status": "not_supplied",
        "trust_governance_bundle_receipt_sha256": "",
        "trust_governance_bundle_receipt_pin_required": bool((expected_governance_bundle_receipt_sha256 or "").strip()),
        "trust_governance_bundle_receipt_pin_status": "not_supplied",
        "trust_governance_bundle_receipt_pin_sha256": "",
        "trust_governance_bundle_receipt_id": "",
        "trust_governance_bundle_receipt_profile": "",
        "trust_governance_bundle_receipt_channel_count": 0,
        "trust_governance_bundle_receipt_independent_channel_count": 0,
        "trust_governance_bundle_receipt_required_independent_channels": 0,
        "trust_status_snapshot_required": bool(require_trust_status_snapshot),
        "trust_status_snapshot_status": "not_supplied",
        "trust_status_snapshot_sha256": "",
        "trust_status_snapshot_pin_required": bool((expected_trust_status_snapshot_sha256 or "").strip()),
        "trust_status_snapshot_pin_status": "not_supplied",
        "trust_status_snapshot_pin_sha256": "",
        "trust_status_snapshot_id": "",
        "trust_status_snapshot_profile": "",
        "trust_status_snapshot_this_update": "",
        "trust_status_snapshot_next_update": "",
        "trust_status_snapshot_verification_time": (verification_time.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if isinstance(verification_time, datetime) else ""),
        "trust_status_snapshot_key_status_count": 0,
        "trust_status_snapshot_revoked_key_count": 0,
        "trust_status_snapshot_authority_count": 0,
        "trust_status_snapshot_required_authority_count": 0,
        "trust_status_snapshot_receipt_required": bool(require_trust_status_snapshot_receipt),
        "trust_status_snapshot_receipt_status": "not_supplied",
        "trust_status_snapshot_receipt_sha256": "",
        "trust_status_snapshot_receipt_pin_required": bool((expected_trust_status_snapshot_receipt_sha256 or "").strip()),
        "trust_status_snapshot_receipt_pin_status": "not_supplied",
        "trust_status_snapshot_receipt_pin_sha256": "",
        "trust_status_snapshot_receipt_id": "",
        "trust_status_snapshot_receipt_profile": "",
        "trust_status_snapshot_receipt_channel_count": 0,
        "trust_status_snapshot_receipt_independent_channel_count": 0,
        "trust_status_snapshot_receipt_required_independent_channels": 0,
        "signer_authorization_roster_required": bool(require_signer_authorization_roster),
        "signer_authorization_roster_status": "not_supplied",
        "signer_authorization_roster_sha256": "",
        "signer_authorization_roster_pin_required": bool((expected_signer_authorization_roster_sha256 or "").strip()),
        "signer_authorization_roster_pin_status": "not_supplied",
        "signer_authorization_roster_pin_sha256": "",
        "signer_authorization_roster_id": "",
        "signer_authorization_roster_profile": "",
        "signer_authorization_authority_count": 0,
        "signer_authorization_required_authority_count": 0,
        "signer_authorization_entry_count": 0,
        "signer_authorization_active_entry_count": 0,
        "signer_authorization_scope_election_id": "",
        "signer_authorization_scope_jurisdiction": "",
        "signer_authorization_roster_issued_at": "",
        "signer_authorization_roster_valid_from": "",
        "signer_authorization_roster_valid_until": "",
        "signer_authorization_roster_verification_time": (verification_time.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if isinstance(verification_time, datetime) else ""),
        "signer_authorization_roster_temporal_status": "not_checked",
        "signer_authorization_authority_observed_at_min": "",
        "signer_authorization_authority_observed_at_max": "",
        "signer_authorization_authority_observed_at_status": "not_checked",
        "signer_authorization_row_validity_status": "not_checked",
        "signer_authorization_roster_receipt_required": bool(require_signer_authorization_roster_receipt),
        "signer_authorization_roster_receipt_status": "not_supplied",
        "signer_authorization_roster_receipt_sha256": "",
        "signer_authorization_roster_receipt_pin_required": bool((expected_signer_authorization_roster_receipt_sha256 or "").strip()),
        "signer_authorization_roster_receipt_pin_status": "not_supplied",
        "signer_authorization_roster_receipt_pin_sha256": "",
        "signer_authorization_roster_receipt_id": "",
        "signer_authorization_roster_receipt_profile": "",
        "signer_authorization_roster_receipt_channel_count": 0,
        "signer_authorization_roster_receipt_independent_channel_count": 0,
        "signer_authorization_roster_receipt_required_independent_channels": 0,
        "policy": {
            "minimum_valid_signatures_per_envelope": 1,
            "minimum_distinct_valid_signatures_per_envelope": 1,
            "require_distinct_key_material": True,
            "require_distinct_kids": True,
            "require_all_envelopes_authenticated": True,
        },
        "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
        "non_claims": [
            "does_not_establish_legal_authority",
            "does_not_check_online_revocation",
            "does_not_fetch_online_status_or_revocation",
            "does_not_authorize_live_pilot",
            "does_not_accept_packet_supplied_trust_roots",
            "does_not_prove_trust_channel_governance",
            "does_not_prove_production_key_ceremony",
            "does_not_prove_signer_employment_or_legal_authority",
        ],
    }

    status_snapshot_requested = bool(
        trust_status_snapshot is not None
        or require_trust_status_snapshot
        or (expected_trust_status_snapshot_sha256 or "").strip()
        or trust_status_snapshot_receipt is not None
        or require_trust_status_snapshot_receipt
        or (expected_trust_status_snapshot_receipt_sha256 or "").strip()
    )
    if status_snapshot_requested and verification_time is None:
        summary["trust_status_snapshot_status"] = "invalid"
        summary["failure_reason"] = "trust_status_snapshot_verification_time_required"
        problems.append("signature_trust_status_snapshot_invalid:verification_time_required")
        return problems, summary

    expected_pin_hex: str | None = None
    if (expected_keyset_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_keyset_sha256))
        if expected_pin_hex is None:
            summary["trust_keyset_pin_status"] = "invalid"
            summary["failure_reason"] = "trust_keyset_pin_invalid"
            problems.append("signature_trust_keyset_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["trust_keyset_pin_sha256"] = "sha256:" + expected_pin_hex

    if _path_inside_dir(keyring_path, packet_dir):
        summary["trust_keyset_location"] = "packet_contained_rejected"
        summary["failure_reason"] = "trust_keyset_untrusted_location"
        problems.append("signature_trust_keyset_untrusted_location:packet_contained")
        return problems, summary

    keyring_bytes, keyring, keyring_problems = _keyring_bytes_and_obj(keyring_path)
    if keyring_bytes is not None:
        actual_keyset_hex = sha256_hex_bytes(keyring_bytes)
        summary["trust_keyset_sha256"] = "sha256:" + actual_keyset_hex
        if expected_pin_hex is not None:
            if actual_keyset_hex.lower() != expected_pin_hex.lower():
                summary["trust_keyset_pin_status"] = "mismatched"
                summary["failure_reason"] = "trust_keyset_pin_mismatch"
                problems.append(f"signature_trust_keyset_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_keyset_hex}")
                return problems, summary
            summary["trust_keyset_pin_status"] = "matched"
    problems.extend(keyring_problems)
    if keyring is None:
        summary["failure_reason"] = "trust_keyset_invalid"
        return problems, summary

    keys, raw_key_count, norm_problems = _normalized_key_rows(keyring)
    summary["trusted_key_count"] = len(keys)
    summary["raw_key_count"] = raw_key_count
    problems.extend(norm_problems)
    policy, policy_problems = _trust_keyset_signature_policy(keyring)
    problems.extend(policy_problems)
    summary["policy"] = policy
    required_threshold = int(policy.get("minimum_distinct_valid_signatures_per_envelope") or 1)
    unique_key_material = {hashlib.sha256(k.get("_public_key_bytes", b"")).hexdigest() for k in keys if k.get("_public_key_bytes")}
    if len(unique_key_material) < required_threshold:
        problems.append(f"signature_threshold_not_met:trust_keyset_distinct_key_material={len(unique_key_material)}:required={required_threshold}")
    if not keys:
        problems.append("signature_trust_keyset_invalid:no_usable_keys")
        summary["failure_reason"] = "no_usable_keys"
        return problems, summary

    receipt_problems, receipt_summary = validate_trust_keyset_publication_receipt(
        packet_dir,
        trust_keyset_receipt,
        str(summary.get("trust_keyset_sha256") or ""),
        bool(require_trust_keyset_receipt),
        expected_trust_keyset_receipt_sha256,
    )
    problems.extend(receipt_problems)
    summary.update(receipt_summary)
    if receipt_problems:
        summary["failure_reason"] = "trust_keyset_publication_receipt_failed"
        return problems, summary

    governance_problems, governance_summary = validate_trust_governance_bundle(
        packet_dir,
        trust_governance_bundle,
        expected_governance_bundle_sha256,
        str(summary.get("trust_keyset_sha256") or ""),
        str(summary.get("trust_keyset_receipt_sha256") or ""),
        keys,
        keyring,
        bool(require_trust_governance_bundle),
    )
    problems.extend(governance_problems)
    summary.update(governance_summary)
    if governance_problems:
        summary["failure_reason"] = "trust_governance_bundle_failed"
        return problems, summary

    governance_receipt_problems, governance_receipt_summary = validate_trust_governance_bundle_publication_receipt(
        packet_dir,
        trust_governance_bundle_receipt,
        str(summary.get("trust_governance_bundle_sha256") or ""),
        bool(require_trust_governance_bundle_receipt),
        expected_governance_bundle_receipt_sha256,
    )
    problems.extend(governance_receipt_problems)
    summary.update(governance_receipt_summary)
    if governance_receipt_problems:
        summary["failure_reason"] = "trust_governance_bundle_receipt_failed"
        return problems, summary

    status_problems, status_summary = validate_trust_status_snapshot(
        packet_dir,
        trust_status_snapshot,
        expected_trust_status_snapshot_sha256,
        str(summary.get("trust_keyset_sha256") or ""),
        str(summary.get("trust_governance_bundle_sha256") or ""),
        str(summary.get("trust_governance_bundle_receipt_sha256") or ""),
        keys,
        bool(require_trust_status_snapshot),
        verification_time,
    )
    problems.extend(status_problems)
    summary.update(status_summary)
    if status_problems:
        summary["failure_reason"] = "trust_status_snapshot_failed"
        return problems, summary

    status_receipt_problems, status_receipt_summary = validate_trust_status_snapshot_publication_receipt(
        packet_dir,
        trust_status_snapshot_receipt,
        str(summary.get("trust_status_snapshot_sha256") or ""),
        bool(require_trust_status_snapshot_receipt),
        expected_trust_status_snapshot_receipt_sha256,
        verification_time,
        status_summary,
    )
    problems.extend(status_receipt_problems)
    summary.update(status_receipt_summary)
    if status_receipt_problems:
        summary["failure_reason"] = "trust_status_snapshot_receipt_failed"
        return problems, summary

    signer_authorization_problems, signer_authorization_summary, signer_authorization_index = validate_signer_authorization_roster(
        packet_dir,
        signer_authorization_roster,
        expected_signer_authorization_roster_sha256,
        str(summary.get("trust_keyset_sha256") or ""),
        str(summary.get("trust_status_snapshot_sha256") or ""),
        keyring,
        keys,
        bool(require_signer_authorization_roster),
        verification_time,
    )
    problems.extend(signer_authorization_problems)
    summary.update(signer_authorization_summary)
    if signer_authorization_problems:
        summary["failure_reason"] = "signer_authorization_roster_failed"
        return problems, summary

    signer_authorization_receipt_problems, signer_authorization_receipt_summary = validate_signer_authorization_roster_publication_receipt(
        packet_dir,
        signer_authorization_roster_receipt,
        str(summary.get("signer_authorization_roster_sha256") or ""),
        bool(require_signer_authorization_roster_receipt),
        expected_signer_authorization_roster_receipt_sha256,
        verification_time,
        signer_authorization_summary,
    )
    problems.extend(signer_authorization_receipt_problems)
    summary.update(signer_authorization_receipt_summary)
    if signer_authorization_receipt_problems:
        summary["failure_reason"] = "signer_authorization_roster_receipt_failed"
        return problems, summary

    if strict_local_trust_chain or strict_local_authorized_trust_chain:
        profile_problems = enforce_strict_local_trust_chain_profile(summary, require_signer_authorization=bool(strict_local_authorized_trust_chain))
        if profile_problems:
            problems.extend(profile_problems)
            summary["failure_reason"] = "auth_profile_not_met"
            return problems, summary

    if Ed25519PublicKey is None:
        problems.append("signature_crypto_unavailable:cryptography")
        summary["failure_reason"] = "dependency_missing"
        return problems, summary

    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        problems.append("signature_threshold_not_met:envelopes_dir_missing")
        summary["failure_reason"] = "envelopes_dir_missing"
        return problems, summary

    per_envelope: list[dict[str, Any]] = []
    for p in sorted(env_dir.glob("*.json")):
        try:
            env = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            problems.append(f"signature_threshold_not_met:{p.name}:envelope_json_parse_failed:{type(e).__name__}")
            continue
        if not isinstance(env, dict):
            problems.append(f"signature_threshold_not_met:{p.name}:envelope_not_object")
            continue
        summary["envelopes_evaluated"] += 1
        sigs = env.get("signatures")
        if not isinstance(sigs, list) or not sigs:
            problems.append(f"signature_missing:{p.name}")
            per_envelope.append({"envelope": p.name, "valid_signature_count": 0, "distinct_valid_key_count": 0, "authenticated": False})
            continue

        valid_key_ids: set[str] = set()
        valid_key_material: set[str] = set()
        saw_candidate = False
        saw_decode_error = False
        saw_unsupported_alg = False
        saw_invalid = False
        saw_policy_problem = False
        for i, sig in enumerate(sigs):
            if not isinstance(sig, dict):
                problems.append(f"signature_entry_not_object:{p.name}:{i}")
                continue
            alg = str(sig.get("alg") or "").strip()
            if alg not in SUPPORTED_AUTH_ALGS:
                saw_unsupported_alg = True
                continue
            enc = str(sig.get("sig_encoding") or "base64").strip().lower()
            if enc not in {"base64", "base64url", "hex"}:
                problems.append(f"signature_encoding_unsupported:{p.name}:{i}:{enc or 'missing'}")
                saw_decode_error = True
                continue
            sig_bytes_preview = _decode_multibase_bytes(str(sig.get("sig") or ""), enc)
            if sig_bytes_preview is None or len(sig_bytes_preview) != 64:
                saw_decode_error = True
                continue
            if not str(sig.get("kid") or "").strip():
                problems.append(f"signature_missing_kid:{p.name}:{i}")
                continue
            candidates = _signature_candidates(sig, keys)
            if not candidates:
                continue
            saw_candidate = True
            for key in candidates:
                policy_problems = _key_allowed_for_envelope(key, env, p.name)
                if policy_problems:
                    problems.extend(policy_problems)
                    saw_policy_problem = True
                    continue
                key_signer = str(key.get("signer_id") or "").strip()
                sig_signer = str(sig.get("signer_id") or "").strip()
                if key_signer and sig_signer and key_signer != sig_signer:
                    problems.append(f"signature_signer_mismatch:{p.name}:{i}")
                    continue
                authorization_problems = _authorization_allows_key_for_envelope(signer_authorization_index, key, env, p.name)
                if authorization_problems:
                    problems.extend(authorization_problems)
                    saw_policy_problem = True
                    continue
                try:
                    summary["trusted_signatures_checked"] += 1
                    if _verify_one_signature(sig, key, env):
                        key_id = str(key.get("kid") or key.get("signer_id") or f"key-{i}").strip()
                        key_material_id = hashlib.sha256(key.get("_public_key_bytes", b"")).hexdigest()
                        valid_key_ids.add(key_id)
                        valid_key_material.add(key_material_id)
                        summary["trusted_signatures_valid"] += 1
                except InvalidSignature:  # type: ignore[misc]
                    saw_invalid = True
                except Exception as e:
                    problems.append(f"signature_verification_error:{p.name}:{i}:{type(e).__name__}")
                    saw_invalid = True

        distinct_valid_for_env = min(len(valid_key_ids), len(valid_key_material))
        valid_signature_count_for_env = len(valid_key_ids)
        required_threshold = int(summary.get("policy", {}).get("minimum_distinct_valid_signatures_per_envelope") or 1)
        if distinct_valid_for_env >= required_threshold:
            summary["envelopes_authenticated"] += 1
            per_envelope.append({
                "envelope": p.name,
                "valid_signature_count": int(valid_signature_count_for_env),
                "distinct_valid_key_count": int(distinct_valid_for_env),
                "authenticated": True,
            })
        else:
            if saw_invalid:
                problems.append(f"signature_invalid:{p.name}")
            if saw_decode_error:
                problems.append(f"signature_decode_failed:{p.name}")
            if saw_unsupported_alg and not saw_candidate:
                problems.append(f"signature_alg_unsupported:{p.name}")
            if not saw_candidate and not saw_unsupported_alg:
                problems.append(f"signature_kid_untrusted:{p.name}")
            if saw_policy_problem and not saw_invalid:
                problems.append(f"signature_threshold_not_met:{p.name}:policy_problem")
            problems.append(f"signature_threshold_not_met:{p.name}:valid={distinct_valid_for_env}:required={required_threshold}")
            per_envelope.append({
                "envelope": p.name,
                "valid_signature_count": int(valid_signature_count_for_env),
                "distinct_valid_key_count": int(distinct_valid_for_env),
                "authenticated": False,
            })

    if summary["envelopes_evaluated"] <= 0:
        problems.append("signature_threshold_not_met:no_envelopes")
    if summary["envelopes_evaluated"] > 0 and summary["envelopes_authenticated"] == summary["envelopes_evaluated"]:
        summary["authentication_status"] = "SIGNATURE_VERIFIED"
    else:
        summary["authentication_status"] = "SIGNATURE_FAILED"
        summary["failure_reason"] = "one_or_more_envelopes_not_authenticated"
    summary["envelopes"] = per_envelope[:20]
    if len(per_envelope) > 20:
        summary["envelopes_truncated"] = len(per_envelope) - 20
    return problems, summary


def _policy_path_rejection_reason(value: Any, *, allow_parent_segments: bool) -> str | None:
    """Return a short public reason if a policy path is unsafe.

    Policy lockfiles are meant to remove hand-assembled CLI risk, not become a
    portable way to point trust roots at arbitrary local or remote locations.
    Strict lockfiles therefore use a packet-external trust_input_base_dir and
    child-only trust-input paths.
    """

    if not isinstance(value, str) or not value.strip():
        return "missing"
    raw = value.strip()
    if "\x00" in raw:
        return "nul"
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
        return "url"
    if raw.startswith("~"):
        return "shell_home"
    if re.match(r"^[A-Za-z]:[\\/]", raw) or raw.startswith("\\\\") or raw.startswith("//"):
        return "windows_or_unc"
    if Path(raw).is_absolute():
        return "absolute"
    parts = [part for part in re.split(r"[\\/]+", raw) if part and part != "."]
    if not allow_parent_segments and ".." in parts:
        return "parent_segment"
    return None


def _policy_path_parts(value: str) -> list[str]:
    return [part for part in re.split(r"[\\/]+", value.strip()) if part and part != "."]


def _path_inside_base(candidate: Path, base_dir: Path) -> bool:
    """Return True only when candidate remains inside base_dir lexically and after resolution."""

    def norm_abs(x: Path) -> Path:
        raw = x if x.is_absolute() else (Path.cwd() / x)
        return Path(os.path.abspath(os.fspath(raw)))

    def child(child_path: Path, parent_path: Path) -> bool:
        try:
            child_path.relative_to(parent_path)
            return True
        except ValueError:
            return False

    base_lex = norm_abs(base_dir)
    cand_lex = norm_abs(candidate)
    if not child(cand_lex, base_lex):
        return False
    try:
        base_res = base_lex.resolve(strict=False)
        cand_res = cand_lex.resolve(strict=False)
    except Exception:
        return False
    return child(cand_res, base_res)

def _string_list(value: Any) -> list[str]:
    """Normalize a policy requirement value into a short string list."""

    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _check_policy_verifier_requirements(
    obj: dict[str, Any],
    auth_profile: str,
    *,
    strict_policy: bool,
) -> tuple[list[str], dict[str, Any]]:
    """Bind strict policy bytes to the verifier/report semantics interpreting them.

    A byte-pinned policy lockfile is dangerous if it silently crosses verifier
    versions or auth-profile meanings.  Strict synthetic policies therefore
    carry an explicit verifier_requirements object and fail closed unless the
    archive version, PacketVerificationReport version, and auth profile match
    the local verifier invocation.
    """

    summary: dict[str, Any] = {
        "verification_policy_lockfile_verifier_requirements_status": "not_required" if not strict_policy else "not_supplied",
        "verification_policy_lockfile_required_archive_version": "",
        "verification_policy_lockfile_actual_archive_version": ARCHIVE_VERSION,
        "verification_policy_lockfile_required_report_version": "",
        "verification_policy_lockfile_actual_report_version": REPORT_VERSION,
        "verification_policy_lockfile_required_auth_profile": "",
        "verification_policy_lockfile_required_auth_profile_status": "not_required" if not strict_policy else "not_checked",
    }
    problems: list[str] = []
    raw = obj.get("verifier_requirements")
    if raw is None:
        if strict_policy:
            summary["verification_policy_lockfile_verifier_requirements_status"] = "missing"
            problems.append("signature_verification_policy_lockfile_verifier_requirement_mismatch:missing")
        return problems, summary
    if not isinstance(raw, dict):
        summary["verification_policy_lockfile_verifier_requirements_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_verifier_requirement_mismatch:not_object")
        return problems, summary

    archive_allowed = _string_list(raw.get("archive_version") or raw.get("archive_versions") or raw.get("allowed_archive_versions"))
    report_allowed = _string_list(
        raw.get("packet_verification_report_version")
        or raw.get("packet_verification_report_versions")
        or raw.get("report_version")
        or raw.get("report_versions")
        or raw.get("allowed_packet_verification_report_versions")
    )
    profile_allowed = _string_list(raw.get("auth_profile") or raw.get("auth_profiles") or raw.get("allowed_auth_profiles"))

    summary["verification_policy_lockfile_required_archive_version"] = ",".join(archive_allowed)[:200]
    summary["verification_policy_lockfile_required_report_version"] = ",".join(report_allowed)[:200]
    summary["verification_policy_lockfile_required_auth_profile"] = ",".join(profile_allowed)[:240]

    if not archive_allowed:
        problems.append("signature_verification_policy_lockfile_verifier_requirement_mismatch:archive_version_missing")
    elif ARCHIVE_VERSION not in archive_allowed:
        problems.append(f"signature_verification_policy_lockfile_verifier_requirement_mismatch:archive_version:{ARCHIVE_VERSION}")

    if not report_allowed:
        problems.append("signature_verification_policy_lockfile_verifier_requirement_mismatch:report_version_missing")
    elif REPORT_VERSION not in report_allowed:
        problems.append(f"signature_verification_policy_lockfile_verifier_requirement_mismatch:report_version:{REPORT_VERSION}")

    if not profile_allowed:
        summary["verification_policy_lockfile_required_auth_profile_status"] = "missing"
        problems.append("signature_verification_policy_lockfile_verifier_requirement_mismatch:auth_profile_missing")
    elif auth_profile not in profile_allowed:
        summary["verification_policy_lockfile_required_auth_profile_status"] = "mismatched"
        problems.append(f"signature_verification_policy_lockfile_verifier_requirement_mismatch:auth_profile:{auth_profile}")
    else:
        summary["verification_policy_lockfile_required_auth_profile_status"] = "matched"

    summary["verification_policy_lockfile_verifier_requirements_status"] = "matched" if not problems else "mismatched"
    return problems, summary



def _resolve_policy_relative_path(policy_path: Path, value: Any) -> Path | None:
    """Resolve a legacy/non-strict lockfile path relative to the lockfile directory."""

    if _policy_path_rejection_reason(value, allow_parent_segments=True) is not None:
        return None
    raw = str(value).strip()
    p = Path(raw)
    if not p.is_absolute():
        p = policy_path.parent / p
    return p


def _json_values_with_key(value: Any, key: str) -> set[str]:
    """Return short string values found for key anywhere in a JSON-like object."""

    found: set[str] = set()
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key and isinstance(v, str) and v.strip():
                found.add(v.strip())
            found.update(_json_values_with_key(v, key))
    elif isinstance(value, list):
        for item in value:
            found.update(_json_values_with_key(item, key))
    return found


def _packet_selector_actuals(packet_dir: Path) -> dict[str, Any]:
    """Collect bounded packet facts used by a verification-policy selector."""

    actuals: dict[str, Any] = {
        "packet_id": packet_dir.name,
        "packet_ids": {packet_dir.name},
        "election_ids": set(),
        "jurisdictions": set(),
    }
    manifest_path = packet_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(manifest, dict):
            if isinstance(manifest.get("packet_id"), str) and manifest.get("packet_id", "").strip():
                actuals["packet_ids"].add(manifest["packet_id"].strip())
            if isinstance(manifest.get("election_id"), str) and manifest.get("election_id", "").strip():
                actuals["election_ids"].add(manifest["election_id"].strip())
            if isinstance(manifest.get("jurisdiction"), str) and manifest.get("jurisdiction", "").strip():
                actuals["jurisdictions"].add(manifest["jurisdiction"].strip())
            # Avoid recursive manifest-wide matching except for common nested metadata blocks.
            for key in ("subject", "crypto_policy", "election", "jurisdiction_scope", "scope"):
                if key in manifest:
                    actuals["packet_ids"].update(_json_values_with_key(manifest[key], "packet_id"))
                    actuals["election_ids"].update(_json_values_with_key(manifest[key], "election_id"))
                    actuals["jurisdictions"].update(_json_values_with_key(manifest[key], "jurisdiction"))
    except Exception:
        pass

    envelopes_dir = packet_dir / "envelopes"
    if envelopes_dir.exists():
        for env_path in sorted(envelopes_dir.glob("*.json"))[:50]:
            try:
                env = json.loads(env_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(env, dict):
                continue
            subject = env.get("subject")
            if isinstance(subject, dict):
                if isinstance(subject.get("packet_id"), str) and subject.get("packet_id", "").strip():
                    actuals["packet_ids"].add(subject["packet_id"].strip())
                if isinstance(subject.get("election_id"), str) and subject.get("election_id", "").strip():
                    actuals["election_ids"].add(subject["election_id"].strip())
                if isinstance(subject.get("jurisdiction"), str) and subject.get("jurisdiction", "").strip():
                    actuals["jurisdictions"].add(subject["jurisdiction"].strip())
                actuals["packet_ids"].update(_json_values_with_key(subject, "packet_id"))
                actuals["election_ids"].update(_json_values_with_key(subject, "election_id"))
                actuals["jurisdictions"].update(_json_values_with_key(subject, "jurisdiction"))
    actuals["packet_ids"] = sorted(actuals["packet_ids"])
    actuals["election_ids"] = sorted(actuals["election_ids"])
    actuals["jurisdictions"] = sorted(actuals["jurisdictions"])
    return actuals


def _check_policy_packet_selector(packet_dir: Path, selector: Any, *, strict_policy: bool) -> tuple[list[str], dict[str, Any]]:
    """Fail closed when a strict policy lockfile does not select this packet."""

    actuals = _packet_selector_actuals(packet_dir)
    summary = {
        "verification_policy_lockfile_packet_selector_status": "not_required",
        "verification_policy_lockfile_packet_selector_packet_id": "",
        "verification_policy_lockfile_packet_selector_election_id": "",
        "verification_policy_lockfile_packet_selector_jurisdiction": "",
        "verification_policy_lockfile_packet_selector_actual_packet_id": str(actuals.get("packet_id") or "")[:200],
        "verification_policy_lockfile_packet_selector_actual_packet_ids": list(actuals.get("packet_ids") or [])[:20],
        "verification_policy_lockfile_packet_selector_actual_election_ids": list(actuals.get("election_ids") or [])[:20],
        "verification_policy_lockfile_packet_selector_actual_jurisdictions": list(actuals.get("jurisdictions") or [])[:20],
        "verification_policy_lockfile_packet_selector_scope_consistency_status": "not_required",
    }
    problems: list[str] = []
    if not strict_policy:
        return problems, summary
    if not isinstance(selector, dict):
        summary["verification_policy_lockfile_packet_selector_status"] = "missing"
        return ["signature_verification_policy_lockfile_packet_selector_mismatch:missing"], summary

    expected_packet_id = str(selector.get("packet_id") or "").strip()
    expected_election_id = str(selector.get("election_id") or "").strip()
    expected_jurisdiction = str(selector.get("jurisdiction") or "").strip()
    summary["verification_policy_lockfile_packet_selector_packet_id"] = expected_packet_id[:200]
    summary["verification_policy_lockfile_packet_selector_election_id"] = expected_election_id[:200]
    summary["verification_policy_lockfile_packet_selector_jurisdiction"] = expected_jurisdiction[:200]

    packet_ids = set(actuals.get("packet_ids") or [])
    election_ids = set(actuals.get("election_ids") or [])
    jurisdictions = set(actuals.get("jurisdictions") or [])

    if not expected_packet_id:
        problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:missing_packet_id")
    elif packet_ids != {expected_packet_id}:
        if expected_packet_id not in packet_ids:
            problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:packet_id")
        else:
            problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:packet_id_ambiguous")
    if not expected_election_id:
        problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:missing_election_id")
    elif election_ids != {expected_election_id}:
        if expected_election_id not in election_ids:
            problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:election_id")
        else:
            problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:election_id_ambiguous")
    if not expected_jurisdiction:
        problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:missing_jurisdiction")
    elif jurisdictions != {expected_jurisdiction}:
        if expected_jurisdiction not in jurisdictions:
            problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:jurisdiction")
        else:
            problems.append("signature_verification_policy_lockfile_packet_selector_mismatch:jurisdiction_ambiguous")

    summary["verification_policy_lockfile_packet_selector_status"] = "matched" if not problems else "mismatched"
    summary["verification_policy_lockfile_packet_selector_scope_consistency_status"] = "consistent" if not problems else "ambiguous_or_mismatched"
    return problems, summary


def _check_policy_packet_public_fingerprint(packet_dir: Path, obj: dict[str, Any], *, strict_policy: bool) -> tuple[list[str], dict[str, Any]]:
    """Bind a strict policy lockfile to the packet's bounded public bytes."""

    max_bytes = PUBLIC_FP_DEFAULT_MAX_BYTES
    raw_max = obj.get("packet_public_fingerprint_max_include_bytes")
    if raw_max is not None:
        try:
            max_bytes = int(raw_max)
        except Exception:
            max_bytes = -1
    expected_raw = str(obj.get("packet_public_fingerprint_sha256") or "").strip()
    expected_hex = normalize_sha256_pin(expected_raw) if expected_raw else None
    expected_profile = str(obj.get("packet_public_fingerprint_profile") or "").strip()
    actual_profile = str(PUBLIC_FP_REPORT_FORMAT_VERSION or "").strip()
    summary: dict[str, Any] = {
        "verification_policy_lockfile_packet_public_fingerprint_status": "not_required" if not strict_policy else "not_supplied",
        "verification_policy_lockfile_packet_public_fingerprint_sha256": expected_raw[:200],
        "verification_policy_lockfile_packet_public_fingerprint_actual_sha256": "",
        "verification_policy_lockfile_packet_public_fingerprint_profile": actual_profile[:80],
        "verification_policy_lockfile_packet_public_fingerprint_expected_profile": expected_profile[:80],
        "verification_policy_lockfile_packet_public_fingerprint_profile_status": "not_required" if not strict_policy else "not_supplied",
        "verification_policy_lockfile_packet_public_fingerprint_max_include_bytes": max(max_bytes, 0),
        "verification_policy_lockfile_packet_public_fingerprint_warn_count": 0,
    }
    problems: list[str] = []
    if not strict_policy:
        return problems, summary
    if not expected_profile:
        summary["verification_policy_lockfile_packet_public_fingerprint_profile_status"] = "missing"
        problems.append("signature_verification_policy_lockfile_packet_fingerprint_profile_mismatch:missing")
    elif expected_profile != actual_profile:
        summary["verification_policy_lockfile_packet_public_fingerprint_profile_status"] = "mismatched"
        problems.append(f"signature_verification_policy_lockfile_packet_fingerprint_profile_mismatch:expected={expected_profile}:got={actual_profile}")
    else:
        summary["verification_policy_lockfile_packet_public_fingerprint_profile_status"] = "matched"
    if not expected_raw:
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "missing"
        problems.append("signature_verification_policy_lockfile_packet_fingerprint_invalid:missing")
        return problems, summary
    if expected_hex is None:
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_packet_fingerprint_invalid:malformed")
        return problems, summary
    if max_bytes <= 0:
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_packet_fingerprint_invalid:max_include_bytes")
        return problems, summary
    if compute_public_fingerprint is None:
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "unavailable"
        problems.append("signature_verification_policy_lockfile_packet_fingerprint_invalid:helper_unavailable")
        return problems, summary
    try:
        actual_hex, _entry_lines, warnings = compute_public_fingerprint(packet_dir, max_bytes)
    except Exception as e:
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "invalid"
        problems.append(f"signature_verification_policy_lockfile_packet_fingerprint_invalid:compute_failed:{type(e).__name__}")
        return problems, summary
    summary["verification_policy_lockfile_packet_public_fingerprint_actual_sha256"] = "sha256:" + actual_hex
    summary["verification_policy_lockfile_packet_public_fingerprint_warn_count"] = len(warnings or [])
    if warnings:
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_packet_fingerprint_invalid:warnings_present")
    if actual_hex.lower() != expected_hex.lower():
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "mismatched"
        problems.append(f"signature_verification_policy_lockfile_packet_fingerprint_mismatch:expected=sha256:{expected_hex}:got=sha256:{actual_hex}")
    elif not problems:
        summary["verification_policy_lockfile_packet_public_fingerprint_status"] = "matched"
    return problems, summary


def _check_policy_validity_window(obj: dict[str, Any], verification_time_text: str, *, strict_policy: bool) -> tuple[list[str], dict[str, Any]]:
    """Validate bounded policy lockfile replay window for strict profiles.

    The timestamp must come from the verifier invocation, not from the policy
    lockfile itself. Otherwise a stale policy/status bundle could pin its own
    old clock and keep passing freshness checks after the status snapshot has
    expired. Strict lockfiles are also deliberately short-lived operator aids,
    not standing trust anchors.
    """

    valid_from_text = str(obj.get("valid_from") or "").strip()
    valid_until_text = str(obj.get("valid_until") or "").strip()
    issued_at_text = str(obj.get("issued_at") or "").strip()
    summary = {
        "verification_policy_lockfile_validity_status": "not_required",
        "verification_policy_lockfile_valid_from": valid_from_text[:64],
        "verification_policy_lockfile_valid_until": valid_until_text[:64],
        "verification_policy_lockfile_external_verification_time": str(verification_time_text or "").strip()[:64],
        "verification_policy_lockfile_issued_at": issued_at_text[:64],
        "verification_policy_lockfile_issued_at_status": "not_required",
        "verification_policy_lockfile_validity_window_seconds": 0,
        "verification_policy_lockfile_max_validity_window_seconds": MAX_STRICT_POLICY_VALIDITY_WINDOW_SECONDS if strict_policy else 0,
    }
    if not strict_policy:
        return [], summary
    problems: list[str] = []
    if not verification_time_text:
        summary["verification_policy_lockfile_validity_status"] = "missing_external_time"
        return ["signature_verification_policy_lockfile_temporal_context_invalid:external_verification_time_required"], summary
    if not valid_from_text or not valid_until_text:
        summary["verification_policy_lockfile_validity_status"] = "missing"
        return ["signature_verification_policy_lockfile_validity_invalid:missing_window"], summary
    valid_from = _parse_rfc3339_utc(valid_from_text)
    valid_until = _parse_rfc3339_utc(valid_until_text)
    issued_at = _parse_rfc3339_utc(issued_at_text) if issued_at_text else None
    verification_time = _parse_rfc3339_utc(verification_time_text) if verification_time_text else None
    if valid_from is None or valid_until is None:
        problems.append("signature_verification_policy_lockfile_validity_invalid:unparseable_window")
    if not issued_at_text:
        summary["verification_policy_lockfile_issued_at_status"] = "missing"
        problems.append("signature_verification_policy_lockfile_validity_invalid:issued_at_missing")
    elif issued_at is None:
        summary["verification_policy_lockfile_issued_at_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_validity_invalid:issued_at_unparseable")
    if verification_time is None:
        problems.append("signature_verification_policy_lockfile_validity_invalid:verification_time_unparseable")
    if valid_from is not None and valid_until is not None:
        window_seconds = int((valid_until - valid_from).total_seconds())
        summary["verification_policy_lockfile_validity_window_seconds"] = max(window_seconds, 0)
        if valid_from > valid_until:
            problems.append("signature_verification_policy_lockfile_validity_invalid:reversed_window")
        elif window_seconds > MAX_STRICT_POLICY_VALIDITY_WINDOW_SECONDS:
            problems.append("signature_verification_policy_lockfile_validity_invalid:window_too_long")
    if issued_at is not None and valid_from is not None and valid_until is not None:
        if issued_at < valid_from or issued_at > valid_until:
            summary["verification_policy_lockfile_issued_at_status"] = "outside_window"
            problems.append("signature_verification_policy_lockfile_validity_invalid:issued_at_outside_window")
        elif verification_time is not None and issued_at > verification_time:
            summary["verification_policy_lockfile_issued_at_status"] = "after_verification_time"
            problems.append("signature_verification_policy_lockfile_validity_invalid:issued_at_after_verification_time")
        else:
            summary["verification_policy_lockfile_issued_at_status"] = "within_window"
    if verification_time is not None and valid_from is not None and valid_until is not None:
        if verification_time < valid_from:
            problems.append("signature_verification_policy_lockfile_validity_invalid:not_yet_valid")
        elif verification_time > valid_until:
            problems.append("signature_verification_policy_lockfile_validity_invalid:expired")
    summary["verification_policy_lockfile_validity_status"] = "within_window" if not problems else "invalid"
    return problems, summary



def validate_verification_policy_lockfile_publication_receipt(
    packet_dir: Path,
    receipt_path: Path | None,
    expected_policy_sha256: str,
    require_receipt: bool,
    expected_receipt_sha256: str | None = None,
    external_verification_time: str | None = None,
    policy_obj: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate an optional external publication receipt for policy-lockfile bytes.

    This is a local replay/substitution guard. It proves only that the verifier
    was given a separate JSON object, outside the packet being authenticated,
    whose bytes bind the supplied verification-policy lockfile digest to named
    publication channels. It does not fetch those channels, prove election-office
    authority, or establish production trust-root governance.
    """

    summary: dict[str, Any] = {
        "verification_policy_lockfile_receipt_required": bool(require_receipt),
        "verification_policy_lockfile_receipt_status": "not_supplied",
        "verification_policy_lockfile_receipt_sha256": "",
        "verification_policy_lockfile_receipt_pin_required": bool(require_receipt or (expected_receipt_sha256 or "").strip()),
        "verification_policy_lockfile_receipt_pin_status": "not_supplied",
        "verification_policy_lockfile_receipt_pin_sha256": "",
        "verification_policy_lockfile_receipt_id": "",
        "verification_policy_lockfile_receipt_profile": "",
        "verification_policy_lockfile_receipt_channel_count": 0,
        "verification_policy_lockfile_receipt_independent_channel_count": 0,
        "verification_policy_lockfile_receipt_required_independent_channels": 0,
        "verification_policy_lockfile_receipt_validity_status": "not_checked",
        "verification_policy_lockfile_receipt_valid_from": "",
        "verification_policy_lockfile_receipt_valid_until": "",
        "verification_policy_lockfile_receipt_issued_at": "",
        "verification_policy_lockfile_receipt_issued_at_status": "not_checked",
        "verification_policy_lockfile_receipt_channel_time_status": "not_checked",
        "verification_policy_lockfile_receipt_temporal_status": "not_checked",
        "verification_policy_lockfile_receipt_temporal_policy_issued_at": "",
        "verification_policy_lockfile_receipt_published_at_min": "",
        "verification_policy_lockfile_receipt_published_at_max": "",
        "verification_policy_lockfile_receipt_earliest_published_at": "",
        "verification_policy_lockfile_receipt_latest_published_at": "",
        "verification_policy_lockfile_receipt_external_verification_time": str(external_verification_time or "").strip()[:64],
        "verification_policy_lockfile_receipt_policy_id_status": "not_checked",
        "verification_policy_lockfile_receipt_policy_id": "",
        "verification_policy_lockfile_receipt_expected_policy_id": "",
        "verification_policy_lockfile_receipt_packet_selector_status": "not_checked",
        "verification_policy_lockfile_receipt_packet_selector_packet_id": "",
        "verification_policy_lockfile_receipt_packet_selector_election_id": "",
        "verification_policy_lockfile_receipt_packet_selector_jurisdiction": "",
        "verification_policy_lockfile_receipt_expected_packet_selector_packet_id": "",
        "verification_policy_lockfile_receipt_expected_packet_selector_election_id": "",
        "verification_policy_lockfile_receipt_expected_packet_selector_jurisdiction": "",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_status": "not_checked",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_sha256": "",
        "verification_policy_lockfile_receipt_expected_packet_public_fingerprint_sha256": "",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_profile_status": "not_checked",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_profile": "",
        "verification_policy_lockfile_receipt_expected_packet_public_fingerprint_profile": "",
    }
    problems: list[str] = []

    expected_pin_hex: str | None = None
    if (expected_receipt_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_receipt_sha256))
        if expected_pin_hex is None:
            summary["verification_policy_lockfile_receipt_pin_status"] = "invalid"
            summary["verification_policy_lockfile_receipt_status"] = "invalid"
            problems.append("signature_verification_policy_lockfile_receipt_pin_invalid:expected_sha256_malformed")
            return problems, summary
        summary["verification_policy_lockfile_receipt_pin_sha256"] = "sha256:" + expected_pin_hex
    elif require_receipt:
        summary["verification_policy_lockfile_receipt_pin_status"] = "required_missing"
        problems.append("signature_verification_policy_lockfile_receipt_pin_required:required_receipt_requires_receipt_sha256")

    want_digest = str(expected_policy_sha256 or "").strip().lower()
    receipt_requested = bool(require_receipt or receipt_path is not None or expected_pin_hex is not None)
    if receipt_requested and not re.fullmatch(r"sha256:[0-9a-f]{64}", want_digest):
        summary["verification_policy_lockfile_receipt_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_receipt_invalid:policy_lockfile_digest_not_available")
        return problems, summary

    if receipt_path is None or not str(receipt_path).strip():
        if require_receipt:
            summary["verification_policy_lockfile_receipt_status"] = "missing"
            problems.append("signature_verification_policy_lockfile_receipt_invalid:required_receipt_not_supplied")
        return problems, summary

    if _path_inside_dir(receipt_path, packet_dir):
        summary["verification_policy_lockfile_receipt_status"] = "packet_contained_rejected"
        problems.append("signature_verification_policy_lockfile_receipt_untrusted_location:packet_contained")
        return problems, summary

    try:
        b = receipt_path.read_bytes()
    except Exception as e:
        summary["verification_policy_lockfile_receipt_status"] = "invalid"
        problems.append(f"signature_verification_policy_lockfile_receipt_invalid:read_failed:{type(e).__name__}")
        return problems, summary

    actual_hex = sha256_hex_bytes(b)
    summary["verification_policy_lockfile_receipt_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["verification_policy_lockfile_receipt_pin_status"] = "mismatched"
            summary["verification_policy_lockfile_receipt_status"] = "mismatched"
            problems.append(f"signature_verification_policy_lockfile_receipt_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}")
            return problems, summary
        summary["verification_policy_lockfile_receipt_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["verification_policy_lockfile_receipt_status"] = "invalid"
        problems.append(f"signature_verification_policy_lockfile_receipt_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary
    if not isinstance(obj, dict):
        summary["verification_policy_lockfile_receipt_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_receipt_invalid:not_object")
        return problems, summary

    profile = str(obj.get("profile") or "").strip()
    receipt_id = str(obj.get("receipt_id") or "").strip()
    summary["verification_policy_lockfile_receipt_profile"] = profile
    summary["verification_policy_lockfile_receipt_id"] = receipt_id[:200]
    if profile != VERIFICATION_POLICY_LOCKFILE_RECEIPT_PROFILE:
        problems.append(f"signature_verification_policy_lockfile_receipt_invalid:unsupported_profile:{profile or 'missing'}")

    digest_alias_values = [str(obj.get(k) or "").strip().lower() for k in ("verification_policy_lockfile_sha256", "policy_lockfile_sha256", "policy_sha256") if str(obj.get(k) or "").strip()]
    if len(set(digest_alias_values)) > 1:
        problems.append("signature_verification_policy_lockfile_receipt_digest_mismatch:policy_digest_alias_mismatch")
    got_digest = digest_alias_values[0] if digest_alias_values else ""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", got_digest):
        problems.append("signature_verification_policy_lockfile_receipt_digest_mismatch:missing_or_bad_verification_policy_lockfile_sha256")
    elif want_digest and got_digest != want_digest:
        summary["verification_policy_lockfile_receipt_status"] = "digest_mismatch"
        problems.append(f"signature_verification_policy_lockfile_receipt_digest_mismatch:expected={want_digest}:got={got_digest}")

    expected_policy_obj = policy_obj if isinstance(policy_obj, dict) else {}
    expected_policy_id = str(expected_policy_obj.get("policy_id") or expected_policy_obj.get("id") or "").strip()
    policy_id_alias_values = [str(obj.get(k) or "").strip() for k in ("verification_policy_lockfile_id", "policy_lockfile_id", "policy_id") if str(obj.get(k) or "").strip()]
    if len(set(policy_id_alias_values)) > 1:
        problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:policy_id_alias_mismatch")
    receipt_policy_id = policy_id_alias_values[0] if policy_id_alias_values else ""
    summary["verification_policy_lockfile_receipt_expected_policy_id"] = expected_policy_id[:200]
    summary["verification_policy_lockfile_receipt_policy_id"] = receipt_policy_id[:200]
    if expected_policy_id:
        if not receipt_policy_id:
            summary["verification_policy_lockfile_receipt_policy_id_status"] = "missing"
            problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:policy_id_missing")
        elif receipt_policy_id != expected_policy_id:
            summary["verification_policy_lockfile_receipt_policy_id_status"] = "mismatched"
            problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:policy_id")
        else:
            summary["verification_policy_lockfile_receipt_policy_id_status"] = "matched"

    expected_selector = expected_policy_obj.get("packet_selector") if isinstance(expected_policy_obj.get("packet_selector"), dict) else {}
    receipt_selector = obj.get("packet_selector") if isinstance(obj.get("packet_selector"), dict) else {}
    selector_problem = False
    for key, suffix in (("packet_id", "packet_id"), ("election_id", "election_id"), ("jurisdiction", "jurisdiction")):
        expected_value = str(expected_selector.get(key) or "").strip() if isinstance(expected_selector, dict) else ""
        receipt_value = str(receipt_selector.get(key) or "").strip() if isinstance(receipt_selector, dict) else ""
        summary[f"verification_policy_lockfile_receipt_expected_packet_selector_{suffix}"] = expected_value[:200]
        summary[f"verification_policy_lockfile_receipt_packet_selector_{suffix}"] = receipt_value[:200]
        if expected_value:
            if not receipt_value:
                selector_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_identity_mismatch:packet_selector_{key}_missing")
            elif receipt_value != expected_value:
                selector_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_identity_mismatch:packet_selector_{key}")
    if expected_selector:
        summary["verification_policy_lockfile_receipt_packet_selector_status"] = "mismatched" if selector_problem else "matched"

    expected_fingerprint = str(expected_policy_obj.get("packet_public_fingerprint_sha256") or "").strip()
    receipt_fingerprint = str(
        obj.get("packet_public_fingerprint_sha256")
        or obj.get("packet_public_fingerprint")
        or obj.get("packet_fingerprint_sha256")
        or ""
    ).strip()
    summary["verification_policy_lockfile_receipt_expected_packet_public_fingerprint_sha256"] = expected_fingerprint[:200]
    summary["verification_policy_lockfile_receipt_packet_public_fingerprint_sha256"] = receipt_fingerprint[:200]
    expected_fingerprint_profile = str(expected_policy_obj.get("packet_public_fingerprint_profile") or "").strip()
    receipt_fingerprint_profile = str(
        obj.get("packet_public_fingerprint_profile")
        or obj.get("packet_public_fingerprint_report_format_version")
        or obj.get("packet_public_fingerprint_profile_version")
        or ""
    ).strip()
    summary["verification_policy_lockfile_receipt_expected_packet_public_fingerprint_profile"] = expected_fingerprint_profile[:80]
    summary["verification_policy_lockfile_receipt_packet_public_fingerprint_profile"] = receipt_fingerprint_profile[:80]
    if expected_fingerprint_profile:
        if not receipt_fingerprint_profile:
            summary["verification_policy_lockfile_receipt_packet_public_fingerprint_profile_status"] = "missing"
            problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:packet_public_fingerprint_profile_missing")
        elif receipt_fingerprint_profile != expected_fingerprint_profile:
            summary["verification_policy_lockfile_receipt_packet_public_fingerprint_profile_status"] = "mismatched"
            problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:packet_public_fingerprint_profile")
        else:
            summary["verification_policy_lockfile_receipt_packet_public_fingerprint_profile_status"] = "matched"
    if expected_fingerprint:
        if normalize_sha256_pin(expected_fingerprint) is None:
            summary["verification_policy_lockfile_receipt_packet_public_fingerprint_status"] = "expected_invalid"
            problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:packet_public_fingerprint_expected_invalid")
        elif not receipt_fingerprint:
            summary["verification_policy_lockfile_receipt_packet_public_fingerprint_status"] = "missing"
            problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:packet_public_fingerprint_missing")
        elif normalize_sha256_pin(receipt_fingerprint) != normalize_sha256_pin(expected_fingerprint):
            summary["verification_policy_lockfile_receipt_packet_public_fingerprint_status"] = "mismatched"
            problems.append("signature_verification_policy_lockfile_receipt_identity_mismatch:packet_public_fingerprint")
        else:
            summary["verification_policy_lockfile_receipt_packet_public_fingerprint_status"] = "matched"

    channels = _as_list_of_dicts(obj.get("publication_channels") or obj.get("channels") or [])
    channel_keys: set[tuple[str, str]] = set()
    for i, ch in enumerate(channels):
        if not isinstance(ch, dict):
            problems.append(f"signature_verification_policy_lockfile_receipt_invalid:channel_not_object:{i}")
            continue
        cid = str(ch.get("channel_id") or "").strip()
        ctype = str(ch.get("channel_type") or "").strip()
        channel_digest_values = [str(ch.get(k) or "").strip().lower() for k in ("observed_verification_policy_lockfile_sha256", "observed_policy_lockfile_sha256", "verification_policy_lockfile_sha256", "policy_lockfile_sha256") if str(ch.get(k) or "").strip()]
        if len(set(channel_digest_values)) > 1:
            problems.append(f"signature_verification_policy_lockfile_receipt_digest_mismatch:channel_digest_alias_mismatch:{cid or i}")
        observed_digest = channel_digest_values[0] if channel_digest_values else ""
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", observed_digest):
            problems.append(f"signature_verification_policy_lockfile_receipt_digest_mismatch:channel_missing_or_bad_observed_digest:{cid or i}")
        elif observed_digest != got_digest:
            problems.append(f"signature_verification_policy_lockfile_receipt_digest_mismatch:channel={cid or i}")
        if not cid or not ctype:
            problems.append(f"signature_verification_policy_lockfile_receipt_invalid:channel_missing_id_or_type:{i}")
            continue
        channel_keys.add((ctype, cid))
    summary["verification_policy_lockfile_receipt_channel_count"] = len(channels)
    summary["verification_policy_lockfile_receipt_independent_channel_count"] = len(channel_keys)

    min_raw = obj.get("minimum_independent_channels", 2)
    try:
        min_channels = int(min_raw)
    except Exception:
        min_channels = 2
        problems.append("signature_verification_policy_lockfile_receipt_invalid:minimum_independent_channels_unparseable")
    if min_channels < 1:
        min_channels = 1
    if min_channels > 10:
        min_channels = 10
    summary["verification_policy_lockfile_receipt_required_independent_channels"] = min_channels

    if len(channel_keys) < min_channels:
        summary["verification_policy_lockfile_receipt_status"] = "channel_quorum_not_met"
        problems.append(f"signature_verification_policy_lockfile_receipt_channel_quorum_not_met:valid={len(channel_keys)}:required={min_channels}")
        return problems, summary
    if not _record_publication_channel_diversity(
        summary=summary,
        problems=problems,
        field_prefix="verification_policy_lockfile_receipt",
        problem_code="signature_verification_policy_lockfile_receipt_channel_diversity_not_met",
        channels=channels,
        channel_keys=channel_keys,
        min_channels=min_channels,
        status_field="verification_policy_lockfile_receipt_status",
    ):
        return problems, summary

    verification_time_text = str(external_verification_time or "").strip()
    if verification_time_text:
        valid_from_text = str(obj.get("valid_from") or "").strip()
        valid_until_text = str(obj.get("valid_until") or "").strip()
        issued_at_text = str(obj.get("issued_at") or "").strip()
        policy_issued_at_text = str((policy_obj or {}).get("issued_at") or "").strip()
        summary["verification_policy_lockfile_receipt_valid_from"] = valid_from_text[:64]
        summary["verification_policy_lockfile_receipt_valid_until"] = valid_until_text[:64]
        summary["verification_policy_lockfile_receipt_issued_at"] = issued_at_text[:64]
        summary["verification_policy_lockfile_receipt_temporal_policy_issued_at"] = policy_issued_at_text[:64]

        vt = _parse_rfc3339_utc(verification_time_text)
        vf = _parse_rfc3339_utc(valid_from_text) if valid_from_text else None
        vu = _parse_rfc3339_utc(valid_until_text) if valid_until_text else None
        issued_at = _parse_rfc3339_utc(issued_at_text) if issued_at_text else None
        policy_issued_at = _parse_rfc3339_utc(policy_issued_at_text) if policy_issued_at_text else None
        temporal_problem = False

        if vt is None:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:verification_time_unparseable")
        if not valid_from_text or not valid_until_text:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:missing_window")
        elif vf is None or vu is None:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:unparseable_window")
        elif vf > vu:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:reversed_window")
        elif vt is not None and vt < vf:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:not_yet_valid")
        elif vt is not None and vt > vu:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:expired")

        if not policy_issued_at_text:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:policy_issued_at_missing")
        elif policy_issued_at is None:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:policy_issued_at_unparseable")
        elif vt is not None and policy_issued_at > vt:
            temporal_problem = True
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:policy_issued_at_after_verification_time")

        if not issued_at_text:
            temporal_problem = True
            summary["verification_policy_lockfile_receipt_issued_at_status"] = "missing"
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:issued_at_missing")
        elif issued_at is None:
            temporal_problem = True
            summary["verification_policy_lockfile_receipt_issued_at_status"] = "invalid"
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:issued_at_unparseable")
        elif vf is not None and vu is not None and (issued_at < vf or issued_at > vu):
            temporal_problem = True
            summary["verification_policy_lockfile_receipt_issued_at_status"] = "outside_window"
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:issued_at_outside_window")
        elif vt is not None and issued_at > vt:
            temporal_problem = True
            summary["verification_policy_lockfile_receipt_issued_at_status"] = "after_verification_time"
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:issued_at_after_verification_time")
        elif policy_issued_at is not None and issued_at < policy_issued_at:
            temporal_problem = True
            summary["verification_policy_lockfile_receipt_issued_at_status"] = "before_policy_issued_at"
            problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:receipt_issued_before_policy_issued_at")
        else:
            summary["verification_policy_lockfile_receipt_issued_at_status"] = "within_window"

        channel_time_problem = False
        channel_times = []
        for i, ch in enumerate(channels):
            if not isinstance(ch, dict):
                continue
            cid = str(ch.get("channel_id") or i).strip()
            published_text = str(ch.get("published_at") or ch.get("observed_at") or "").strip()
            if not published_text:
                channel_time_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_temporal_invalid:channel_published_at_missing:{cid}")
                continue
            published_at = _parse_rfc3339_utc(published_text)
            if published_at is None:
                channel_time_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_temporal_invalid:channel_published_at_unparseable:{cid}")
                continue
            channel_times.append(published_at)
            if vf is not None and published_at < vf:
                channel_time_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_temporal_invalid:channel_published_before_window:{cid}")
            if vu is not None and published_at > vu:
                channel_time_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_temporal_invalid:channel_published_after_window:{cid}")
            if vt is not None and published_at > vt:
                channel_time_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_temporal_invalid:channel_published_after_verification_time:{cid}")
            if policy_issued_at is not None and published_at < policy_issued_at:
                channel_time_problem = True
                problems.append(f"signature_verification_policy_lockfile_receipt_temporal_invalid:channel_predates_policy_issued_at:{cid}")

        if channel_times:
            earliest = min(channel_times)
            latest = max(channel_times)
            earliest_text = earliest.strftime("%Y-%m-%dT%H:%M:%SZ")
            latest_text = latest.strftime("%Y-%m-%dT%H:%M:%SZ")
            summary["verification_policy_lockfile_receipt_published_at_min"] = earliest_text
            summary["verification_policy_lockfile_receipt_published_at_max"] = latest_text
            summary["verification_policy_lockfile_receipt_earliest_published_at"] = earliest_text
            summary["verification_policy_lockfile_receipt_latest_published_at"] = latest_text
            if issued_at is not None and issued_at < latest:
                temporal_problem = True
                problems.append("signature_verification_policy_lockfile_receipt_temporal_invalid:receipt_issued_before_latest_channel_observation")

        summary["verification_policy_lockfile_receipt_channel_time_status"] = "invalid" if channel_time_problem else "within_window"
        summary["verification_policy_lockfile_receipt_validity_status"] = "invalid" if temporal_problem or channel_time_problem else "within_window"
        summary["verification_policy_lockfile_receipt_temporal_status"] = "invalid" if temporal_problem or channel_time_problem else "coherent"

    summary["verification_policy_lockfile_receipt_status"] = "invalid" if problems else "matched"
    return problems, summary


def load_verification_policy_lockfile(
    packet_dir: Path,
    policy_path: Path | None,
    expected_policy_sha256: str | None = None,
    external_verification_time: str | None = None,
    policy_receipt_path: Path | None = None,
    expected_policy_receipt_sha256: str | None = None,
    require_policy_receipt: bool = False,
) -> tuple[list[str], dict[str, Any], dict[str, Any]]:
    """Load an external verifier policy lockfile into CLI-equivalent config.

    This is an operator-error firewall: the strict local trust chain has many
    external inputs, pins, and require flags.  A lockfile lets an operator pass
    one external, byte-pinned policy instead of hand-retyping the trust keyset,
    receipt, governance, governance-receipt, and status-snapshot arguments.
    A separate external policy publication receipt can also be required so the
    policy digest is not merely copied from the same local working directory.
    """

    summary: dict[str, Any] = {
        "verification_policy_lockfile_status": "not_supplied",
        "verification_policy_lockfile_sha256": "",
        "verification_policy_lockfile_pin_required": bool((expected_policy_sha256 or "").strip()),
        "verification_policy_lockfile_pin_status": "not_supplied",
        "verification_policy_lockfile_pin_sha256": "",
        "verification_policy_lockfile_receipt_required": bool(require_policy_receipt),
        "verification_policy_lockfile_receipt_status": "not_supplied",
        "verification_policy_lockfile_receipt_sha256": "",
        "verification_policy_lockfile_receipt_pin_required": bool((expected_policy_receipt_sha256 or "").strip()),
        "verification_policy_lockfile_receipt_pin_status": "not_supplied",
        "verification_policy_lockfile_receipt_pin_sha256": "",
        "verification_policy_lockfile_receipt_id": "",
        "verification_policy_lockfile_receipt_profile": "",
        "verification_policy_lockfile_receipt_channel_count": 0,
        "verification_policy_lockfile_receipt_independent_channel_count": 0,
        "verification_policy_lockfile_receipt_required_independent_channels": 0,
        "verification_policy_lockfile_receipt_validity_status": "not_checked",
        "verification_policy_lockfile_receipt_valid_from": "",
        "verification_policy_lockfile_receipt_valid_until": "",
        "verification_policy_lockfile_receipt_issued_at": "",
        "verification_policy_lockfile_receipt_issued_at_status": "not_checked",
        "verification_policy_lockfile_receipt_channel_time_status": "not_checked",
        "verification_policy_lockfile_receipt_temporal_status": "not_checked",
        "verification_policy_lockfile_receipt_temporal_policy_issued_at": "",
        "verification_policy_lockfile_receipt_published_at_min": "",
        "verification_policy_lockfile_receipt_published_at_max": "",
        "verification_policy_lockfile_receipt_earliest_published_at": "",
        "verification_policy_lockfile_receipt_latest_published_at": "",
        "verification_policy_lockfile_receipt_external_verification_time": "",
        "verification_policy_lockfile_receipt_policy_id_status": "not_checked",
        "verification_policy_lockfile_receipt_policy_id": "",
        "verification_policy_lockfile_receipt_expected_policy_id": "",
        "verification_policy_lockfile_receipt_packet_selector_status": "not_checked",
        "verification_policy_lockfile_receipt_packet_selector_packet_id": "",
        "verification_policy_lockfile_receipt_packet_selector_election_id": "",
        "verification_policy_lockfile_receipt_packet_selector_jurisdiction": "",
        "verification_policy_lockfile_receipt_expected_packet_selector_packet_id": "",
        "verification_policy_lockfile_receipt_expected_packet_selector_election_id": "",
        "verification_policy_lockfile_receipt_expected_packet_selector_jurisdiction": "",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_status": "not_checked",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_sha256": "",
        "verification_policy_lockfile_receipt_expected_packet_public_fingerprint_sha256": "",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_profile_status": "not_checked",
        "verification_policy_lockfile_receipt_packet_public_fingerprint_profile": "",
        "verification_policy_lockfile_receipt_expected_packet_public_fingerprint_profile": "",
        "verification_policy_lockfile_id": "",
        "verification_policy_lockfile_profile": "",
        "verification_policy_lockfile_input_count": 0,
        "verification_policy_lockfile_unknown_trust_input_count": 0,
        "verification_policy_lockfile_auth_profile": "",
        "verification_policy_lockfile_verifier_requirements_status": "not_supplied",
        "verification_policy_lockfile_required_archive_version": "",
        "verification_policy_lockfile_actual_archive_version": ARCHIVE_VERSION,
        "verification_policy_lockfile_required_report_version": "",
        "verification_policy_lockfile_actual_report_version": REPORT_VERSION,
        "verification_policy_lockfile_required_auth_profile": "",
        "verification_policy_lockfile_required_auth_profile_status": "not_supplied",
        "verification_policy_lockfile_path_policy_status": "not_supplied",
        "verification_policy_lockfile_trust_input_base_dir": "",
        "verification_policy_lockfile_input_paths_bounded_count": 0,
        "verification_policy_lockfile_validity_status": "not_supplied",
        "verification_policy_lockfile_valid_from": "",
        "verification_policy_lockfile_valid_until": "",
        "verification_policy_lockfile_external_verification_time": "",
        "verification_policy_lockfile_temporal_context_status": "not_supplied",
        "verification_policy_lockfile_embedded_verification_time_present": False,
        "verification_policy_lockfile_packet_selector_status": "not_supplied",
        "verification_policy_lockfile_packet_selector_packet_id": "",
        "verification_policy_lockfile_packet_selector_election_id": "",
        "verification_policy_lockfile_packet_selector_jurisdiction": "",
        "verification_policy_lockfile_packet_selector_actual_packet_id": "",
        "verification_policy_lockfile_packet_selector_actual_packet_ids": [],
        "verification_policy_lockfile_packet_selector_actual_election_ids": [],
        "verification_policy_lockfile_packet_selector_actual_jurisdictions": [],
        "verification_policy_lockfile_packet_selector_scope_consistency_status": "not_supplied",
        "verification_policy_lockfile_packet_public_fingerprint_status": "not_supplied",
        "verification_policy_lockfile_packet_public_fingerprint_sha256": "",
        "verification_policy_lockfile_packet_public_fingerprint_actual_sha256": "",
        "verification_policy_lockfile_packet_public_fingerprint_profile": "",
        "verification_policy_lockfile_packet_public_fingerprint_expected_profile": "",
        "verification_policy_lockfile_packet_public_fingerprint_profile_status": "not_supplied",
        "verification_policy_lockfile_packet_public_fingerprint_max_include_bytes": 0,
        "verification_policy_lockfile_packet_public_fingerprint_warn_count": 0,
        "verification_policy_lockfile_trust_closure_status": "not_supplied",
        "verification_policy_lockfile_trust_closure_sha256": "",
        "verification_policy_lockfile_trust_closure_input_count": 0,
    }
    problems: list[str] = []
    config: dict[str, Any] = {}

    expected_pin_hex: str | None = None
    if (expected_policy_sha256 or "").strip():
        expected_pin_hex = normalize_sha256_pin(str(expected_policy_sha256))
        if expected_pin_hex is None:
            summary["verification_policy_lockfile_pin_status"] = "invalid"
            summary["verification_policy_lockfile_status"] = "invalid"
            problems.append("signature_verification_policy_lockfile_pin_invalid:expected_sha256_malformed")
            return problems, summary, config
        summary["verification_policy_lockfile_pin_sha256"] = "sha256:" + expected_pin_hex

    if policy_path is None or not str(policy_path).strip():
        return problems, summary, config

    if _path_inside_dir(policy_path, packet_dir):
        summary["verification_policy_lockfile_status"] = "packet_contained_rejected"
        problems.append("signature_verification_policy_lockfile_untrusted_location:packet_contained")
        return problems, summary, config

    try:
        b = policy_path.read_bytes()
    except Exception as e:
        summary["verification_policy_lockfile_status"] = "invalid"
        problems.append(f"signature_verification_policy_lockfile_invalid:read_failed:{type(e).__name__}")
        return problems, summary, config

    actual_hex = sha256_hex_bytes(b)
    summary["verification_policy_lockfile_sha256"] = "sha256:" + actual_hex
    if expected_pin_hex is not None:
        if actual_hex.lower() != expected_pin_hex.lower():
            summary["verification_policy_lockfile_pin_status"] = "mismatched"
            summary["verification_policy_lockfile_status"] = "mismatched"
            problems.append(
                f"signature_verification_policy_lockfile_pin_mismatch:expected=sha256:{expected_pin_hex}:got=sha256:{actual_hex}"
            )
            return problems, summary, config
        summary["verification_policy_lockfile_pin_status"] = "matched"

    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        summary["verification_policy_lockfile_status"] = "invalid"
        problems.append(f"signature_verification_policy_lockfile_invalid:json_parse_failed:{type(e).__name__}")
        return problems, summary, config
    if not isinstance(obj, dict):
        summary["verification_policy_lockfile_status"] = "invalid"
        problems.append("signature_verification_policy_lockfile_invalid:not_object")
        return problems, summary, config

    pre_auth_profile = str(obj.get("auth_profile") or STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE).strip()
    pre_strict_policy = pre_auth_profile in {STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE, STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE}
    effective_require_policy_receipt = bool(require_policy_receipt) or pre_strict_policy
    receipt_problems, receipt_summary = validate_verification_policy_lockfile_publication_receipt(
        packet_dir,
        policy_receipt_path,
        "sha256:" + actual_hex,
        effective_require_policy_receipt,
        expected_policy_receipt_sha256,
        external_verification_time,
        obj,
    )
    problems.extend(receipt_problems)
    summary.update(receipt_summary)

    profile = str(obj.get("profile") or "").strip()
    policy_id = str(obj.get("policy_id") or obj.get("id") or "").strip()
    status = str(obj.get("status") or "active").strip().lower()
    auth_profile = str(obj.get("auth_profile") or STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE).strip()
    summary["verification_policy_lockfile_profile"] = profile
    summary["verification_policy_lockfile_id"] = policy_id[:200]
    summary["verification_policy_lockfile_auth_profile"] = auth_profile
    if profile != VERIFICATION_POLICY_LOCKFILE_PROFILE:
        problems.append(f"signature_verification_policy_lockfile_invalid:unsupported_profile:{profile or 'missing'}")
    if not policy_id:
        problems.append("signature_verification_policy_lockfile_invalid:missing_policy_id")
    if status not in {"active", "current"}:
        problems.append(f"signature_verification_policy_lockfile_invalid:status_not_active:{status or 'missing'}")
    if auth_profile not in {DEFAULT_AUTH_PROFILE, STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE, STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE}:
        problems.append(f"signature_verification_policy_lockfile_invalid:unsupported_auth_profile:{auth_profile or 'missing'}")

    verifier_req_problems, verifier_req_summary = _check_policy_verifier_requirements(
        obj,
        auth_profile,
        strict_policy=(auth_profile in {STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE, STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE}),
    )
    problems.extend(verifier_req_problems)
    summary.update(verifier_req_summary)

    trust_inputs = obj.get("trust_inputs")
    if not isinstance(trust_inputs, dict):
        trust_inputs = {}
        problems.append("signature_verification_policy_lockfile_invalid:trust_inputs_not_object")

    input_map = {
        "trust_keyset": ("auth_keyring", "trust_keyset_sha256", None),
        "trust_keyset_receipt": ("trust_keyset_receipt", "trust_keyset_receipt_sha256", "require_trust_keyset_receipt"),
        "trust_governance_bundle": ("trust_governance_bundle", "trust_governance_bundle_sha256", "require_trust_governance_bundle"),
        "trust_governance_bundle_receipt": ("trust_governance_bundle_receipt", "trust_governance_bundle_receipt_sha256", "require_trust_governance_bundle_receipt"),
        "trust_status_snapshot": ("trust_status_snapshot", "trust_status_snapshot_sha256", "require_trust_status_snapshot"),
        "trust_status_snapshot_receipt": ("trust_status_snapshot_receipt", "trust_status_snapshot_receipt_sha256", "require_trust_status_snapshot_receipt"),
        "signer_authorization_roster": ("signer_authorization_roster", "signer_authorization_roster_sha256", "require_signer_authorization_roster"),
        "signer_authorization_roster_receipt": ("signer_authorization_roster_receipt", "signer_authorization_roster_receipt_sha256", "require_signer_authorization_roster_receipt"),
    }

    unknown_inputs = sorted(str(k) for k in set(trust_inputs.keys()) - set(input_map.keys())) if isinstance(trust_inputs, dict) else []
    summary["verification_policy_lockfile_unknown_trust_input_count"] = len(unknown_inputs)
    for input_name in unknown_inputs:
        problems.append(f"signature_verification_policy_lockfile_unknown_trust_input:{input_name}")

    strict_policy = auth_profile in {STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE, STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE}
    if strict_policy and expected_pin_hex is None:
        summary["verification_policy_lockfile_pin_required"] = True
        summary["verification_policy_lockfile_pin_status"] = "required_missing"
        problems.append("signature_verification_policy_lockfile_pin_required:strict_policy_requires_policy_lockfile_sha256")
    embedded_verification_time_text = str(obj.get("verification_time") or "").strip()
    external_verification_time_text = str(external_verification_time or "").strip()
    summary["verification_policy_lockfile_embedded_verification_time_present"] = bool(embedded_verification_time_text)
    if strict_policy and embedded_verification_time_text:
        problems.append("signature_verification_policy_lockfile_temporal_context_invalid:embedded_verification_time_forbidden")
    if strict_policy and not external_verification_time_text:
        summary["verification_policy_lockfile_temporal_context_status"] = "missing_external_time"
    elif strict_policy:
        summary["verification_policy_lockfile_temporal_context_status"] = "external_time_supplied"
    else:
        summary["verification_policy_lockfile_temporal_context_status"] = "not_required"
    validity_problems, validity_summary = _check_policy_validity_window(obj, external_verification_time_text, strict_policy=strict_policy)
    problems.extend(validity_problems)
    summary.update(validity_summary)
    selector_problems, selector_summary = _check_policy_packet_selector(packet_dir, obj.get("packet_selector"), strict_policy=strict_policy)
    problems.extend(selector_problems)
    summary.update(selector_summary)
    fp_problems, fp_summary = _check_policy_packet_public_fingerprint(packet_dir, obj, strict_policy=strict_policy)
    problems.extend(fp_problems)
    summary.update(fp_summary)
    path_scope_problem = False
    trust_input_base_dir: Path | None = None
    base_dir_raw = obj.get("trust_input_base_dir")
    if strict_policy:
        base_reason = _policy_path_rejection_reason(base_dir_raw, allow_parent_segments=True)
        if base_reason is not None:
            path_scope_problem = True
            problems.append(f"signature_verification_policy_lockfile_path_scope_violation:trust_input_base_dir:{base_reason}")
        else:
            summary["verification_policy_lockfile_trust_input_base_dir"] = str(base_dir_raw).strip()[:240]
            trust_input_base_dir = policy_path.parent / Path(str(base_dir_raw).strip())
            if _path_inside_dir(trust_input_base_dir, packet_dir):
                path_scope_problem = True
                problems.append("signature_verification_policy_lockfile_path_scope_violation:trust_input_base_dir:packet_contained")
    elif isinstance(base_dir_raw, str) and base_dir_raw.strip():
        base_reason = _policy_path_rejection_reason(base_dir_raw, allow_parent_segments=True)
        if base_reason is None:
            summary["verification_policy_lockfile_trust_input_base_dir"] = base_dir_raw.strip()[:240]
            trust_input_base_dir = policy_path.parent / Path(base_dir_raw.strip())
        else:
            path_scope_problem = True
            problems.append(f"signature_verification_policy_lockfile_path_scope_violation:trust_input_base_dir:{base_reason}")

    seen_inputs = 0
    bounded_paths = 0
    closure_inputs: list[dict[str, Any]] = []
    for input_name, (path_arg, pin_arg, require_arg) in input_map.items():
        row = trust_inputs.get(input_name)
        if row is None:
            continue
        if not isinstance(row, dict):
            problems.append(f"signature_verification_policy_lockfile_invalid:trust_input_not_object:{input_name}")
            continue
        seen_inputs += 1
        raw_path = row.get("path")
        path: Path | None = None
        if trust_input_base_dir is not None:
            reason = _policy_path_rejection_reason(raw_path, allow_parent_segments=False)
            if reason is not None:
                path_scope_problem = True
                problems.append(f"signature_verification_policy_lockfile_path_scope_violation:{input_name}:{reason}")
            else:
                parts = _policy_path_parts(str(raw_path))
                candidate = trust_input_base_dir.joinpath(*parts)
                if not _path_inside_base(candidate, trust_input_base_dir):
                    path_scope_problem = True
                    problems.append(f"signature_verification_policy_lockfile_path_scope_violation:{input_name}:outside_base_dir")
                elif _path_inside_dir(candidate, packet_dir):
                    path_scope_problem = True
                    problems.append(f"signature_verification_policy_lockfile_path_scope_violation:{input_name}:packet_contained")
                else:
                    path = candidate
                    bounded_paths += 1
        else:
            path = _resolve_policy_relative_path(policy_path, raw_path)
            if strict_policy:
                # Strict profiles must not silently fall back to policy-relative paths.
                path = None
        if path is None:
            problems.append(f"signature_verification_policy_lockfile_invalid:trust_input_path_missing_or_not_filesystem:{input_name}")
        else:
            config[path_arg] = str(path)
        pin = str(row.get("sha256") or row.get("digest") or "").strip()
        normalized_pin = normalize_sha256_pin(pin) if pin else None
        if pin:
            if normalized_pin is None:
                problems.append(f"signature_verification_policy_lockfile_invalid:trust_input_pin_malformed:{input_name}")
            else:
                config[pin_arg] = "sha256:" + normalized_pin
        required_flag = bool(row.get("required", True))
        if normalized_pin is not None:
            closure_inputs.append({
                "name": input_name,
                "path": str(raw_path or "").strip(),
                "required": required_flag,
                "sha256": "sha256:" + normalized_pin,
            })
        if require_arg is not None:
            config[require_arg] = required_flag

    summary["verification_policy_lockfile_input_count"] = seen_inputs
    summary["verification_policy_lockfile_input_paths_bounded_count"] = bounded_paths
    if path_scope_problem:
        summary["verification_policy_lockfile_path_policy_status"] = "violated"
    elif trust_input_base_dir is not None:
        summary["verification_policy_lockfile_path_policy_status"] = "bounded"
    else:
        summary["verification_policy_lockfile_path_policy_status"] = "not_required"
    if closure_inputs:
        selector = obj.get("packet_selector") if isinstance(obj.get("packet_selector"), dict) else {}
        closure_obj = {
            "profile": "tes.verification_policy_trust_closure.v1",
            "auth_profile": auth_profile,
            "policy_id": policy_id,
            "policy_sha256": "sha256:" + actual_hex,
            "policy_receipt_sha256": str(summary.get("verification_policy_lockfile_receipt_sha256") or ""),
            "packet_selector": {
                "packet_id": str(selector.get("packet_id") or ""),
                "election_id": str(selector.get("election_id") or ""),
                "jurisdiction": str(selector.get("jurisdiction") or ""),
            },
            "packet_public_fingerprint_sha256": str(summary.get("verification_policy_lockfile_packet_public_fingerprint_sha256") or ""),
            "trust_input_base_dir": str(summary.get("verification_policy_lockfile_trust_input_base_dir") or ""),
            "trust_inputs": sorted(closure_inputs, key=lambda r: str(r.get("name") or "")),
        }
        summary["verification_policy_lockfile_trust_closure_input_count"] = len(closure_inputs)
        summary["verification_policy_lockfile_trust_closure_sha256"] = "sha256:" + sha256_hex_bytes(jcs_bytes(closure_obj))
        summary["verification_policy_lockfile_trust_closure_status"] = "computed"

    config["auth_profile"] = auth_profile
    config["require_authentication"] = bool(obj.get("require_authentication", True))
    if not strict_policy and embedded_verification_time_text:
        # Compatibility only for non-strict policy lockfiles. Strict profiles must
        # use caller-supplied temporal context so freshness checks cannot be replayed.
        config["verification_time"] = embedded_verification_time_text

    if auth_profile in {STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE, STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE}:
        required_inputs = set(input_map)
        if auth_profile == STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE:
            required_inputs.discard("signer_authorization_roster")
            required_inputs.discard("signer_authorization_roster_receipt")
        missing = sorted(required_inputs - set(trust_inputs.keys()))
        for name in missing:
            problems.append(f"signature_verification_policy_lockfile_invalid:strict_profile_missing_input:{name}")
        for name in required_inputs:
            row = trust_inputs.get(name)
            if isinstance(row, dict) and not str(row.get("sha256") or row.get("digest") or "").strip():
                problems.append(f"signature_verification_policy_lockfile_invalid:strict_profile_missing_pin:{name}")
        if not external_verification_time_text:
            problems.append("signature_verification_policy_lockfile_temporal_context_invalid:strict_profile_missing_external_verification_time")

    summary["verification_policy_lockfile_status"] = "invalid" if problems else "matched"
    return problems, summary, config


def _verification_policy_conflict_names(args: argparse.Namespace) -> list[str]:
    """Return manually supplied auth/trust flags that conflict with a lockfile."""

    checks = {
        "trust_keyset": bool((args.auth_keyring or "").strip()),
        "trust_keyset_sha256": bool((args.trust_keyset_sha256 or "").strip()),
        "trust_keyset_receipt": bool((args.trust_keyset_receipt or "").strip()),
        "trust_keyset_receipt_sha256": bool((getattr(args, "trust_keyset_receipt_sha256", "") or "").strip()),
        "require_trust_keyset_receipt": bool(args.require_trust_keyset_receipt),
        "trust_governance_bundle": bool((args.trust_governance_bundle or "").strip()),
        "trust_governance_bundle_sha256": bool((args.trust_governance_bundle_sha256 or "").strip()),
        "require_trust_governance_bundle": bool(args.require_trust_governance_bundle),
        "trust_governance_bundle_receipt": bool((args.trust_governance_bundle_receipt or "").strip()),
        "trust_governance_bundle_receipt_sha256": bool((args.trust_governance_bundle_receipt_sha256 or "").strip()),
        "require_trust_governance_bundle_receipt": bool(args.require_trust_governance_bundle_receipt),
        "trust_status_snapshot": bool((args.trust_status_snapshot or "").strip()),
        "trust_status_snapshot_sha256": bool((args.trust_status_snapshot_sha256 or "").strip()),
        "require_trust_status_snapshot": bool(args.require_trust_status_snapshot),
        "trust_status_snapshot_receipt": bool((args.trust_status_snapshot_receipt or "").strip()),
        "trust_status_snapshot_receipt_sha256": bool((args.trust_status_snapshot_receipt_sha256 or "").strip()),
        "require_trust_status_snapshot_receipt": bool(args.require_trust_status_snapshot_receipt),
        "signer_authorization_roster": bool((getattr(args, "signer_authorization_roster", "") or "").strip()),
        "signer_authorization_roster_sha256": bool((getattr(args, "signer_authorization_roster_sha256", "") or "").strip()),
        "require_signer_authorization_roster": bool(getattr(args, "require_signer_authorization_roster", False)),
        "signer_authorization_roster_receipt": bool((getattr(args, "signer_authorization_roster_receipt", "") or "").strip()),
        "signer_authorization_roster_receipt_sha256": bool((getattr(args, "signer_authorization_roster_receipt_sha256", "") or "").strip()),
        "require_signer_authorization_roster_receipt": bool(getattr(args, "require_signer_authorization_roster_receipt", False)),
        # Verification time is intentionally allowed with a policy lockfile: strict
        # policy mode requires caller-supplied temporal context so stale status
        # snapshots cannot be replayed by embedding an old clock in the policy.
        "require_authentication": bool(args.require_authentication),
        "auth_profile": str(args.auth_profile or DEFAULT_AUTH_PROFILE) != DEFAULT_AUTH_PROFILE,
    }
    return [name for name, yes in sorted(checks.items()) if yes]


def _apply_verification_policy_config(args: argparse.Namespace, config: dict[str, Any]) -> None:
    for name, value in config.items():
        if hasattr(args, name):
            setattr(args, name, value)


def _policy_lockfile_failed_signature_summary(
    envelopes_checked: int,
    policy_summary: dict[str, Any],
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "profile": "ed25519-jcs-tbs-v1",
        "authentication_status": "SIGNATURE_FAILED",
        "failure_reason": "verification_policy_lockfile_failed",
        "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
        "envelopes_evaluated": int(envelopes_checked),
        "envelopes_authenticated": 0,
        "trusted_signatures_checked": 0,
        "trusted_signatures_valid": 0,
        "trusted_key_count": 0,
        "trust_keyset_location": "not_supplied",
        "trust_keyset_pin_required": False,
        "trust_keyset_pin_status": "not_supplied",
        "trust_keyset_receipt_required": False,
        "trust_keyset_receipt_status": "not_supplied",
        "policy": {
            "minimum_valid_signatures_per_envelope": 1,
            "minimum_distinct_valid_signatures_per_envelope": 1,
            "require_distinct_key_material": True,
            "require_distinct_kids": True,
            "require_all_envelopes_authenticated": True,
        },
        "non_claims": [
            "does_not_establish_legal_authority",
            "does_not_check_online_revocation",
            "does_not_authorize_live_pilot",
            "does_not_accept_packet_supplied_trust_roots",
        ],
    }
    out.update(policy_summary)
    return out


def read_payload_bytes_from_pointer(env: Dict[str, Any], packet_dir: Path) -> Tuple[bytes, str, str, List[str]]:
    """Load payload bytes and validate pointer hash/size when present."""
    problems: List[str] = []

    ptr = env.get("payload_pointer")
    if not isinstance(ptr, dict):
        return b"", "missing_payload_pointer", "", ["payload_pointer_missing"]

    uri = ptr.get("uri", "")
    if not uri:
        return b"", "missing_uri", "", ["payload_pointer_missing_uri"]

    rel = uri if uri.startswith("objects/") else f"objects/{uri}"
    p = safe_join(packet_dir, rel)
    if p is None:
        return b"", f"unsafe:{uri}", ptr.get("media_type", ""), ["payload_pointer_unsafe_uri"]
    if not p.exists():
        return b"", f"missing:{uri}", ptr.get("media_type", ""), ["payload_pointer_object_missing"]
    hardened = safe_join(packet_dir, rel, must_exist=True)
    if hardened is None:
        return b"", f"unsafe:{uri}", ptr.get("media_type", ""), ["payload_pointer_unsafe_uri"]

    b = hardened.read_bytes()

    # Pointer integrity: hash + size match the referenced object bytes.
    want_digest = ptr.get("digest")
    if isinstance(want_digest, str) and want_digest.startswith("sha256:"):
        want_hex = want_digest.split(":", 1)[1]
        got_hex = sha256_hex(b)
        if got_hex.lower() != want_hex.lower():
            problems.append(f"payload_pointer_hash_mismatch:{uri}")

    if "size_bytes" in ptr:
        try:
            if int(p.stat().st_size) != int(ptr["size_bytes"]):
                problems.append(f"payload_pointer_size_mismatch:{uri}")
        except Exception:
            pass

    return b, f"objects/{uri}", ptr.get("media_type", ""), problems


def recompute_payload_digest(env: Dict[str, Any], packet_dir: Path) -> Tuple[str, str, List[str]]:
    """Recompute payload_digest per docs/176."""
    if "payload_inline" in env:
        try:
            return payload_digest_for_json_value(env["payload_inline"]), "inline", []
        except Exception:
            # Best effort: if object can't be canonicalized, fall back to a sentinel.
            return "sha256:" + ("0" * 64), "inline", ["payload_inline_unserializable"]

    payload_bytes, where, media_type, problems = read_payload_bytes_from_pointer(env, packet_dir)
    if not payload_bytes:
        return "sha256:" + ("0" * 64), where, problems

    canon = env.get("canonicalization", "")
    bytes_to_hash, note = canonicalize_payload_bytes_for_digest(payload_bytes, media_type, canon)
    if note == "raw_non_json_media_type":
        problems.append("payload_pointer_media_type_not_json")
    elif note == "raw_json_parse_failed":
        problems.append("payload_pointer_json_parse_failed")
    return f"sha256:{sha256_hex(bytes_to_hash)}", where, problems


def verify_objects(objects_dir: Path) -> Tuple[List[str], int]:
    problems: List[str] = []
    checked = 0
    if not objects_dir.exists():
        return ["objects_dir_missing"], 0
    for p in objects_dir.iterdir():
        if not p.is_file():
            continue
        name = p.name
        if not name.startswith("sha256-"):
            continue
        checked += 1
        hexpart = name[len("sha256-") :].split(".", 1)[0]
        got = sha256_hex(p.read_bytes())
        if got.lower() != hexpart.lower():
            problems.append(f"object_hash_mismatch:{name}")
    return problems, checked


def verify_attachments(env: Dict[str, Any], packet_dir: Path, env_name: str) -> List[str]:
    problems: List[str] = []
    atts = env.get("attachments")
    if not atts:
        return problems
    if not isinstance(atts, list):
        return [f"attachments_not_array:{env_name}"]

    for i, att in enumerate(atts):
        if not isinstance(att, dict):
            problems.append(f"attachment_not_object:{env_name}:{i}")
            continue
        d = att.get("digest")
        if not d or not isinstance(d, str) or not d.startswith("sha256:"):
            problems.append(f"attachment_missing_digest:{env_name}:{i}")
            continue
        uri = att.get("uri", "")
        if not uri:
            problems.append(f"attachment_missing_uri:{env_name}:{i}:{d}")
            continue
        rel = uri if uri.startswith("objects/") else f"objects/{uri}"
        tgt = safe_join(packet_dir, rel)
        if tgt is None:
            problems.append(f"attachment_unsafe_uri:{env_name}:{i}:{d}")
            continue
        if not tgt.exists():
            problems.append(f"attachment_missing_object:{env_name}:{i}:{d}")
            continue
        hardened = safe_join(packet_dir, rel, must_exist=True)
        if hardened is None:
            problems.append(f"attachment_unsafe_uri:{env_name}:{i}:{d}")
            continue

        b = hardened.read_bytes()
        got = sha256_hex(b)
        want = d.split(":", 1)[1]
        if got.lower() != want.lower():
            problems.append(f"attachment_hash_mismatch:{env_name}:{i}:{tgt.relative_to(packet_dir)}")
            continue

        if "size_bytes" in att:
            try:
                if int(tgt.stat().st_size) != int(att["size_bytes"]):
                    problems.append(f"attachment_size_mismatch:{env_name}:{i}:{tgt.relative_to(packet_dir)}")
            except Exception:
                pass

        # Optional: validate receipt profile identifiers (drift firewall)
        if att.get("rel") == "transparency_receipt" and tgt.suffix == ".json":
            try:
                robj = json.loads(tgt.read_text(encoding="utf-8"))
                prof = robj.get("profile")
                if not prof:
                    problems.append(f"receipt_profile_missing:{env_name}:{i}")
                elif RECEIPT_PROFILES and prof not in RECEIPT_PROFILES:
                    problems.append(f"receipt_profile_unknown:{env_name}:{i}:{prof}")
            except Exception:
                problems.append(f"receipt_unparseable:{env_name}:{i}")

    return problems


def verify_envelopes(env_dir: Path, packet_dir: Path) -> Tuple[List[str], int, Dict[str, int]]:
    problems: List[str] = []
    checked = 0
    kinds_seen: Dict[str, int] = {}
    if not env_dir.exists():
        return ["envelopes_dir_missing"], 0, {}

    for p in env_dir.iterdir():
        if not p.is_file() or not p.name.endswith(".json"):
            continue
        checked += 1
        env = json.loads(p.read_text(encoding="utf-8"))

        kind = str(env.get("kind", "")).strip()
        if kind:
            kinds_seen[kind] = kinds_seen.get(kind, 0) + 1

        # Envelope version interop: reject unknown major versions.
        ev = str(env.get("envelope_version", "")).strip()
        maj = parse_semver_major(ev)
        if maj is None:
            problems.append(f"envelope_version_unparseable:{p.name}:{ev}")
        elif maj not in SUPPORTED_ENVELOPE_MAJORS:
            problems.append(f"envelope_version_unsupported_major:{p.name}:{ev}")

        canon = str(env.get("canonicalization", "")).strip()
        if canon != "RFC8785-JCS":
            problems.append(f"canonicalization_unsupported:{p.name}:{canon or 'missing'}")

        # Registry checks (tight verifier surface).
        row = KIND_ROWS.get(kind)
        if not row:
            if kind:
                problems.append(f"unknown_kind:{p.name}:{kind}")
        else:
            expected_schema = row.get("payload_schema", "").strip()
            got_schema = str(env.get("payload_schema", "")).strip()
            if got_schema and expected_schema and got_schema != expected_schema:
                problems.append(f"payload_schema_mismatch:{p.name}:{kind}:{got_schema}:{expected_schema}")
            expected_track = row.get("track", "").strip()
            got_track = str(env.get("track", "")).strip()
            # Track strings are sometimes human-annotated (e.g., "A (Deployable core)").
            if got_track and expected_track:
                ok_track = (
                    got_track == expected_track
                    or got_track.startswith(expected_track + " ")
                    or got_track.startswith(expected_track + "(")
                )
                if not ok_track:
                    problems.append(f"track_mismatch:{p.name}:{kind}:{got_track}:{expected_track}")

            # Required attachments per kind (anti-selective-disclosure).
            required = ATT_REQS.get(kind) or []
            if required:
                atts = env.get("attachments") or []
                rels_present: dict[str, list[dict]] = {}
                if isinstance(atts, list):
                    for a in atts:
                        if isinstance(a, dict):
                            r = str(a.get("rel", "")).strip()
                            if r:
                                rels_present.setdefault(r, []).append(a)
                for req in required:
                    rel = req.get("rel", "").strip()
                    if not rel:
                        continue
                    if rel not in rels_present:
                        problems.append(f"missing_required_attachment:{p.name}:{kind}:{rel}")
                        continue
                    # Best-effort media_type match (drift firewall).
                    exp_mt = req.get("media_type", "").strip()
                    if exp_mt:
                        for a in rels_present[rel]:
                            mt = (a.get("media_type") or a.get("content_type") or "").strip()
                            if mt and mt != exp_mt:
                                problems.append(f"attachment_media_type_mismatch:{p.name}:{kind}:{rel}:{mt}:{exp_mt}")
        problems += verify_attachments(env, packet_dir, p.name)

        recomputed, where, ptr_problems = recompute_payload_digest(env, packet_dir)
        for pp in ptr_problems:
            problems.append(f"{pp}:{p.name}")
        if recomputed != env.get("payload_digest"):
            problems.append(f"payload_digest_mismatch:{p.name}:{where}")

        # Optional: enforce payload_schema is a real file for schema-path references.
        ps = env.get("payload_schema")
        if isinstance(ps, str) and ps.startswith("schemas/"):
            if not (ROOT / ps).exists():
                problems.append(f"payload_schema_missing:{p.name}:{ps}")

        tbs_digest = tbs_digest_for_envelope(env)
        if tbs_digest != env.get("tbs_digest"):
            problems.append(f"tbs_digest_mismatch:{p.name}")

    return problems, checked, kinds_seen


def verify_manifest(packet_dir: Path) -> List[str]:
    problems: List[str] = []

    mpath = packet_dir / "manifest.json"
    if not mpath.exists():
        return ["manifest_missing"]

    m = json.loads(mpath.read_text(encoding="utf-8"))
    arts = m.get("artifacts", [])
    for a in arts:
        if not isinstance(a, dict):
            continue

        d = a.get("digest") or (("sha256:" + a["sha256"]) if "sha256" in a else "")
        if not isinstance(d, str) or not d.startswith("sha256:"):
            continue
        want_hex = d.split(":", 1)[1]

        # Prefer url field when present.
        url = a.get("url")
        if isinstance(url, str) and url:
            fp = safe_join(packet_dir, url)
            if fp is None:
                problems.append(f"manifest_url_unsafe:{a.get('name','?')}:{url}")
                continue
            if not fp.exists():
                problems.append(f"manifest_url_missing:{a.get('name','?')}:{url}")
                continue
            hardened = safe_join(packet_dir, url, must_exist=True)
            if hardened is None:
                problems.append(f"manifest_url_unsafe:{a.get('name','?')}:{url}")
                continue
            got_hex = sha256_hex(hardened.read_bytes())
            if got_hex.lower() != want_hex.lower():
                problems.append(f"manifest_url_hash_mismatch:{a.get('name','?')}:{url}")
                continue
            if "size_bytes" in a:
                try:
                    if int(fp.stat().st_size) != int(a["size_bytes"]):
                        problems.append(f"manifest_url_size_mismatch:{a.get('name','?')}:{url}")
                except Exception:
                    pass
            continue

        # Fallback: locate by digest in common locations.
        found = False
        for root in [packet_dir / "objects", packet_dir]:
            for ext in [".json", ".bin", ".txt", ".md", ".csv", ".toml", ""]:
                pp = root / f"sha256-{want_hex}{ext}"
                if pp.exists():
                    found = True
                    break
            if found:
                break
        if not found:
            problems.append(f"missing_artifact_object:{a.get('name','?')}:{d}")

    return problems


def build_report(
    packet_dir: Path,
    problems: List[str],
    envelopes_checked: int,
    objects_checked: int,
    kinds_seen: Dict[str, int],
    public: bool,
    verifier_report_tbs_digest: str | None = None,
    policy_profile_sha256: str | None = None,
    public_fingerprint_sha256: str | None = None,
    public_fingerprint_warn_count: int | None = None,
    signature_verification: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    # Public mode: avoid leaking absolute paths and keep outputs comparable.
    packet_id = packet_dir.name if public else str(packet_dir)
    authentication_status = "HASH_ONLY_NOT_AUTHENTICATED"
    notes: List[str] = []
    if signature_verification:
        authentication_status = str(signature_verification.get("authentication_status") or "SIGNATURE_FAILED")
        if authentication_status == "SIGNATURE_VERIFIED" and any(severity_for_code(code_of(p)) == "FAIL" for p in problems):
            # A valid envelope signature alone must not authenticate a packet
            # whose detached payload, manifest, registry, or schema checks fail.
            authentication_status = "SIGNATURE_FAILED"
            signature_verification = dict(signature_verification)
            signature_verification["authentication_status"] = authentication_status
            signature_verification["failure_reason"] = "packet_integrity_or_policy_failure"
        if authentication_status == "SIGNATURE_VERIFIED":
            notes.append("authentication_status=SIGNATURE_VERIFIED under the bounded ed25519-jcs-tbs-v1 offline trust-keyset profile; this still does not establish legal authority or live-pilot authorization.")
        else:
            notes.append("authentication_status=SIGNATURE_FAILED under the bounded ed25519-jcs-tbs-v1 offline trust-keyset profile or because packet integrity/policy checks failed.")
    else:
        notes.extend([
            "authentication_status=HASH_ONLY_NOT_AUTHENTICATED; default verifier profile checks packet integrity but not signer identity.",
            "Run with --trust-keyset to verify Ed25519-JCS-TBS-v1 signatures against a local public-key trust keyset; add --trust-keyset-sha256, receipts/governance/status arguments, and --signer-authorization-roster for stronger local trust-root/status/role binding.",
        ])
    if public_fingerprint_sha256:
        notes.append(f"public_fingerprint_sha256=sha256:{public_fingerprint_sha256}")
        if public_fingerprint_warn_count is not None and int(public_fingerprint_warn_count) > 0:
            notes.append(f"public_fingerprint_warn_count={int(public_fingerprint_warn_count)}")

    # Drift firewall: if the verifier emits an unknown code, add a stable sentinel.
    # Keep the original problem strings (they may contain useful local context).
    if not public:
        codes = sorted(set([code_of(x) for x in problems if isinstance(x, str) and x.strip()]))
        unknown = [c for c in codes if c and not is_known(c)]
        if unknown:
            for c in unknown:
                problems.append(f"unknown_problem_code:{c}")
            notes.append(f"Detected {len(unknown)} unrecognized problem code(s); emitted unknown_problem_code sentinel(s).")
    if public:
        codes = sorted(set([code_of(x) for x in problems if isinstance(x, str) and x.strip()]))
        unknown = [c for c in codes if c and not is_known(c)]
        codes = [c for c in codes if c and is_known(c)]
        if unknown:
            # Public mode only publishes stable codes; collapse any unrecognized codes.
            codes.append("unknown_problem_code")
            codes = sorted(set(codes))
            notes.append(f"Suppressed {len(unknown)} unknown problem code(s) in public output.")
        problems = codes
    report: Dict[str, Any] = {
        "report_version": REPORT_VERSION,
        "generated_at": generated_at,
        "packet_dir": packet_id,
        "tool": {
            "name": "observer_verify_packet",
            "version": ARCHIVE_VERSION,
            "archive_version": ARCHIVE_VERSION,
        },
        "authentication_status": authentication_status,
        "status": (
            "PASS"
            if not problems
            else ("FAIL" if any(severity_for_code(code_of(p)) == "FAIL" for p in problems) else "PASS_WITH_WARNINGS")
        ),
        "problems": list(problems),
        "envelopes_checked": int(envelopes_checked),
        "objects_checked": int(objects_checked),
        "kinds_seen": dict(sorted(kinds_seen.items())),
        "notes": notes,
    }

    if signature_verification:
        # Publishable bounded auth summary: no private material and no absolute paths.
        report["signature_verification"] = dict(signature_verification)
        if signature_verification.get("profile"):
            report["signature_profile"] = str(signature_verification.get("profile"))
        if signature_verification.get("trust_keyset_sha256"):
            report["trust_keyset_sha256"] = str(signature_verification.get("trust_keyset_sha256"))
        policy = signature_verification.get("policy") if isinstance(signature_verification.get("policy"), dict) else {}
        if "minimum_valid_signatures_per_envelope" in policy:
            try:
                report["signature_threshold"] = int(policy["minimum_valid_signatures_per_envelope"])
            except Exception:
                pass
        for src_key, out_key in (
            ("envelopes_evaluated", "signature_envelopes_checked"),
            ("envelopes_authenticated", "signature_envelopes_verified"),
            ("trusted_signatures_checked", "trusted_signatures_checked"),
            ("trusted_signatures_valid", "trusted_signatures_valid"),
        ):
            if src_key in signature_verification:
                try:
                    report[out_key] = int(signature_verification[src_key])
                except Exception:
                    pass

    # Optional: link packet-scoped results to an implementation-scoped verifier identity report.
    # This is publishable and enables comparison across verifier identities.
    if verifier_report_tbs_digest:
        report["verifier_report_tbs_digest"] = verifier_report_tbs_digest

    if policy_profile_sha256:
        report["policy_profile_sha256"] = policy_profile_sha256


    # Optional comparability pins: include sha256 of key public-surface registries when available.
    try:
        if VERIFIER_PROBLEM_CODES_REGISTRY.exists():
            report["verifier_problem_codes_sha256"] = "sha256:" + sha256_hex_bytes(VERIFIER_PROBLEM_CODES_REGISTRY.read_bytes())
    except Exception:
        pass

    try:
        if VERIFIER_PROFILES_REGISTRY.exists():
            report["verifier_profiles_sha256"] = "sha256:" + sha256_hex_bytes(VERIFIER_PROFILES_REGISTRY.read_bytes())
    except Exception:
        pass

    try:
        if KIND_REGISTRY.exists():
            report["envelope_kinds_sha256"] = "sha256:" + sha256_hex_bytes(KIND_REGISTRY.read_bytes())
    except Exception:
        pass

    try:
        if ATTACHMENT_REQUIREMENTS.exists():
            report["attachment_requirements_sha256"] = "sha256:" + sha256_hex_bytes(ATTACHMENT_REQUIREMENTS.read_bytes())
    except Exception:
        pass

    try:
        if RECEIPT_PROFILE_REGISTRY.exists():
            report["receipt_profiles_sha256"] = "sha256:" + sha256_hex_bytes(RECEIPT_PROFILE_REGISTRY.read_bytes())
    except Exception:
        pass

    mpath = packet_dir / "manifest.json"
    if mpath.exists():
        try:
            mbytes = mpath.read_bytes()
            report["manifest_sha256"] = "sha256:" + sha256_hex_bytes(mbytes)
            # Optional: formatting-independent digest for JSON manifests (RFC8785-JCS).
            try:
                mobj = json.loads(mbytes.decode("utf-8"))
                report["manifest_jcs_sha256"] = "sha256:" + sha256_hex_bytes(jcs_bytes(mobj))
            except Exception:
                pass
        except Exception:
            pass

    return report


def _best_effort_election_id(packet_dir: Path) -> str:
    """Pull election_id from a packet manifest when available."""
    try:
        m = json.loads((packet_dir / "manifest.json").read_text(encoding="utf-8"))
        eid = (m.get("election_id") or "").strip()
        return eid or "ELECTION_UNKNOWN"
    except Exception:
        return "ELECTION_UNKNOWN"


def emit_report_as_packet(out_dir: Path, report_public: Dict[str, Any], issuer_id: str, subject_extra: Dict[str, Any] | None = None, policy_profile_bytes: bytes | None = None) -> Path:
    """Emit a minimal evidence packet containing a publishable PacketVerificationReport.

    Returns the written envelope path.
    """

    out_dir = out_dir.resolve()
    (out_dir / "objects").mkdir(parents=True, exist_ok=True)
    (out_dir / "envelopes").mkdir(parents=True, exist_ok=True)
    (out_dir / "notes").mkdir(parents=True, exist_ok=True)

    payload_bytes = jcs_bytes(report_public)
    payload_hex = sha256_hex(payload_bytes)
    payload_digest = f"sha256:{payload_hex}"

    obj_name = f"sha256-{payload_hex}.json"
    obj_path = out_dir / "objects" / obj_name
    if not obj_path.exists():
        obj_path.write_bytes(payload_bytes)


    # Optional: if a policy profile file was provided, ship its canonical bytes as a content-addressed object
    # in the emitted report packet so third parties can reproduce verifier decisions offline.
    policy_artifact: Dict[str, Any] | None = None
    pp_digest = report_public.get("policy_profile_sha256")
    if policy_profile_bytes and isinstance(pp_digest, str) and pp_digest.startswith("sha256:"):
        pp_hex = pp_digest.split(":", 1)[1]
        pp_name = f"sha256-{pp_hex}.json"
        pp_path = out_dir / "objects" / pp_name
        # Only emit if the bytes actually match the declared digest (fail-closed for portability).
        if sha256_hex(policy_profile_bytes).lower() == pp_hex.lower():
            if not pp_path.exists():
                pp_path.write_bytes(policy_profile_bytes)
            policy_artifact = {
                "name": "VerifierPolicyProfile (detached; RFC8785-JCS bytes)",
                "media_type": "application/json",
                "digest": pp_digest,
                "size_bytes": int(pp_path.stat().st_size),
                "url": str(pp_path.relative_to(out_dir)).replace("\\", "/"),
                "kind": "hfv.verifier.policy_profile",
                "schema": "schemas/VerifierPolicyProfile.json",
            }

    issued_at = iso_utc_now_seconds()
    subject: Dict[str, Any] = {
        "packet_dir": report_public.get("packet_dir", ""),
    }
    if isinstance(report_public.get("manifest_sha256"), str) and report_public.get("manifest_sha256"):
        subject["packet_manifest_sha256"] = report_public["manifest_sha256"]
    # Optional: include policy-profile pin on the envelope subject for index-only scans.
    # This is publishable (digest only) and helps third parties compare reports without fetching payload bytes.
    if isinstance(report_public.get("policy_profile_sha256"), str) and report_public.get("policy_profile_sha256"):
        subject["policy_profile_sha256"] = report_public["policy_profile_sha256"]
    if subject_extra:
        for k, v in subject_extra.items():
            if k not in subject:
                subject[k] = v

    env: Dict[str, Any] = {
        "envelope_version": "1.1.0",
        "kind": "hfv.verifier.packet_verification_report",
        "track": "A",
        "issued_at": issued_at,
        "issuer": {"issuer_id": issuer_id},
        "subject": subject,
        "payload_schema": "schemas/PacketVerificationReport.json",
        "canonicalization": "RFC8785-JCS",
        "payload_digest": payload_digest,
        "payload_pointer": {
            "digest": payload_digest,
            "media_type": "application/json",
            "size_bytes": int(len(payload_bytes)),
            "uri": obj_name,
        },
    }
    env["tbs_digest"] = tbs_digest_for_envelope(env)
    env["signatures"] = [
        {
            "signer_id": issuer_id,
            "alg": "none",
            "sig": "UNSIGNED",
            "sig_encoding": "base64",
        }
    ]

    env_path = out_dir / "envelopes" / f"packet_verification_report_{payload_hex[:16]}.json"
    env_path.write_text(json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Minimal manifest (so this packet can be re-verified offline).
    created_at = issued_at
    election_id = (subject_extra or {}).get("election_id") or "ELECTION_UNKNOWN"
    manifest = {
        "election_id": election_id,
        "created_at": created_at,
        "crypto_policy": {
            "election_id": election_id,
            "allowed_crypto_suites": ["hfv.placeholder.suite"],
            "default_crypto_suite": "hfv.placeholder.suite",
            "deprecation": [],
            "notes": "Placeholder crypto policy for verifier report packets; replace in production bundles. authentication_status=HASH_ONLY_NOT_AUTHENTICATED means this packet is not signer-authenticated by the stdlib verifier.",
        },
        "artifacts": [
            {
                "name": "PacketVerificationReport envelope",
                "media_type": "application/json",
                "digest": f"sha256:{sha256_hex(env_path.read_bytes())}",
                "size_bytes": int(env_path.stat().st_size),
                "url": str(env_path.relative_to(out_dir)).replace("\\\\", "/"),
                "kind": "hfv.envelope",
                "schema": "schemas/EvidenceEnvelope.json",
            },
            {
                "name": "PacketVerificationReport payload (detached)",
                "media_type": "application/json",
                "digest": payload_digest,
                "size_bytes": int(obj_path.stat().st_size),
                "url": str(obj_path.relative_to(out_dir)).replace("\\\\", "/"),
                "kind": "hfv.verifier.packet_verification_report",
                "schema": "schemas/PacketVerificationReport.json",
            },
        ]
        + ([policy_artifact] if policy_artifact else []),
        "signatures": [
            {
                "signer_id": issuer_id,
                "alg": "none",
                "sig": "UNSIGNED",
            }
        ],
        "bundle_version": "0.1",
        "created_by": "tools/observer_verify_packet.py --emit-evidence-object",
        "notes": "This packet is a minimal verifier-report bundle. authentication_status=HASH_ONLY_NOT_AUTHENTICATED; replace placeholder signatures/crypto policy before production use.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    readme = out_dir / "notes" / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Verifier report packet\n\n**Track:** Shared (cross-cutting)\n\n"
            "This is a minimal evidence packet containing a publishable `PacketVerificationReport` as an `EvidenceEnvelope`.\n\n"
            "Generated by `tools/observer_verify_packet.py --emit-evidence-object`.\n\n"
            "`authentication_status=HASH_ONLY_NOT_AUTHENTICATED` means this stdlib report packet checks hash/shape integrity only; it does not authenticate signer identity.\n",
            encoding="utf-8",
            newline="\n",
        )

    return env_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet_dir", nargs="?", default="", help="Packet directory")
    ap.add_argument("--list-codes", action="store_true", help="List publishable verifier problem codes and exit")
    ap.add_argument("--explain", default="", help="Explain one verifier problem code (or problem string) and exit")
    ap.add_argument("--json", action="store_true", help="Emit PacketVerificationReport JSON to stdout")
    ap.add_argument("--public", action="store_true", help="Public-safe output: codes only; sanitize packet_dir")
    ap.add_argument(
        "--lint-public",
        action="store_true",
        help="Also run publishable artifact lint and report only stable codes (adds public_artifact_lint_failed|warn)",
    )
    ap.add_argument(
        "--lint-max-string",
        type=int,
        default=int(PUBLIC_LINT_DEFAULT_MAX_STRING),
        help="Maximum allowed string length for --lint-public (default aligns with tools/publication_policy.py)",
    )
    ap.add_argument(
        "--public-fingerprint",
        action="store_true",
        help="Also compute a bounded public fingerprint (docs/226) and add it to notes as public_fingerprint_sha256=...",
    )
    ap.add_argument(
        "--public-fingerprint-out",
        default="",
        help="Optional: write PUBLIC_FINGERPRINT report JSON to this path (suggested: <packet_dir>/public-fingerprint.json)",
    )
    ap.add_argument(
        "--public-fingerprint-stable",
        action="store_true",
        help="When writing --public-fingerprint-out, omit generated_at so the file is stable across regenerations",
    )
    ap.add_argument(
        "--public-fingerprint-max-bytes",
        type=int,
        default=int(PUBLIC_FP_DEFAULT_MAX_BYTES),
        help="Max bytes read per included file for --public-fingerprint (default aligns with tools/public_fingerprint_report.py)",
    )

    ap.add_argument(
        "--verify-public-fingerprint",
        action="store_true",
        help="Verify a shipped public-fingerprint.json (or the path from --public-fingerprint-out) matches the computed bounded fingerprint (adds public_fingerprint_* codes on failure)",
    )

    ap.add_argument("--out", help="Write PacketVerificationReport JSON to this path")
    ap.add_argument(
        "--emit-evidence-object",
        dest="emit_packet_dir",
        default="",
        help="Emit a minimal verifier-report evidence packet to this directory (always uses public-safe payload)",
    )
    ap.add_argument(
        "--verifier-report-envelope",
        default="",
        help="Optional: path to an EvidenceEnvelope JSON of kind hfv.verifier.report; include its tbs_digest in the PacketVerificationReport as verifier_report_tbs_digest",
    )
    ap.add_argument(
        "--verifier-report-tbs-digest",
        default="",
        help="Optional: set verifier_report_tbs_digest directly (sha256:<hex>)",
    )

    ap.add_argument(
        "--policy-profile",
        default="",
        help="Optional: path to a verifier policy profile JSON file; include sha256 of its RFC8785-JCS canonical bytes as policy_profile_sha256",
    )
    ap.add_argument(
        "--policy-profile-sha256",
        default="",
        help="Optional: set policy_profile_sha256 directly (sha256:<hex>)",
    )

    ap.add_argument(
        "--verification-policy-lockfile",
        default="",
        help="Optional external JSON policy lockfile that supplies the strict local trust-chain inputs and pins as one governed verifier configuration; rejected if packet-contained.",
    )
    ap.add_argument(
        "--verification-policy-lockfile-sha256",
        default="",
        help="Optional fail-closed pin for --verification-policy-lockfile bytes (sha256:<hex> or bare 64-hex).",
    )
    ap.add_argument(
        "--verification-policy-lockfile-receipt",
        default="",
        help="Optional external JSON receipt binding the verification-policy lockfile sha256 to independent publication channels; rejected if packet-contained.",
    )
    ap.add_argument(
        "--verification-policy-lockfile-receipt-sha256",
        default="",
        help="Optional fail-closed pin for --verification-policy-lockfile-receipt bytes (sha256:<hex> or bare 64-hex).",
    )
    ap.add_argument(
        "--require-verification-policy-lockfile-receipt",
        action="store_true",
        help="Fail unless --verification-policy-lockfile-receipt is supplied, external to the packet, and matches the policy-lockfile digest/channel quorum.",
    )

    ap.add_argument(
        "--trust-keyset",
        "--auth-keyring",
        dest="auth_keyring",
        default="",
        help="Optional: verify Ed25519-JCS-TBS-v1 EvidenceEnvelope signatures using this local public trust-keyset JSON",
    )
    ap.add_argument(
        "--trust-keyset-sha256",
        default="",
        help="Optional fail-closed pin for --trust-keyset bytes (sha256:<hex> or bare 64-hex). Prevents silent local trust-keyset swap.",
    )
    ap.add_argument(
        "--trust-keyset-receipt",
        default="",
        help="Optional external JSON receipt binding the trust-keyset sha256 to independent publication channels; rejected if packet-contained.",
    )
    ap.add_argument(
        "--trust-keyset-receipt-sha256",
        default="",
        help="Optional fail-closed pin for --trust-keyset-receipt bytes (sha256:<hex> or bare 64-hex). Prevents silent local trust-keyset publication-receipt swap.",
    )
    ap.add_argument(
        "--require-trust-keyset-receipt",
        action="store_true",
        help="Fail unless --trust-keyset-receipt is supplied, external to the packet, and matches the trust-keyset digest/channel quorum.",
    )
    ap.add_argument(
        "--trust-governance-bundle",
        default="",
        help="Optional external JSON governance bundle binding key ceremony, witness quorum, key events, keyset digest, and receipt digest; rejected if packet-contained.",
    )
    ap.add_argument(
        "--trust-governance-bundle-sha256",
        default="",
        help="Optional fail-closed pin for --trust-governance-bundle bytes (sha256:<hex> or bare 64-hex). Prevents silent local governance-bundle swap.",
    )
    ap.add_argument(
        "--require-trust-governance-bundle",
        action="store_true",
        help="Fail unless --trust-governance-bundle is supplied, external to the packet, digest-pinned when requested, and internally coherent with the keyset and receipt.",
    )
    ap.add_argument(
        "--trust-governance-bundle-receipt",
        default="",
        help="Optional external JSON receipt binding the trust-governance-bundle sha256 to independent publication channels; rejected if packet-contained.",
    )
    ap.add_argument(
        "--trust-governance-bundle-receipt-sha256",
        default="",
        help="Optional fail-closed pin for --trust-governance-bundle-receipt bytes (sha256:<hex> or bare 64-hex).",
    )
    ap.add_argument(
        "--require-trust-governance-bundle-receipt",
        action="store_true",
        help="Fail unless --trust-governance-bundle-receipt is supplied, external to the packet, and matches the governance-bundle digest/channel quorum.",
    )
    ap.add_argument(
        "--trust-status-snapshot",
        default="",
        help="Optional external JSON status snapshot binding the trust keyset/governance digests to key status and update-window evidence; rejected if packet-contained.",
    )
    ap.add_argument(
        "--trust-status-snapshot-sha256",
        default="",
        help="Optional fail-closed pin for --trust-status-snapshot bytes (sha256:<hex> or bare 64-hex).",
    )
    ap.add_argument(
        "--require-trust-status-snapshot",
        action="store_true",
        help="Fail unless --trust-status-snapshot is supplied, external to the packet, fresh for verification time, and does not revoke or omit trusted keys.",
    )
    ap.add_argument(
        "--trust-status-snapshot-receipt",
        default="",
        help="Optional external JSON receipt binding the trust-status-snapshot sha256 to independent publication channels; rejected if packet-contained.",
    )
    ap.add_argument(
        "--trust-status-snapshot-receipt-sha256",
        default="",
        help="Optional fail-closed pin for --trust-status-snapshot-receipt bytes (sha256:<hex> or bare 64-hex).",
    )
    ap.add_argument(
        "--require-trust-status-snapshot-receipt",
        action="store_true",
        help="Fail unless --trust-status-snapshot-receipt is supplied, external to the packet, and matches the status-snapshot digest/channel quorum.",
    )
    ap.add_argument(
        "--signer-authorization-roster",
        default="",
        help="Optional external JSON signer-authorization roster binding trusted keys/signers to allowed envelope kinds, roles, scope, and authorities; rejected if packet-contained.",
    )
    ap.add_argument(
        "--signer-authorization-roster-sha256",
        default="",
        help="Optional fail-closed pin for --signer-authorization-roster bytes (sha256:<hex> or bare 64-hex).",
    )
    ap.add_argument(
        "--require-signer-authorization-roster",
        action="store_true",
        help="Fail unless --signer-authorization-roster is supplied, external to the packet, byte-pinned when requested, and authorizes trusted signers for checked envelope kinds/roles.",
    )
    ap.add_argument(
        "--signer-authorization-roster-receipt",
        default="",
        help="Optional external JSON receipt binding the signer-authorization roster sha256 to independent publication channels; rejected if packet-contained.",
    )
    ap.add_argument(
        "--signer-authorization-roster-receipt-sha256",
        default="",
        help="Optional fail-closed pin for --signer-authorization-roster-receipt bytes (sha256:<hex> or bare 64-hex).",
    )
    ap.add_argument(
        "--require-signer-authorization-roster-receipt",
        action="store_true",
        help="Fail unless --signer-authorization-roster-receipt is supplied, external to the packet, and matches the signer-authorization roster digest/channel quorum.",
    )
    ap.add_argument(
        "--verification-time",
        default="",
        help="Optional RFC3339 time used for bounded status-snapshot freshness checks; defaults to verifier wall-clock time.",
    )
    ap.add_argument(
        "--auth-profile",
        default=DEFAULT_AUTH_PROFILE,
        choices=[DEFAULT_AUTH_PROFILE, STRICT_LOCAL_TRUST_CHAIN_AUTH_PROFILE, STRICT_LOCAL_AUTHORIZED_TRUST_CHAIN_AUTH_PROFILE],
        help="Authentication profile to enforce when --trust-keyset is supplied. strict-local-trust-chain-v1 requires pinned external trust keyset, receipts, governance, status, quorum evidence, and threshold>=2. strict-local-authorized-trust-chain-v1 also requires a pinned external signer-authorization roster and signer-authorization publication receipt.",
    )

    ap.add_argument(
        "--require-authentication",
        action="store_true",
        help="Fail unless a supplied trust keyset authenticates every envelope under the bounded Ed25519-JCS-TBS-v1 profile",
    )

    ap.add_argument(
        "--issuer-id",
        default="verifier:observer_verify_packet",
        help="issuer_id to place in the emitted EvidenceEnvelope/manifest (for --emit-evidence-object)",
    )
    args = ap.parse_args()
    if args.list_codes:
        print("Verifier problem codes (publishable surface)")
        for pc in all_codes_sorted():
            print(f"{pc.code}	{pc.severity}	{pc.summary}")
        return 0

    if args.explain:
        code = code_of(args.explain)
        pc = CODES.get(code)
        if not pc:
            # Fail closed: unknown codes should not be normalized into publication without review.
            print(f"UNKNOWN	{code}")
            print(CODES["unknown_problem_code"].summary)
            return 2
        print(f"{pc.code}	{pc.severity}	{pc.summary}")
        return 0

    if not args.packet_dir:
        ap.error("packet_dir is required unless --list-codes or --explain is used")

    packet_dir = Path(args.packet_dir)

    policy_lockfile_problems: list[str] = []
    policy_lockfile_summary: dict[str, Any] = {}
    if (args.verification_policy_lockfile or "").strip():
        conflicts = _verification_policy_conflict_names(args)
        if conflicts:
            policy_lockfile_summary = {
                "verification_policy_lockfile_status": "conflict",
                "verification_policy_lockfile_sha256": "",
                "verification_policy_lockfile_pin_required": bool((args.verification_policy_lockfile_sha256 or "").strip()),
                "verification_policy_lockfile_pin_status": "not_checked",
                "verification_policy_lockfile_pin_sha256": "",
                "verification_policy_lockfile_receipt_required": bool(getattr(args, "require_verification_policy_lockfile_receipt", False)),
                "verification_policy_lockfile_receipt_status": "not_checked",
                "verification_policy_lockfile_receipt_sha256": "",
                "verification_policy_lockfile_receipt_pin_required": bool((getattr(args, "verification_policy_lockfile_receipt_sha256", "") or "").strip()),
                "verification_policy_lockfile_receipt_pin_status": "not_checked",
                "verification_policy_lockfile_receipt_pin_sha256": "",
                "verification_policy_lockfile_receipt_id": "",
                "verification_policy_lockfile_receipt_profile": "",
                "verification_policy_lockfile_receipt_channel_count": 0,
                "verification_policy_lockfile_receipt_independent_channel_count": 0,
                "verification_policy_lockfile_receipt_required_independent_channels": 0,
                "verification_policy_lockfile_id": "",
                "verification_policy_lockfile_profile": "",
                "verification_policy_lockfile_input_count": 0,
                "verification_policy_lockfile_auth_profile": "",
                "verification_policy_lockfile_path_policy_status": "not_checked",
                "verification_policy_lockfile_trust_input_base_dir": "",
                "verification_policy_lockfile_input_paths_bounded_count": 0,
                "verification_policy_lockfile_validity_status": "not_checked",
                "verification_policy_lockfile_valid_from": "",
                "verification_policy_lockfile_valid_until": "",
                "verification_policy_lockfile_external_verification_time": str(args.verification_time or "")[:64],
                "verification_policy_lockfile_temporal_context_status": "not_checked",
                "verification_policy_lockfile_embedded_verification_time_present": False,
                "verification_policy_lockfile_packet_selector_status": "not_checked",
                "verification_policy_lockfile_packet_selector_packet_id": "",
                "verification_policy_lockfile_packet_selector_election_id": "",
                "verification_policy_lockfile_packet_selector_jurisdiction": "",
                "verification_policy_lockfile_packet_selector_actual_packet_id": "",
                "verification_policy_lockfile_packet_selector_actual_election_ids": [],
                "verification_policy_lockfile_packet_selector_actual_jurisdictions": [],
                "verification_policy_lockfile_conflicts": conflicts,
            }
            policy_lockfile_problems.append(
                "signature_verification_policy_lockfile_conflict:" + ",".join(conflicts[:20])
            )
        else:
            policy_lockfile_problems, policy_lockfile_summary, policy_config = load_verification_policy_lockfile(
                packet_dir,
                Path(args.verification_policy_lockfile),
                args.verification_policy_lockfile_sha256,
                args.verification_time,
                Path(args.verification_policy_lockfile_receipt) if (args.verification_policy_lockfile_receipt or "").strip() else None,
                args.verification_policy_lockfile_receipt_sha256,
                bool(args.require_verification_policy_lockfile_receipt),
            )
            if not policy_lockfile_problems:
                _apply_verification_policy_config(args, policy_config)

    elif (
        (getattr(args, "verification_policy_lockfile_receipt", "") or "").strip()
        or (getattr(args, "verification_policy_lockfile_receipt_sha256", "") or "").strip()
        or bool(getattr(args, "require_verification_policy_lockfile_receipt", False))
    ):
        policy_lockfile_summary = {
            "verification_policy_lockfile_status": "not_supplied",
            "verification_policy_lockfile_sha256": "",
            "verification_policy_lockfile_pin_required": bool((args.verification_policy_lockfile_sha256 or "").strip()),
            "verification_policy_lockfile_pin_status": "not_supplied",
            "verification_policy_lockfile_pin_sha256": "",
            "verification_policy_lockfile_receipt_required": bool(args.require_verification_policy_lockfile_receipt),
            "verification_policy_lockfile_receipt_status": "invalid",
            "verification_policy_lockfile_receipt_sha256": "",
            "verification_policy_lockfile_receipt_pin_required": bool((args.verification_policy_lockfile_receipt_sha256 or "").strip()),
            "verification_policy_lockfile_receipt_pin_status": "not_checked",
            "verification_policy_lockfile_receipt_pin_sha256": "",
            "verification_policy_lockfile_receipt_id": "",
            "verification_policy_lockfile_receipt_profile": "",
            "verification_policy_lockfile_receipt_channel_count": 0,
            "verification_policy_lockfile_receipt_independent_channel_count": 0,
            "verification_policy_lockfile_receipt_required_independent_channels": 0,
            "verification_policy_lockfile_id": "",
            "verification_policy_lockfile_profile": "",
            "verification_policy_lockfile_input_count": 0,
            "verification_policy_lockfile_auth_profile": "",
            "verification_policy_lockfile_path_policy_status": "not_checked",
            "verification_policy_lockfile_trust_input_base_dir": "",
            "verification_policy_lockfile_input_paths_bounded_count": 0,
            "verification_policy_lockfile_validity_status": "not_checked",
            "verification_policy_lockfile_valid_from": "",
            "verification_policy_lockfile_valid_until": "",
            "verification_policy_lockfile_packet_selector_status": "not_checked",
            "verification_policy_lockfile_packet_selector_packet_id": "",
            "verification_policy_lockfile_packet_selector_election_id": "",
            "verification_policy_lockfile_packet_selector_jurisdiction": "",
            "verification_policy_lockfile_packet_selector_actual_packet_id": "",
            "verification_policy_lockfile_packet_selector_actual_election_ids": [],
            "verification_policy_lockfile_packet_selector_actual_jurisdictions": [],
        }
        policy_lockfile_problems.append(
            "signature_verification_policy_lockfile_receipt_invalid:policy_lockfile_not_supplied"
        )

    verifier_report_tbs_digest: str | None = None
    # Optional linkage: allow packet reports to point at an implementation-scoped verifier report envelope.
    if args.verifier_report_tbs_digest:
        v = args.verifier_report_tbs_digest.strip()
        if re.fullmatch(r"sha256:[0-9a-f]{64}", v):
            verifier_report_tbs_digest = v
        else:
            # Do not treat as a packet failure; just ignore and keep the report publishable.
            # Avoid leaking full paths in public notes.
            pass
    elif args.verifier_report_envelope:
        p = Path(args.verifier_report_envelope)
        try:
            env_obj = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(env_obj, dict) and env_obj.get("kind") == "hfv.verifier.report":
                computed = tbs_digest_for_envelope(env_obj)
                # If the envelope includes a tbs_digest field and it disagrees, ignore the linkage.
                existing = env_obj.get("tbs_digest")
                if isinstance(existing, str) and existing and existing != computed:
                    # Don't fail the packet; just avoid publishing a confusing pointer.
                    pass
                else:
                    verifier_report_tbs_digest = computed
        except Exception:
            pass

    policy_profile_sha256: str | None = None
    policy_profile_bytes: bytes | None = None
    if args.policy_profile_sha256:
        v = args.policy_profile_sha256.strip()
        if re.fullmatch(r"sha256:[0-9a-f]{64}", v):
            policy_profile_sha256 = v
        else:
            # Ignore invalid values to keep output publishable.
            pass
    elif args.policy_profile:
        p = Path(args.policy_profile)
        try:
            # Policy profiles are JSON; hash their RFC8785-JCS canonical bytes for comparability.
            obj = json.loads(p.read_text(encoding="utf-8"))
            b = jcs_bytes(obj)
            policy_profile_bytes = b
            policy_profile_sha256 = "sha256:" + sha256_hex_bytes(b)
        except Exception:
            # Fallback: if parsing fails, hash raw bytes (best-effort).
            try:
                b = p.read_bytes()
                policy_profile_bytes = b
                policy_profile_sha256 = "sha256:" + sha256_hex_bytes(b)
            except Exception:
                pass

    problems: List[str] = []
    problems += policy_lockfile_problems
    obj_problems, objects_checked = verify_objects(packet_dir / "objects")
    problems += obj_problems
    env_problems, envelopes_checked, kinds_seen = verify_envelopes(packet_dir / "envelopes", packet_dir)
    problems += env_problems
    problems += verify_manifest(packet_dir)

    verification_time: datetime | None = None
    if (args.verification_time or "").strip():
        verification_time = _parse_rfc3339_utc(str(args.verification_time))
        if verification_time is None:
            problems.append("signature_trust_status_snapshot_invalid:verification_time_unparseable")

    signature_verification: Dict[str, Any] | None = None
    if (args.auth_keyring or "").strip():
        sig_problems, signature_verification = verify_packet_signatures(
            packet_dir,
            Path(args.auth_keyring),
            expected_keyset_sha256=(args.trust_keyset_sha256 or ""),
            trust_keyset_receipt=Path(args.trust_keyset_receipt) if (args.trust_keyset_receipt or "").strip() else None,
            expected_trust_keyset_receipt_sha256=(args.trust_keyset_receipt_sha256 or ""),
            require_trust_keyset_receipt=bool(args.require_trust_keyset_receipt),
            trust_governance_bundle=Path(args.trust_governance_bundle) if (args.trust_governance_bundle or "").strip() else None,
            expected_governance_bundle_sha256=(args.trust_governance_bundle_sha256 or ""),
            require_trust_governance_bundle=bool(args.require_trust_governance_bundle),
            trust_governance_bundle_receipt=Path(args.trust_governance_bundle_receipt) if (args.trust_governance_bundle_receipt or "").strip() else None,
            expected_governance_bundle_receipt_sha256=(args.trust_governance_bundle_receipt_sha256 or ""),
            require_trust_governance_bundle_receipt=bool(args.require_trust_governance_bundle_receipt),
            trust_status_snapshot=Path(args.trust_status_snapshot) if (args.trust_status_snapshot or "").strip() else None,
            expected_trust_status_snapshot_sha256=(args.trust_status_snapshot_sha256 or ""),
            require_trust_status_snapshot=bool(args.require_trust_status_snapshot),
            trust_status_snapshot_receipt=Path(args.trust_status_snapshot_receipt) if (args.trust_status_snapshot_receipt or "").strip() else None,
            expected_trust_status_snapshot_receipt_sha256=(args.trust_status_snapshot_receipt_sha256 or ""),
            require_trust_status_snapshot_receipt=bool(args.require_trust_status_snapshot_receipt),
            signer_authorization_roster=Path(args.signer_authorization_roster) if (args.signer_authorization_roster or "").strip() else None,
            expected_signer_authorization_roster_sha256=(args.signer_authorization_roster_sha256 or ""),
            require_signer_authorization_roster=bool(args.require_signer_authorization_roster),
            signer_authorization_roster_receipt=Path(args.signer_authorization_roster_receipt) if (args.signer_authorization_roster_receipt or "").strip() else None,
            expected_signer_authorization_roster_receipt_sha256=(args.signer_authorization_roster_receipt_sha256 or ""),
            require_signer_authorization_roster_receipt=bool(args.require_signer_authorization_roster_receipt),
            verification_time=verification_time,
            auth_profile=str(args.auth_profile or DEFAULT_AUTH_PROFILE),
        )
        if policy_lockfile_summary:
            signature_verification.update(policy_lockfile_summary)
        problems += sig_problems
    elif policy_lockfile_summary:
        signature_verification = _policy_lockfile_failed_signature_summary(
            envelopes_checked,
            policy_lockfile_summary,
        )
    elif (
        (args.signer_authorization_roster or "").strip()
        or bool(args.require_signer_authorization_roster)
        or (args.signer_authorization_roster_sha256 or "").strip()
        or (args.signer_authorization_roster_receipt or "").strip()
        or bool(args.require_signer_authorization_roster_receipt)
        or (args.signer_authorization_roster_receipt_sha256 or "").strip()
    ):
        signature_verification = {
            "profile": "ed25519-jcs-tbs-v1",
            "authentication_status": "SIGNATURE_FAILED",
            "failure_reason": "signer_authorization_roster_without_trust_keyset",
            "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
            "envelopes_evaluated": int(envelopes_checked),
            "envelopes_authenticated": 0,
            "trusted_signatures_checked": 0,
            "trusted_signatures_valid": 0,
            "trusted_key_count": 0,
            "trust_keyset_location": "not_supplied",
            "trust_keyset_pin_required": bool((args.trust_keyset_sha256 or "").strip()),
            "trust_keyset_pin_status": "not_supplied",
            "trust_keyset_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_keyset_sha256)) if normalize_sha256_pin(args.trust_keyset_sha256 or "") else "",
            "trust_keyset_receipt_required": bool(args.require_trust_keyset_receipt),
            "trust_keyset_receipt_status": "not_supplied",
            "signer_authorization_roster_required": bool(args.require_signer_authorization_roster),
            "signer_authorization_roster_status": "missing" if bool(args.require_signer_authorization_roster) else "invalid",
            "signer_authorization_roster_sha256": "",
            "signer_authorization_roster_pin_required": bool((args.signer_authorization_roster_sha256 or "").strip()),
            "signer_authorization_roster_pin_status": "not_supplied",
            "signer_authorization_roster_pin_sha256": ("sha256:" + normalize_sha256_pin(args.signer_authorization_roster_sha256)) if normalize_sha256_pin(args.signer_authorization_roster_sha256 or "") else "",
            "signer_authorization_roster_id": "",
            "signer_authorization_roster_profile": "",
            "signer_authorization_authority_count": 0,
            "signer_authorization_required_authority_count": 0,
            "signer_authorization_entry_count": 0,
            "signer_authorization_active_entry_count": 0,
            "signer_authorization_roster_receipt_required": bool(args.require_signer_authorization_roster_receipt),
            "signer_authorization_roster_receipt_status": "missing" if bool(args.require_signer_authorization_roster_receipt) else ("invalid" if (args.signer_authorization_roster_receipt or "").strip() else "not_supplied"),
            "signer_authorization_roster_receipt_sha256": "",
            "signer_authorization_roster_receipt_pin_required": bool((args.signer_authorization_roster_receipt_sha256 or "").strip()),
            "signer_authorization_roster_receipt_pin_status": "not_supplied",
            "signer_authorization_roster_receipt_pin_sha256": ("sha256:" + normalize_sha256_pin(args.signer_authorization_roster_receipt_sha256)) if normalize_sha256_pin(args.signer_authorization_roster_receipt_sha256 or "") else "",
            "signer_authorization_roster_receipt_id": "",
            "signer_authorization_roster_receipt_profile": "",
            "signer_authorization_roster_receipt_channel_count": 0,
            "signer_authorization_roster_receipt_independent_channel_count": 0,
            "signer_authorization_roster_receipt_required_independent_channels": 0,
            "policy": {
                "minimum_valid_signatures_per_envelope": 1,
                "minimum_distinct_valid_signatures_per_envelope": 1,
                "require_distinct_key_material": True,
                "require_distinct_kids": True,
                "require_all_envelopes_authenticated": True,
            },
            "non_claims": [
                "does_not_establish_legal_authority",
                "does_not_authorize_live_pilot",
                "does_not_accept_packet_supplied_trust_roots",
            ],
        }
        if (args.signer_authorization_roster_receipt or "").strip() or bool(args.require_signer_authorization_roster_receipt) or (args.signer_authorization_roster_receipt_sha256 or "").strip():
            problems.append("signature_signer_authorization_roster_receipt_invalid:receipt_without_trust_keyset")
        problems.append("signature_signer_authorization_roster_invalid:roster_without_trust_keyset")
    elif (
        (args.trust_status_snapshot or "").strip()
        or bool(args.require_trust_status_snapshot)
        or (args.trust_status_snapshot_sha256 or "").strip()
        or (args.trust_status_snapshot_receipt or "").strip()
        or bool(args.require_trust_status_snapshot_receipt)
        or (args.trust_status_snapshot_receipt_sha256 or "").strip()
    ):
        signature_verification = {
            "profile": "ed25519-jcs-tbs-v1",
            "authentication_status": "SIGNATURE_FAILED",
            "failure_reason": "trust_status_snapshot_without_trust_keyset",
            "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
            "envelopes_evaluated": int(envelopes_checked),
            "envelopes_authenticated": 0,
            "trusted_signatures_checked": 0,
            "trusted_signatures_valid": 0,
            "trusted_key_count": 0,
            "trust_keyset_location": "not_supplied",
            "trust_keyset_pin_required": bool((args.trust_keyset_sha256 or "").strip()),
            "trust_keyset_pin_status": "not_supplied",
            "trust_keyset_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_keyset_sha256)) if normalize_sha256_pin(args.trust_keyset_sha256 or "") else "",
            "trust_keyset_receipt_required": bool(args.require_trust_keyset_receipt),
            "trust_keyset_receipt_status": "not_supplied",
            "trust_keyset_receipt_sha256": "",
            "trust_keyset_receipt_id": "",
            "trust_keyset_receipt_profile": "",
            "trust_keyset_receipt_channel_count": 0,
            "trust_keyset_receipt_independent_channel_count": 0,
            "trust_keyset_receipt_required_independent_channels": 0,
            "trust_status_snapshot_required": bool(args.require_trust_status_snapshot),
            "trust_status_snapshot_status": "missing" if bool(args.require_trust_status_snapshot) else "invalid",
            "trust_status_snapshot_sha256": "",
            "trust_status_snapshot_pin_required": bool((args.trust_status_snapshot_sha256 or "").strip()),
            "trust_status_snapshot_pin_status": "not_supplied",
            "trust_status_snapshot_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_status_snapshot_sha256)) if normalize_sha256_pin(args.trust_status_snapshot_sha256 or "") else "",
            "trust_status_snapshot_id": "",
            "trust_status_snapshot_profile": "",
            "trust_status_snapshot_this_update": "",
            "trust_status_snapshot_next_update": "",
            "trust_status_snapshot_verification_time": verification_time.isoformat(timespec="seconds").replace("+00:00", "Z") if verification_time is not None else "",
            "trust_status_snapshot_key_status_count": 0,
            "trust_status_snapshot_revoked_key_count": 0,
            "trust_status_snapshot_authority_count": 0,
            "trust_status_snapshot_required_authority_count": 0,
            "trust_status_snapshot_receipt_required": bool(args.require_trust_status_snapshot_receipt),
            "trust_status_snapshot_receipt_status": "missing" if bool(args.require_trust_status_snapshot_receipt) else ("invalid" if ((args.trust_status_snapshot_receipt or "").strip() or (args.trust_status_snapshot_receipt_sha256 or "").strip()) else "not_supplied"),
            "trust_status_snapshot_receipt_sha256": "",
            "trust_status_snapshot_receipt_pin_required": bool((args.trust_status_snapshot_receipt_sha256 or "").strip()),
            "trust_status_snapshot_receipt_pin_status": "not_supplied",
            "trust_status_snapshot_receipt_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_status_snapshot_receipt_sha256)) if normalize_sha256_pin(args.trust_status_snapshot_receipt_sha256 or "") else "",
            "trust_status_snapshot_receipt_id": "",
            "trust_status_snapshot_receipt_profile": "",
            "trust_status_snapshot_receipt_channel_count": 0,
            "trust_status_snapshot_receipt_independent_channel_count": 0,
            "trust_status_snapshot_receipt_required_independent_channels": 0,
            "policy": {
                "minimum_valid_signatures_per_envelope": 1,
                "minimum_distinct_valid_signatures_per_envelope": 1,
                "require_distinct_key_material": True,
                "require_distinct_kids": True,
                "require_all_envelopes_authenticated": True,
            },
            "non_claims": [
                "does_not_establish_legal_authority",
                "does_not_check_online_revocation",
                "does_not_authorize_live_pilot",
                "does_not_accept_packet_supplied_trust_roots",
            ],
        }
        problems.append("signature_trust_status_snapshot_invalid:status_snapshot_without_trust_keyset")
    elif (
        (args.trust_governance_bundle or "").strip()
        or bool(args.require_trust_governance_bundle)
        or (args.trust_governance_bundle_sha256 or "").strip()
        or (args.trust_governance_bundle_receipt or "").strip()
        or bool(args.require_trust_governance_bundle_receipt)
        or (args.trust_governance_bundle_receipt_sha256 or "").strip()
    ):
        signature_verification = {
            "profile": "ed25519-jcs-tbs-v1",
            "authentication_status": "SIGNATURE_FAILED",
            "failure_reason": "trust_governance_bundle_without_trust_keyset",
            "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
            "envelopes_evaluated": int(envelopes_checked),
            "envelopes_authenticated": 0,
            "trusted_signatures_checked": 0,
            "trusted_signatures_valid": 0,
            "trusted_key_count": 0,
            "trust_keyset_location": "not_supplied",
            "trust_keyset_pin_required": bool((args.trust_keyset_sha256 or "").strip()),
            "trust_keyset_pin_status": "not_supplied",
            "trust_keyset_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_keyset_sha256)) if normalize_sha256_pin(args.trust_keyset_sha256 or "") else "",
            "trust_keyset_receipt_required": bool(args.require_trust_keyset_receipt),
            "trust_keyset_receipt_status": "not_supplied",
            "trust_keyset_receipt_sha256": "",
            "trust_keyset_receipt_id": "",
            "trust_keyset_receipt_profile": "",
            "trust_keyset_receipt_channel_count": 0,
            "trust_keyset_receipt_independent_channel_count": 0,
            "trust_keyset_receipt_required_independent_channels": 0,
            "trust_governance_bundle_required": bool(args.require_trust_governance_bundle),
            "trust_governance_bundle_status": "missing" if bool(args.require_trust_governance_bundle) else "invalid",
            "trust_governance_bundle_sha256": "",
            "trust_governance_bundle_pin_required": bool((args.trust_governance_bundle_sha256 or "").strip()),
            "trust_governance_bundle_pin_status": "not_supplied",
            "trust_governance_bundle_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_governance_bundle_sha256)) if normalize_sha256_pin(args.trust_governance_bundle_sha256 or "") else "",
            "trust_governance_bundle_id": "",
            "trust_governance_bundle_profile": "",
            "trust_governance_witness_count": 0,
            "trust_governance_required_witness_count": 0,
            "trust_governance_event_count": 0,
            "trust_governance_rotation_or_revocation_event_count": 0,
            "policy": {
                "minimum_valid_signatures_per_envelope": 1,
                "minimum_distinct_valid_signatures_per_envelope": 1,
                "require_distinct_key_material": True,
                "require_distinct_kids": True,
                "require_all_envelopes_authenticated": True,
            },
            "non_claims": [
                "does_not_establish_legal_authority",
                "does_not_check_online_revocation",
                "does_not_authorize_live_pilot",
                "does_not_accept_packet_supplied_trust_roots",
            ],
        }
        problems.append("signature_trust_governance_bundle_invalid:governance_bundle_without_trust_keyset")
    elif (args.trust_keyset_receipt or "").strip() or bool(args.require_trust_keyset_receipt):
        signature_verification = {
            "profile": "ed25519-jcs-tbs-v1",
            "authentication_status": "SIGNATURE_FAILED",
            "failure_reason": "trust_keyset_receipt_without_trust_keyset",
            "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
            "envelopes_evaluated": int(envelopes_checked),
            "envelopes_authenticated": 0,
            "trusted_signatures_checked": 0,
            "trusted_signatures_valid": 0,
            "trusted_key_count": 0,
            "trust_keyset_location": "not_supplied",
            "trust_keyset_pin_required": bool((args.trust_keyset_sha256 or "").strip()),
            "trust_keyset_pin_status": "not_supplied",
            "trust_keyset_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_keyset_sha256)) if normalize_sha256_pin(args.trust_keyset_sha256 or "") else "",
            "trust_keyset_receipt_required": bool(args.require_trust_keyset_receipt),
            "trust_keyset_receipt_status": "missing" if bool(args.require_trust_keyset_receipt) else "invalid",
            "trust_keyset_receipt_sha256": "",
            "trust_keyset_receipt_id": "",
            "trust_keyset_receipt_profile": "",
            "trust_keyset_receipt_channel_count": 0,
            "trust_keyset_receipt_independent_channel_count": 0,
            "trust_keyset_receipt_required_independent_channels": 0,
            "policy": {
                "minimum_valid_signatures_per_envelope": 1,
                "minimum_distinct_valid_signatures_per_envelope": 1,
                "require_distinct_key_material": True,
                "require_distinct_kids": True,
                "require_all_envelopes_authenticated": True,
            },
            "non_claims": [
                "does_not_establish_legal_authority",
                "does_not_check_online_revocation",
                "does_not_authorize_live_pilot",
                "does_not_accept_packet_supplied_trust_roots",
            ],
        }
        problems.append("signature_trust_keyset_receipt_invalid:receipt_without_trust_keyset")
    elif (args.trust_keyset_sha256 or "").strip():
        signature_verification = {
            "profile": "ed25519-jcs-tbs-v1",
            "authentication_status": "SIGNATURE_FAILED",
            "failure_reason": "trust_keyset_pin_without_trust_keyset",
            "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
            "envelopes_evaluated": int(envelopes_checked),
            "envelopes_authenticated": 0,
            "trusted_signatures_checked": 0,
            "trusted_signatures_valid": 0,
            "trusted_key_count": 0,
            "trust_keyset_location": "not_supplied",
            "trust_keyset_pin_required": True,
            "trust_keyset_pin_status": "not_supplied",
            "trust_keyset_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_keyset_sha256)) if normalize_sha256_pin(args.trust_keyset_sha256 or "") else "",
            "policy": {
                "minimum_valid_signatures_per_envelope": 1,
                "minimum_distinct_valid_signatures_per_envelope": 1,
                "require_distinct_key_material": True,
                "require_distinct_kids": True,
                "require_all_envelopes_authenticated": True,
            },
            "trust_keyset_receipt_required": False,
            "trust_keyset_receipt_status": "not_supplied",
            "trust_keyset_receipt_sha256": "",
            "trust_keyset_receipt_id": "",
            "trust_keyset_receipt_profile": "",
            "trust_keyset_receipt_channel_count": 0,
            "trust_keyset_receipt_independent_channel_count": 0,
            "trust_keyset_receipt_required_independent_channels": 0,
            "non_claims": [
                "does_not_establish_legal_authority",
                "does_not_check_online_revocation",
                "does_not_authorize_live_pilot",
                "does_not_accept_packet_supplied_trust_roots",
            ],
        }
        problems.append("signature_trust_keyset_invalid:trust_keyset_sha256_without_trust_keyset")
    elif args.require_authentication:
        signature_verification = {
            "profile": "ed25519-jcs-tbs-v1",
            "authentication_status": "SIGNATURE_FAILED",
            "failure_reason": "trust_keyset_not_supplied",
            "dependency": "cryptography" if CRYPTOGRAPHY_AVAILABLE else "cryptography_missing",
            "envelopes_evaluated": int(envelopes_checked),
            "envelopes_authenticated": 0,
            "trusted_signatures_checked": 0,
            "trusted_signatures_valid": 0,
            "trusted_key_count": 0,
            "trust_keyset_location": "not_supplied",
            "trust_keyset_pin_required": bool((args.trust_keyset_sha256 or "").strip()),
            "trust_keyset_pin_status": "not_supplied",
            "trust_keyset_pin_sha256": ("sha256:" + normalize_sha256_pin(args.trust_keyset_sha256)) if normalize_sha256_pin(args.trust_keyset_sha256 or "") else "",
            "policy": {
                "minimum_valid_signatures_per_envelope": 1,
                "minimum_distinct_valid_signatures_per_envelope": 1,
                "require_distinct_key_material": True,
                "require_distinct_kids": True,
                "require_all_envelopes_authenticated": True,
            },
            "trust_keyset_receipt_required": False,
            "trust_keyset_receipt_status": "not_supplied",
            "trust_keyset_receipt_sha256": "",
            "trust_keyset_receipt_id": "",
            "trust_keyset_receipt_profile": "",
            "trust_keyset_receipt_channel_count": 0,
            "trust_keyset_receipt_independent_channel_count": 0,
            "trust_keyset_receipt_required_independent_channels": 0,
            "non_claims": [
                "does_not_establish_legal_authority",
                "does_not_check_online_revocation",
                "does_not_authorize_live_pilot",
                "does_not_accept_packet_supplied_trust_roots",
            ],
        }
        problems.append("signature_trust_keyset_invalid:require_authentication_without_trust_keyset")

    # Optional: compute bounded public fingerprint digest (docs/226).
    want_public_fp = bool(args.public_fingerprint or (args.public_fingerprint_out or "").strip() or args.verify_public_fingerprint)
    public_fp_hex: str | None = None
    public_fp_warn_count: int | None = None
    public_fp_warnings: list[str] = []
    public_fp_lines: list[str] = []
    public_fp_truncated_count: int | None = None
    public_fp_jcs_fail_count: int | None = None
    if want_public_fp:
        if compute_public_fingerprint is None:
            # Keep the report publishable; surface the missing feature as a note later.
            pass
        else:
            try:
                public_fp_hex, public_fp_lines, public_fp_warnings = compute_public_fingerprint(
                    packet_dir,
                    max_include_bytes=int(args.public_fingerprint_max_bytes),
                )
                public_fp_warn_count = len(public_fp_warnings)
                # Public fingerprint warnings are comparability signals; elevate key ones
                # to stable publishable verifier codes.
                public_fp_truncated_count = sum(1 for w in public_fp_warnings if "file_truncated_for_hash:" in (w or ""))
                public_fp_jcs_fail_count = sum(1 for w in public_fp_warnings if "json_canonicalize_failed:" in (w or ""))
            except Exception:
                public_fp_hex = None
                public_fp_lines = []
                public_fp_warnings = []
                public_fp_warn_count = None
                public_fp_truncated_count = None
                public_fp_jcs_fail_count = None

    # Public fingerprint warning codes (docs/226): keep the report publishable and stable.
    if want_public_fp and public_fp_truncated_count is not None and int(public_fp_truncated_count) > 0:
        problems.append(f"public_fingerprint_input_truncated:count={int(public_fp_truncated_count)}")
    if want_public_fp and public_fp_jcs_fail_count is not None and int(public_fp_jcs_fail_count) > 0:
        problems.append(f"public_fingerprint_json_canonicalize_failed:count={int(public_fp_jcs_fail_count)}")

    # Optional publishable artifact lint (secrets/bodies/unbounded headers).
    if args.lint_public:
        if lint_public_packet is None:
            # Fail closed: if the lint helper can't be loaded, surface a stable code.
            problems.append("public_artifact_lint_failed:lint_tool_unavailable")
        else:
            try:
                findings = lint_public_packet(packet_dir, max_string=int(args.lint_max_string))
                fail = sum(1 for f in findings if getattr(f, "severity", "") == "FAIL")
                warn = sum(1 for f in findings if getattr(f, "severity", "") == "WARN")
                if fail > 0:
                    problems.append(f"public_artifact_lint_failed:fail={fail}:warn={warn}")
                elif warn > 0:
                    problems.append(f"public_artifact_lint_warn:warn={warn}")
            except Exception as e:
                # Fail closed; keep the report publishable.
                problems.append(f"public_artifact_lint_failed:exception={type(e).__name__}")

    report = build_report(
        packet_dir,
        problems,
        envelopes_checked,
        objects_checked,
        kinds_seen,
        args.public,
        verifier_report_tbs_digest=verifier_report_tbs_digest,
        policy_profile_sha256=policy_profile_sha256,
        public_fingerprint_sha256=public_fp_hex,
        public_fingerprint_warn_count=public_fp_warn_count,
        signature_verification=signature_verification,
    )

    # Optional: write a public fingerprint report file.
    if want_public_fp and (args.public_fingerprint_out or "").strip() and public_fp_hex:
        try:
            out_path = Path(args.public_fingerprint_out)
            if not out_path.is_absolute():
                out_path = (packet_dir / out_path).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            fp_report: Dict[str, Any] = {
                "report_format_version": PUBLIC_FP_REPORT_FORMAT_VERSION,
                "hash_alg": "sha256",
                "root_hash_construction": "sha256(sorted_lines_of('sha256  relpath'))",
                "public_fingerprint_sha256": public_fp_hex,
                "included_file_count": len(public_fp_lines),
                "include_rules": {
                    "root_text_names": sorted(PUBLIC_FP_ROOT_TEXT_NAMES),
                    "root_json_names": sorted(PUBLIC_FP_ROOT_JSON_NAMES),
                    "root_excludes": sorted(PUBLIC_FP_EXCLUDE_ROOT_NAMES),
                    "envelopes": "envelopes/*.envelope.json",
                    "objects": "objects/*.json",
                    "notes": "notes/**/*.md|txt",
                    "json_canonicalization": "RFC8785 JCS",
                },
                "warnings": list(public_fp_warnings),
            }
            if not args.public_fingerprint_stable:
                fp_report["generated_at"] = iso_utc_now_seconds()
            out_path.write_text(json.dumps(fp_report, indent=2) + "\n", encoding="utf-8")
        except Exception:
            # Keep the verifier report publishable; fingerprint output is a convenience artifact.
            pass


    # Optional: verify a shipped fingerprint file matches computed digest (useful for mirrored bundles).
    if args.verify_public_fingerprint:
        if not public_fp_hex:
            problems.append("public_fingerprint_unavailable")
        else:
            fp_path_str = (args.public_fingerprint_out or "").strip() or "public-fingerprint.json"
            fp_path = Path(fp_path_str)
            if not fp_path.is_absolute():
                fp_path = (packet_dir / fp_path).resolve()
            if not fp_path.exists() or not fp_path.is_file():
                problems.append("public_fingerprint_file_missing")
            else:
                try:
                    fp_obj = json.loads(fp_path.read_text(encoding="utf-8"))
                    found = fp_obj.get("public_fingerprint_sha256") if isinstance(fp_obj, dict) else None
                    if not isinstance(found, str) or not re.fullmatch(r"[0-9a-f]{64}", found.strip()):
                        problems.append("public_fingerprint_file_invalid")
                    else:
                        found_hex = found.strip()
                        if found_hex != public_fp_hex:
                            problems.append(
                                f"public_fingerprint_mismatch:found=sha256:{found_hex}:expected=sha256:{public_fp_hex}"
                            )
                except Exception:
                    problems.append("public_fingerprint_file_invalid")
    
        # Rebuild the report so JSON output reflects any newly-added public_fingerprint_* codes.
        report = build_report(
            packet_dir,
            problems,
            envelopes_checked,
            objects_checked,
            kinds_seen,
            args.public,
            verifier_report_tbs_digest=verifier_report_tbs_digest,
            policy_profile_sha256=policy_profile_sha256,
            public_fingerprint_sha256=public_fp_hex,
            public_fingerprint_warn_count=public_fp_warn_count,
            signature_verification=signature_verification,
        )
    if want_public_fp and not public_fp_hex:
        report.get("notes", []).append("public_fingerprint_unavailable")

    # Optional: emit a publishable evidence object as its own minimal packet.
    if args.emit_packet_dir:
        report_public = build_report(
            packet_dir,
            problems,
            envelopes_checked,
            objects_checked,
            kinds_seen,
            True,
            verifier_report_tbs_digest=verifier_report_tbs_digest,
            policy_profile_sha256=policy_profile_sha256,
            public_fingerprint_sha256=public_fp_hex,
            public_fingerprint_warn_count=public_fp_warn_count,
            signature_verification=signature_verification,
        )
        subject_extra = {"election_id": _best_effort_election_id(packet_dir)}
        emit_report_as_packet(Path(args.emit_packet_dir), report_public, issuer_id=args.issuer_id, subject_extra=subject_extra, policy_profile_bytes=policy_profile_bytes)

    if args.out:
        try:
            Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except Exception as e:
            # If we can't write the report, fail closed.
            problems.append(f"report_write_failed:{args.out}:{e}")
            report = build_report(
                packet_dir,
                problems,
                envelopes_checked,
                objects_checked,
                kinds_seen,
                args.public,
                verifier_report_tbs_digest=verifier_report_tbs_digest,
                policy_profile_sha256=policy_profile_sha256,
                public_fingerprint_sha256=public_fp_hex,
                public_fingerprint_warn_count=public_fp_warn_count,
                signature_verification=signature_verification,
            )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if not problems else 2

    if problems:
        for p in problems:
            print("PROBLEM", p)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
