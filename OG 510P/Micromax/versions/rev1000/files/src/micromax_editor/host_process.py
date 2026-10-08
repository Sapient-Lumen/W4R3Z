"""Bounded process helpers for editor hostcalls.

``ed.shell`` is intentionally capability-gated, but once a trusted user enables
it the helper still needs local resource boundaries.  ``subprocess.run`` with
``capture_output=True`` waits through ``communicate()`` and only returns output
after it has been buffered, so the VM's post-hostcall result budget is too late
to protect the editor process.  This module streams pipe output into bounded
byte buffers and tears down the child process tree on timeout or output-budget
exhaustion.
"""

from __future__ import annotations

import math
import os
import signal
import stat
import subprocess
import threading
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any, BinaryIO

from micromax.subprocess_start import (
    SubprocessStartError,
    SubprocessStartTimeoutError,
    start_subprocess_with_deadline,
)

_CAPTURE_DRAIN_GRACE_SECONDS = 0.25
_CAPTURE_TREE_TERM_GRACE_SECONDS = 0.10
_FORCE_KILL_SIGNAL = int(getattr(signal, "SIGKILL", -1))


@dataclass(frozen=True)
class ShellCommandResult:
    """Result tuple for a bounded shell command."""

    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    output_truncated: bool = False


@dataclass(frozen=True)
class BoundedProcessResult:
    """Result tuple for a bounded argv process."""

    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    output_truncated: bool = False


@dataclass(frozen=True)
class _CapturedProcessResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    output_truncated: bool = False


def _finite_timeout_seconds(value: object, *, default: float) -> float:
    """Return a finite process deadline, preserving the historical 50 ms floor."""

    if isinstance(value, bool):
        return float(default)
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return float(default)
    if not math.isfinite(parsed):
        return float(default)
    return max(0.05, parsed)


def _output_byte_limit(value: object, *, default: int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return max(0, parsed)


def _process_group_kwargs() -> dict[str, object]:
    """Return Popen kwargs that isolate child process groups when supported."""

    if os.name == "posix":
        return {"start_new_session": True}
    creationflags = int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) or 0)
    return {"creationflags": creationflags} if creationflags else {}


def _confirmed_child_process_group_id(proc: subprocess.Popen[bytes]) -> int | None:
    """Return a confirmed POSIX child process group id, never a guessed PID."""

    if os.name != "posix":
        return None
    pid = getattr(proc, "pid", None)
    if not isinstance(pid, int) or pid <= 0:
        return None
    try:
        pgid = os.getpgid(pid)
    except (OSError, ProcessLookupError):
        return None
    return int(pgid) if int(pgid) == int(pid) else None


def _posix_ppid_map() -> dict[int, int]:
    if os.name != "posix":
        return {}
    proc_root = Path("/proc")
    if not proc_root.exists():
        return {}
    mapping: dict[int, int] = {}
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            pid = int(entry.name)
            status = (entry / "status").read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for line in status.splitlines():
            if line.startswith("PPid:"):
                with suppress(IndexError, ValueError):
                    mapping[pid] = int(line.split()[1])
                break
    return mapping


def _posix_descendant_pids(pid: int) -> list[int]:
    if os.name != "posix" or pid <= 0:
        return []
    ppid = _posix_ppid_map()
    children: dict[int, list[int]] = {}
    for child, parent in ppid.items():
        children.setdefault(parent, []).append(child)
    out: list[int] = []
    stack = list(children.get(int(pid), ()))
    seen: set[int] = set()
    while stack:
        child = stack.pop()
        if child in seen:
            continue
        seen.add(child)
        out.append(child)
        stack.extend(children.get(child, ()))
    return out


