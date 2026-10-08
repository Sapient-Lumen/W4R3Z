from __future__ import annotations

"""Bounded project-root discovery and project-file inventory.

This module owns two related read-only filesystem policies that used to pull
more coordinator gravity into :mod:`micromax_editor.editor`:

* short-lived, batched project-root marker discovery for picker grouping; and
* one-shot project-file snapshots for the interactive file picker.

The inventory is deliberately not a background index. Each picker open builds
one immutable, bounded snapshot. The snapshot is deterministic for the names it
observes, never follows symlinks, excludes hidden/generated directories by
default, and can be killed after a host-owned wall-clock budget.
"""

from dataclasses import dataclass
import math
import multiprocessing
import os
from pathlib import Path, PurePosixPath
import socket
import stat
import time
from typing import Iterable

from .file_access import (
    isolated_filesystem_worker_context,
    stat_paths_contained_bounded,
)
from .file_write import assert_path_within_root
from .worker_process import (
    DEFAULT_WORKER_START_TIMEOUT_SECONDS,
    WorkerResultError,
    WorkerResultStartError,
    WorkerResultStartTimeoutError,
    WorkerResultTimeoutError,
    collect_worker_result,
    create_one_shot_worker,
)


PROJECT_ROOT_MARKERS: tuple[str, ...] = (
    ".git",
    ".hg",
    ".svn",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
)
PROJECT_ROOT_MAX_DEPTH = 8
PROJECT_ROOT_CACHE_TTL_SECONDS = 2.0
PROJECT_ROOT_MARKER_BATCH_LIMIT = PROJECT_ROOT_MAX_DEPTH * len(PROJECT_ROOT_MARKERS) * 32

_PROJECT_SCAN_READY = b"R"
_PROJECT_SCAN_GO = b"G"


# These directories are implementation/build metadata rather than useful file
# picker destinations. They remain excluded even when ``include_hidden`` is
# enabled; that option reveals ordinary dotfiles, not VCS databases or caches.
PROJECT_FILE_ALWAYS_IGNORED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".cache",
        ".mypy_cache",
        ".nox",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "target",
        "venv",
    }
)
_PROJECT_FILE_ALWAYS_IGNORED_CASEFOLD = frozenset(
    name.casefold() for name in PROJECT_FILE_ALWAYS_IGNORED_DIRS
)
_PROJECT_FILE_ALWAYS_IGNORED_NAMES_CASEFOLD = frozenset({".git", ".hg", ".svn"})


@dataclass(frozen=True, slots=True)
class ProjectFileScanLimits:
    """Host-owned resource limits for one project-file snapshot."""

    max_files: int = 4096
    max_dirs: int = 2048
    max_depth: int = 32
    max_entries: int = 32768
    max_path_bytes: int = 1_048_576
    timeout_seconds: float = 1.0

    def normalized(self) -> "ProjectFileScanLimits":
        """Return finite, non-negative limits suitable for a worker."""

        timeout = float(self.timeout_seconds)
        if not math.isfinite(timeout):
            timeout = 1.0
        return ProjectFileScanLimits(
            max_files=max(1, int(self.max_files)),
            max_dirs=max(1, int(self.max_dirs)),
            max_depth=max(0, int(self.max_depth)),
            max_entries=max(1, int(self.max_entries)),
            max_path_bytes=max(1, int(self.max_path_bytes)),
            timeout_seconds=max(0.0, timeout),
        )


@dataclass(frozen=True, slots=True)
class ProjectFileScan:
    """Immutable result of one bounded project-file inventory pass."""

    root: str
    files: tuple[str, ...] = ()
    dirs_scanned: int = 0
    entries_scanned: int = 0
    path_bytes: int = 0
    truncated: bool = False
    timed_out: bool = False
    reason: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.timed_out and not self.error


