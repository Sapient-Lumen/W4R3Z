"""Shared canonical JSON digest helpers for cube checkers.

The archive has several guardrails that need deterministic example digests.
Keeping the rule in one place avoids each checker inventing a subtly different
serialization posture.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def load_json(root: Path, rel: str) -> Any:
    """Load repo-relative JSON using UTF-8."""
    return json.loads((root / rel).read_text(encoding="utf-8"))


def canonical_json_bytes(obj: Any) -> bytes:
    """Return the current archive canonical JSON byte representation.

    This is intentionally compact and deterministic.  It is not a claim that
    all historical symbolic fixture digests used this rule; r521+ computed
    joins do.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def file_json_digest(root: Path, rel: str) -> str:
    return canonical_digest(load_json(root, rel))
