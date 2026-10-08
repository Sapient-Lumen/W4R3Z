from __future__ import annotations

"""Capability checks for script-originated dirty-buffer discard.

Filesystem capabilities decide whether a script may touch host files.  Dirty
editor buffers are a separate user-data surface: forced close, quit, only, or
revert can discard unsaved in-memory edits without touching the filesystem.
"""

from typing import Any, Iterable


class BufferCapabilityError(RuntimeError):
    """Raised when script-originated code lacks buffer-discard authority."""


def _in_script_context(ed: Any) -> bool:
    try:
        return bool(ed.in_script_context())
    except Exception:
        return False


def _option_enabled(ed: Any, name: str) -> bool:
    try:
        return bool(ed.options.get(str(name)))
    except Exception:
        return False


def dirty_buffer_names(ed: Any, names: Iterable[str] | None = None) -> list[str]:
    """Return dirty buffer names from ``ed`` for a requested subset or all buffers."""

    try:
        buffers = getattr(ed, "buffers", {}) or {}
    except Exception:
        return []
    keys = list(buffers.keys()) if names is None else [str(n) for n in names]
    dirty: list[str] = []
    for name in keys:
        try:
            eb = buffers.get(str(name))
            if eb is not None and bool(getattr(eb.buf, "dirty", False)):
                dirty.append(str(name))
        except Exception:
            continue
    return dirty


def require_buffer_discard_capability(ed: Any, op: str, dirty_names: Iterable[str]) -> None:
    """Require ``cap.buffer-discard`` before scripts discard dirty buffers."""

    names = [str(n) for n in dirty_names if str(n or "")]
    if not names or not _in_script_context(ed):
        return
    if _option_enabled(ed, "cap.buffer-discard"):
        return
    preview = ", ".join(sorted(names)[:6])
    more = max(0, len(names) - 6)
    suffix = f" ... (+{more} more)" if more else ""
    detail = f": {preview}{suffix}" if preview else ""
    raise BufferCapabilityError(f"{op}: disabled for scripts (cap.buffer-discard){detail}")
