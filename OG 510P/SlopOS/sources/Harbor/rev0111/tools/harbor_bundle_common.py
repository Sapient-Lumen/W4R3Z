#!/usr/bin/env python3
"""Shared helper primitives for Harbor proof-bundle checks.

This module is maintenance scaffolding only.  It centralizes deterministic
JSON digesting, basic assertion helpers, digest-string checks, and forbidden
phrase scanning so new proof slices do not copy small checker idioms into
divergent local dialects.  It is not a schema, trust root, validator API,
CI status source, conformance suite, or promotion gate.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

FORBIDDEN_CONFIDENCE_PHRASES = [
    "global truth",
    "corrected everywhere",
    "compliant",
    "resolved",
    "all downstream repaired",
    "green badge",
    "red badge",
    "automatic repair",
    "prior falsehood",
    "trust root",
]

GUARD_WORDS = [
    "not ",
    "no ",
    "without",
    "refuse",
    "refused",
    "refusal",
    "reject",
    "rejected",
    "rejection",
    "must not",
    "non-promise",
    "non_promises",
    "counterfeit",
    "guard",
    "smaller than",
    "unsafe",
    "blocked",
    "forbidden",
]

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)

def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def check_digest_string(value: str, message: str) -> None:
    expect(isinstance(value, str) and value.startswith("sha256:") and len(value) == 71, message)

def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_strings(child)

def unguarded_confidence_phrases(value: Any) -> list[str]:
    hits: list[str] = []
    for string in iter_strings(value):
        lower = string.lower()
        if not any(phrase in lower for phrase in FORBIDDEN_CONFIDENCE_PHRASES):
            continue
        if any(guard in lower for guard in GUARD_WORDS):
            continue
        hits.append(string)
    return hits
