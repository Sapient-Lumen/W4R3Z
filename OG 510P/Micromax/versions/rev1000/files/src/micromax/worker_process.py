"""Per-operation multiprocessing contexts for killable Micromax workers.

Micromax owns a multithreaded TUI. Cloning that live process with ``fork`` can
inherit locks whose owning thread does not exist in the child. Keep worker
selection local instead of changing the embedding application's global start
method, and prefer ``spawn`` so the worker never depends on a forkserver whose
own interpreter startup may have loaded native libraries that created threads.
``forkserver`` remains a secondary choice for hosts where ``spawn`` is absent.
Process construction and ``start()`` are handed to one deadline-owned starter
thread.  That makes a POSIX ``fork`` fallback self-defeating—the caller waiting
beside the starter is already another live thread—so bounded workers now fail
closed when no spawn-style context can reconstruct the entrypoint.
"""

from __future__ import annotations

import io
import math
import multiprocessing
import pickle
import select
import socket
import struct
import sys
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

ISOLATED_START_METHODS = ("spawn", "forkserver")
DEFAULT_WORKER_RESULT_MAX_BYTES = 64 * 1024 * 1024
DEFAULT_WORKER_START_TIMEOUT_SECONDS = 5.0
_WORKER_RESULT_MAGIC = b"MXW1"
_WORKER_RESULT_HEADER = struct.Struct("!4sQ")
_WORKER_RESULT_READ_CHUNK = 64 * 1024
_WORKER_START_GATE = threading.Lock()


class WorkerContextUnavailableError(RuntimeError):
    """Raised when no safe/importable worker start method is available."""


class WorkerResultError(RuntimeError):
    """Base error for one-shot worker result transport/lifecycle failures."""


class WorkerResultStartError(WorkerResultError):
    """Raised when a one-shot result worker cannot be started."""


class WorkerResultTimeoutError(WorkerResultError):
    """Raised when a one-shot worker does not publish a complete result in time."""


class WorkerResultStartTimeoutError(
    WorkerResultStartError,
    WorkerResultTimeoutError,
):
    """Raised when construction/start does not finish within its own deadline."""


class WorkerResultProtocolError(WorkerResultError):
    """Raised when a worker closes or corrupts its one allowed result frame."""


class WorkerResultTooLargeError(WorkerResultProtocolError):
    """Raised before allocating or accepting a result beyond the channel budget."""


class WorkerResultProcessError(WorkerResultError):
    """Raised when a result-producing worker fails its required exit postcondition."""


def normalize_worker_result_max_bytes(
    value: object,
    *,
    default: int = DEFAULT_WORKER_RESULT_MAX_BYTES,
) -> int:
    """Return a positive finite byte ceiling for one serialized worker result."""

    fallback = int(default)
    if fallback <= 0:
        raise ValueError("worker result byte default must be positive")
    if isinstance(value, bool):
        return fallback
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return fallback
    if parsed <= 0:
        return fallback
    return parsed


class WorkerResultSender:
    """Picklable child endpoint for exactly one bounded result frame.

    The worker serializes before publishing so a pickle/size failure can still
    be converted by the caller's existing ``try/except`` into a small terminal
    error row. Once frame transmission begins, a second publication is refused:
    after a partial write there is no safe message boundary to reuse.
    """

    def __init__(self, sock: socket.socket, *, max_bytes: int) -> None:
        self._socket = sock
        self._max_bytes = normalize_worker_result_max_bytes(max_bytes)
        self._attempted = False
        self._closed = False

    @property
    def max_bytes(self) -> int:
        return int(self._max_bytes)

    def fileno(self) -> int:
        return int(self._socket.fileno())

    def put(self, value: object) -> None:
        """Serialize and publish one result, matching the old Queue target API."""

        if self._closed:
            raise WorkerResultProtocolError("worker result sender is closed")
        if self._attempted:
            raise WorkerResultProtocolError("worker result sender already published")
        payload = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        if len(payload) > self._max_bytes:
            raise WorkerResultTooLargeError(
                "serialized worker result exceeds channel budget "
                f"({len(payload)} > {self._max_bytes} bytes)"
            )
        self._attempted = True
        try:
            self._socket.sendall(
                _WORKER_RESULT_HEADER.pack(_WORKER_RESULT_MAGIC, len(payload))
            )
            if payload:
                self._socket.sendall(payload)
        finally:
            self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._socket.close()
        except OSError:
            pass