class ProjectRootLocator:
    """Small owner for bounded, short-lived project-root marker witnesses."""

    def __init__(
        self,
        *,
        markers: Iterable[str] = PROJECT_ROOT_MARKERS,
        max_depth: int = PROJECT_ROOT_MAX_DEPTH,
        cache_ttl_seconds: float = PROJECT_ROOT_CACHE_TTL_SECONDS,
        marker_batch_limit: int = PROJECT_ROOT_MARKER_BATCH_LIMIT,
        max_cache_rows: int = 256,
        trim_cache_rows: int = 192,
    ) -> None:
        self.markers = tuple(str(marker) for marker in markers)
        self.max_depth = max(1, int(max_depth))
        self.cache_ttl_seconds = max(0.0, float(cache_ttl_seconds))
        self.marker_batch_limit = max(1, int(marker_batch_limit))
        self.max_cache_rows = max(1, int(max_cache_rows))
        self.trim_cache_rows = max(1, min(int(trim_cache_rows), self.max_cache_rows))
        self.cache: dict[str, tuple[float, str]] = {}

    def cache_get(self, key: str) -> str | None:
        row = self.cache.get(str(key))
        if not isinstance(row, tuple) or len(row) != 2:
            return None
        try:
            timestamp = float(row[0])
            if time.monotonic() - timestamp > self.cache_ttl_seconds:
                self.cache.pop(str(key), None)
                return None
            return str(row[1] or "")
        except Exception:
            self.cache.pop(str(key), None)
            return None

    def cache_put(self, key: str, root: str) -> None:
        self.cache[str(key)] = (time.monotonic(), str(root or ""))
        if len(self.cache) <= self.max_cache_rows:
            return
        try:
            oldest = sorted(self.cache.items(), key=lambda item: item[1][0])
            drop_count = max(1, len(oldest) - self.trim_cache_rows)
            for drop_key, _row in oldest[:drop_count]:
                self.cache.pop(str(drop_key), None)
        except Exception:
            self.cache.clear()

    def candidate_dirs(self, path: str) -> tuple[str, list[Path]]:
        """Return the legacy normalized cache key and bounded parent walk."""

        raw = str(path or "")
        if not raw:
            return "", []
        try:
            candidate = Path(raw).expanduser().resolve(strict=False)
        except Exception:
            candidate = Path(raw).expanduser()
        key = str(candidate)
        current = candidate
        candidates: list[Path] = []
        seen: set[str] = set()
        for _ in range(self.max_depth):
            current_key = str(current)
            if current_key not in seen:
                seen.add(current_key)
                candidates.append(current)
            if current.parent == current:
                break
            current = current.parent
        return key, candidates

    def seed(
        self,
        paths: Iterable[str | Path],
        *,
        containment_root: str | Path | None = None,
        timeout_seconds: float | None = 5.0,
    ) -> None:
        """Batch marker observations for every uncached path in ``paths``."""

        wanted: dict[str, list[Path]] = {}
        marker_paths: list[Path] = []
        seen_markers: set[str] = set()
        for raw in paths:
            key, candidates = self.candidate_dirs(str(raw))
            if not key or not candidates or self.cache_get(key) is not None:
                continue
            wanted[key] = candidates
            for current in candidates:
                for marker in self.markers:
                    marker_path = current / marker
                    marker_key = str(marker_path)
                    if marker_key in seen_markers:
                        continue
                    seen_markers.add(marker_key)
                    marker_paths.append(marker_path)
                    if len(marker_paths) >= self.marker_batch_limit:
                        break
                if len(marker_paths) >= self.marker_batch_limit:
                    break
            if len(marker_paths) >= self.marker_batch_limit:
                break

        if not wanted:
            return

        results = {}
        if marker_paths:
            try:
                results = stat_paths_contained_bounded(
                    marker_paths,
                    containment_root=containment_root,
                    timeout_seconds=timeout_seconds,
                    max_paths=self.marker_batch_limit,
                    worker_context=isolated_filesystem_worker_context(),
                )
            except Exception:
                results = {}

        for key, candidates in wanted.items():
            root = ""
            for current in candidates:
                for marker in self.markers:
                    observed = results.get(str(current / marker))
                    if observed is not None and bool(getattr(observed, "exists", False)):
                        root = str(current)
                        break
                if root:
                    break
            self.cache_put(key, root)

    def root_for_path(
        self,
        path: str,
        *,
        containment_root: str | Path | None = None,
        timeout_seconds: float | None = 5.0,
    ) -> str:
        """Return the nearest observed marker root, or an empty string."""

        key, candidates = self.candidate_dirs(str(path or ""))
        if not key or not candidates:
            return ""
        cached = self.cache_get(key)
        if cached is not None:
            return str(cached)
        self.seed(
            [path],
            containment_root=containment_root,
            timeout_seconds=timeout_seconds,
        )
        cached = self.cache_get(key)
        return str(cached or "")


