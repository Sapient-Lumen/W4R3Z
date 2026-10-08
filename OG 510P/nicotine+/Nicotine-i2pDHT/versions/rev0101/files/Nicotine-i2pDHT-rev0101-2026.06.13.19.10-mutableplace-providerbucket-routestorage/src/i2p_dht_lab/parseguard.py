"""Guarded canonical bdecode before accepting wire payloads.

The cube has used deterministic bencoding for signatures and transcripts from
its first mutable-record surfaces.  Encoding alone is not enough.  A live DHT
will eventually receive arbitrary bytes over I2P/SAM, and a parser bug can turn
"valid enough to inspect" into an attack surface.

This module is intentionally small and strict.  It implements the bencode
subset produced by :mod:`i2p_dht_lab.bencode`, adds byte/depth/item limits, and
rejects non-canonical forms such as unsorted dictionary keys, duplicate keys,
negative zero, leading-zero integers, and trailing data.  It is not a full
BitTorrent parser; it is a prototype safety boundary for this cube's own wire
fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

PARSE_GUARD_DOMAIN = DOMAIN + b":parse-guard-v1:"


class ParseGuardKind(str, Enum):
    ACCEPT_CANONICAL = "accept_canonical"
    REJECT_TOO_LARGE = "reject_too_large"
    REJECT_DEPTH_LIMIT = "reject_depth_limit"
    REJECT_ITEM_LIMIT = "reject_item_limit"
    REJECT_TRAILING_DATA = "reject_trailing_data"
    REJECT_INVALID_TOKEN = "reject_invalid_token"
    REJECT_INVALID_INTEGER = "reject_invalid_integer"
    REJECT_STRING_LENGTH = "reject_string_length"
    REJECT_DUPLICATE_KEY = "reject_duplicate_key"
    REJECT_UNSORTED_KEY = "reject_unsorted_key"
    REJECT_NON_CANONICAL_REENCODE = "reject_non_canonical_reencode"


class ParseGuardError(ValueError):
    """Structured parser rejection used by tests and future wire dispatch."""

    def __init__(self, kind: ParseGuardKind, reason: str, *, offset: int = 0) -> None:
        super().__init__(reason)
        self.kind = kind
        self.reason = reason
        self.offset = offset


@dataclass(frozen=True)
class ParseLimits:
    max_bytes: int = 64_000
    max_depth: int = 16
    max_list_items: int = 2048
    max_dict_items: int = 512
    max_string_bytes: int = 64_000
    max_abs_int: int = 2**63 - 1
    require_canonical_reencode: bool = True

    def validate(self) -> None:
        if min(self.max_bytes, self.max_depth, self.max_list_items, self.max_dict_items, self.max_string_bytes, self.max_abs_int) <= 0:
            raise ValueError("parse limits must be positive")


@dataclass(frozen=True)
class GuardedParseReport:
    value: BValue
    consumed: int
    digest: bytes
    kind: ParseGuardKind = ParseGuardKind.ACCEPT_CANONICAL

    def expect_dict(self) -> dict[bytes, BValue]:
        if not isinstance(self.value, dict):
            raise ParseGuardError(ParseGuardKind.REJECT_INVALID_TOKEN, "expected dictionary at top level")
        return self.value  # type: ignore[return-value]


def _reject(kind: ParseGuardKind, reason: str, offset: int) -> None:
    raise ParseGuardError(kind, reason, offset=offset)


def _read_until(data: bytes, start: int, marker: bytes, kind: ParseGuardKind) -> tuple[bytes, int]:
    end = data.find(marker, start)
    if end < 0:
        _reject(kind, "unterminated bencode token", start)
    return data[start:end], end + 1


def _parse_int(data: bytes, index: int, limits: ParseLimits) -> tuple[int, int]:
    raw, next_index = _read_until(data, index + 1, b"e", ParseGuardKind.REJECT_INVALID_INTEGER)
    if not raw:
        _reject(ParseGuardKind.REJECT_INVALID_INTEGER, "empty integer", index)
    if raw == b"-0" or raw.startswith(b"--"):
        _reject(ParseGuardKind.REJECT_INVALID_INTEGER, "invalid negative integer", index)
    if raw.startswith(b"0") and raw != b"0":
        _reject(ParseGuardKind.REJECT_INVALID_INTEGER, "integer has leading zero", index)
    if raw.startswith(b"-") and len(raw) > 2 and raw[1:2] == b"0":
        _reject(ParseGuardKind.REJECT_INVALID_INTEGER, "negative integer has leading zero", index)
    try:
        value = int(raw)
    except ValueError:
        _reject(ParseGuardKind.REJECT_INVALID_INTEGER, "integer contains non-digits", index)
    if abs(value) > limits.max_abs_int:
        _reject(ParseGuardKind.REJECT_INVALID_INTEGER, "integer exceeds configured magnitude limit", index)
    return value, next_index


def _parse_bytes(data: bytes, index: int, limits: ParseLimits) -> tuple[bytes, int]:
    colon = data.find(b":", index)
    if colon < 0:
        _reject(ParseGuardKind.REJECT_STRING_LENGTH, "unterminated byte-string length", index)
    raw_length = data[index:colon]
    if not raw_length or not raw_length.isdigit():
        _reject(ParseGuardKind.REJECT_STRING_LENGTH, "invalid byte-string length", index)
    if raw_length.startswith(b"0") and raw_length != b"0":
        _reject(ParseGuardKind.REJECT_STRING_LENGTH, "byte-string length has leading zero", index)
    length = int(raw_length)
    if length > limits.max_string_bytes:
        _reject(ParseGuardKind.REJECT_STRING_LENGTH, "byte-string exceeds configured limit", index)
    start = colon + 1
    end = start + length
    if end > len(data):
        _reject(ParseGuardKind.REJECT_STRING_LENGTH, "byte-string overruns input", index)
    return data[start:end], end


def _parse_value(data: bytes, index: int, depth: int, limits: ParseLimits) -> tuple[BValue, int]:
    if depth > limits.max_depth:
        _reject(ParseGuardKind.REJECT_DEPTH_LIMIT, "bencode nesting exceeds configured depth", index)
    if index >= len(data):
        _reject(ParseGuardKind.REJECT_INVALID_TOKEN, "unexpected end of input", index)
    token = data[index:index + 1]
    if token == b"i":
        return _parse_int(data, index, limits)
    if token and 48 <= token[0] <= 57:
        return _parse_bytes(data, index, limits)
    if token == b"l":
        items: list[BValue] = []
        next_index = index + 1
        while True:
            if next_index >= len(data):
                _reject(ParseGuardKind.REJECT_INVALID_TOKEN, "unterminated list", index)
            if data[next_index:next_index + 1] == b"e":
                return items, next_index + 1
            if len(items) >= limits.max_list_items:
                _reject(ParseGuardKind.REJECT_ITEM_LIMIT, "list exceeds configured item limit", next_index)
            item, next_index = _parse_value(data, next_index, depth + 1, limits)
            items.append(item)
    if token == b"d":
        items: dict[bytes, BValue] = {}
        next_index = index + 1
        last_key: bytes | None = None
        while True:
            if next_index >= len(data):
                _reject(ParseGuardKind.REJECT_INVALID_TOKEN, "unterminated dictionary", index)
            if data[next_index:next_index + 1] == b"e":
                return items, next_index + 1
            if len(items) >= limits.max_dict_items:
                _reject(ParseGuardKind.REJECT_ITEM_LIMIT, "dictionary exceeds configured item limit", next_index)
            key, next_index = _parse_bytes(data, next_index, limits)
            if last_key is not None and key < last_key:
                _reject(ParseGuardKind.REJECT_UNSORTED_KEY, "dictionary keys are not sorted", next_index)
            if key in items:
                _reject(ParseGuardKind.REJECT_DUPLICATE_KEY, "dictionary contains duplicate key", next_index)
            last_key = key
            value, next_index = _parse_value(data, next_index, depth + 1, limits)
            items[key] = value
    _reject(ParseGuardKind.REJECT_INVALID_TOKEN, "unknown bencode token", index)


def bdecode_guarded(data: bytes, *, limits: ParseLimits | None = None) -> GuardedParseReport:
    """Parse canonical bencode with cube-local resource limits."""
    limits = limits or ParseLimits()
    limits.validate()
    if len(data) > limits.max_bytes:
        raise ParseGuardError(ParseGuardKind.REJECT_TOO_LARGE, "input exceeds configured byte limit", offset=0)
    value, consumed = _parse_value(data, 0, 0, limits)
    if consumed != len(data):
        raise ParseGuardError(ParseGuardKind.REJECT_TRAILING_DATA, "trailing bytes after canonical value", offset=consumed)
    if limits.require_canonical_reencode and bencode(value) != data:
        raise ParseGuardError(ParseGuardKind.REJECT_NON_CANONICAL_REENCODE, "re-encoded value differs from input", offset=0)
    return GuardedParseReport(value=value, consumed=consumed, digest=sha256(PARSE_GUARD_DOMAIN + b":parsed:" + data))


def as_bytes(mapping: dict[bytes, Any], key: bytes, *, length: int | None = None) -> bytes:
    value = mapping.get(key)
    if not isinstance(value, bytes):
        raise ParseGuardError(ParseGuardKind.REJECT_INVALID_TOKEN, f"field {key!r} must be bytes")
    if length is not None and len(value) != length:
        raise ParseGuardError(ParseGuardKind.REJECT_STRING_LENGTH, f"field {key!r} must be {length} bytes")
    return value


def as_int(mapping: dict[bytes, Any], key: bytes, *, min_value: int = 0) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ParseGuardError(ParseGuardKind.REJECT_INVALID_INTEGER, f"field {key!r} must be integer")
    if value < min_value:
        raise ParseGuardError(ParseGuardKind.REJECT_INVALID_INTEGER, f"field {key!r} is below minimum")
    return value


def as_text(mapping: dict[bytes, Any], key: bytes, *, max_len: int = 128) -> str:
    raw = as_bytes(mapping, key)
    if len(raw) > max_len:
        raise ParseGuardError(ParseGuardKind.REJECT_STRING_LENGTH, f"field {key!r} exceeds text length budget")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ParseGuardError(ParseGuardKind.REJECT_INVALID_TOKEN, f"field {key!r} is not valid utf-8") from exc
