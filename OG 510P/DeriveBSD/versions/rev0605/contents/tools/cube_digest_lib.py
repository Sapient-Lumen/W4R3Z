"""Shared restricted-JCS/I-JSON canonical JSON digest helpers for cube checkers.

The cube has many digest joins.  This module keeps the byte rule in one place
so evidence does not quietly drift between subtly different per-checker
``json.dumps(sort_keys=True)`` helpers.

Profile: ``derivebsd-jcs-ijson-no-float-v1``.

This v1 producer profile intentionally admits only the JSON value space we can
make boring and portable today: duplicate-free objects, UTF-16 object-member
ordering, RFC 8785-compatible string escaping, no insignificant whitespace,
UTF-8 bytes, booleans/null/strings/arrays/objects, and exact safe JSON
integers.  JSON floating-point numbers are rejected for hash-bound objects in
v1 rather than pretending Python's JSON serializer is a complete RFC 8785 JCS
implementation for arbitrary numbers.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

PROFILE = "derivebsd-jcs-ijson-no-float-v1"
_SAFE_JSON_INT_MIN = -(2**53) + 1
_SAFE_JSON_INT_MAX = (2**53) - 1


class CanonicalJsonError(ValueError):
    """Raised when an object is not admissible for the cube digest profile."""


# Backward-compatible spelling for older in-tree experiments.
CanonicalJSONError = CanonicalJsonError


def _duplicate_rejecting_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise CanonicalJsonError(f"duplicate JSON object member {key!r}")
        out[key] = value
    return out


def _reject_non_json_constants(value: str) -> None:
    raise CanonicalJsonError(f"non-JSON numeric constant {value!r} is not allowed")


def load_json_strict_text(text: str) -> Any:
    """Parse JSON while rejecting duplicate object members and NaN/Infinity tokens."""
    try:
        return json.loads(
            text,
            object_pairs_hook=_duplicate_rejecting_object,
            parse_constant=_reject_non_json_constants,
        )
    except CanonicalJsonError:
        raise
    except json.JSONDecodeError as exc:
        raise CanonicalJsonError(f"invalid JSON: {exc}") from exc


def load_json(root: Path, rel: str) -> Any:
    """Load repo-relative JSON using UTF-8 with duplicate-key rejection."""
    return load_json_strict_text((root / rel).read_text(encoding="utf-8"))


def _ensure_string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise CanonicalJsonError(f"{path}: value {value!r} is not a string")
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        raise CanonicalJsonError(f"{path}: lone surrogate code point is not canonical-json admissible")
    return value


def _utf16_sort_key(value: object) -> tuple[int, ...]:
    text = _ensure_string(value, "object member name")
    raw = text.encode("utf-16-be")
    return tuple((raw[i] << 8) | raw[i + 1] for i in range(0, len(raw), 2))


def _quote_string(value: str, path: str) -> str:
    text = _ensure_string(value, path)
    out: list[str] = ['"']
    for ch in text:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append('\\\\')
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\r":
            out.append("\\r")
        elif 0 <= code <= 0x1F:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _serialize(obj: Any, path: str = "$") -> str:
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if isinstance(obj, str):
        return _quote_string(obj, path)
    if isinstance(obj, int):
        # bool is handled above; keep true JSON integers inside I-JSON's exact
        # interoperable range.  Bigger numbers should be string-typed.
        if obj < _SAFE_JSON_INT_MIN or obj > _SAFE_JSON_INT_MAX:
            raise CanonicalJsonError(f"{path}: integer {obj!r} is outside the I-JSON exact integer range")
        return str(obj)
    if isinstance(obj, float):
        raise CanonicalJsonError(
            f"{path}: JSON floating-point number {obj!r} is not admitted by {PROFILE}; "
            "use a schema-defined string for hash-bound decimal values"
        )
    if isinstance(obj, list):
        return "[" + ",".join(_serialize(item, f"{path}[{idx}]") for idx, item in enumerate(obj)) + "]"
    if isinstance(obj, dict):
        chunks: list[str] = []
        keys: list[str] = []
        for key in obj.keys():
            if not isinstance(key, str):
                raise CanonicalJsonError(f"{path}: object member name {key!r} is not a string")
            keys.append(key)
        for key in sorted(keys, key=_utf16_sort_key):
            chunks.append(_quote_string(key, f"{path}.<key>") + ":" + _serialize(obj[key], f"{path}.{key}"))
        return "{" + ",".join(chunks) + "}"
    raise CanonicalJsonError(f"{path}: unsupported JSON value type {type(obj).__name__}")


def canonical_json_profile() -> str:
    return PROFILE


def canonical_json_text(obj: Any) -> str:
    """Return canonical JSON text for DeriveBSD hash-bound JSON objects."""
    return _serialize(obj)


def canonical_json_bytes(obj: Any) -> bytes:
    """Return canonical UTF-8 bytes for DeriveBSD hash-bound JSON objects."""
    return canonical_json_text(obj).encode("utf-8")


def canonical_digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def file_json_digest(root: Path, rel: str) -> str:
    return canonical_digest(load_json(root, rel))


def pretty_json_text(obj: Any) -> str:
    """Return deterministic human-readable JSON with one trailing newline.

    This is for checked-in examples and validation receipts, not for digest
    identity.  Hash-bound JSON must use ``canonical_json_bytes`` or
    ``canonical_digest`` above.
    """
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def write_pretty_json(path: Path, obj: Any) -> None:
    """Write deterministic human-readable JSON for examples/validation ledgers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json_text(obj), encoding="utf-8")