@dataclass(slots=True)
class WorkerResultChannel:
    """Parent receiver plus the child endpoint passed to one Process target."""

    receiver: socket.socket
    sender: WorkerResultSender
    max_bytes: int

    def close_parent_sender(self) -> None:
        """Drop the parent's sender copy after Process.start transferred it."""

        self.sender.close()

    def close(self) -> None:
        self.sender.close()
        try:
            self.receiver.close()
        except OSError:
            pass


def create_worker_result_channel(
    *,
    max_bytes: object = DEFAULT_WORKER_RESULT_MAX_BYTES,
) -> WorkerResultChannel:
    """Return a one-producer, one-consumer result channel without a feeder thread.

    ``socketpair`` is used rather than ``multiprocessing.Queue`` because the
    parent can incrementally read a private frame under its own deadline. A
    killed/crashed worker can therefore leave only a bounded partial bytearray,
    never trap the caller inside ``Queue.get(timeout=...)`` after the queue's
    readiness check has already consumed a forged/incomplete length prefix.
    """

    limit = normalize_worker_result_max_bytes(max_bytes)
    receiver, child = socket.socketpair()
    receiver.setblocking(False)
    child.setblocking(True)
    return WorkerResultChannel(
        receiver=receiver,
        sender=WorkerResultSender(child, max_bytes=limit),
        max_bytes=limit,
    )


class _DeferredWorkerProcess:
    """Construct the real ``multiprocessing.Process`` inside the start owner.

    ``BaseContext.Process(...)`` is ordinarily cheap, but it is still executable
    platform/library code and previously happened before any deadline.  The
    wrapper keeps the public worker factory shape while moving both construction
    and ``Process.start()`` into the same single-owner handoff.  After the start
    event, only the caller *or* the abandoned-start cleanup thread touches the
    underlying process, never both.
    """

    def __init__(
        self,
        context: multiprocessing.context.BaseContext,
        *,
        target: Callable[..., object],
        args: tuple[object, ...],
        daemon: bool,
    ) -> None:
        self._context = context
        self._target = target
        self._args = args
        self._daemon = bool(daemon)
        self._process: multiprocessing.Process | None = None
        self._closed = False
        try:
            self.start_method = str(context.get_start_method())
        except Exception:
            self.start_method = ""

    def start(self) -> None:
        if self._closed:
            raise ValueError("worker process plan is closed")
        if self._process is not None:
            raise AssertionError("cannot start a worker process twice")
        process = self._context.Process(
            target=self._target,
            args=self._args,
            daemon=self._daemon,
        )
        # Retain a partially launched Process so the single owner can still
        # reclaim it when ``start()`` raises after platform resources exist.
        self._process = process
        process.start()

    @property
    def pid(self) -> int | None:
        process = self._process
        if process is None:
            return None
        try:
            raw = process.pid
            return None if raw is None else int(raw)
        except Exception:
            return None

    @property
    def exitcode(self) -> int | None:
        process = self._process
        if process is None:
            return None
        try:
            raw = process.exitcode
            return None if raw is None else int(raw)
        except Exception:
            return None

    def is_alive(self) -> bool:
        process = self._process
        if process is None:
            return False
        return bool(process.is_alive())

    def terminate(self) -> None:
        process = self._process
        if process is not None:
            process.terminate()

    def kill(self) -> None:
        process = self._process
        if process is not None:
            process.kill()

    def join(self, timeout: float | None = None) -> None:
        process = self._process
        if process is not None:
            process.join(timeout=timeout)

    def close(self) -> None:
        if self._closed:
            return
        process = self._process
        if process is not None:
            process.close()
        self._closed = True


def create_one_shot_worker(
    context: multiprocessing.context.BaseContext,
    *,
    target: Callable[..., object],
    args: Iterable[object] = (),
    daemon: bool = True,
    max_result_bytes: object = DEFAULT_WORKER_RESULT_MAX_BYTES,
) -> tuple[_DeferredWorkerProcess, WorkerResultChannel]:
    """Plan one result-producing Process without running constructor code yet.

    Every bounded Micromax worker has the same shape: ordinary positional
    inputs followed by one private result sender.  The real Process constructor
    and ``start()`` both run later inside the deadline-owned starter, preventing
    either phase from freezing the editor thread.  Keeping the plan here also
    makes it harder for a new worker family to revive Queue feeder threads or an
    unbounded receive path.
    """

    channel = create_worker_result_channel(max_bytes=max_result_bytes)
    process = _DeferredWorkerProcess(
        context,
        target=target,
        args=(*tuple(args), channel.sender),
        daemon=bool(daemon),
    )
    return process, channel


