"""Fd-backed contained read/list/stat helpers.

These helpers are the read-side sibling of the save writer's dir-fd boundary.
When a capability root is active, path preflight alone is not enough: a symlink
or parent directory can change between the high-level check and the actual
filesystem operation.  On POSIX hosts that expose /proc/self/fd, open the target
first, verify the opened fd's concrete target is still inside the configured
root, and only then read/list/stat from that fd.
"""

from __future__ import annotations

import multiprocessing
import os
import stat
from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

from .file_write import FileContainmentError, assert_path_within_root
from .worker_process import (
    WorkerResultChannel,
    WorkerResultProtocolError,
    WorkerResultTimeoutError,
    WorkerResultTooLargeError,
    collect_worker_result,
    create_one_shot_worker,
    isolated_worker_context,
    normalize_worker_timeout_seconds,
    terminate_worker_process,
)


_FILESYSTEM_METADATA_RESULT_MAX_BYTES = 1024 * 1024
_FILESYSTEM_LIST_RESULT_MAX_BYTES = 8 * 1024 * 1024
_FILESYSTEM_RESULT_OVERHEAD_BYTES = 256 * 1024


@dataclass(frozen=True)
class ContainedBytesResult:
    path: str
    data: bytes
    byte_count: int


@dataclass(frozen=True)
class ContainedReadPreflightResult:
    path: str
    byte_count: int


@dataclass(frozen=True)
class ContainedStatResult:
    path: str
    exists: bool
    kind: str
    size: int
    mtime: int


@dataclass(frozen=True)
class ContainedAccessResult:
    path: str
    exists: bool
    kind: str
    writable: bool


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


class FilesystemOperationTimeoutError(RuntimeError):
    """Raised when a contained filesystem operation exceeds its wall-clock budget."""


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
    with suppress(OSError):
        os.close(fd)


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


def read_file_prefix_contained(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    max_bytes: int | None = 65536,
) -> ContainedBytesResult:
    """Read at most ``max_bytes`` from a contained regular file.

    Catalog and preview surfaces often need just enough bytes to identify a
    file, not the whole file.  This binds the open fd to the containment root
    like ``read_file_bytes_contained`` but deliberately does not reject files
    whose total size is larger than the prefix budget.
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
        limit = 65536 if max_bytes is None else max(0, int(max_bytes))
        chunks: list[bytes] = []
        total = 0
        while total < limit:
            chunk = os.read(fd, min(65536, limit - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        data = b"".join(chunks)
        return ContainedBytesResult(path=str(target), data=data, byte_count=len(data))
    finally:
        _close_fd(fd)


def preflight_file_read_size_contained(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    max_bytes: int | None = None,
) -> ContainedReadPreflightResult:
    """Check a contained read target's kind and size before reading bytes.

    This is a deliberately separate first pass for script-visible file
    observation.  It does not replace the final fd-bound check in
    ``read_file_bytes_contained`` because a file can be swapped or grow after
    preflight.  It only keeps obviously oversized reads from entering the byte
    loading loop in the common case.
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
        return ContainedReadPreflightResult(path=str(target), byte_count=size)
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


def access_path_contained(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
) -> ContainedAccessResult:
    """Return contained file-access truth for status cues.

    This is deliberately a small observation helper, not an authorization
    decision.  It binds the existence/kind check to the opened fd when possible
    and keeps the potentially blocking ``os.access`` probe inside the same
    filesystem boundary family used by stat/list/read wrappers.
    """

    p = Path(path)
    if _root_active(containment_root):
        assert_path_within_root(p, containment_root)
    try:
        fd = _open_read_fd(p)
    except FileNotFoundError:
        return ContainedAccessResult(path=str(p), exists=False, kind="missing", writable=False)
    except PermissionError:
        # Permission-denied opens are still useful status information.  The
        # access probe runs in the same call/worker as the rest of this helper
        # so callers with a positive timeout can still kill unusual filesystem
        # stalls instead of doing an ambient hot-path os.access().
        try:
            writable = bool(os.access(p, os.W_OK))
        except OSError:
            writable = False
        return ContainedAccessResult(path=str(p), exists=True, kind="file", writable=writable)
    try:
        target = _assert_fd_within_root(fd, containment_root, p)
        st = os.fstat(fd)
        kind = _kind_from_mode(int(getattr(st, "st_mode", 0) or 0))
        try:
            writable = bool(os.access(target, os.W_OK)) if kind == "file" else False
        except OSError:
            writable = False
        return ContainedAccessResult(
            path=str(target),
            exists=True,
            kind=kind,
            writable=writable,
        )
    finally:
        _close_fd(fd)


