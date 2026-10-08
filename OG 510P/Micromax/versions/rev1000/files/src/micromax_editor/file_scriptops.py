from __future__ import annotations

"""Capability-checked editor file operations for scripts/hostcalls.

The interactive command bar may operate on ordinary user paths, but scripted
surfaces (`ed.command`, plugin hostcalls, prompt submission from a script) must
honor the explicit cap.fs-* options.  This module keeps that policy in one
place so command wrappers and direct hostcalls do not drift apart.
"""

from pathlib import Path
from typing import Any

from .file_access import chdir_contained
from .fs_sandbox import (
    deny_reason as fs_deny_reason,
    is_allowed as fs_path_allowed,
    nominal_path as fs_nominal_path,
    resolve_path as fs_resolve_path,
    fs_root as fs_cap_root,
)


class FileCapabilityError(RuntimeError):
    """Raised when a scripted file operation lacks authority or a safe target."""


def _option_enabled(ed: Any, name: str) -> bool:
    try:
        return bool(ed.options.get(str(name)))
    except Exception:
        return False


def require_file_capability(ed: Any, cap_name: str, op: str) -> None:
    """Raise if a scripted operation lacks the requested filesystem capability."""

    if not _option_enabled(ed, cap_name):
        raise FileCapabilityError(f"disabled for scripts ({cap_name})")


def checked_sandbox_path(ed: Any, raw_path: str) -> Path:
    """Return the nominal operation path after a cap.fs-root containment check.

    The check is performed against the resolved path so symlink escapes are
    denied.  The returned value is the nominal absolute path so writes through a
    symlink can still preserve the link instead of replacing it with its target.
    """

    resolved = fs_resolve_path(ed, raw_path)
    if not fs_path_allowed(ed, resolved):
        raise FileCapabilityError(fs_deny_reason(ed, resolved))
    return fs_nominal_path(ed, raw_path)


def chdir_under_caps(ed: Any, raw_path: str) -> str:
    """Change cwd through the script filesystem capability boundary."""

    require_file_capability(ed, "cap.fs-chdir", "cd")
    nominal = checked_sandbox_path(ed, raw_path)
    return chdir_contained(nominal, containment_root=fs_cap_root(ed))


def current_buffer_nominal_path(ed: Any, *, cap_name: str, op: str) -> Path:
    """Return the script-authorized nominal path for the active buffer."""

    require_file_capability(ed, cap_name, op)
    eb = ed.cur()
    raw = str(getattr(eb.buf, "path", "") or "").strip()
    if not raw:
        raise FileCapabilityError("buffer has no path")
    return checked_sandbox_path(ed, raw)


def _same_editor_path(ed: Any, a: str, b: str) -> bool:
    try:
        return str(ed._normalize_path(a)) == str(ed._normalize_path(b))
    except Exception:
        return str(a) == str(b)



def _disk_state_error(kind: str, message: object) -> dict[str, object]:
    """Return the disk-state map used for capability-denied script views."""

    label = str(kind or "unknown")
    return {
        "disk_state": label,
        "disk_summary": f"disk:{label}",
        "disk_changed": 0,
        "disk_missing": 0,
        "disk_known": 0,
        "disk_warning": 1,
        "disk_error": str(message or ""),
    }


def _disk_state_for_buffer_under_caps(ed: Any, eb: Any, *, op: str = "disk-state") -> dict[str, object]:
    """Return one buffer's disk state using explicit script stat authority."""

    raw = str(getattr(eb.buf, "path", "") or "").strip()
    if not raw:
        return dict(ed.buffer_disk_state(eb, refresh=True))
    try:
        require_file_capability(ed, "cap.fs-stat", op)
        nominal = checked_sandbox_path(ed, raw)
    except FileCapabilityError as e:
        return _disk_state_error("unauthorized", e)
    except Exception as e:
        return _disk_state_error("unknown", e)

    try:
        same = _same_editor_path(ed, raw, str(nominal))
        return dict(ed.buffer_disk_state(eb, path=str(nominal), use_buffer_witness=same, refresh=True))
    except Exception as e:
        return _disk_state_error("unknown", e)


def disk_state_under_caps(ed: Any) -> dict[str, object]:
    """Return the active buffer disk freshness without ambient stat access.

    ``ed.disk-state`` preserves its historical single-map shape, so capability
    failures are represented as warning/error maps rather than exceptions.
    Path-backed buffers require ``cap.fs-stat`` and respect ``cap.fs-root``
    before any filesystem stat occurs.
    """

    return _disk_state_for_buffer_under_caps(ed, ed.cur(), op="disk-state")