@dataclass(slots=True)
class _ScanState:
    root: Path
    include_hidden: bool
    limits: ProjectFileScanLimits
    files: list[str]
    dirs_scanned: int = 0
    entries_scanned: int = 0
    path_bytes: int = 0
    truncated: bool = False
    reason: str = ""
    hard_exhausted: bool = False

    def stop(self, reason: str, *, terminal: bool = True) -> None:
        """Record truncation without confusing a depth cue for a hard stop.

        Reaching ``max_depth`` only skips that descendant; sibling files and
        directories remain useful. File, directory, entry, and path-byte caps
        are terminal for the whole snapshot. If a hard cap follows an earlier
        depth cue, promote the public reason so diagnostics name the resource
        boundary that actually ended the scan.
        """

        self.truncated = True
        if terminal:
            self.hard_exhausted = True
        if not self.reason or (terminal and self.reason == "depth"):
            self.reason = str(reason)

    @property
    def exhausted(self) -> bool:
        return bool(self.hard_exhausted)


def _portable_relative_path(parts: tuple[str, ...]) -> str:
    return str(PurePosixPath(*parts))


def _observe_entry_path(state: _ScanState, parts: tuple[str, ...]) -> bool:
    state.entries_scanned += 1
    if state.entries_scanned > state.limits.max_entries:
        state.stop("entries")
        return False
    relative = _portable_relative_path(parts)
    state.path_bytes += len(relative.encode("utf-8", errors="replace"))
    if state.path_bytes > state.limits.max_path_bytes:
        state.stop("path-bytes")
        return False
    return True


def _skip_name(state: _ScanState, name: str, *, is_dir: bool) -> bool:
    folded = str(name).casefold()
    if folded in _PROJECT_FILE_ALWAYS_IGNORED_NAMES_CASEFOLD:
        return True
    if not state.include_hidden and str(name).startswith("."):
        return True
    return bool(is_dir and folded in _PROJECT_FILE_ALWAYS_IGNORED_CASEFOLD)


def _record_file(state: _ScanState, parts: tuple[str, ...]) -> bool:
    if len(state.files) >= state.limits.max_files:
        state.stop("files")
        return False
    state.files.append(_portable_relative_path(parts))
    return True