def _signal_descendant_process_groups(
    proc: subprocess.Popen[bytes], sig: int, *, parent_pgid: int | None
) -> None:
    """Signal descendants that escaped the direct child process group."""

    if os.name != "posix":
        return
    pid = getattr(proc, "pid", None)
    if not isinstance(pid, int) or pid <= 0:
        return
    try:
        own_pgid = os.getpgrp()
    except OSError:
        own_pgid = None
    protected_pgids = {
        value for value in (own_pgid, parent_pgid) if isinstance(value, int) and value > 0
    }
    signaled_groups: set[int] = set()
    for child_pid in sorted(_posix_descendant_pids(pid), reverse=True):
        if child_pid in {os.getpid(), os.getppid(), pid}:
            continue
        try:
            child_pgid = os.getpgid(child_pid)
        except (OSError, ProcessLookupError):
            continue
        if child_pgid > 0 and child_pgid not in protected_pgids:
            if child_pgid in signaled_groups:
                continue
            with suppress(OSError, ProcessLookupError):
                os.killpg(child_pgid, sig)
                signaled_groups.add(child_pgid)
                continue
        with suppress(OSError, ProcessLookupError):
            os.kill(child_pid, sig)


def _signal_process_group_or_child(
    proc: subprocess.Popen[bytes], sig: int, *, pgid: int | None
) -> None:
    if os.name == "posix" and isinstance(pgid, int) and pgid > 0:
        with suppress(OSError, ProcessLookupError):
            os.killpg(pgid, sig)
            return
    if sig == signal.SIGTERM:
        with suppress(OSError, ProcessLookupError):
            proc.terminate()
    else:
        with suppress(OSError, ProcessLookupError):
            proc.kill()


def _signal_process_tree_or_child(
    proc: subprocess.Popen[bytes], sig: int, *, pgid: int | None
) -> None:
    _signal_descendant_process_groups(proc, sig, parent_pgid=pgid)
    _signal_process_group_or_child(proc, sig, pgid=pgid)


def terminate_process_tree(
    proc: subprocess.Popen[bytes], *, pgid: int | None = None, timeout: float = 1.0
) -> None:
    """Best-effort child and escaped-grandchild teardown."""

    wait_timeout = _finite_timeout_seconds(timeout, default=1.0)
    if proc.poll() is not None:
        # The direct child can exit between a liveness check and teardown while
        # same-group descendants remain.  A confirmed POSIX process group is an
        # owned resource even after its leader has gone, so signal it rather
        # than treating leader exit as proof that the tree is empty.
        _signal_process_tree_or_child(proc, signal.SIGTERM, pgid=pgid)
        time.sleep(min(wait_timeout, _CAPTURE_TREE_TERM_GRACE_SECONDS))
        _signal_process_tree_or_child(proc, _FORCE_KILL_SIGNAL, pgid=pgid)
        return
    _signal_process_tree_or_child(proc, signal.SIGTERM, pgid=pgid)
    try:
        proc.wait(timeout=wait_timeout)
    except subprocess.TimeoutExpired:
        _signal_process_tree_or_child(proc, _FORCE_KILL_SIGNAL, pgid=pgid)
        with suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=wait_timeout)


class _BoundedPipeCapture:
    def __init__(self, *, max_bytes: int | None) -> None:
        self._max_bytes = None if max_bytes is None else max(0, int(max_bytes))
        self._lock = threading.Lock()
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.total = 0
        self.truncated = False

    def append(self, channel: str, data: bytes) -> None:
        if not data:
            return
        with self._lock:
            limit = self._max_bytes
            if limit is not None and self.total >= limit:
                self.truncated = True
                return
            piece = bytes(data)
            if limit is not None and self.total + len(piece) > limit:
                keep = max(0, limit - self.total)
                piece = piece[:keep]
                self.truncated = True
            if channel == "stdout":
                self.stdout.extend(piece)
            else:
                self.stderr.extend(piece)
            self.total += len(piece)

    def is_truncated(self) -> bool:
        with self._lock:
            return bool(self.truncated)


def _reader(stream: BinaryIO, capture: _BoundedPipeCapture, channel: str) -> None:
    try:
        while True:
            chunk = stream.read(8192)
            if not chunk:
                break
            capture.append(channel, bytes(chunk))
            if capture.is_truncated():
                break
    except Exception:
        pass


def _stdin_writer(stream: BinaryIO, data: bytes) -> None:
    try:
        try:
            stream.write(data)
            stream.flush()
        finally:
            stream.close()
    except Exception:
        pass