def _disk_state_row(ed: Any, name: str, eb: Any, state: dict[str, object]) -> list[object]:
    """Return the shared disk-state row shape for one buffer."""

    try:
        dirty = 1 if bool(getattr(eb.buf, "dirty", False)) else 0
    except Exception:
        dirty = 0
    return [
        str(name),
        str(state.get("disk_state", "") or ""),
        1 if int(state.get("disk_warning", 0) or 0) else 0,
        1 if int(state.get("disk_changed", 0) or 0) else 0,
        1 if int(state.get("disk_missing", 0) or 0) else 0,
        dirty,
        1 if str(name) == str(getattr(ed, "active", "") or "") else 0,
        str(getattr(eb.buf, "path", "") or ""),
        str(state.get("disk_error", "") or ""),
    ]


def disk_state_rows_under_caps(ed: Any, *, include_fresh: bool = False) -> list[list[object]]:
    """Return per-buffer disk-state rows without ambient script stat access.

    This is the script/hostcall sibling of ``Editor.disk_state_rows``.  It keeps
    the same row shape while requiring ``cap.fs-stat`` for each path-backed
    buffer, so structured hostcalls cannot become a filesystem-existence oracle
    outside the explicit capability lane.
    """

    rows: list[list[object]] = []
    try:
        names = list(ed.buffer_names())
    except Exception:
        names = []
    for name in names:
        try:
            eb = ed.buffers.get(str(name))
        except Exception:
            eb = None
        if eb is None:
            continue
        state = _disk_state_for_buffer_under_caps(ed, eb, op="disk-state")
        warning = 1 if int(state.get("disk_warning", 0) or 0) else 0
        if not include_fresh and not warning:
            continue
        rows.append(_disk_state_row(ed, str(name), eb, state))
    return rows

def save_current_buffer_under_caps(ed: Any, *, force: bool = False, target: str | None = None) -> dict[str, object]:
    """Save the current buffer through script filesystem capability checks.

    Relative targets are anchored under cap.fs-root when a sandbox root exists.
    If that changes the effective path, the save is routed through the editor's
    transactional save-as boundary so failed writes do not half-retitle buffers.
    """

    require_file_capability(ed, "cap.fs-save", "save")
    if force:
        require_file_capability(ed, "cap.fs-force-save", "force save")
    eb = ed.cur()
    raw = str(target if target is not None else (getattr(eb.buf, "path", "") or "")).strip()
    if not raw:
        raise FileCapabilityError("buffer has no path")
    nominal = checked_sandbox_path(ed, raw)
    containment_root = fs_cap_root(ed)
    try:
        st = ed._bounded_fs_stat(nominal, containment_root=containment_root)
        is_dir = bool(getattr(st, "exists", False) and getattr(st, "kind", "") == "dir")
    except OSError:
        # Let the underlying save path surface a more concrete failure.
        is_dir = False
    if is_dir:
        raise IsADirectoryError(f"is a directory: {nominal}")

    current_path = str(getattr(eb.buf, "path", "") or "")
    if target is not None or not _same_editor_path(ed, current_path, str(nominal)):
        return ed.save_as(str(nominal), force=force, containment_root=containment_root)
    return ed.save(force=force, containment_root=containment_root)


def disk_diff_lines_under_caps(ed: Any, *, max_lines: int = 80) -> list[str]:
    """Return current disk-vs-buffer diff lines after cap.fs-open checks."""

    nominal = current_buffer_nominal_path(ed, cap_name="cap.fs-open", op="diff")
    containment_root = fs_cap_root(ed)
    if _same_editor_path(ed, str(getattr(ed.cur().buf, "path", "") or ""), str(nominal)):
        return ed.disk_diff_lines(max_lines=max_lines, containment_root=containment_root)
    return ed.disk_diff_lines(max_lines=max_lines, path=str(nominal), containment_root=containment_root)


def revert_buffer_under_caps(ed: Any, *, force: bool = False) -> dict[str, object]:
    """Revert the active buffer after cap.fs-open checks."""

    nominal = current_buffer_nominal_path(ed, cap_name="cap.fs-open", op="revert")
    containment_root = fs_cap_root(ed)
    if _same_editor_path(ed, str(getattr(ed.cur().buf, "path", "") or ""), str(nominal)):
        return ed.revert_buffer_from_disk(force=force, containment_root=containment_root)
    return ed.revert_buffer_from_disk(force=force, path=str(nominal), containment_root=containment_root)
