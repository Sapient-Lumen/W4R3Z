from __future__ import annotations

import hmac
import re
import secrets
from typing import Any

from .errors import LacunaError
from .util import canonical_json, require_id, sha256_text

SEAL_SCHEME = "lacuna.salted-sha256-json.v1"
SEAL_DOMAIN = "lacuna.fair-play-seal.v1"
SEAL_PURPOSES = {"mystery", "continuity", "choice", "other"}
SEAL_VISIBILITIES = {"public", "restricted"}
SEAL_NONCE_BYTES = 32
SEAL_NONCE_RE = re.compile(r"^[0-9a-f]{64}$")
SEAL_MAX_PAYLOAD_BYTES = 65536
SEAL_MAX_DEPTH = 32
SEAL_MAX_ITEMS = 10000
SEAL_SAFE_INTEGER = (1 << 53) - 1


def _validate_unicode_scalars(value: str, *, path: str) -> None:
    for index, character in enumerate(value):
        code_point = ord(character)
        if 0xD800 <= code_point <= 0xDFFF:
            raise LacunaError(
                "seal-payload-unicode-scalar",
                "seal payload strings and object keys may not contain unpaired UTF-16 surrogate code points",
                {"path": path, "character_index": index},
            )


def _validate_portable_json(value: Any, *, path: str, depth: int, counter: list[int]) -> None:
    """Validate the deliberately small, cross-language seal payload profile.

    Floats are excluded because equivalent JSON numbers can serialize differently across
    runtimes. Object keys are strings and integer values are kept within I-JSON's exactly
    representable range. Unicode code points are preserved exactly; no normalization occurs.
    """

    if depth > SEAL_MAX_DEPTH:
        raise LacunaError(
            "seal-payload-too-deep",
            f"seal payload exceeds maximum nesting depth {SEAL_MAX_DEPTH}",
            {"path": path},
        )
    counter[0] += 1
    if counter[0] > SEAL_MAX_ITEMS:
        raise LacunaError(
            "seal-payload-too-large",
            f"seal payload exceeds maximum item count {SEAL_MAX_ITEMS}",
            {"path": path},
        )
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        _validate_unicode_scalars(value, path=path)
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > SEAL_SAFE_INTEGER:
            raise LacunaError(
                "seal-payload-unsafe-integer",
                "seal payload integers must be exactly representable in interoperable JSON",
                {"path": path, "limit": SEAL_SAFE_INTEGER},
            )
        return
    if isinstance(value, float):
        raise LacunaError(
            "seal-payload-float",
            "seal payloads do not permit floating-point values; encode exact decimals as strings",
            {"path": path},
        )
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_portable_json(
                item,
                path=f"{path}[{index}]",
                depth=depth + 1,
                counter=counter,
            )
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise LacunaError(
                    "seal-payload-key",
                    "seal payload object keys must be strings",
                    {"path": path},
                )
            _validate_unicode_scalars(key, path=f"{path}.<key>")
            _validate_portable_json(
                item,
                path=f"{path}.{key}",
                depth=depth + 1,
                counter=counter,
            )
        return
    raise LacunaError(
        "seal-payload-type",
        "seal payload must contain only JSON null, booleans, strings, safe integers, arrays, and objects",
        {"path": path, "python_type": type(value).__name__},
    )


def validate_seal_payload(payload: Any) -> Any:
    _validate_portable_json(payload, path="payload", depth=0, counter=[0])
    encoded = canonical_json(payload).encode("utf-8")
    if len(encoded) > SEAL_MAX_PAYLOAD_BYTES:
        raise LacunaError(
            "seal-payload-too-large",
            f"canonical seal payload exceeds {SEAL_MAX_PAYLOAD_BYTES} UTF-8 bytes",
            {"actual_bytes": len(encoded), "maximum_bytes": SEAL_MAX_PAYLOAD_BYTES},
        )
    return payload


def validate_seal_nonce(nonce: Any) -> str:
    if not isinstance(nonce, str) or not SEAL_NONCE_RE.fullmatch(nonce):
        raise LacunaError(
            "bad-seal-nonce",
            "seal nonce must be exactly 32 random bytes encoded as 64 lowercase hexadecimal characters",
        )
    return nonce


def seal_commitment_core(
    *,
    cube_id: str,
    seal_id: str,
    payload: Any,
    nonce: str,
    scheme: str = SEAL_SCHEME,
) -> dict[str, Any]:
    require_id(cube_id, "cube_id")
    require_id(seal_id, "seal_id")
    if scheme != SEAL_SCHEME:
        raise LacunaError(
            "unsupported-seal-scheme",
            f"seal scheme must be {SEAL_SCHEME!r}",
            {"actual": scheme},
        )
    validate_seal_nonce(nonce)
    validate_seal_payload(payload)
    return {
        "domain": SEAL_DOMAIN,
        "scheme": scheme,
        "cube_id": cube_id,
        "seal_id": seal_id,
        "nonce": nonce,
        "payload": payload,
    }