def _decode(data: bytes | bytearray) -> str:
    return bytes(data).decode("utf-8", errors="replace")


def _with_diagnostic(stderr: str, message: str) -> str:
    return (stderr + "\n" if stderr else "") + str(message)


def _join_threads_until(
    threads: list[threading.Thread], *, deadline: float
) -> list[threading.Thread]:
    """Join ``threads`` against one absolute deadline and return survivors."""

    for thread in threads:
        try:
            alive = thread.is_alive()
        except RuntimeError:
            alive = False
        if thread.ident is None and not alive:
            # The capture owner appends all prospective threads before starting
            # them.  A failure partway through that loop leaves later entries
            # unstarted, and joining an unstarted Thread raises RuntimeError.
            continue
        remaining = max(0.0, float(deadline) - time.monotonic())
        if remaining <= 0:
            break
        with suppress(RuntimeError):
            thread.join(timeout=remaining)
    survivors: list[threading.Thread] = []
    for thread in threads:
        with suppress(RuntimeError):
            if thread.is_alive():
                survivors.append(thread)
    return survivors


def _pipe_id(stream: IO[Any] | None) -> tuple[int, int] | None:
    """Return a stable device/inode identity for one anonymous process pipe."""

    if stream is None or os.name != "posix":
        return None
    try:
        info = os.fstat(stream.fileno())
    except (OSError, ValueError):
        return None
    if not stat.S_ISFIFO(info.st_mode):
        return None
    return (int(info.st_dev), int(info.st_ino))


def _process_pipe_ids(proc: subprocess.Popen[bytes]) -> frozenset[tuple[int, int]]:
    """Return the POSIX identities of stdin/stdout/stderr pipes owned by ``proc``."""

    identities = {
        identity
        for identity in (
            _pipe_id(proc.stdin),
            _pipe_id(proc.stdout),
            _pipe_id(proc.stderr),
        )
        if identity is not None
    }
    return frozenset(identities)


def _linux_pipe_holder_discovery_available(
    pipe_ids: frozenset[tuple[int, int]],
) -> bool:
    """Return whether exact Linux capture-pipe discovery is usable."""

    return (
        os.name == "posix"
        and bool(pipe_ids)
        and (Path("/proc") / "self" / "fd").is_dir()
    )


def _linux_pipe_holder_pids(
    pipe_ids: frozenset[tuple[int, int]],
) -> tuple[int, ...]:
    """Find Linux processes that still hold one of Micromax's capture pipes.

    This is an exceptional cleanup path, not a process registry.  It runs only
    after the direct process has exited or been killed while an I/O thread still
    lacks EOF.  Anonymous pipe identity is stronger evidence than ancestry at
    that point: a child can create a new session and be reparented before the
    parent polls ``/proc``, but it cannot keep a capture reader blocked without
    retaining the exact pipe object.
    """

    proc_root = Path("/proc")
    if not _linux_pipe_holder_discovery_available(pipe_ids):
        return ()

    protected = {os.getpid(), os.getppid()}
    holders: set[int] = set()
    try:
        processes = os.scandir(proc_root)
    except OSError:
        return ()
    with processes:
        for process_dir in processes:
            if not process_dir.name.isdigit():
                continue
            pid = int(process_dir.name)
            if pid <= 0 or pid in protected:
                continue
            if _pid_holds_pipe_ids(pid, pipe_ids):
                holders.add(pid)
    return tuple(sorted(holders, reverse=True))


def _pid_holds_pipe_ids(
    pid: int,
    pipe_ids: frozenset[tuple[int, int]],
) -> bool:
    """Return whether ``pid`` currently retains an exact capture pipe."""

    if pid <= 0 or pid in {os.getpid(), os.getppid()} or not pipe_ids:
        return False
    try:
        descriptors = os.scandir(Path("/proc") / str(pid) / "fd")
    except OSError:
        return False
    with descriptors:
        for descriptor in descriptors:
            try:
                info = descriptor.stat(follow_symlinks=True)
            except OSError:
                continue
            if stat.S_ISFIFO(info.st_mode) and (
                int(info.st_dev),
                int(info.st_ino),
            ) in pipe_ids:
                return True
    return False


