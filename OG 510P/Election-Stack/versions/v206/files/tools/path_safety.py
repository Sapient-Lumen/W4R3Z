"""tools/path_safety.py

Small helpers to prevent path traversal when resolving in-packet URIs.

Design goals:
- Very small surface area (used by verifiers / checks).
- Reject absolute paths, drive letters, backslashes, and any '..' segment.
- Treat empty paths as unsafe.
- Keep semantics simple: packet URIs are *paths*, not URL-encoded strings.

This is not a sandbox; it is a defensive input validator.
"""

from __future__ import annotations

from pathlib import Path


def is_safe_relpath(rel: str) -> bool:
    if not isinstance(rel, str) or not rel:
        return False

    # Reject leading/trailing whitespace and ASCII control chars.
    if rel != rel.strip():
        return False
    if any((ord(c) < 32) or (ord(c) == 127) for c in rel):
        return False

    # Keep semantics tight: packet paths are not URL-encoded.
    # Reject any percent-escapes (also blocks encoded traversal like "%2e%2e/").
    if "%" in rel:
        return False

    # Forbid Windows-style separators to keep rules simple/portable.
    if "\\" in rel:
        return False

    p = Path(rel)

    # Forbid absolute paths (POSIX or Windows drive).
    if p.is_absolute() or (len(p.parts) > 0 and ":" in p.parts[0]):
        return False

    # Forbid parent directory traversal.
    if any(part == ".." for part in p.parts):
        return False

    # Forbid empty/"." path.
    if all(part in (".", "") for part in p.parts):
        return False

    return True


def safe_join(base: Path, rel: str, *, must_exist: bool = False) -> Path | None:
    """Return base/rel if rel is safe and stays within base.

    If must_exist=True, also reject paths that do not exist and enforce a strict
    resolved-path containment check (guards against symlink escapes).
    """
    if not is_safe_relpath(rel):
        return None

    candidate = base / Path(rel)

    # Containment check: reject anything that would resolve outside base.
    try:
        base_r = base.resolve(strict=True)
    except Exception:
        base_r = base.resolve(strict=False)

    try:
        cand_r = candidate.resolve(strict=must_exist)
    except Exception:
        return None

    try:
        cand_r.relative_to(base_r)
    except Exception:
        return None

    return candidate
