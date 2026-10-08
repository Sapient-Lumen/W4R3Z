#!/usr/bin/env python3
"""Minimal TimeSync JCS/RFC 8785 canonicalization support.

This module implements the current TimeSync digest subset rather than using
Python's deterministic-but-nonportable JSON sort-keys convention. The subset is
matched to the archive's digest-binding policy:

* duplicate JSON member names are rejected at parse time;
* strings are preserved as-is and lone surrogate code points are rejected;
* object member names are sorted recursively by raw UTF-16 code units;
* no insignificant whitespace is emitted;
* current TimeSync-owned digest surfaces use only null, booleans, strings,
  arrays, objects, and I-JSON safe integers.

Floating-point JSON numbers are rejected for digest-bound TimeSync objects. That
is narrower than full RFC 8785 number serialization, but it is fail-closed and
portable for this archive's declared current-use digest surfaces.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Iterable

IJSON_SAFE_INT_MIN = -(2**53) + 1
IJSON_SAFE_INT_MAX = (2**53) - 1


class JcsCanonicalizationError(ValueError):
    """Raised when an object cannot be represented by the TimeSync JCS subset."""


class DuplicateJsonMemberError(JcsCanonicalizationError):
    """Raised when parsed JSON contains duplicate object member names."""


def _reject_json_constant(value: str) -> None:
    raise JcsCanonicalizationError(f'non-I-JSON numeric literal is not allowed: {value}')


def _object_pairs_no_duplicates(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise DuplicateJsonMemberError(f'duplicate JSON object member name: {key!r}')
        obj[key] = value
    return obj


def load_json_ijson(text: str) -> Any:
    """Parse JSON with I-JSON checks needed before JCS digesting."""
    obj = json.loads(
        text,
        object_pairs_hook=_object_pairs_no_duplicates,
        parse_constant=_reject_json_constant,
    )
    _assert_no_lone_surrogates(obj)
    return obj


def _assert_no_lone_surrogates(value: Any) -> None:
    if isinstance(value, str):
        for ch in value:
            cp = ord(ch)
            if 0xD800 <= cp <= 0xDFFF:
                raise JcsCanonicalizationError('JSON string contains a lone surrogate code point')
    elif isinstance(value, list):
        for item in value:
            _assert_no_lone_surrogates(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise JcsCanonicalizationError('JSON object member names must be strings')
            _assert_no_lone_surrogates(key)
            _assert_no_lone_surrogates(item)


def _utf16_sort_key(value: str) -> tuple[int, ...]:
    encoded = value.encode('utf-16-be')
    return tuple((encoded[i] << 8) | encoded[i + 1] for i in range(0, len(encoded), 2))


def _quote_string(value: str) -> str:
    parts: list[str] = ['"']
    for ch in value:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise JcsCanonicalizationError('JSON string contains a lone surrogate code point')
        if cp == 0x22:
            parts.append('\\"')
        elif cp == 0x5C:
            parts.append('\\\\')
        elif cp == 0x08:
            parts.append('\\b')
        elif cp == 0x09:
            parts.append('\\t')
        elif cp == 0x0A:
            parts.append('\\n')
        elif cp == 0x0C:
            parts.append('\\f')
        elif cp == 0x0D:
            parts.append('\\r')
        elif cp < 0x20:
            parts.append(f'\\u{cp:04x}')
        else:
            parts.append(ch)
    parts.append('"')
    return ''.join(parts)


def canonicalize(value: Any) -> str:
    """Return TimeSync's canonical JSON string for a digest-bound object."""
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        return _quote_string(value)
    if isinstance(value, int):
        if value < IJSON_SAFE_INT_MIN or value > IJSON_SAFE_INT_MAX:
            raise JcsCanonicalizationError(
                f'integer {value} is outside the I-JSON safe integer range '
                f'[{IJSON_SAFE_INT_MIN}, {IJSON_SAFE_INT_MAX}]'
            )
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise JcsCanonicalizationError('NaN and Infinity are not permitted JSON numbers')
        raise JcsCanonicalizationError(
            'floating-point JSON numbers are outside the current TimeSync JCS subset; '
            'encode as strings or bind external bytes instead'
        )
    if isinstance(value, list):
        return '[' + ','.join(canonicalize(item) for item in value) + ']'
    if isinstance(value, dict):
        for key in value:
            if not isinstance(key, str):
                raise JcsCanonicalizationError('JSON object member names must be strings')
        items = []
        for key in sorted(value.keys(), key=_utf16_sort_key):
            items.append(_quote_string(key) + ':' + canonicalize(value[key]))
        return '{' + ','.join(items) + '}'
    raise JcsCanonicalizationError(f'unsupported JSON value type: {type(value).__name__}')


def canonical_bytes(value: Any) -> bytes:
    return canonicalize(value).encode('utf-8')


def sha256_hexdigest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def self_test() -> list[str]:
    """Return a list of canonicalizer self-test failures."""
    errors: list[str] = []

    # RFC 8785 Section 3.2.3 UTF-16 code-unit property ordering sample.
    sorting_sample = {
        chr(0x20AC): 'Euro Sign',
        chr(0x000D): 'Carriage Return',
        chr(0xFB33): 'Hebrew Letter Dalet With Dagesh',
        '1': 'One',
        chr(0x1F600): 'Emoji: Grinning Face',
        chr(0x0080): 'Control',
        chr(0x00F6): 'Latin Small Letter O With Diaeresis',
    }
    expected_values = [
        'Carriage Return',
        'One',
        'Control',
        'Latin Small Letter O With Diaeresis',
        'Euro Sign',
        'Emoji: Grinning Face',
        'Hebrew Letter Dalet With Dagesh',
    ]
    encoded = canonicalize(sorting_sample)
    actual_values = list(json.loads(encoded).values())
    if actual_values != expected_values:
        errors.append(f'JCS UTF-16 member ordering self-test failed: {actual_values}')

    string_sample = {'x': ''.join(['€', '$', chr(0x000F), chr(0x000A), 'A', "'", 'B', '"', '\\', '\\', '"', '/'])}
    expected = '{"x":"€$\\u000f\\nA\'B\\"\\\\\\\\\\"/"}'
    actual = canonicalize(string_sample)
    if actual != expected:
        errors.append(f'JCS string escaping self-test failed: {actual!r}')

    try:
        load_json_ijson('{"a":1,"a":2}')
        errors.append('duplicate JSON member self-test failed: duplicate was accepted')
    except DuplicateJsonMemberError:
        pass

    try:
        canonicalize({'too_big': IJSON_SAFE_INT_MAX + 1})
        errors.append('unsafe integer self-test failed: unsafe integer was accepted')
    except JcsCanonicalizationError:
        pass

    try:
        canonicalize({'fractional': 0.5})
        errors.append('floating-point self-test failed: float was accepted for TimeSync digest subset')
    except JcsCanonicalizationError:
        pass

    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync JCS subset self-test passed.')
