from __future__ import annotations

import threading
import time

import pytest

from micromax import subprocess_start


class _Process:
    pass


def test_subprocess_start_returns_on_time_process_without_cleanup() -> None:
    process = _Process()
    cleaned: list[_Process] = []

    result = subprocess_start.start_subprocess_with_deadline(
        lambda: process,
        cleanup=cleaned.append,
        deadline=time.monotonic() + 1.0,
        timeout_seconds=1.0,
        operation="normal process",
    )

    assert result is process
    assert cleaned == []


def test_blocked_subprocess_constructor_times_out_and_late_process_is_cleaned() -> None:
    entered = threading.Event()
    release = threading.Event()
    cleaned = threading.Event()
    process = _Process()

    def factory() -> _Process:
        entered.set()
        release.wait(timeout=5.0)
        return process

    def cleanup(value: _Process) -> None:
        assert value is process
        cleaned.set()

    started = time.monotonic()
    try:
        with pytest.raises(
            subprocess_start.SubprocessStartTimeoutError,
            match="startup timed out",
        ):
            subprocess_start.start_subprocess_with_deadline(
                factory,
                cleanup=cleanup,
                deadline=time.monotonic() + 0.05,
                timeout_seconds=0.05,
                operation="blocked process",
            )
        assert time.monotonic() - started < 0.5
        assert entered.wait(timeout=0.5)
    finally:
        release.set()

    assert cleaned.wait(timeout=1.0)
    assert subprocess_start._SUBPROCESS_START_GATE.acquire(timeout=0.1)  # type: ignore[attr-defined]
    subprocess_start._SUBPROCESS_START_GATE.release()  # type: ignore[attr-defined]


def test_one_unresolved_subprocess_start_prevents_retry_thread_accumulation() -> None:
    entered = threading.Event()
    release = threading.Event()
    cleaned = threading.Event()
    second_calls: list[str] = []

    def first_factory() -> _Process:
        entered.set()
        release.wait(timeout=5.0)
        return _Process()

    try:
        with pytest.raises(subprocess_start.SubprocessStartTimeoutError):
            subprocess_start.start_subprocess_with_deadline(
                first_factory,
                cleanup=lambda _process: cleaned.set(),
                deadline=time.monotonic() + 0.05,
                timeout_seconds=0.05,
                operation="first blocked process",
            )
        assert entered.wait(timeout=0.5)

        def second_factory() -> _Process:
            second_calls.append("called")
            return _Process()

        with pytest.raises(
            subprocess_start.SubprocessStartTimeoutError,
            match="earlier unresolved subprocess start",
        ):
            subprocess_start.start_subprocess_with_deadline(
                second_factory,
                cleanup=lambda _process: None,
                deadline=time.monotonic() + 0.05,
                timeout_seconds=0.05,
                operation="blocked retry",
            )
        assert second_calls == []
    finally:
        release.set()

    assert cleaned.wait(timeout=1.0)


def test_subprocess_constructor_failure_is_projected_without_cleanup() -> None:
    cleaned: list[_Process] = []

    def fail() -> _Process:
        raise OSError("constructor failed")

    with pytest.raises(
        subprocess_start.SubprocessStartError,
        match="constructor failed",
    ):
        subprocess_start.start_subprocess_with_deadline(
            fail,
            cleanup=cleaned.append,
            deadline=time.monotonic() + 1.0,
            timeout_seconds=1.0,
            operation="failed process",
        )

    assert cleaned == []


def test_start_deadline_includes_gate_wait_and_constructor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [100.0]
    observed: dict[str, float | int] = {}
    process = _Process()

    class Gate:
        def acquire(self, timeout: float = -1.0) -> bool:
            observed["gate_timeout"] = float(timeout)
            clock[0] += 3.0
            return True

        def release(self) -> None:
            observed["gate_releases"] = int(observed.get("gate_releases", 0)) + 1

    class Thread:
        ident: int | None = None

        def __init__(self, *, target, **_kwargs: object) -> None:  # type: ignore[no-untyped-def]
            self._target = target

        def start(self) -> None:
            self.ident = 7
            clock[0] += 2.0
            self._target()

    def factory() -> _Process:
        observed["factory_at"] = clock[0]
        clock[0] += 2.0
        return process

    monkeypatch.setattr(subprocess_start, "_SUBPROCESS_START_GATE", Gate())
    monkeypatch.setattr(subprocess_start.threading, "Thread", Thread)
    monkeypatch.setattr(subprocess_start.time, "monotonic", lambda: clock[0])

    result = subprocess_start.start_subprocess_with_deadline(
        factory,
        cleanup=lambda _process: None,
        deadline=110.0,
        timeout_seconds=10.0,
        operation="absolute process deadline",
    )

    assert result is process
    assert observed == {
        "gate_timeout": 10.0,
        "factory_at": 105.0,
        "gate_releases": 1,
    }


def test_completion_timestamp_accepts_on_time_constructor_after_caller_delay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    process = _Process()
    cleaned: list[_Process] = []

    class Gate:
        def acquire(self, timeout: float = -1.0) -> bool:
            assert timeout == pytest.approx(10.0)
            return True

        def release(self) -> None:
            pass

    class Thread:
        ident: int | None = None

        def __init__(self, *, target, **_kwargs: object) -> None:  # type: ignore[no-untyped-def]
            self._target = target

        def start(self) -> None:
            self.ident = 8
            clock[0] = 9.0
            self._target()
            clock[0] = 11.0

    monkeypatch.setattr(subprocess_start, "_SUBPROCESS_START_GATE", Gate())
    monkeypatch.setattr(subprocess_start.threading, "Thread", Thread)
    monkeypatch.setattr(subprocess_start.time, "monotonic", lambda: clock[0])

    result = subprocess_start.start_subprocess_with_deadline(
        lambda: process,
        cleanup=cleaned.append,
        deadline=10.0,
        timeout_seconds=10.0,
        operation="boundary process",
    )

    assert result is process
    assert cleaned == []