def _fs_worker_context() -> multiprocessing.context.BaseContext:
    """Return an isolated context for ordinary killable filesystem workers."""

    return isolated_worker_context()


def isolated_filesystem_worker_context() -> multiprocessing.context.BaseContext:
    """Return a non-fork context for new isolated filesystem workers.

    ``spawn`` starts a fresh interpreter and does not clone either the editor's
    active threads or a forkserver that may itself have acquired native threads
    during interpreter startup. ``forkserver`` is a secondary POSIX choice. The
    platform default is only a last-resort fallback when neither is available.
    """

    return isolated_worker_context()


def _stat_path_worker(path: str, root: str | None, queue: object) -> None:
    try:
        result = stat_path_contained(path, containment_root=root)
        queue.put(("ok", result))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", f"{type(e).__name__}: {e}"))


def _access_path_worker(path: str, root: str | None, queue: object) -> None:
    try:
        result = access_path_contained(path, containment_root=root)
        queue.put(("ok", result))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", f"{type(e).__name__}: {e}"))


def terminate_filesystem_worker(proc: multiprocessing.Process) -> None:
    """Compatibility wrapper around the shared short-lived worker teardown."""

    terminate_worker_process(proc)


def _terminate_worker(proc: multiprocessing.Process) -> None:
    """Compatibility alias for existing contained-operation workers."""

    terminate_filesystem_worker(proc)


def _collect_filesystem_worker_result(
    proc: multiprocessing.Process,
    channel: WorkerResultChannel,
    *,
    timeout_seconds: float,
    timeout_message: str,
    missing_message: str,
) -> object:
    """Receive one framed result without entering an unpreemptible Queue read."""

    operation = missing_message.split(" worker exited without result", 1)[0]
    try:
        return collect_worker_result(
            proc,
            channel,
            timeout_seconds=timeout_seconds,
            operation=operation,
            require_clean_exit=False,
        )
    except WorkerResultTimeoutError as exc:
        raise FilesystemOperationTimeoutError(timeout_message) from exc
    except WorkerResultTooLargeError as exc:
        raise RuntimeError(f"{operation} worker result exceeded its byte budget") from exc
    except WorkerResultProtocolError as exc:
        if "exited without result" in str(exc):
            raise RuntimeError(missing_message) from exc
        raise RuntimeError(f"{operation} worker result failed: {exc}") from exc


def stat_path_contained_bounded(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    timeout_seconds: float | None = 5.0,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> ContainedStatResult:
    """Return contained stat info, using a killable worker when timed.

    ``stat_path_contained`` binds the operation to an opened fd, but open/stat
    calls can still block on unusual filesystems.  This wrapper keeps the
    existing fd-bound semantics while letting hostcalls cap wall-clock time for
    metadata observations.
    """

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    if timeout <= 0:
        return stat_path_contained(path, containment_root=containment_root)

    ctx = worker_context or _fs_worker_context()
    root = None if containment_root is None else str(containment_root)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_stat_path_worker,
        args=(str(path), root),
        max_result_bytes=_FILESYSTEM_METADATA_RESULT_MAX_BYTES,
    )
    row = _collect_filesystem_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        timeout_message=f"filesystem stat timed out after {timeout:.3g}s: {path}",
        missing_message=f"filesystem stat worker exited without result: {path}",
    )
    if not isinstance(row, tuple) or len(row) != 2:
        raise RuntimeError(f"invalid filesystem stat worker result: {row!r}")
    status, payload = row

    if status == "ok":
        return payload
    raise RuntimeError(str(payload))



def access_path_contained_bounded(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    timeout_seconds: float | None = 5.0,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> ContainedAccessResult:
    """Return contained access truth, using a killable worker when timed."""

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    if timeout <= 0:
        return access_path_contained(path, containment_root=containment_root)

    ctx = worker_context or _fs_worker_context()
    root = None if containment_root is None else str(containment_root)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_access_path_worker,
        args=(str(path), root),
        max_result_bytes=_FILESYSTEM_METADATA_RESULT_MAX_BYTES,
    )
    row = _collect_filesystem_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        timeout_message=f"filesystem access timed out after {timeout:.3g}s: {path}",
        missing_message=f"filesystem access worker exited without result: {path}",
    )
    if not isinstance(row, tuple) or len(row) != 2:
        raise RuntimeError(f"invalid filesystem access worker result: {row!r}")
    status, payload = row

    if status == "ok":
        return payload
    raise RuntimeError(str(payload))