def seal_commitment_sha256(
    *,
    cube_id: str,
    seal_id: str,
    payload: Any,
    nonce: str,
    scheme: str = SEAL_SCHEME,
) -> str:
    return sha256_text(
        canonical_json(
            seal_commitment_core(
                cube_id=cube_id,
                seal_id=seal_id,
                payload=payload,
                nonce=nonce,
                scheme=scheme,
            )
        )
    )


def prepare_seal_opening(
    *,
    cube_id: str,
    seal_id: str,
    payload: Any,
    nonce: str | None = None,
) -> dict[str, Any]:
    opening_nonce = validate_seal_nonce(nonce) if nonce is not None else secrets.token_hex(SEAL_NONCE_BYTES)
    digest = seal_commitment_sha256(
        cube_id=cube_id,
        seal_id=seal_id,
        payload=payload,
        nonce=opening_nonce,
    )
    return {
        "event": "lacuna.seal.opening.prepared",
        "schema": "lacuna.seal-opening.v1",
        "scheme": SEAL_SCHEME,
        "cube_id": cube_id,
        "seal_id": seal_id,
        "commitment_sha256": digest,
        "nonce": opening_nonce,
        "payload": payload,
        "custody_warning": (
            "Keep this opening outside the cube until reveal. Anyone who obtains it can learn the payload; "
            "loss of the nonce makes the commitment impossible to open."
        ),
    }


def parse_seal_opening(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise LacunaError("bad-seal-opening", "seal opening root must be a JSON object")
    allowed = {
        "event",
        "schema",
        "scheme",
        "cube_id",
        "seal_id",
        "commitment_sha256",
        "nonce",
        "payload",
        "custody_warning",
    }
    unexpected = sorted(set(document) - allowed)
    if unexpected:
        raise LacunaError(
            "unexpected-seal-opening-field",
            "seal opening contains unrecognized fields",
            {"fields": unexpected},
        )
    required = allowed
    missing = sorted(required - set(document))
    if missing:
        raise LacunaError(
            "bad-seal-opening",
            "seal opening is missing required fields",
            {"fields": missing},
        )
    if document.get("event") != "lacuna.seal.opening.prepared":
        raise LacunaError(
            "bad-seal-opening",
            "seal opening event must be 'lacuna.seal.opening.prepared'",
        )
    if document.get("schema") != "lacuna.seal-opening.v1":
        raise LacunaError("bad-seal-opening", "seal opening schema must be 'lacuna.seal-opening.v1'")
    if document.get("scheme") != SEAL_SCHEME:
        raise LacunaError(
            "unsupported-seal-scheme",
            f"seal scheme must be {SEAL_SCHEME!r}",
            {"actual": document.get("scheme")},
        )
    custody_warning = document.get("custody_warning")
    if not isinstance(custody_warning, str) or not custody_warning.strip():
        raise LacunaError(
            "bad-seal-opening",
            "seal opening custody_warning must be a non-empty string",
        )
    cube_id = require_id(document.get("cube_id"), "cube_id")
    seal_id = require_id(document.get("seal_id"), "seal_id")
    nonce = validate_seal_nonce(document.get("nonce"))
    if "payload" not in document:
        raise LacunaError("bad-seal-opening", "seal opening must contain payload")
    payload = validate_seal_payload(document["payload"])
    supplied_digest = document.get("commitment_sha256")
    if not isinstance(supplied_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", supplied_digest):
        raise LacunaError(
            "bad-seal-opening",
            "seal opening commitment_sha256 must be a lowercase SHA-256 digest",
        )
    actual_digest = seal_commitment_sha256(
        cube_id=cube_id,
        seal_id=seal_id,
        payload=payload,
        nonce=nonce,
    )
    if not hmac.compare_digest(actual_digest, supplied_digest):
        raise LacunaError(
            "seal-opening-self-mismatch",
            "seal opening payload and nonce do not match its embedded commitment digest",
            {"expected": supplied_digest, "actual": actual_digest},
        )
    return {
        "schema": "lacuna.seal-opening.v1",
        "scheme": SEAL_SCHEME,
        "cube_id": cube_id,
        "seal_id": seal_id,
        "commitment_sha256": supplied_digest,
        "nonce": nonce,
        "payload": payload,
    }


def opening_matches_commitment(
    *,
    cube_id: str,
    seal_id: str,
    commitment_sha256: str,
    payload: Any,
    nonce: str,
    scheme: str = SEAL_SCHEME,
) -> bool:
    actual = seal_commitment_sha256(
        cube_id=cube_id,
        seal_id=seal_id,
        payload=payload,
        nonce=nonce,
        scheme=scheme,
    )
    return hmac.compare_digest(actual, commitment_sha256)
