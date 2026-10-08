"""Small deterministic bencoder for DHT record test vectors.

The prototype uses bencoding for BEP44/BEP46-compatible mutable record payloads
because those specs define their signatures over bencoded values. The encoder is
small by design: it accepts bytes/str, integers, lists/tuples, and dictionaries
with sorted byte keys. It rejects bools because bool is an int subclass in
Python but is not a useful DHT integer here.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeAlias

BValue: TypeAlias = bytes | str | int | list["BValue"] | tuple["BValue", ...] | Mapping[bytes | str, "BValue"]


def _to_bytes_key(key: bytes | str) -> bytes:
    if isinstance(key, bytes):
        return key
    if isinstance(key, str):
        return key.encode("utf-8")
    raise TypeError(f"dictionary key must be bytes or str, got {type(key)!r}")


def bencode(value: BValue) -> bytes:
    """Return canonical bencoding for the supported Python value."""
    if isinstance(value, bool):
        raise TypeError("bool is not accepted as a DHT integer")
    if isinstance(value, int):
        return b"i" + str(value).encode("ascii") + b"e"
    if isinstance(value, str):
        value = value.encode("utf-8")
    if isinstance(value, bytes):
        return str(len(value)).encode("ascii") + b":" + value
    if isinstance(value, tuple):
        return b"l" + b"".join(bencode(item) for item in value) + b"e"
    if isinstance(value, list):
        return b"l" + b"".join(bencode(item) for item in value) + b"e"
    if isinstance(value, Mapping):
        encoded_items: list[tuple[bytes, bytes]] = []
        seen: set[bytes] = set()
        for raw_key, raw_value in value.items():
            key = _to_bytes_key(raw_key)
            if key in seen:
                raise ValueError("duplicate dictionary key after byte normalization")
            seen.add(key)
            encoded_items.append((key, bencode(raw_value)))
        encoded_items.sort(key=lambda item: item[0])
        body = b"".join(bencode(key) + encoded_value for key, encoded_value in encoded_items)
        return b"d" + body + b"e"
    raise TypeError(f"unsupported bencode value type: {type(value)!r}")