_WorkerProcess = multiprocessing.Process | _DeferredWorkerProcess


def _worker_is_alive(process: _WorkerProcess) -> bool:
    try:
        return bool(process.is_alive())
    except Exception:
        return False


def _read_worker_result_bytes(
    sock: socket.socket,
    *,
    timeout_seconds: float,
    operation: str,
    max_bytes: int,
) -> bytes:
    """Read one frame incrementally; every wait remains inside the deadline."""

    deadline = time.monotonic() + timeout_seconds
    header = bytearray()
    payload = bytearray()
    expected: int | None = None

    while True:
        if expected is not None and len(payload) == expected:
            return bytes(payload)

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise WorkerResultTimeoutError(
                f"{operation} timed out after {timeout_seconds:.3g}s"
            )
        try:
            readable, _, _ = select.select([sock], [], [], min(0.05, remaining))
        except InterruptedError:
            continue
        except (OSError, ValueError) as exc:
            raise WorkerResultProtocolError(
                f"{operation} worker result channel failed: {exc}"
            ) from exc
        if not readable:
            continue

        if expected is None:
            wanted = _WORKER_RESULT_HEADER.size - len(header)
        else:
            wanted = expected - len(payload)
        try:
            chunk = sock.recv(min(_WORKER_RESULT_READ_CHUNK, max(1, wanted)))
        except (BlockingIOError, InterruptedError):
            continue
        except OSError as exc:
            raise WorkerResultProtocolError(
                f"{operation} worker result channel failed: {exc}"
            ) from exc
        if not chunk:
            if not header and expected is None:
                raise WorkerResultProtocolError(
                    f"{operation} worker exited without result"
                )
            raise WorkerResultProtocolError(
                f"{operation} worker closed an incomplete result frame"
            )

        if expected is None:
            header.extend(chunk)
            if len(header) < _WORKER_RESULT_HEADER.size:
                continue
            if len(header) != _WORKER_RESULT_HEADER.size:
                raise WorkerResultProtocolError(
                    f"{operation} worker sent an invalid result header"
                )
            magic, declared = _WORKER_RESULT_HEADER.unpack(header)
            if magic != _WORKER_RESULT_MAGIC:
                raise WorkerResultProtocolError(
                    f"{operation} worker sent an unknown result protocol"
                )
            expected = int(declared)
            if expected <= 0:
                raise WorkerResultProtocolError(
                    f"{operation} worker sent an empty result frame"
                )
            if expected > max_bytes:
                raise WorkerResultTooLargeError(
                    f"{operation} worker result exceeds {max_bytes} bytes"
                )
            continue

        payload.extend(chunk)


def _decode_worker_result(payload: bytes, *, operation: str) -> object:
    """Decode exactly one trusted-worker pickle and reject trailing frame data."""

    stream = io.BytesIO(payload)
    try:
        value = pickle.Unpickler(stream).load()
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise WorkerResultProtocolError(
            f"{operation} worker result could not be decoded: {exc}"
        ) from exc
    if stream.tell() != len(payload):
        raise WorkerResultProtocolError(
            f"{operation} worker result contains trailing serialized data"
        )
    return value


def _run_worker_abnormal_cleanup(
    cleanup: Callable[[int | None], None] | None,
    worker_pid: int | None,
) -> None:
    if cleanup is None:
        return
    try:
        cleanup(worker_pid)
    except Exception:
        pass


def _worker_pid(process: _WorkerProcess) -> int | None:
    try:
        raw_pid = getattr(process, "pid", None)
        return None if raw_pid is None else int(raw_pid)
    except Exception:
        return None


def _worker_start_method(process: _WorkerProcess) -> str:
    raw = getattr(process, "start_method", None)
    if raw is None:
        raw = getattr(process, "_start_method", None)
    return str(raw or "").strip().lower()


