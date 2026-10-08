from __future__ import annotations

"""Capability-root-aware helpers for script filesystem hostcalls.

The Micromax bridge exposes tiny ``ed.fs-read`` / ``ed.fs-list`` /
``ed.fs-stat`` hostcalls.  The bridge should own VM stack plumbing, but the
filesystem policy needs to be testable as an ordinary Python seam: resolve the
script path under ``cap.fs-root``, keep relative paths anchored under that root,
and recheck containment immediately before the actual read/list/stat operation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .file_access import (
    FileTooLargeError,
    FilesystemOperationTimeoutError,
    NotADirectoryPathError,
    NotARegularFileError,
    list_dir_contained_bounded,
    read_file_bytes_contained_bounded,
    stat_path_contained_bounded,
)
from .fs_sandbox import (
    deny_reason as fs_deny_reason,
    fs_root as fs_cap_root,
    is_allowed as fs_path_allowed,
    nominal_path as fs_nominal_path,
    resolve_path as fs_resolve_path,
)
from .hostcall_boundary import (
    DEFAULT_FS_LIST_MAX_ROWS,
    DEFAULT_FS_LIST_TIMEOUT_SECONDS,
    DEFAULT_FS_READ_MAX_BYTES,
    DEFAULT_FS_READ_TIMEOUT_SECONDS,
    DEFAULT_FS_STAT_TIMEOUT_SECONDS,
)


MAX_FS_READ_BYTES = DEFAULT_FS_READ_MAX_BYTES
MAX_FS_READ_TIMEOUT_SECONDS = DEFAULT_FS_READ_TIMEOUT_SECONDS
MAX_FS_LIST_ROWS = DEFAULT_FS_LIST_MAX_ROWS
MAX_FS_LIST_TIMEOUT_SECONDS = DEFAULT_FS_LIST_TIMEOUT_SECONDS
MAX_FS_STAT_TIMEOUT_SECONDS = DEFAULT_FS_STAT_TIMEOUT_SECONDS


@dataclass(frozen=True)
class FsTextResult:
    ok: bool
    text: str
    err: str


@dataclass(frozen=True)
class FsRowsResult:
    ok: bool
    rows: list[list[object]]
    err: str


@dataclass(frozen=True)
class FsStatResult:
    ok: bool
    info: dict[str, object]
    err: str


def checked_operation_path(ed: Any, raw_path: str) -> Path:
    """Return the nominal operation path after the script sandbox preflight.

    The preflight uses the resolved path so existing symlink escapes are denied.
    The returned value is the nominal absolute path, not the resolved target, so
    the final operation can re-resolve it and catch a late parent/symlink swap.
    """

    resolved = fs_resolve_path(ed, str(raw_path))
    if not fs_path_allowed(ed, resolved):
        raise PermissionError(fs_deny_reason(ed, resolved))
    return fs_nominal_path(ed, str(raw_path))


def _containment_root(ed: Any) -> Path | None:
    return fs_cap_root(ed)


def fs_read_text(
    ed: Any,
    raw_path: str,
    *,
    max_bytes: int | None = MAX_FS_READ_BYTES,
    timeout_seconds: float | None = MAX_FS_READ_TIMEOUT_SECONDS,
) -> FsTextResult:
    """Read UTF-8-ish text through the script filesystem capability boundary."""

    try:
        p = checked_operation_path(ed, raw_path)
        root = _containment_root(ed)
        try:
            # The bounded helper performs both size/kind preflight and final
            # fd-bound read inside the same killable worker when the timeout is
            # positive.  The final read still repeats kind/size/root checks so
            # late swaps/growth fail closed.
            result = read_file_bytes_contained_bounded(
                p,
                containment_root=root,
                max_bytes=max_bytes,
                timeout_seconds=timeout_seconds,
            )
        except FileNotFoundError:
            return FsTextResult(False, "", f"not a file: {p}")
        except (IsADirectoryError, NotARegularFileError):
            return FsTextResult(False, "", f"not a file: {p}")
        except FileTooLargeError as e:
            return FsTextResult(False, "", str(e))
        except FilesystemOperationTimeoutError as e:
            return FsTextResult(False, "", str(e))
        return FsTextResult(True, result.data.decode("utf-8", errors="replace"), "")
    except Exception as e:
        return FsTextResult(False, "", str(e))



def fs_list_dir(
    ed: Any,
    raw_path: str,
    *,
    limit: int | None = MAX_FS_LIST_ROWS,
    timeout_seconds: float | None = MAX_FS_LIST_TIMEOUT_SECONDS,
) -> FsRowsResult:
    """List directory entries through the script filesystem capability boundary."""

    try:
        p = checked_operation_path(ed, raw_path)
        root = _containment_root(ed)
        try:
            listed = list_dir_contained_bounded(
                p, containment_root=root, limit=limit, timeout_seconds=timeout_seconds
            )
        except FileNotFoundError:
            return FsRowsResult(False, [], f"not a directory: {p}")
        except (NotADirectoryError, NotADirectoryPathError):
            return FsRowsResult(False, [], f"not a directory: {p}")
        except FilesystemOperationTimeoutError as e:
            return FsRowsResult(False, [], str(e))
        except OSError as e:
            return FsRowsResult(False, [], str(e))

        entries = [[entry.name, entry.kind, entry.path] for entry in listed]
        return FsRowsResult(True, entries, "")
    except Exception as e:
        return FsRowsResult(False, [], str(e))


def fs_stat_path(
    ed: Any,
    raw_path: str,
    *,
    timeout_seconds: float | None = MAX_FS_STAT_TIMEOUT_SECONDS,
) -> FsStatResult:
    """Stat a path through the script filesystem capability boundary."""

    try:
        p = checked_operation_path(ed, raw_path)
        root = _containment_root(ed)
        result = stat_path_contained_bounded(
            p, containment_root=root, timeout_seconds=timeout_seconds
        )
        if not result.exists:
            return FsStatResult(False, {"path": result.path, "exists": 0}, f"not found: {p}")

        return FsStatResult(
            True,
            {
                "path": str(result.path),
                "exists": 1,
                "kind": str(result.kind),
                "size": int(result.size),
                "mtime": int(result.mtime),
            },
            "",
        )
    except FilesystemOperationTimeoutError as e:
        return FsStatResult(False, {}, str(e))
    except Exception as e:
        return FsStatResult(False, {}, str(e))