def test_completion_after_absolute_deadline_is_cleaned_not_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    process = _Process()
    cleaned: list[_Process] = []

    class Gate:
        def acquire(self, timeout: float = -1.0) -> bool:
            assert timeout == pytest.approx(10.0)
            return True

        def release(self) -> None:
            pass

    class Thread:
        ident: int | None = None

        def __init__(self, *, target, **_kwargs: object) -> None:  # type: ignore[no-untyped-def]
            self._target = target

        def start(self) -> None:
            self.ident = 9
            self._target()

    def factory() -> _Process:
        clock[0] = 10.25
        return process

    monkeypatch.setattr(subprocess_start, "_SUBPROCESS_START_GATE", Gate())
    monkeypatch.setattr(subprocess_start.threading, "Thread", Thread)
    monkeypatch.setattr(subprocess_start.time, "monotonic", lambda: clock[0])

    with pytest.raises(
        subprocess_start.SubprocessStartTimeoutError,
        match="startup timed out after 10s",
    ):
        subprocess_start.start_subprocess_with_deadline(
            factory,
            cleanup=cleaned.append,
            deadline=10.0,
            timeout_seconds=10.0,
            operation="late process",
        )

    assert cleaned == [process]


def test_interruption_during_completed_process_handoff_cleans_exactly_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = _Process()
    cleaned: list[_Process] = []
    original = subprocess_start._SubprocessStartAttempt._classify_completion  # type: ignore[attr-defined]

    def interrupt_after_observing_completion(self):  # type: ignore[no-untyped-def]
        original(self)
        raise KeyboardInterrupt

    monkeypatch.setattr(
        subprocess_start._SubprocessStartAttempt,  # type: ignore[attr-defined]
        "_classify_completion",
        interrupt_after_observing_completion,
    )

    with pytest.raises(KeyboardInterrupt):
        subprocess_start.start_subprocess_with_deadline(
            lambda: process,
            cleanup=cleaned.append,
            deadline=time.monotonic() + 1.0,
            timeout_seconds=1.0,
            operation="interrupted process handoff",
        )

    assert cleaned == [process]
    assert subprocess_start._SUBPROCESS_START_GATE.acquire(timeout=1.0)  # type: ignore[attr-defined]
    subprocess_start._SUBPROCESS_START_GATE.release()  # type: ignore[attr-defined]


def test_interrupted_thread_start_with_unpublished_ident_keeps_single_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_thread = threading.Thread
    factory_entered = threading.Event()
    release_factory = threading.Event()
    cleanup_finished = threading.Event()
    background: list[threading.Thread] = []
    second_calls: list[str] = []
    process = _Process()

    class InterruptedThread:
        ident: int | None = None

        def __init__(self, *, target, **_kwargs: object) -> None:  # type: ignore[no-untyped-def]
            self._target = target

        def start(self) -> None:
            def publish_then_run() -> None:
                time.sleep(0.02)
                self.ident = 73
                self._target()

            owner = real_thread(target=publish_then_run, daemon=True)
            background.append(owner)
            owner.start()
            raise KeyboardInterrupt

    def first_factory() -> _Process:
        factory_entered.set()
        release_factory.wait(timeout=5.0)
        return process

    monkeypatch.setattr(subprocess_start.threading, "Thread", InterruptedThread)

    try:
        with pytest.raises(KeyboardInterrupt):
            subprocess_start.start_subprocess_with_deadline(
                first_factory,
                cleanup=lambda value: cleanup_finished.set() if value is process else None,
                deadline=time.monotonic() + 1.0,
                timeout_seconds=1.0,
                operation="interrupted starter publication",
            )
        assert factory_entered.wait(timeout=1.0)

        def second_factory() -> _Process:
            second_calls.append("called")
            return _Process()

        with pytest.raises(
            subprocess_start.SubprocessStartTimeoutError,
            match="earlier unresolved subprocess start",
        ):
            subprocess_start.start_subprocess_with_deadline(
                second_factory,
                cleanup=lambda _process: None,
                deadline=time.monotonic() + 0.05,
                timeout_seconds=0.05,
                operation="retry during interrupted starter publication",
            )
        assert second_calls == []
    finally:
        release_factory.set()
        for owner in background:
            owner.join(timeout=1.0)

    assert cleanup_finished.wait(timeout=1.0)
    assert subprocess_start._SUBPROCESS_START_GATE.acquire(timeout=1.0)  # type: ignore[attr-defined]
    subprocess_start._SUBPROCESS_START_GATE.release()  # type: ignore[attr-defined]


def test_plain_thread_start_failure_releases_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailedThread:
        ident: int | None = None

        def __init__(self, **_kwargs: object) -> None:
            pass

        def start(self) -> None:
            raise RuntimeError("native thread unavailable")

    monkeypatch.setattr(subprocess_start.threading, "Thread", FailedThread)

    with pytest.raises(
        subprocess_start.SubprocessStartError,
        match="starter could not run: native thread unavailable",
    ):
        subprocess_start.start_subprocess_with_deadline(
            _Process,
            cleanup=lambda _process: None,
            deadline=time.monotonic() + 1.0,
            timeout_seconds=1.0,
            operation="failed starter",
        )

    assert subprocess_start._SUBPROCESS_START_GATE.acquire(timeout=1.0)  # type: ignore[attr-defined]
    subprocess_start._SUBPROCESS_START_GATE.release()  # type: ignore[attr-defined]