class _WorkerStartAttempt:
    """Single-owner construction/start handoff with one unresolved-attempt cap.

    Python offers no operation that cancels another thread blocked in platform
    process creation.  The caller can nevertheless remain finite by transferring
    exclusive process/channel ownership to the starter when its deadline wins.
    The module gate stays held until that starter eventually returns and reclaims
    any late child, so retries cannot accumulate unbounded stuck threads or
    partially launched processes.
    """

    def __init__(
        self,
        process: _WorkerProcess,
        channel: WorkerResultChannel,
        *,
        operation: str,
        abnormal_cleanup: Callable[[int | None], None] | None,
    ) -> None:
        self._process = process
        self._channel = channel
        self._operation = operation
        self._abnormal_cleanup = abnormal_cleanup
        self._done = threading.Event()
        self._state_lock = threading.Lock()
        self._caller_owns = True
        self._failure: BaseException | None = None
        self._started = False
        self._worker_pid: int | None = None
        self._completed_at: float | None = None

    @property
    def caller_owns_resources(self) -> bool:
        with self._state_lock:
            return bool(self._caller_owns)

    def _transfer_cleanup_if_pending(self) -> bool:
        with self._state_lock:
            if self._done.is_set():
                return False
            self._caller_owns = False
            return True

    def _completed_within(self, deadline: float) -> bool:
        """Classify startup against one absolute deadline and hand off if late."""

        with self._state_lock:
            completed_at = self._completed_at
            if completed_at is not None and completed_at <= deadline:
                return True
            if completed_at is None:
                self._caller_owns = False
            return False

    def _cleanup_abandoned_start(self) -> None:
        # ``start()`` has returned, so the child has either received its sender
        # or construction failed.  This starter remains the only resource owner.
        try:
            self._channel.close_parent_sender()
        except Exception:
            pass
        if _worker_is_alive(self._process):
            terminate_worker_process(self._process)
        _run_worker_abnormal_cleanup(
            self._abnormal_cleanup,
            self._worker_pid,
        )
        self._channel.close()
        try:
            self._process.close()
        except Exception:
            pass

    def _run(self) -> None:
        failure: BaseException | None = None
        started = False
        worker_pid: int | None = None
        try:
            self._process.start()
            started = True
            worker_pid = _worker_pid(self._process)
        except BaseException as exc:
            failure = exc
            worker_pid = _worker_pid(self._process)

        completed_at = time.monotonic()
        with self._state_lock:
            self._failure = failure
            self._started = started
            self._worker_pid = worker_pid
            self._completed_at = completed_at
            abandoned = not self._caller_owns
            self._done.set()

        try:
            if abandoned:
                self._cleanup_abandoned_start()
        finally:
            _WORKER_START_GATE.release()

    def wait(self, *, timeout_seconds: float) -> int | None:
        method = _worker_start_method(self._process)
        if method == "fork":
            raise WorkerResultStartError(
                f"{self._operation} worker cannot use fork with a deadline-owned "
                "starter; use spawn/forkserver or disable the worker timeout"
            )

        deadline = time.monotonic() + timeout_seconds
        gate_wait = max(0.0, deadline - time.monotonic())
        if not _WORKER_START_GATE.acquire(timeout=gate_wait):
            raise WorkerResultStartTimeoutError(
                f"{self._operation} worker startup timed out after "
                f"{timeout_seconds:.3g}s waiting for an earlier unresolved start"
            )

        # Acquiring the gate and creating the small starter share the same budget
        # as Process construction/start.  Do not launch a process after a prior
        # unresolved start consumed the complete deadline.
        if time.monotonic() >= deadline:
            _WORKER_START_GATE.release()
            raise WorkerResultStartTimeoutError(
                f"{self._operation} worker startup timed out after "
                f"{timeout_seconds:.3g}s waiting for an earlier unresolved start"
            )

        starter: threading.Thread | None = None
        try:
            starter = threading.Thread(
                target=self._run,
                name="micromax-worker-start",
                daemon=True,
            )
            starter.start()
        except BaseException as exc:
            # Thread.start() normally raises before a native thread exists.  If an
            # asynchronous interruption lands after creation, transfer ownership
            # instead of racing the possibly running target or releasing its gate.
            started_thread = starter is not None and starter.ident is not None
            if started_thread:
                self._transfer_cleanup_if_pending()
            else:
                _WORKER_START_GATE.release()
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            raise WorkerResultStartError(
                f"{self._operation} worker starter could not run: {exc}"
            ) from exc

        remaining = max(0.0, deadline - time.monotonic())
        try:
            self._done.wait(remaining)
        except BaseException:
            self._transfer_cleanup_if_pending()
            raise

        # Event.wait() can lose a boundary race: the starter may publish just
        # after the wait expires but before this thread reacquires the state lock.
        # The starter's own completion timestamp is the authoritative witness.
        if not self._completed_within(deadline):
            raise WorkerResultStartTimeoutError(
                f"{self._operation} worker startup timed out after "
                f"{timeout_seconds:.3g}s"
            )

        with self._state_lock:
            failure = self._failure
            started = self._started
            worker_pid = self._worker_pid
        if failure is not None:
            if isinstance(failure, (KeyboardInterrupt, SystemExit)):
                raise failure
            raise WorkerResultStartError(
                f"{self._operation} worker could not start: {failure}"
            ) from failure
        if not started:
            raise WorkerResultStartError(
                f"{self._operation} worker did not complete startup"
            )
        return worker_pid



