"""Finite ownership for synchronous :class:`subprocess.Popen` construction.

Python's subprocess timeouts begin only after ``Popen(...)`` has returned, and
CPython documents that initial process creation cannot be interrupted on many
platform APIs.  Micromax therefore hands one constructor call to a temporary
starter thread, applies one absolute deadline across the single-pending gate and
the constructor, and transfers cleanup of any late process to that starter.

This is a circuit breaker around construction, not a process pool or launcher
service.  A platform call that never returns can retain one daemon starter; later
callers still return within their own deadlines instead of accumulating threads.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from contextlib import suppress
from typing import Generic, TypeVar

_ProcessT = TypeVar("_ProcessT")
_SUBPROCESS_START_GATE = threading.Lock()


class SubprocessStartError(RuntimeError):
    """Raised when a deadline-owned subprocess constructor cannot complete."""


class SubprocessStartTimeoutError(SubprocessStartError, TimeoutError):
    """Raised when subprocess construction does not finish by its deadline."""


class _SubprocessStartAttempt(Generic[_ProcessT]):
    """One temporary constructor owner with an exact late-cleanup handoff."""

    def __init__(
        self,
        factory: Callable[[], _ProcessT],
        cleanup: Callable[[_ProcessT], None],
        *,
        operation: str,
        deadline: float,
        timeout_seconds: float,
    ) -> None:
        self._factory = factory
        self._cleanup = cleanup
        self._operation = str(operation or "subprocess")
        self._deadline = float(deadline)
        self._timeout_seconds = float(timeout_seconds)
        self._done = threading.Event()
        self._state_lock = threading.Lock()
        self._caller_owns = True
        self._process: _ProcessT | None = None
        self._failure: BaseException | None = None
        self._completed_at: float | None = None

    @property
    def caller_owns_resources(self) -> bool:
        with self._state_lock:
            return bool(self._caller_owns)

    def _cleanup_process(self, process: _ProcessT | None) -> None:
        if process is None:
            return
        with suppress(BaseException):
            self._cleanup(process)
        # Cleanup runs only for an abandoned constructor.  There is no caller
        # left to receive a cleanup exception, and the gate must be released
        # even when platform teardown itself is defective.

    def _abandon_if_pending(self) -> _ProcessT | None:
        """Transfer a pending attempt, or return an already-owned process."""

        with self._state_lock:
            if self._completed_at is None:
                self._caller_owns = False
                return None
            if not self._caller_owns:
                return None
            self._caller_owns = False
            return self._process

    def _classify_completion(self) -> tuple[float | None, BaseException | None, _ProcessT | None]:
        """Return immutable completion state and hand pending work to starter."""

        with self._state_lock:
            completed_at = self._completed_at
            if completed_at is None:
                self._caller_owns = False
            return completed_at, self._failure, self._process

    def _run(self) -> None:
        process: _ProcessT | None = None
        failure: BaseException | None = None
        try:
            process = self._factory()
        except BaseException as exc:
            failure = exc

        completed_at = time.monotonic()
        with self._state_lock:
            self._process = process
            self._failure = failure
            self._completed_at = completed_at
            # A constructor that returned after the absolute deadline never
            # becomes caller-owned, even if Event.wait lost a scheduling race.
            if completed_at > self._deadline:
                self._caller_owns = False
            abandoned = not self._caller_owns
            self._done.set()

        try:
            if abandoned:
                self._cleanup_process(process)
        finally:
            _SUBPROCESS_START_GATE.release()

    def wait(self) -> _ProcessT:
        gate_wait = max(0.0, self._deadline - time.monotonic())
        if not _SUBPROCESS_START_GATE.acquire(timeout=gate_wait):
            raise SubprocessStartTimeoutError(
                f"{self._operation} startup timed out after "
                f"{self._timeout_seconds:.3g}s waiting for an earlier "
                "unresolved subprocess start"
            )

        if time.monotonic() >= self._deadline:
            _SUBPROCESS_START_GATE.release()
            raise SubprocessStartTimeoutError(
                f"{self._operation} startup timed out after "
                f"{self._timeout_seconds:.3g}s waiting for an earlier "
                "unresolved subprocess start"
            )

        starter: threading.Thread | None = None
        try:
            starter = threading.Thread(
                target=self._run,
                name="micromax-subprocess-start",
                daemon=True,
            )
            starter.start()
        except BaseException as exc:
            # Thread.start() normally fails before a native thread exists.  If
            # an asynchronous interruption lands while start() is publishing
            # the native thread, ``ident`` can still be unavailable.  Treat an
            # interrupt as uncertain ownership and conservatively leave the
            # gate to the possible starter; ordinary start failures can release
            # it only when no native identity was published.
            uncertain_start = isinstance(exc, (KeyboardInterrupt, SystemExit))
            started_thread = starter is not None and starter.ident is not None
            if uncertain_start or started_thread:
                process = self._abandon_if_pending()
                self._cleanup_process(process)
            else:
                _SUBPROCESS_START_GATE.release()
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            raise SubprocessStartError(
                f"{self._operation} subprocess starter could not run: {exc}"
            ) from exc

        remaining = max(0.0, self._deadline - time.monotonic())
        try:
            self._done.wait(remaining)

            completed_at, failure, process = self._classify_completion()
            if completed_at is None or completed_at > self._deadline:
                raise SubprocessStartTimeoutError(
                    f"{self._operation} startup timed out after "
                    f"{self._timeout_seconds:.3g}s"
                )
            if failure is not None:
                if isinstance(failure, (KeyboardInterrupt, SystemExit)):
                    raise failure
                raise SubprocessStartError(
                    f"{self._operation} subprocess could not start: {failure}"
                ) from failure
            if process is None:
                raise SubprocessStartError(
                    f"{self._operation} subprocess constructor returned no process"
                )
            return process
        except BaseException:
            # The starter stops owning an on-time process as soon as it records
            # completion.  Keep the entire wait/classification/return sequence
            # under one interruption handler so a signal or injected exception
            # in that handoff window cannot orphan the completed child.
            process = self._abandon_if_pending()
            self._cleanup_process(process)
            raise


def start_subprocess_with_deadline(
    factory: Callable[[], _ProcessT],
    *,
    cleanup: Callable[[_ProcessT], None],
    deadline: float,
    timeout_seconds: float,
    operation: str,
) -> _ProcessT:
    """Run one synchronous constructor under a finite single-pending owner.

    ``deadline`` is absolute monotonic time so callers can share it with later
    readiness or execution work.  ``timeout_seconds`` is retained only for a
    stable diagnostic.  On timeout before completion, the starter exclusively
    owns any process that appears later and runs ``cleanup`` before releasing the
    one-pending gate.
    """

    attempt = _SubprocessStartAttempt(
        factory,
        cleanup,
        operation=operation,
        deadline=float(deadline),
        timeout_seconds=float(timeout_seconds),
    )
    return attempt.wait()