def _linux_pid_start_time(pid: int) -> str | None:
    """Return Linux procfs start-time identity for ``pid`` when available."""

    if pid <= 0:
        return None
    try:
        raw = (Path("/proc") / str(pid) / "stat").read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    # The second field is a parenthesized command and may itself contain
    # spaces or parentheses.  Split only after its final closing parenthesis;
    # starttime is field 22, hence tail index 19 when tail begins at state (3).
    close = raw.rfind(")")
    if close < 0:
        return None
    tail = raw[close + 1 :].split()
    if len(tail) <= 19:
        return None
    value = str(tail[19]).strip()
    return value or None


def _signal_pipe_holder_pid(
    pid: int,
    sig: int,
    *,
    pipe_ids: frozenset[tuple[int, int]],
) -> bool:
    """Signal one exact Linux pipe holder with the best available identity.

    ``/proc`` identifies the resource owner, but a numeric PID can be recycled
    after discovery.  When Python and the kernel expose pidfds, open one and
    revalidate pipe ownership before signalling that process identity.  Older
    Linux kernels fall back to repeated capture-pipe plus process-start-time
    validation immediately before ``kill``; that is narrower than ancestry-only
    signalling but remains a best-effort race boundary rather than a pidfd claim.
    """

    start_time = _linux_pid_start_time(int(pid))
    if start_time is None or not _pid_holds_pipe_ids(int(pid), pipe_ids):
        return False

    pidfd_open = getattr(os, "pidfd_open", None)
    pidfd_send_signal = getattr(signal, "pidfd_send_signal", None)
    if callable(pidfd_open) and callable(pidfd_send_signal):
        try:
            pidfd = int(pidfd_open(int(pid), 0))
        except (OSError, ProcessLookupError, TypeError, ValueError):
            pidfd = -1
        if pidfd >= 0:
            try:
                if (
                    _linux_pid_start_time(int(pid)) != start_time
                    or not _pid_holds_pipe_ids(int(pid), pipe_ids)
                ):
                    return False
                try:
                    pidfd_send_signal(pidfd, int(sig), None, 0)
                except (OSError, ProcessLookupError, TypeError, ValueError):
                    return False
                return True
            finally:
                with suppress(OSError):
                    os.close(pidfd)

    if (
        _linux_pid_start_time(int(pid)) != start_time
        or not _pid_holds_pipe_ids(int(pid), pipe_ids)
        or _linux_pid_start_time(int(pid)) != start_time
    ):
        return False
    try:
        os.kill(int(pid), int(sig))
    except (OSError, ProcessLookupError, TypeError, ValueError):
        return False
    return True


def _signal_pipe_holder_pids(
    pids: tuple[int, ...],
    sig: int,
    *,
    pipe_ids: frozenset[tuple[int, int]],
) -> bool:
    """Signal only exact pipe-holder process identities."""

    delivered = False
    for pid in pids:
        if _signal_pipe_holder_pid(pid, sig, pipe_ids=pipe_ids):
            delivered = True
    return delivered


def _signal_pipe_holders(
    pipe_ids: frozenset[tuple[int, int]], sig: int
) -> bool:
    """Signal Linux processes retaining exact pipes; report successful delivery."""

    if os.name != "posix":
        return False
    return _signal_pipe_holder_pids(
        _linux_pipe_holder_pids(pipe_ids),
        sig,
        pipe_ids=pipe_ids,
    )


