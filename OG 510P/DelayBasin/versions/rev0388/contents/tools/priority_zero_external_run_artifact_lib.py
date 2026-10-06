"""Small strict-artifact primitives for the Priority-0 external run.

This module is intentionally safe to ship in every stage kit.  It contains no
answer key, expected outcome, or current bundle digest.  Stage tools use it so
JSON parsing, timestamp handling, digest calculation, and immutable-output
behavior do not drift independently.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import pathlib
import tempfile
import zipfile
from datetime import datetime
from typing import Any

PLACEHOLDERS = {"", "n/a", "na", "tbd", "todo", "placeholder", "none", "null"}
LOCAL_PROCESS_CLOCK = "local-process-clock"


class ExternalRunArtifactError(ValueError):
    """Raised when a run artifact is malformed or would be overwritten."""


def resolve_input(path: str | pathlib.Path) -> pathlib.Path:
    candidate = pathlib.Path(path)
    return candidate if candidate.is_absolute() else pathlib.Path.cwd() / candidate


def resolve_local(root: pathlib.Path, path: str | pathlib.Path) -> pathlib.Path:
    candidate = pathlib.Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    """Parse exact UTF-8 JSON bytes with the same strictness used for files.

    ZIP-contained templates and packets must not receive a weaker parser than
    filesystem artifacts.  This byte-oriented primitive lets prefreeze tools
    validate members in place without extracting scorer-safe bundles or
    duplicating duplicate-key/non-finite-number logic.
    """

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ExternalRunArtifactError(f"{label} contains duplicate JSON object key: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ExternalRunArtifactError(f"{label} contains non-standard JSON numeric constant: {value}")

    def finite_float(value: str) -> float:
        """Reject standards-valid spellings that overflow Python's float.

        ``json.loads`` already rejects NaN/Infinity through ``parse_constant``,
        but a finite JSON token such as ``1e999`` otherwise becomes ``inf``.
        Artifact validation must not let the parser manufacture a non-finite
        runtime value from standards-valid input.
        """
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ExternalRunArtifactError(
                f"{label} contains JSON number outside the finite runtime range: {value}"
            )
        return parsed

    try:
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_constant,
            parse_float=finite_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, OverflowError, ValueError) as exc:
        if isinstance(exc, ExternalRunArtifactError):
            raise
        raise ExternalRunArtifactError(f"{label} is not strict UTF-8 JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ExternalRunArtifactError(f"{label} must contain a JSON object")
    return data


def strict_json(path: pathlib.Path, label: str) -> tuple[dict[str, Any], bytes]:
    if not path.exists():
        raise ExternalRunArtifactError(f"missing {label}: {path}")
    raw = path.read_bytes()
    return strict_json_bytes(raw, label), raw


def non_placeholder_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or value.strip().lower() in PLACEHOLDERS:
        raise ExternalRunArtifactError(f"{label} must be a non-placeholder string")
    return value.strip()


def parse_timestamp(value: Any, label: str) -> tuple[str, datetime]:
    text = non_placeholder_text(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ExternalRunArtifactError(f"{label} must be ISO-8601 with timezone offset") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ExternalRunArtifactError(f"{label} must include timezone offset")
    return text, parsed


def now_timestamp() -> tuple[str, datetime]:
    value = datetime.now().astimezone()
    return value.isoformat(timespec="microseconds"), value


def positive_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ExternalRunArtifactError(f"{label} must be a positive finite number")
    try:
        numeric = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ExternalRunArtifactError(f"{label} must be a positive finite number") from exc
    if not math.isfinite(numeric) or numeric <= 0:
        raise ExternalRunArtifactError(f"{label} must be a positive finite number")
    return numeric


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    if not path.exists() or not path.is_file():
        raise ExternalRunArtifactError(f"missing digest input file: {path}")
    return sha256_bytes(path.read_bytes())


def publish_new_bytes(
    path: pathlib.Path,
    payload: bytes,
    *,
    readonly: bool = False,
) -> None:
    """Atomically publish complete bytes without clobbering.

    The payload is fsynced in a same-directory temporary file, then hard-linked
    into the requested name.  ``os.link`` fails atomically if another process
    already created the target, avoiding the check-then-write race and keeping
    a crash-partial payload out of the final artifact name.
    """
    if not isinstance(payload, bytes):
        raise ExternalRunArtifactError("published artifact payload must be bytes")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.publishing-",
        dir=path.parent,
    )
    temp_path = pathlib.Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, 0o444 if readonly else 0o644)
        try:
            os.link(temp_path, path)
        except FileExistsError as exc:
            raise ExternalRunArtifactError(
                f"output already exists; refusing to overwrite a possibly frozen artifact: {path}"
            ) from exc
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def write_new_json(
    path: pathlib.Path,
    data: dict[str, Any],
    *,
    readonly: bool = False,
) -> None:
    """Serialize strict JSON and publish it atomically without clobbering."""
    payload = (
        json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")
    publish_new_bytes(path, payload, readonly=readonly)


def _safe_zip_member_name(name: str) -> str:
    if not isinstance(name, str) or not name or "\\" in name:
        raise ExternalRunArtifactError("ZIP member names must be non-empty POSIX paths")
    pure = pathlib.PurePosixPath(name)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ExternalRunArtifactError(f"unsafe ZIP member name: {name!r}")
    normalized = pure.as_posix()
    if normalized != name or name.endswith("/"):
        raise ExternalRunArtifactError(f"ZIP member name is not canonical: {name!r}")
    return normalized


def write_new_zip(
    path: pathlib.Path,
    members: list[tuple[str, bytes]],
    *,
    readonly: bool = False,
) -> None:
    """Publish one deterministic, no-clobber ZIP from exact member bytes.

    Dynamic run bundles use stored members and fixed metadata so the archive
    digest depends only on ordered member names and payload bytes.  The complete
    archive is constructed in memory and then published through the same atomic
    byte path used by frozen JSON artifacts.
    """
    if not isinstance(members, list) or not members:
        raise ExternalRunArtifactError("ZIP publication requires at least one member")
    seen: set[str] = set()
    normalized: list[tuple[str, bytes]] = []
    for index, item in enumerate(members):
        if not isinstance(item, tuple) or len(item) != 2:
            raise ExternalRunArtifactError(
                f"ZIP member {index + 1} must be a (name, bytes) tuple"
            )
        name, payload = item
        name = _safe_zip_member_name(name)
        if name in seen:
            raise ExternalRunArtifactError(f"duplicate ZIP member name: {name}")
        if not isinstance(payload, bytes):
            raise ExternalRunArtifactError(f"ZIP member {name} payload must be bytes")
        seen.add(name)
        normalized.append((name, payload))

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in normalized:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (0o100444 & 0xFFFF) << 16
            archive.writestr(info, payload)
    publish_new_bytes(path, buffer.getvalue(), readonly=readonly)