def _stat_paths_worker(paths: list[str], root: str | None, queue: object) -> None:
    try:
        rows: list[tuple[str, str, ContainedStatResult | str]] = []
        for path in paths:
            try:
                rows.append((str(path), "ok", stat_path_contained(path, containment_root=root)))
            except BaseException as e:  # pragma: no cover - serialized to parent.
                rows.append((str(path), "err", f"{type(e).__name__}: {e}"))
        queue.put(("ok", rows))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", f"{type(e).__name__}: {e}"))


def stat_paths_contained_bounded(
    paths: Iterable[str | Path],
    *,
    containment_root: str | Path | None = None,
    timeout_seconds: float | None = 5.0,
    max_paths: int | None = None,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> dict[str, ContainedStatResult]:
    """Return contained stat info for many paths through one killable worker.

    Command-palette/recent-file surfaces may need tiny disk truth for several
    remembered paths at once.  Spawning one timeout worker per row creates the
    same resource-consumption problem the timeout boundary was meant to avoid,
    while doing direct metadata probes can still block on unusual filesystems.
    This helper batches a bounded set of fd-backed stat observations inside one
    short-lived process.  Per-path filesystem errors are best-effort and omitted
    from the result map; missing files still return ``exists=False`` because the
    single-path helper represents them as ordinary stat results.
    """

    seen: dict[str, None] = {}
    limit = None if max_paths is None else max(0, int(max_paths))
    for path in paths:
        if limit is not None and len(seen) >= limit:
            break
        key = str(path)
        if key not in seen:
            seen[key] = None
    xs = list(seen.keys())
    if not xs:
        return {}

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    if timeout <= 0:
        out: dict[str, ContainedStatResult] = {}
        for key in xs:
            try:
                out[key] = stat_path_contained(key, containment_root=containment_root)
            except Exception:
                continue
        return out

    ctx = worker_context or _fs_worker_context()
    root = None if containment_root is None else str(containment_root)
    path_budget = sum(len(key.encode("utf-8", "surrogatepass")) for key in xs)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_stat_paths_worker,
        args=(xs, root),
        max_result_bytes=max(
            _FILESYSTEM_METADATA_RESULT_MAX_BYTES,
            path_budget * 4 + _FILESYSTEM_RESULT_OVERHEAD_BYTES,
        ),
    )
    payload_row = _collect_filesystem_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        timeout_message=(
            f"filesystem stat batch timed out after {timeout:.3g}s "
            f"({len(xs)} path(s))"
        ),
        missing_message="filesystem stat batch worker exited without result",
    )
    if not isinstance(payload_row, tuple) or len(payload_row) != 2:
        raise RuntimeError(f"invalid filesystem stat batch result: {payload_row!r}")
    status, payload = payload_row
    if status != "ok":
        raise RuntimeError(str(payload))

    out: dict[str, ContainedStatResult] = {}
    for row in list(payload or []):
        try:
            key, kind, value = row
        except Exception:
            continue
        if kind == "ok" and isinstance(value, ContainedStatResult):
            out[str(key)] = value
    return out


def _read_file_bytes_worker(
    path: str,
    root: str | None,
    max_bytes: int | None,
    queue: object,
) -> None:
    try:
        preflight_file_read_size_contained(path, containment_root=root, max_bytes=max_bytes)
        result = read_file_bytes_contained(path, containment_root=root, max_bytes=max_bytes)
        queue.put(("ok", result))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", type(e).__name__, str(e)))


def _raise_filesystem_worker_error(kind: str, message: str) -> None:
    if kind == "FileNotFoundError":
        raise FileNotFoundError(message)
    if kind == "IsADirectoryError":
        raise IsADirectoryError(message)
    if kind == "NotADirectoryError":
        raise NotADirectoryError(message)
    if kind == "NotARegularFileError":
        raise NotARegularFileError(message)
    if kind == "NotADirectoryPathError":
        raise NotADirectoryPathError(message)
    if kind == "FileTooLargeError":
        raise FileTooLargeError(message)
    if kind == "FileContainmentError":
        raise FileContainmentError(message)
    if kind == "PermissionError":
        raise PermissionError(message)
    if kind == "OSError":
        raise OSError(message)
    raise RuntimeError(message or kind)