def _terminate_lingering_capture_owners(
    proc: subprocess.Popen[bytes],
    *,
    pgid: int | None,
    pipe_ids: frozenset[tuple[int, int]],
) -> None:
    """Release inherited pipes after the direct child has stopped.

    A command can exit successfully after starting a background descendant that
    still owns stdout, stderr, or the read end of stdin.  Pipe EOF then never
    arrives and daemon I/O threads accumulate.  On Linux, signal only stable
    process identities that still retain the exact anonymous pipe object; use
    the confirmed POSIX group only where exact discovery is unavailable.  A
    genuinely detached child that redirected all standard descriptors never
    reaches this path and is left alive.
    """

    if _linux_pipe_holder_discovery_available(pipe_ids):
        # Exact pipe ownership is narrower than process-group membership.  A
        # launched group may also contain a sibling that deliberately redirected
        # all standard descriptors; do not kill that independent effect merely
        # because another sibling retained a capture pipe.  Once exact discovery
        # is available, an empty or raced-away holder set is evidence to stop,
        # not authority to broaden teardown to the whole group.
        holders = _linux_pipe_holder_pids(pipe_ids)
        if holders:
            _signal_pipe_holder_pids(
                holders,
                signal.SIGTERM,
                pipe_ids=pipe_ids,
            )
            time.sleep(_CAPTURE_TREE_TERM_GRACE_SECONDS)
            _signal_pipe_holders(pipe_ids, _FORCE_KILL_SIGNAL)
        return

    _signal_process_tree_or_child(proc, signal.SIGTERM, pgid=pgid)
    time.sleep(_CAPTURE_TREE_TERM_GRACE_SECONDS)
    _signal_process_tree_or_child(proc, _FORCE_KILL_SIGNAL, pgid=pgid)


def _capture_started_process(
    proc: subprocess.Popen[bytes],
    *,
    stdin_bytes: bytes | None,
    timeout_value: float,
    deadline: float,
    output_limit: int | None,
    label: str,
    output_budget_name: str,
) -> _CapturedProcessResult:
    """Capture one started child while retaining every teardown handle."""

    threads: list[threading.Thread] = []
    pgid: int | None = None
    pipe_ids: frozenset[tuple[int, int]] = frozenset()
    try:
        pgid = _confirmed_child_process_group_id(proc)
        pipe_ids = _process_pipe_ids(proc)
        return _capture_started_process_body(
            proc,
            threads=threads,
            pgid=pgid,
            pipe_ids=pipe_ids,
            stdin_bytes=stdin_bytes,
            timeout_value=timeout_value,
            deadline=deadline,
            output_limit=output_limit,
            label=label,
            output_budget_name=output_budget_name,
        )
    except BaseException:
        # Keep thread handles in the same owner as the child.  A signal or
        # startup failure after only some readers began must not demote them to
        # anonymous daemon threads while the outer wrapper cleans only Popen.
        _cleanup_interrupted_capture(
            proc,
            threads=threads,
            pgid=pgid,
            pipe_ids=pipe_ids,
        )
        raise