def _dir_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _scan_dir_fd(state: _ScanState, dir_fd: int, parts: tuple[str, ...], depth: int) -> None:
    if state.exhausted:
        return
    if state.dirs_scanned >= state.limits.max_dirs:
        state.stop("directories")
        return
    state.dirs_scanned += 1

    entries: list[tuple[str, str]] = []
    try:
        with os.scandir(dir_fd) as iterator:
            for entry in iterator:
                name = str(entry.name)
                child_parts = parts + (name,)
                if not _observe_entry_path(state, child_parts):
                    return
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        kind = "dir"
                    elif entry.is_file(follow_symlinks=False):
                        kind = "file"
                    else:
                        continue
                except OSError:
                    continue
                if _skip_name(state, name, is_dir=(kind == "dir")):
                    continue
                entries.append((name, kind))
    except OSError:
        # An unreadable descendant should not make an otherwise useful project
        # snapshot disappear. The root itself is validated/opened separately.
        return

    entries.sort(key=lambda row: (str(row[0]).casefold(), str(row[0])))
    for name, kind in entries:
        if state.exhausted:
            return
        child_parts = parts + (name,)
        if kind == "file":
            if not _record_file(state, child_parts):
                return
            continue
        if depth >= state.limits.max_depth:
            state.stop("depth", terminal=False)
            continue
        try:
            child_fd = os.open(name, _dir_open_flags(), dir_fd=dir_fd)
        except OSError:
            continue
        try:
            mode = int(getattr(os.fstat(child_fd), "st_mode", 0) or 0)
            if not stat.S_ISDIR(mode):
                continue
            _scan_dir_fd(state, child_fd, child_parts, depth + 1)
        finally:
            try:
                os.close(child_fd)
            except OSError:
                pass


def _scan_dir_path(state: _ScanState, directory: Path, parts: tuple[str, ...], depth: int) -> None:
    """Portable fallback for hosts without fd-relative directory traversal."""

    if state.exhausted:
        return
    if state.dirs_scanned >= state.limits.max_dirs:
        state.stop("directories")
        return
    state.dirs_scanned += 1

    entries: list[tuple[str, str, Path]] = []
    try:
        with os.scandir(directory) as iterator:
            for entry in iterator:
                name = str(entry.name)
                child_parts = parts + (name,)
                if not _observe_entry_path(state, child_parts):
                    return
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        kind = "dir"
                    elif entry.is_file(follow_symlinks=False):
                        kind = "file"
                    else:
                        continue
                except OSError:
                    continue
                if _skip_name(state, name, is_dir=(kind == "dir")):
                    continue
                entries.append((name, kind, Path(entry.path)))
    except OSError:
        return

    entries.sort(key=lambda row: (str(row[0]).casefold(), str(row[0])))
    for name, kind, child in entries:
        if state.exhausted:
            return
        child_parts = parts + (name,)
        if kind == "file":
            if not _record_file(state, child_parts):
                return
            continue
        if depth >= state.limits.max_depth:
            state.stop("depth", terminal=False)
            continue
        try:
            resolved_child = child.resolve(strict=True)
            assert_path_within_root(resolved_child, state.root)
        except (OSError, RuntimeError, ValueError):
            continue
        _scan_dir_path(state, resolved_child, child_parts, depth + 1)


def _scan_project_files_direct(
    root: str | Path,
    *,
    containment_root: str | Path | None,
    include_hidden: bool,
    limits: ProjectFileScanLimits,
) -> ProjectFileScan:
    normalized = limits.normalized()
    resolved_root = Path(root).expanduser().resolve(strict=True)
    if containment_root is not None and str(containment_root).strip():
        assert_path_within_root(resolved_root, containment_root)
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"not a directory: {resolved_root}")

    state = _ScanState(
        root=resolved_root,
        include_hidden=bool(include_hidden),
        limits=normalized,
        files=[],
    )

    used_fd_walk = False
    try:
        root_fd = os.open(resolved_root, _dir_open_flags())
    except (OSError, TypeError, NotImplementedError):
        root_fd = -1
    if root_fd >= 0:
        try:
            mode = int(getattr(os.fstat(root_fd), "st_mode", 0) or 0)
            if not stat.S_ISDIR(mode):
                raise NotADirectoryError(f"not a directory: {resolved_root}")
            try:
                _scan_dir_fd(state, root_fd, (), 0)
                used_fd_walk = True
            except (TypeError, NotImplementedError):
                # Windows and a few alternative Python ports do not accept a
                # directory fd in scandir/openat. Fall through to path traversal.
                used_fd_walk = False
        finally:
            try:
                os.close(root_fd)
            except OSError:
                pass
    if not used_fd_walk:
        state.files.clear()
        state.dirs_scanned = 0
        state.entries_scanned = 0
        state.path_bytes = 0
        state.truncated = False
        state.reason = ""
        state.hard_exhausted = False
        _scan_dir_path(state, resolved_root, (), 0)

    # Traversal is stable per directory; a final sort makes the public contract
    # independent of whether the host used the fd-relative or path fallback.
    state.files.sort(key=lambda value: (str(value).casefold(), str(value)))
    return ProjectFileScan(
        root=str(resolved_root),
        files=tuple(state.files),
        dirs_scanned=int(state.dirs_scanned),
        entries_scanned=min(int(state.entries_scanned), normalized.max_entries),
        path_bytes=min(int(state.path_bytes), normalized.max_path_bytes),
        truncated=bool(state.truncated),
        reason=str(state.reason),
    )


