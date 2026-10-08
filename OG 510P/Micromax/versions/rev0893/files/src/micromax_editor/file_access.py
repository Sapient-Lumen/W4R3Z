from __future__ import annotations

"""Fd-backed contained read/list/stat helpers.

These helpers are the read-side sibling of the save writer's dir-fd boundary.
When a capability root is active, path preflight alone is not enough: a symlink
or parent directory can change between the high-level check and the actual
filesystem operation.  On POSIX hosts that expose /proc/self/fd, open the target
first, verify the opened fd's concrete target is still inside the configured
root, and only then read/list/stat from that fd.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import stat

from .file_write import FileContainmentError, assert_path_within_root


@dataclass(frozen=True)
class ContainedBytesResult:
    path: str
    data: bytes
    byte_count: int


@dataclass(frozen=True)
class ContainedStatResult:
    path: str
    exists: bool
    kind: str
    size: int
    mtime: int


@dataclass(frozen=True)
class ContainedDirEntry:
    name: str
    kind: str
    path: str


class FileTooLargeError(RuntimeError):
    """Raised when a contained read would exceed its caller's byte budget."""


class NotARegularFileError(RuntimeError):
    """Raised when a contained read target is not a regular file."""


class NotADirectoryPathError(RuntimeError):
    """Raised when a contained list target is not a directory."""


def _root_active(root: str | Path | None) -> bool:
    return root is not None and str(root).strip() != ""


def _fd_target_path(fd: int) -> Path | None:
    proc = Path(f"/proc/self/fd/{fd}")
    if not proc.exists():
        return None
    try:
        return proc.resolve(strict=True)
    except OSError:
        return None


def _assert_fd_within_root(fd: int, root: str | Path | None, fallback_path: Path) -> Path:
    """Return the opened fd target, raising if it escaped ``root``."""

    target = _fd_target_path(fd)
    if target is None:
        # Portable fallback: still re-resolve the nominal path, even though this
        # cannot bind the operation as tightly as an fd target check.
        assert_path_within_root(fallback_path, root)
        return fallback_path
    assert_path_within_root(target, root)
    return target


def _open_read_fd(path: Path) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    return os.open(path, flags)


def _open_dir_fd(path: Path) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    return os.open(path, flags)


def _close_fd(fd: int) -> None:
    try:
        os.close(fd)
    except OSError:
        pass


def _kind_from_mode(mode: int) -> str:
    if stat.S_ISDIR(mode):
        return "dir"
    if stat.S_ISREG(mode):
        return "file"
    return "other"


def read_file_bytes_contained(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    max_bytes: int | None = None,
) -> ContainedBytesResult:
    """Read a regular file after binding the operation to an opened fd.

    The fd target check is only materially stronger when ``containment_root`` is
    active, but using the same helper for ordinary reads keeps behavior and error
    classification centralized.
    """

    p = Path(path)
    if _root_active(containment_root):
        assert_path_within_root(p, containment_root)
    fd = _open_read_fd(p)
    try:
        target = _assert_fd_within_root(fd, containment_root, p)
        st = os.fstat(fd)
        mode = int(getattr(st, "st_mode", 0) or 0)
        if not stat.S_ISREG(mode):
            raise NotARegularFileError(f"not a file: {p}")
        size = int(getattr(st, "st_size", 0) or 0)
        limit = None if max_bytes is None else int(max_bytes)
        if limit is not None and limit >= 0 and size > limit:
            raise FileTooLargeError(f"file too large (> {limit} bytes): {p}")

        chunks: list[bytes] = []
        total = 0
        while True:
            budget = 65536
            if limit is not None and limit >= 0:
                budget = max(1, min(budget, limit + 1 - total))
            chunk = os.read(fd, budget)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if limit is not None and limit >= 0 and total > limit:
                raise FileTooLargeError(f"file too large (> {limit} bytes): {p}")
        data = b"".join(chunks)
        return ContainedBytesResult(path=str(target), data=data, byte_count=len(data))
    finally:
        _close_fd(fd)


def stat_path_contained(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
) -> ContainedStatResult:
    """Return stat-like info for a path through the contained fd seam."""

    p = Path(path)
    if _root_active(containment_root):
        assert_path_within_root(p, containment_root)
    try:
        fd = _open_read_fd(p)
    except FileNotFoundError:
        return ContainedStatResult(path=str(p), exists=False, kind="missing", size=0, mtime=0)
    try:
        target = _assert_fd_within_root(fd, containment_root, p)
        st = os.fstat(fd)
        mode = int(getattr(st, "st_mode", 0) or 0)
        return ContainedStatResult(
            path=str(target),
            exists=True,
            kind=_kind_from_mode(mode),
            size=int(getattr(st, "st_size", 0) or 0),
            mtime=int(getattr(st, "st_mtime", 0) or 0),
        )
    finally:
        _close_fd(fd)


def _child_kind_at(dir_fd: int, name: str) -> tuple[str, str]:
    kind = "other"
    try:
        st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        kind = _kind_from_mode(int(getattr(st, "st_mode", 0) or 0))
    except Exception:
        pass
    display = str(name) + "/" if kind == "dir" else str(name)
    return display, kind


def _child_rank_at(dir_fd: int, name: str) -> tuple[int, str]:
    try:
        st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        if stat.S_ISDIR(int(getattr(st, "st_mode", 0) or 0)):
            return (0, str(name).casefold())
    except Exception:
        pass
    return (1, str(name).casefold())


def list_dir_contained(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    limit: int = 500,
) -> list[ContainedDirEntry]:
    """List a directory after binding the directory itself to an fd."""

    p = Path(path)
    if _root_active(containment_root):
        assert_path_within_root(p, containment_root)
    try:
        fd = _open_dir_fd(p)
    except NotADirectoryError as e:
        raise NotADirectoryPathError(f"not a directory: {p}") from e
    except FileNotFoundError as e:
        raise NotADirectoryPathError(f"not a directory: {p}") from e
    try:
        _assert_fd_within_root(fd, containment_root, p)
        try:
            names = [str(name) for name in os.listdir(fd)]
        except NotADirectoryError as e:
            raise NotADirectoryPathError(f"not a directory: {p}") from e
        names.sort(key=lambda name: _child_rank_at(fd, name))
        rows: list[ContainedDirEntry] = []
        for name in names[: max(0, int(limit))]:
            display, kind = _child_kind_at(fd, name)
            rows.append(ContainedDirEntry(display, kind, str(p / name)))
        return rows
    finally:
        _close_fd(fd)


def chdir_contained(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
) -> str:
    """Change cwd after binding the target directory to an fd when possible.

    Script-facing ``cd`` is process-global, so it needs the same late
    containment discipline as file reads/writes.  On POSIX hosts, open the
    directory, verify the opened fd target is still inside the configured root,
    then ``fchdir`` to that fd.  The path fallback keeps pre/post containment
    checks for simpler hosts.
    """

    p = Path(path)
    if _root_active(containment_root):
        assert_path_within_root(p, containment_root)
    if hasattr(os, "fchdir"):
        fd = _open_dir_fd(p)
        try:
            _assert_fd_within_root(fd, containment_root, p)
            os.fchdir(fd)
            cwd = Path.cwd()
            if _root_active(containment_root):
                assert_path_within_root(cwd, containment_root)
            return str(cwd)
        finally:
            _close_fd(fd)
    os.chdir(p)
    cwd = Path.cwd()
    if _root_active(containment_root):
        assert_path_within_root(cwd, containment_root)
    return str(cwd)