def collect_worker_result(
    process: _WorkerProcess,
    channel: WorkerResultChannel,
    *,
    timeout_seconds: object,
    operation: str,
    startup_timeout_seconds: object = DEFAULT_WORKER_START_TIMEOUT_SECONDS,
    join_timeout: object = 0.5,
    require_clean_exit: bool = False,
    abnormal_cleanup: Callable[[int | None], None] | None = None,
    after_start: Callable[[int | None], None] | None = None,
) -> object:
    """Own finite construction/start, frame receive, reap/kill, and release.

    Construction and ``start()`` run in one deadline-owned starter. If that
    deadline wins, exclusive cleanup transfers to the starter and the caller
    returns; one module gate prevents retries from accumulating unresolved start
    threads. ``after_start`` may perform one caller-owned, independently bounded
    target-readiness handshake after the child has received its resources and
    before the operation/result deadline begins. Once that boundary completes,
    no result read can outlive the normalized operation deadline—even if the child
    writes only a frame prefix, crashes during serialization, or is terminated
    while publishing. The socket endpoint is private to this one-shot owner, so
    forced teardown cannot corrupt a channel reused by another operation.
    """

    timeout = max(
        0.01,
        normalize_worker_timeout_seconds(timeout_seconds, default=5.0),
    )
    reap_timeout = max(
        0.0,
        normalize_worker_timeout_seconds(join_timeout, default=0.5),
    )
    startup_timeout = max(
        0.01,
        normalize_worker_timeout_seconds(
            startup_timeout_seconds,
            default=DEFAULT_WORKER_START_TIMEOUT_SECONDS,
        ),
    )
    label = str(operation or "worker operation")
    cleanup_ran = False
    worker_pid: int | None = None
    caller_owns_resources = True

    def abnormal() -> None:
        nonlocal cleanup_ran
        if cleanup_ran:
            return
        cleanup_ran = True
        _run_worker_abnormal_cleanup(abnormal_cleanup, worker_pid)

    try:
        start_attempt = _WorkerStartAttempt(
            process,
            channel,
            operation=label,
            abnormal_cleanup=abnormal_cleanup,
        )
        try:
            worker_pid = start_attempt.wait(timeout_seconds=startup_timeout)
        except BaseException:
            caller_owns_resources = start_attempt.caller_owns_resources
            raise
        # The child now owns its duplicated/transferred endpoint. Keeping the
        # parent's writer open would suppress EOF after a child crash.
        channel.close_parent_sender()

        try:
            if after_start is not None:
                after_start(worker_pid)
            encoded = _read_worker_result_bytes(
                channel.receiver,
                timeout_seconds=timeout,
                operation=label,
                max_bytes=channel.max_bytes,
            )
            payload = _decode_worker_result(encoded, operation=label)
        except BaseException:
            terminate_worker_process(process)
            abnormal()
            raise

        try:
            process.join(timeout=reap_timeout)
        except BaseException:
            terminate_worker_process(process)
            abnormal()
            raise
        if _worker_is_alive(process):
            terminate_worker_process(process)
            if require_clean_exit:
                abnormal()
                raise WorkerResultProcessError(
                    f"{label} worker returned a result but did not exit"
                )
        if require_clean_exit:
            try:
                exitcode = getattr(process, "exitcode", None)
            except Exception:
                exitcode = None
            if exitcode not in (None, 0):
                abnormal()
                raise WorkerResultProcessError(
                    f"{label} worker exited with status {exitcode} after returning a result"
                )
        return payload
    finally:
        if caller_owns_resources:
            # ``Process.start`` can fail after allocating or partially launching
            # platform resources.  Probe unconditionally: an unstarted real Process
            # simply reports no liveness through the defensive wrapper, while an
            # alternate context that did launch before raising is still reclaimed.
            if _worker_is_alive(process):
                if worker_pid is None:
                    worker_pid = _worker_pid(process)
                terminate_worker_process(process)
                abnormal()
            channel.close()
            try:
                process.close()
            except Exception:
                pass