def _capture_started_process_body(
    proc: subprocess.Popen[bytes],
    *,
    threads: list[threading.Thread],
    pgid: int | None,
    pipe_ids: frozenset[tuple[int, int]],
    stdin_bytes: bytes | None,
    timeout_value: float,
    deadline: float,
    output_limit: int | None,
    label: str,
    output_budget_name: str,
) -> _CapturedProcessResult:
    capture = _BoundedPipeCapture(max_bytes=output_limit)
    if proc.stdout is not None:
        threads.append(
            threading.Thread(
                target=_reader,
                args=(proc.stdout, capture, "stdout"),
                name="micromax-process-stdout",
                daemon=True,
            )
        )
    if proc.stderr is not None:
        threads.append(
            threading.Thread(
                target=_reader,
                args=(proc.stderr, capture, "stderr"),
                name="micromax-process-stderr",
                daemon=True,
            )
        )
    if stdin_bytes is not None and proc.stdin is not None:
        threads.append(
            threading.Thread(
                target=_stdin_writer,
                args=(proc.stdin, stdin_bytes),
                name="micromax-process-stdin",
                daemon=True,
            )
        )
    for thread in threads:
        thread.start()

    timed_out = False
    output_truncated = False
    while proc.poll() is None:
        if capture.is_truncated():
            output_truncated = True
            terminate_process_tree(
                proc,
                pgid=pgid,
                timeout=_CAPTURE_TREE_TERM_GRACE_SECONDS,
            )
            break
        if time.monotonic() >= deadline:
            timed_out = True
            terminate_process_tree(
                proc,
                pgid=pgid,
                timeout=_CAPTURE_TREE_TERM_GRACE_SECONDS,
            )
            break
        time.sleep(0.01)

    if proc.poll() is None:
        terminate_process_tree(
            proc,
            pgid=pgid,
            timeout=_CAPTURE_TREE_TERM_GRACE_SECONDS,
        )

    drain_deadline = min(
        deadline,
        time.monotonic() + _CAPTURE_DRAIN_GRACE_SECONDS,
    )
    survivors = _join_threads_until(threads, deadline=drain_deadline)
    if survivors:
        _terminate_lingering_capture_owners(proc, pgid=pgid, pipe_ids=pipe_ids)
        _join_threads_until(
            survivors,
            deadline=time.monotonic() + _CAPTURE_DRAIN_GRACE_SECONDS,
        )
    _close_process_streams(proc)
    try:
        returncode = int(
            proc.returncode if proc.returncode is not None else proc.wait(timeout=0.1)
        )
    except Exception:
        returncode = 124 if timed_out else 125 if output_truncated else 127

    output_truncated = output_truncated or capture.is_truncated()
    stdout = _decode(capture.stdout)
    stderr = _decode(capture.stderr)
    if timed_out:
        return _CapturedProcessResult(
            124,
            stdout,
            _with_diagnostic(stderr, f"{label}: timed out after {timeout_value:.3g}s"),
            timed_out=True,
            output_truncated=output_truncated,
        )
    if output_truncated:
        rendered_limit = "disabled" if output_limit is None else f"{output_limit} bytes"
        return _CapturedProcessResult(
            125,
            stdout,
            _with_diagnostic(
                stderr,
                f"{label}: output exceeded {output_budget_name} {rendered_limit}",
            ),
            output_truncated=True,
        )
    return _CapturedProcessResult(returncode, stdout, stderr)


def _close_process_streams(proc: subprocess.Popen[bytes]) -> None:
    """Close every parent-side standard stream without assuming completion."""

    for stream in (proc.stdin, proc.stdout, proc.stderr):
        if stream is None:
            continue
        with suppress(Exception):
            stream.close()


def _cleanup_interrupted_capture(
    proc: subprocess.Popen[bytes],
    *,
    threads: list[threading.Thread],
    pgid: int | None,
    pipe_ids: frozenset[tuple[int, int]],
) -> None:
    """Best-effort process, pipe, and partial-thread cleanup on interruption."""

    with suppress(BaseException):
        terminate_process_tree(
            proc,
            pgid=pgid,
            timeout=_CAPTURE_TREE_TERM_GRACE_SECONDS,
        )
    survivors = list(threads)
    with suppress(BaseException):
        survivors = _join_threads_until(
            threads,
            deadline=time.monotonic() + _CAPTURE_DRAIN_GRACE_SECONDS,
        )
    if survivors:
        with suppress(BaseException):
            _terminate_lingering_capture_owners(
                proc,
                pgid=pgid,
                pipe_ids=pipe_ids,
            )
    with suppress(BaseException):
        _close_process_streams(proc)
    with suppress(BaseException):
        _join_threads_until(
            survivors,
            deadline=time.monotonic() + _CAPTURE_DRAIN_GRACE_SECONDS,
        )
    with suppress(BaseException):
        proc.wait(timeout=_CAPTURE_TREE_TERM_GRACE_SECONDS)


def _cleanup_abandoned_popen(proc: subprocess.Popen[bytes]) -> None:
    """Reclaim a process whose constructor completed after caller timeout."""

    pgid = _confirmed_child_process_group_id(proc)
    pipe_ids = _process_pipe_ids(proc)
    terminate_process_tree(
        proc,
        pgid=pgid,
        timeout=_CAPTURE_TREE_TERM_GRACE_SECONDS,
    )
    if pipe_ids:
        _terminate_lingering_capture_owners(proc, pgid=pgid, pipe_ids=pipe_ids)
    _close_process_streams(proc)
    with suppress(Exception):
        proc.wait(timeout=_CAPTURE_TREE_TERM_GRACE_SECONDS)


