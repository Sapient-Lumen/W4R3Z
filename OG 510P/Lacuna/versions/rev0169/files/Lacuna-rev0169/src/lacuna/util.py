from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GENESIS_HASH = "0" * 64


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def pretty_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)


def atomic_write_text(path: str | os.PathLike[str], text: str) -> None:
    """Replace a small text file without exposing a partial write.

    Production/default operation fsyncs the file and parent directory for local
    crash-durability. Acceptance and CI may set ``LACUNA_FAST_TEST_IO=1`` to
    skip those fsync calls while preserving temp-file plus atomic-replace
    semantics; this keeps the full pure-Python suite practical on slower
    sandbox filesystems without changing the default custody posture.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fast_test_io = os.environ.get("LACUNA_FAST_TEST_IO") == "1"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            if not fast_test_io:
                os.fsync(handle.fileno())
        os.replace(temporary, target)
        if not fast_test_io:
            try:
                directory_fd = os.open(target.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            except OSError:
                directory_fd = None
            if directory_fd is not None:
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: str | os.PathLike[str], value: Any) -> None:
    atomic_write_text(path, pretty_json(value) + "\n")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:24]}"


def deterministic_claim_id(subject: str, predicate: str, object_value: Any, scope: str) -> str:
    body = canonical_json(
        {
            "subject": subject,
            "predicate": predicate,
            "object": object_value,
            "scope": scope,
        }
    )
    return "clm_" + sha256_text(body)


def require_id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ValueError(f"{field} must match {ID_RE.pattern}")
    return value


def optional_id(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return require_id(value, field)


def require_string(value: Any, field: str, *, allow_empty: bool = False, max_len: int = 4096) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    if not allow_empty and not value.strip():
        raise ValueError(f"{field} must not be empty")
    if len(value) > max_len:
        raise ValueError(f"{field} exceeds {max_len} characters")
    return value


def optional_string(value: Any, field: str, *, max_len: int = 16384) -> str | None:
    if value is None:
        return None
    return require_string(value, field, allow_empty=True, max_len=max_len)


def require_enum(value: Any, field: str, allowed: set[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{field} must be one of {sorted(allowed)}")
    return value


def optional_probability(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number between 0 and 1")
    number = float(value)
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError(f"{field} must be a finite number between 0 and 1")
    return number


def require_weight(value: Any, field: str = "weight") -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a nonnegative finite number")
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise ValueError(f"{field} must be a nonnegative finite number")
    return number


def optional_tick(value: Any, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer narrative tick or null")
    return value


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return value


def normalize_audience(value: Any) -> list[str]:
    if value is None:
        return []
    audience = require_list(value, "audience")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(audience):
        agent_id = require_id(item, f"audience[{index}]")
        if agent_id not in seen:
            normalized.append(agent_id)
            seen.add(agent_id)
    return normalized


def intervals_overlap(
    timeline_a: str,
    start_a: int | None,
    end_a: int | None,
    timeline_b: str,
    start_b: int | None,
    end_b: int | None,
) -> bool:
    if timeline_a != timeline_b:
        return False
    a0 = -math.inf if start_a is None else start_a
    a1 = math.inf if end_a is None else end_a
    b0 = -math.inf if start_b is None else start_b
    b1 = math.inf if end_b is None else end_b
    return max(a0, b0) <= min(a1, b1)


def parse_json_value(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON value: {exc.msg} at offset {exc.pos}") from exc