def normalize_worker_timeout_seconds(
    value: object,
    *,
    default: float,
    none_disables: bool = False,
) -> float:
    """Return a finite worker timeout without erasing explicit direct mode.

    Worker wrappers commonly use ``None`` or a non-positive value to select an
    intentional in-process path.  NaN and infinity are never useful selectors:
    they poison deadline arithmetic or turn ``join`` into an accidental
    unbounded wait.  Preserve ``None`` only where the caller declares that it
    disables the worker; replace malformed, boolean, and non-finite values with
    the caller's documented finite default.
    """

    fallback = float(default)
    if not math.isfinite(fallback) or fallback <= 0:
        raise ValueError("worker timeout default must be finite and positive")
    if value is None and none_disables:
        return 0.0
    if isinstance(value, bool):
        return fallback
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return fallback
    if not math.isfinite(parsed):
        return fallback
    return float(parsed)


def main_module_is_importable() -> bool:
    """Return whether spawn-style workers can reload the current entrypoint.

    ``spawn`` and ``forkserver`` reconstruct the main module in the child.
    Shell snippets such as ``python -c`` and ``python -`` expose no real source
    path, so those methods fail before a package-level worker target can run.
    """

    main = sys.modules.get("__main__")
    raw = str(getattr(main, "__file__", "") or "").strip()
    if not raw or raw.startswith("<"):
        return False
    try:
        return Path(raw).is_file()
    except OSError:
        return False


def _context_for(method: str) -> multiprocessing.context.BaseContext | None:
    try:
        return multiprocessing.get_context(str(method))
    except Exception:
        return None


def isolated_worker_context(
    preferred: Iterable[str] = ISOLATED_START_METHODS,
) -> multiprocessing.context.BaseContext:
    """Return a safe per-operation multiprocessing context.

    Real module/script entrypoints prefer ``spawn``. ``forkserver`` is only a
    secondary choice because its server is allowed to load system libraries or
    preloaded imports that create threads before it calls ``fork``. A bounded
    start now necessarily uses a helper thread, so even an initially
    single-threaded ``python -c`` or REPL process cannot safely switch to POSIX
    ``fork``. Non-importable embeddings must pass a spawn-style context whose
    bootstrap they own or disable the operation timeout and use its direct path.
    """

    try:
        methods = set(multiprocessing.get_all_start_methods())
    except Exception:
        methods = set()

    if main_module_is_importable():
        for raw in preferred:
            method = str(raw or "").strip()
            if not method or method == "fork" or method not in methods:
                continue
            context = _context_for(method)
            if context is not None:
                return context

    if main_module_is_importable():
        context = _context_for(multiprocessing.get_start_method(allow_none=False))
        if context is not None and context.get_start_method() != "fork":
            return context

    raise WorkerContextUnavailableError(
        "no safe multiprocessing context is available: run from an importable "
        "module/script, pass worker_context explicitly, or use a non-positive timeout"
    )


def terminate_worker_process(
    process: _WorkerProcess,
    *,
    join_timeout: float = 0.2,
) -> None:
    """Best-effort terminate, then kill, one short-lived worker process.

    Process construction and startup can fail independently. Treat an unstarted
    or already-reaped process as finished so cleanup never masks the operation's
    original error.
    """

    try:
        alive = bool(process.is_alive())
    except Exception:
        return
    if not alive:
        return
    try:
        process.terminate()
    except Exception:
        pass
    try:
        process.join(
            timeout=max(
                0.0,
                normalize_worker_timeout_seconds(join_timeout, default=0.2),
            )
        )
    except Exception:
        return
    try:
        alive = bool(process.is_alive())
    except Exception:
        return
    if alive and hasattr(process, "kill"):
        try:
            process.kill()
        except Exception:
            pass
        try:
            process.join(
                timeout=max(
                    0.0,
                    normalize_worker_timeout_seconds(join_timeout, default=0.2),
                )
            )
        except Exception:
            pass