class _ProjectFileWorkerReadyGate:
    """One-shot READY/GO boundary between spawn bootstrap and traversal.

    ``multiprocessing.Process.start()`` returns before a spawn child has imported
    its main module and entered the requested target.  Project scans deliberately
    expose a small traversal timeout, so charging fresh-interpreter bootstrap to
    that timeout creates false failures before one directory is observed.  This
    private socketpair keeps target readiness separately bounded by the existing
    worker-start allowance; the generic result owner still controls process kill,
    reap, and result framing.
    """

    __slots__ = ("_parent", "_child", "_timeout")

    def __init__(
        self,
        *,
        timeout_seconds: float = DEFAULT_WORKER_START_TIMEOUT_SECONDS,
    ) -> None:
        parent, child = socket.socketpair()
        try:
            timeout = float(timeout_seconds)
            if not math.isfinite(timeout) or timeout <= 0:
                timeout = float(DEFAULT_WORKER_START_TIMEOUT_SECONDS)
            parent.settimeout(max(0.01, timeout))
            child.setblocking(True)
        except BaseException:
            try:
                parent.close()
            finally:
                child.close()
            raise
        self._parent = parent
        self._child = child
        self._timeout = max(0.01, timeout)

    @property
    def child_endpoint(self) -> socket.socket:
        return self._child

    def _close_parent_child_copy(self) -> None:
        try:
            self._child.close()
        except OSError:
            pass

    def wait_and_release(self, worker_pid: int | None) -> None:
        """Wait for target entry, then release traversal under its own timer."""

        self._close_parent_child_copy()
        label = (
            "project file scan worker"
            if worker_pid is None
            else f"project file scan worker {int(worker_pid)}"
        )
        try:
            ready = self._parent.recv(1)
        except socket.timeout as exc:
            raise WorkerResultStartTimeoutError(
                f"{label} readiness timed out after {self._timeout:.3g}s"
            ) from exc
        except OSError as exc:
            raise WorkerResultStartError(
                f"{label} readiness channel failed: {exc}"
            ) from exc
        if ready != _PROJECT_SCAN_READY:
            detail = (
                "closed before readiness" if not ready else "sent invalid readiness"
            )
            raise WorkerResultStartError(f"{label} {detail}")
        try:
            self._parent.sendall(_PROJECT_SCAN_GO)
        except OSError as exc:
            raise WorkerResultStartError(
                f"{label} readiness release failed: {exc}"
            ) from exc

    def close(self) -> None:
        self._close_parent_child_copy()
        try:
            self._parent.close()
        except OSError:
            pass


def _project_scan_wait_for_release(ready_socket: socket.socket) -> bool:
    """Publish target readiness and wait for the parent-owned operation lease."""

    try:
        ready_socket.sendall(_PROJECT_SCAN_READY)
        return ready_socket.recv(1) == _PROJECT_SCAN_GO
    except OSError:
        return False
    finally:
        try:
            ready_socket.close()
        except OSError:
            pass


