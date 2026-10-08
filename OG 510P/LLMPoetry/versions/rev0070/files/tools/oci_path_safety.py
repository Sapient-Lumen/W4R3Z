#!/usr/bin/env python3
"""Fail-closed path and descriptor helpers for LLMPoetry OCI artifacts.

The OCI image-layout specification gives descriptor digests a constrained
algorithm:encoded grammar and stores blobs beneath blobs/<algorithm>/<encoded>.
These helpers validate the project-local sha256 subset before any filesystem
lookup and keep all spec-declared paths beneath their declared root without
following symlinks.
"""
from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

SHA256_DIGEST_RE = re.compile(r"sha256:[a-f0-9]{64}\Z")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


def canonical_rel(raw: str, *, label: str = "path") -> str:
    """Return a canonical POSIX relative path or raise ValueError."""
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"{label} must be a non-empty string")
    if raw.startswith("/") or "\\" in raw or _CONTROL_RE.search(raw):
        raise ValueError(f"unsafe {label}: {raw!r}")
    p = PurePosixPath(raw)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise ValueError(f"unsafe {label}: {raw!r}")
    canonical = p.as_posix()
    if canonical != raw or raw.endswith("/"):
        raise ValueError(f"non-canonical {label}: {raw!r}")
    return canonical


def _ensure_no_symlink_chain(base: Path, candidate: Path, *, label: str) -> None:
    """Reject any existing symlink from base through candidate."""
    base = base.resolve()
    try:
        rel = candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"{label} escapes base: {candidate}") from exc
    cursor = base
    if cursor.is_symlink():
        raise ValueError(f"{label} base is a symlink: {cursor}")
    for part in rel.parts:
        cursor = cursor / part
        if cursor.exists() or cursor.is_symlink():
            if cursor.is_symlink():
                raise ValueError(f"{label} contains symlink component: {cursor}")


def resolve_under(
    base: Path,
    rel: str,
    *,
    label: str = "path",
    must_exist: bool | None = None,
    expect_dir: bool | None = None,
) -> Path:
    """Resolve a canonical relative path beneath base without symlink traversal."""
    clean = canonical_rel(rel, label=label)
    base = base.resolve()
    candidate = base.joinpath(*PurePosixPath(clean).parts)
    _ensure_no_symlink_chain(base, candidate, label=label)
    resolved = candidate.resolve(strict=False)
    try:
        common = Path(os.path.commonpath([str(base), str(resolved)]))
    except ValueError as exc:
        raise ValueError(f"{label} escapes base: {rel!r}") from exc
    if common != base:
        raise ValueError(f"{label} escapes base: {rel!r}")
    if must_exist is True and not resolved.exists():
        raise ValueError(f"{label} does not exist: {rel!r}")
    if must_exist is False and resolved.exists():
        raise ValueError(f"{label} already exists: {rel!r}")
    if expect_dir is True and resolved.exists() and not resolved.is_dir():
        raise ValueError(f"{label} is not a directory: {rel!r}")
    if expect_dir is False and resolved.exists() and not resolved.is_file():
        raise ValueError(f"{label} is not a regular file: {rel!r}")
    return resolved


def parse_sha256_digest(digest: str, *, label: str = "descriptor digest") -> str:
    """Return the lower-case sha256 hex payload or raise ValueError."""
    if not isinstance(digest, str) or not SHA256_DIGEST_RE.fullmatch(digest):
        raise ValueError(f"invalid {label}: {digest!r}")
    return digest.split(":", 1)[1]


def descriptor_blob_path(layout: Path, digest: str) -> Path:
    """Map a validated project-local sha256 descriptor to a contained blob path."""
    hexdigest = parse_sha256_digest(digest)
    return resolve_under(
        layout,
        f"blobs/sha256/{hexdigest}",
        label="descriptor blob path",
        expect_dir=False,
    )
