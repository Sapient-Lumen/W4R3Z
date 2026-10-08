from __future__ import annotations

"""Contained I/O helpers for editor-owned persistence files.

The recent-file list, prompt history, and saved-cursor stores are small
editor-owned JSON files.  They are optional and gated by ``cap.persist``, but
once enabled they should follow the same late-containment discipline as the
script-visible filesystem surfaces: resolve under ``cap.persist-root`` for the
policy decision, then re-check at the actual read/write seam so symlink swaps
or parent changes fail closed instead of using ambient filesystem authority.
"""

from pathlib import Path
from typing import Any

from .file_access import FileTooLargeError, NotARegularFileError, read_file_bytes_contained
from .file_write import FileContainmentError, ensure_parent_directory, write_file_bytes
from .hostcall_boundary import effective_file_write_timeout_seconds
from .persist_sandbox import persist_root

DEFAULT_PERSIST_MAX_BYTES = 1024 * 1024


def persist_containment_root(ed: Any) -> Path | None:
    """Return the active persistence root, or ``None`` when unrestricted."""

    return persist_root(ed)


def persist_max_bytes(ed: Any) -> int:
    """Return the maximum bytes to read for one persistence file."""

    try:
        raw = ed.options.get("persist.maxbytes")
    except Exception:
        raw = DEFAULT_PERSIST_MAX_BYTES
    try:
        return max(1, int(raw))
    except Exception:
        return DEFAULT_PERSIST_MAX_BYTES


def persist_atomic_enabled(ed: Any) -> bool:
    """Return whether persistence writes should use the atomic writer."""

    try:
        return bool(ed.options.get("persist.atomic"))
    except Exception:
        return True


def persist_fsync_enabled(ed: Any) -> bool:
    """Return whether persistence writes should fsync file/directory state."""

    try:
        return bool(ed.options.get("persist.fsync"))
    except Exception:
        return False


def read_persist_text(ed: Any, path: str | Path) -> str | None:
    """Read a persistence file as UTF-8 text, or ``None`` when absent/invalid.

    Missing files and directories are normal for optional persistence.  Other
    errors are deliberately allowed to propagate so callers can surface a clear
    ``... load error`` message.
    """

    p = Path(path)
    root = persist_containment_root(ed)
    try:
        result = read_file_bytes_contained(
            p,
            containment_root=root,
            max_bytes=persist_max_bytes(ed),
        )
    except FileNotFoundError:
        return None
    except IsADirectoryError:
        return None
    except NotARegularFileError:
        return None
    return result.data.decode("utf-8")


def write_persist_text(ed: Any, path: str | Path, text: str) -> None:
    """Write a persistence file through the contained atomic writer."""

    p = Path(path)
    root = persist_containment_root(ed)
    ensure_parent_directory(p.parent, containment_root=root)
    payload = str(text).encode("utf-8")
    write_file_bytes(
        p,
        payload,
        atomic=persist_atomic_enabled(ed),
        preserve_mode=True,
        fsync=persist_fsync_enabled(ed),
        containment_root=root,
        timeout_seconds=effective_file_write_timeout_seconds(getattr(ed, "vm", None)),
    )


__all__ = [
    "DEFAULT_PERSIST_MAX_BYTES",
    "FileContainmentError",
    "FileTooLargeError",
    "persist_atomic_enabled",
    "persist_containment_root",
    "persist_fsync_enabled",
    "persist_max_bytes",
    "read_persist_text",
    "write_persist_text",
]