def _scan_project_files_worker(
    root: str,
    containment_root: str | None,
    include_hidden: bool,
    limits: ProjectFileScanLimits,
    ready_socket: socket.socket,
    queue: object,
) -> None:
    if not _project_scan_wait_for_release(ready_socket):
        close = getattr(queue, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass
        return
    try:
        result = _scan_project_files_direct(
            root,
            containment_root=containment_root,
            include_hidden=include_hidden,
            limits=limits,
        )
        queue.put(("ok", result))
    except BaseException as exc:  # pragma: no cover - serialized to parent.
        queue.put(("err", f"{type(exc).__name__}: {exc}"))


def scan_project_files(
    root: str | Path,
    *,
    containment_root: str | Path | None = None,
    include_hidden: bool = False,
    limits: ProjectFileScanLimits | None = None,
) -> ProjectFileScan:
    """Build one bounded, symlink-nonfollowing project-file snapshot.

    A positive timeout runs the entire recursive traversal in one killable
    worker. The caller receives a typed timeout/error result instead of partial
    worker state, making prompt creation transactional: either a coherent
    snapshot is installed or no picker is opened.
    """

    active_limits = (limits or ProjectFileScanLimits()).normalized()
    timeout = float(active_limits.timeout_seconds)
    if timeout <= 0:
        try:
            return _scan_project_files_direct(
                root,
                containment_root=containment_root,
                include_hidden=include_hidden,
                limits=active_limits,
            )
        except Exception as exc:
            return ProjectFileScan(root=str(root), error=f"{type(exc).__name__}: {exc}")

    context: multiprocessing.context.BaseContext = isolated_filesystem_worker_context()
    cap_root = None if containment_root is None else str(containment_root)
    ready_gate: _ProjectFileWorkerReadyGate | None = None
    try:
        ready_gate = _ProjectFileWorkerReadyGate()
        proc, channel = create_one_shot_worker(
            context,
            target=_scan_project_files_worker,
            args=(
                str(root),
                cap_root,
                bool(include_hidden),
                active_limits,
                ready_gate.child_endpoint,
            ),
            max_result_bytes=max(
                1024 * 1024,
                int(active_limits.max_path_bytes) * 4 + 1024 * 1024,
            ),
        )
        received = collect_worker_result(
            proc,
            channel,
            timeout_seconds=timeout,
            operation=f"project file scan: {root}",
            require_clean_exit=True,
            after_start=ready_gate.wait_and_release,
        )
        if not isinstance(received, tuple) or len(received) != 2:
            return ProjectFileScan(
                root=str(root),
                error=f"invalid project scan result: {received!r}",
            )
        status, payload = received
        if status == "ok" and isinstance(payload, ProjectFileScan):
            return payload
        return ProjectFileScan(root=str(root), error=str(payload))
    except WorkerResultStartTimeoutError as exc:
        return ProjectFileScan(
            root=str(root),
            truncated=True,
            timed_out=True,
            reason="startup-timeout",
            error=str(exc),
        )
    except WorkerResultTimeoutError:
        return ProjectFileScan(
            root=str(root),
            truncated=True,
            timed_out=True,
            reason="timeout",
            error=f"project file scan timed out after {timeout:.3g}s",
        )
    except WorkerResultError as exc:
        return ProjectFileScan(root=str(root), error=str(exc))
    except Exception as exc:
        return ProjectFileScan(root=str(root), error=f"{type(exc).__name__}: {exc}")
    finally:
        if ready_gate is not None:
            ready_gate.close()


__all__ = [
    "PROJECT_FILE_ALWAYS_IGNORED_DIRS",
    "PROJECT_ROOT_CACHE_TTL_SECONDS",
    "PROJECT_ROOT_MARKER_BATCH_LIMIT",
    "PROJECT_ROOT_MARKERS",
    "PROJECT_ROOT_MAX_DEPTH",
    "ProjectFileScan",
    "ProjectFileScanLimits",
    "ProjectRootLocator",
    "scan_project_files",
]