def read_file_bytes_contained_bounded(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    max_bytes: int | None = None,
    timeout_seconds: float | None = 5.0,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> ContainedBytesResult:
    """Read contained file bytes, using a killable worker when timed.

    ``read_file_bytes_contained`` already binds the final read to an opened fd
    and enforces a byte budget.  This wrapper moves the preflight and final read
    into one short-lived worker so script-visible ``ed.fs-read`` can cap
    accepted filesystem open/fstat/read wall-clock time in the same family as
    ``ed.fs-stat`` and ``ed.fs-list``.
    """

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    if timeout <= 0:
        preflight_file_read_size_contained(
            path, containment_root=containment_root, max_bytes=max_bytes
        )
        return read_file_bytes_contained(
            path, containment_root=containment_root, max_bytes=max_bytes
        )

    ctx = worker_context or _fs_worker_context()
    root = None if containment_root is None else str(containment_root)
    limit = None if max_bytes is None else int(max_bytes)
    result_budget = (
        64 * 1024 * 1024
        if limit is None or limit < 0
        else max(
            _FILESYSTEM_METADATA_RESULT_MAX_BYTES,
            limit + _FILESYSTEM_RESULT_OVERHEAD_BYTES,
        )
    )
    proc, channel = create_one_shot_worker(
        ctx,
        target=_read_file_bytes_worker,
        args=(str(path), root, limit),
        max_result_bytes=result_budget,
    )
    payload = _collect_filesystem_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        timeout_message=f"filesystem read timed out after {timeout:.3g}s: {path}",
        missing_message=f"filesystem read worker exited without result: {path}",
    )

    if not isinstance(payload, tuple) or not payload:
        raise RuntimeError(f"invalid filesystem read worker result: {payload!r}")
    status = payload[0]
    if status == "ok":
        return payload[1]
    if status == "err" and len(payload) >= 3:
        _raise_filesystem_worker_error(str(payload[1]), str(payload[2]))
    raise RuntimeError(str(payload))


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
    limit: int | None = 500,
) -> list[ContainedDirEntry]:
    """List a directory after binding the directory itself to an fd.

    The directory is scanned from the opened fd so capability-root checks remain
    bound to the same directory object, and positive limits stop collection
    before materializing an unbounded name list.
    """

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
        max_rows = None if limit is None else max(0, int(limit))
        names: list[str] = []
        try:
            with os.scandir(fd) as entries:
                for entry in entries:
                    names.append(str(entry.name))
                    if max_rows is not None and len(names) >= max_rows:
                        break
        except NotADirectoryError as e:
            raise NotADirectoryPathError(f"not a directory: {p}") from e
        names.sort(key=lambda name: _child_rank_at(fd, name))
        rows: list[ContainedDirEntry] = []
        for name in names:
            display, kind = _child_kind_at(fd, name)
            rows.append(ContainedDirEntry(display, kind, str(p / name)))
        return rows
    finally:
        _close_fd(fd)


def _list_dir_worker(path: str, root: str | None, limit: int | None, queue: object) -> None:
    try:
        result = list_dir_contained(path, containment_root=root, limit=limit)
        queue.put(("ok", result))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", f"{type(e).__name__}: {e}"))


def list_dir_contained_bounded(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    limit: int | None = 500,
    timeout_seconds: float | None = 5.0,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> list[ContainedDirEntry]:
    """List a contained directory, using a killable worker when timed.

    ``list_dir_contained`` already binds the directory to an fd and applies a
    positive row limit before sorting/building row payloads.  This wrapper keeps
    that containment behavior but caps the wall-clock time spent in directory
    open/scandir/child-stat work, which may otherwise block on unusual or remote
    filesystems.
    """

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    if timeout <= 0:
        return list_dir_contained(path, containment_root=containment_root, limit=limit)

    ctx = worker_context or _fs_worker_context()
    root = None if containment_root is None else str(containment_root)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_list_dir_worker,
        args=(str(path), root, limit),
        max_result_bytes=_FILESYSTEM_LIST_RESULT_MAX_BYTES,
    )
    row = _collect_filesystem_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        timeout_message=f"filesystem list timed out after {timeout:.3g}s: {path}",
        missing_message=f"filesystem list worker exited without result: {path}",
    )
    if not isinstance(row, tuple) or len(row) != 2:
        raise RuntimeError(f"invalid filesystem list worker result: {row!r}")
    status, payload = row

    if status == "ok":
        return payload
    raise RuntimeError(str(payload))


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