def _run_captured_process(
    popen_factory: Callable[[], subprocess.Popen[bytes]],
    *,
    stdin_bytes: bytes | None,
    timeout_value: float,
    output_limit: int | None,
    label: str,
    output_budget_name: str,
) -> _CapturedProcessResult:
    """Own constructor, execution, capture, and teardown under one deadline."""

    deadline = time.monotonic() + timeout_value
    try:
        proc = start_subprocess_with_deadline(
            popen_factory,
            cleanup=_cleanup_abandoned_popen,
            deadline=deadline,
            timeout_seconds=timeout_value,
            operation=label,
        )
    except SubprocessStartTimeoutError as exc:
        return _CapturedProcessResult(
            124,
            "",
            str(exc),
            timed_out=True,
        )
    except SubprocessStartError as exc:
        return _CapturedProcessResult(127, "", str(exc))

    try:
        return _capture_started_process(
            proc,
            stdin_bytes=stdin_bytes,
            timeout_value=timeout_value,
            deadline=deadline,
            output_limit=output_limit,
            label=label,
            output_budget_name=output_budget_name,
        )
    except BaseException:
        # Constructor ownership has transferred, but capture may still fail or
        # be interrupted before its own teardown path is active.  Keep that
        # handoff exact: no exception can leave a started child or pipe owner
        # behind in this wrapper.
        with suppress(BaseException):
            _cleanup_abandoned_popen(proc)
        raise


def run_argv_bounded(
    argv: list[str],
    *,
    input_text: str | None = None,
    timeout_seconds: float = 1.0,
    max_output_bytes: int | None = 100_000,
    label: str = "process",
) -> BoundedProcessResult:
    """Run an argv command with timeout, process-tree teardown, and output caps.

    This is the non-shell sibling of ``run_shell_command_bounded``.  It is used
    for trusted editor integrations such as external clipboard tools where the
    command is an argv vector, not user shell text.  Return code ``124`` means
    timeout, ``125`` means combined stdout/stderr capture exceeded the byte
    budget, and ``127`` means startup failed.
    """

    args = [str(part) for part in list(argv or [])]
    if not args:
        return BoundedProcessResult(127, "", f"{label}: empty argv")

    timeout_value = _finite_timeout_seconds(timeout_seconds, default=1.0)
    limit = _output_byte_limit(max_output_bytes, default=100_000)
    stdin_bytes = None
    if input_text is not None:
        stdin_bytes = str(input_text).encode("utf-8", errors="replace")

    captured = _run_captured_process(
        lambda: subprocess.Popen(
            args,
            stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            **_process_group_kwargs(),
        ),
        stdin_bytes=stdin_bytes,
        timeout_value=timeout_value,
        output_limit=limit,
        label=str(label),
        output_budget_name="process output budget",
    )
    return BoundedProcessResult(
        captured.returncode,
        captured.stdout,
        captured.stderr,
        timed_out=captured.timed_out,
        output_truncated=captured.output_truncated,
    )


def run_shell_command_bounded(
    command: str,
    *,
    timeout_seconds: float = 5.0,
    max_output_bytes: int | None = 262_144,
) -> ShellCommandResult:
    """Run ``command`` through the shell with timeout and output caps.

    The returned stderr carries the budget/timeout diagnostic while preserving
    any stderr bytes captured before teardown.  Return code ``124`` means wall
    timeout; ``125`` means the combined stdout/stderr capture exceeded the byte
    budget.  Other process failures use the child return code or ``127`` when
    process creation itself fails.
    """

    timeout_value = _finite_timeout_seconds(timeout_seconds, default=5.0)
    limit = _output_byte_limit(max_output_bytes, default=262_144)
    captured = _run_captured_process(
        lambda: subprocess.Popen(
            str(command),
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            **_process_group_kwargs(),
        ),
        stdin_bytes=None,
        timeout_value=timeout_value,
        output_limit=limit,
        label="ed.shell",
        output_budget_name="shell output budget",
    )
    return ShellCommandResult(
        captured.returncode,
        captured.stdout,
        captured.stderr,
        timed_out=captured.timed_out,
        output_truncated=captured.output_truncated,
    )
