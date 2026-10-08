#!/usr/bin/env python3
"""Shared release path policy helpers.

The deterministic release surfaces use POSIX-style repository-relative names.
Keep this helper small and stdlib-only so manifest builders, ZIP verifiers, and
extraction probes can share the same syntactic and portable-namespace firewall.
"""

from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable

WINDOWS_RESERVED_BASENAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)
WINDOWS_FORBIDDEN_CHARS = frozenset('<>:"|?*')
MAX_PATH_CHARS = 240
MAX_COMPONENT_CHARS = 220


def normalize_release_rel(rel: str) -> str:
    """Normalize a user-supplied repo-relative path without hiding dotfiles.

    A literal leading ``./`` is presentation noise and may be removed.  Do not
    trim whitespace and do not use character-set stripping: leading-dot names
    such as ``.git/config`` must remain visible to exclusion rules.
    """

    rel = str(rel)
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def portable_path_key(rel: str) -> str:
    """Return the case-insensitive portable namespace key for ``rel``.

    Release paths are ASCII-only, so ``casefold`` is deterministic and enough to
    model the collision class that would overwrite on common case-insensitive
    extraction targets.  Callers should run ``release_path_problem`` first; this
    helper intentionally does not make unsafe paths safe.
    """

    return normalize_release_rel(rel).casefold()


def find_portable_path_collisions(paths: Iterable[str]) -> dict[str, list[str]]:
    """Return portable-namespace collisions in ``paths``.

    Exact duplicates are included too; callers that already report exact
    duplicates can still use the returned mapping for a single portable collision
    firewall.
    """

    by_key: dict[str, list[str]] = {}
    for rel in paths:
        by_key.setdefault(portable_path_key(rel), []).append(normalize_release_rel(rel))
    return {key: vals for key, vals in by_key.items() if len(vals) > 1}




def find_extraction_shape_conflicts(paths: Iterable[str]) -> dict[str, list[str]]:
    """Return file/directory shape conflicts in release member paths.

    Release ZIP members and MANIFEST.sha256 entries are all regular files.  A
    set that contains both ``a`` and ``a/b`` is syntactically safe per-member but
    cannot be extracted as a portable regular-file tree: ``a`` would have to be
    both a file and a directory.  Reject that shape before extraction so ZIP,
    manifest, and extracted-tree verification agree.
    """

    normalized = [normalize_release_rel(p) for p in paths]
    path_set = set(normalized)
    conflicts: dict[str, list[str]] = {}
    for rel in normalized:
        parts = rel.split("/")
        for i in range(1, len(parts)):
            prefix = "/".join(parts[:i])
            if prefix in path_set:
                conflicts.setdefault(prefix, []).append(rel)
    return {key: sorted(vals) for key, vals in sorted(conflicts.items())}


def _windows_reserved_component(part: str) -> str | None:
    """Return a problem string if ``part`` collides with Windows device names."""

    # Windows treats device basenames as reserved even with extensions, e.g.
    # AUX.txt or com1.json.  Release paths are ASCII-only, so upper() is stable.
    basename = part.split(".", 1)[0].upper()
    if basename in WINDOWS_RESERVED_BASENAMES:
        return f"reserved Windows device basename {basename!r}"
    return None


def release_path_problem(rel: str) -> str | None:
    """Return a short problem string when ``rel`` is not release-path-safe."""

    rel = normalize_release_rel(rel)
    if not rel:
        return "empty path"
    if len(rel) > MAX_PATH_CHARS:
        return f"path too long ({len(rel)} > {MAX_PATH_CHARS})"
    if rel.endswith("/"):
        return "directory entry path"
    if "\x00" in rel:
        return "NUL byte in path"
    if "\\" in rel:
        return "backslash in path"
    if rel.startswith("/"):
        return "absolute path"

    first = rel.split("/", 1)[0]
    if first.endswith(":"):
        return "drive-like leading component"

    if rel != rel.strip():
        return "leading/trailing whitespace in path"

    parts = rel.split("/")
    for part in parts:
        if part in {"", ".", ".."}:
            return "empty/current/parent traversal component"
        if len(part) > MAX_COMPONENT_CHARS:
            return f"path component too long ({len(part)} > {MAX_COMPONENT_CHARS})"
        if part != part.strip():
            return "leading/trailing whitespace in path component"
        if part.endswith("."):
            return "trailing dot in path component"
        reserved = _windows_reserved_component(part)
        if reserved:
            return reserved
        for ch in part:
            code = ord(ch)
            if code < 32 or code == 127:
                return "control character in path"
            if code > 126:
                return "non-ASCII character in path"
            if ch.isspace():
                return "whitespace in path"
            if ch in WINDOWS_FORBIDDEN_CHARS:
                return "Windows-forbidden character in path"

    return None


def is_release_path_safe(rel: str) -> bool:
    return release_path_problem(rel) is None


def safe_extract_destination(root: Path, member_name: str) -> Path | None:
    """Return the extraction destination for ``member_name`` or ``None``.

    This uses ``Path.relative_to`` rather than string-prefix checks, so a root
    like ``/tmp/out`` cannot be confused with ``/tmp/outside``.
    """

    rel = normalize_release_rel(member_name)
    if release_path_problem(rel):
        return None
    root_resolved = root.resolve()
    dest = (root_resolved / rel).resolve()
    try:
        dest.relative_to(root_resolved)
    except ValueError:
        return None
    return dest
