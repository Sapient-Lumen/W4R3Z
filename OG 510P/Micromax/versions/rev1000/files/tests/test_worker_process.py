from __future__ import annotations

import multiprocessing
import os
import subprocess
import sys
import threading
import time
import warnings
from pathlib import Path

import pytest

from micromax import worker_process
from micromax_editor.docs_index import _docs_worker_context
from micromax_editor.file_access import _fs_worker_context, stat_path_contained_bounded
from micromax_editor.file_write import _file_write_worker_context
from micromax_editor.plugins import _plugin_worker_context
from micromax_editor.worker_process import (
    WorkerContextUnavailableError,
    isolated_worker_context,
)


def _worker_publish(payload: object, sender: object) -> None:
    sender.put(payload)  # type: ignore[attr-defined]


def _worker_ready_then_publish(
    ready_socket: object,
    payload: object,
    sender: object,
) -> None:
    try:
        ready_socket.sendall(b"R")  # type: ignore[attr-defined]
        if ready_socket.recv(1) != b"G":  # type: ignore[attr-defined]
            return
        sender.put(payload)  # type: ignore[attr-defined]
    finally:
        ready_socket.close()  # type: ignore[attr-defined]


def _worker_publish_then_linger(payload: object, seconds: float, sender: object) -> None:
    sender.put(payload)  # type: ignore[attr-defined]
    time.sleep(float(seconds))


def _worker_publish_raw_frame(payload: bytes, seconds: float, sender: object) -> None:
    sock = sender._socket  # type: ignore[attr-defined]
    sock.sendall(
        worker_process._WORKER_RESULT_HEADER.pack(  # type: ignore[attr-defined]
            worker_process._WORKER_RESULT_MAGIC,  # type: ignore[attr-defined]
            len(payload),
        )
    )
    if payload:
        sock.sendall(payload)
    if seconds > 0:
        time.sleep(float(seconds))
    sender.close()  # type: ignore[attr-defined]


def _worker_publish_partial_frame(declared: int, seconds: float, sender: object) -> None:
    sock = sender._socket  # type: ignore[attr-defined]
    sock.sendall(
        worker_process._WORKER_RESULT_HEADER.pack(  # type: ignore[attr-defined]
            worker_process._WORKER_RESULT_MAGIC,  # type: ignore[attr-defined]
            int(declared),
        )
        + b"x"
    )
    time.sleep(float(seconds))


def _worker_exit_without_result(sender: object) -> None:
    sender.close()  # type: ignore[attr-defined]
    os._exit(17)


def _spawn_context() -> multiprocessing.context.BaseContext:
    if "spawn" in multiprocessing.get_all_start_methods():
        return multiprocessing.get_context("spawn")
    return multiprocessing.get_context()


def _safe_method_available() -> bool:
    methods = set(multiprocessing.get_all_start_methods())
    return bool(methods.intersection({"forkserver", "spawn"}))


def test_isolated_worker_context_avoids_fork_when_safe_method_exists() -> None:
    ctx = isolated_worker_context()

    if _safe_method_available():
        assert ctx.get_start_method() in {"forkserver", "spawn"}
    else:
        assert ctx.get_start_method() == multiprocessing.get_start_method()


def test_isolated_worker_context_prefers_spawn_over_forkserver(monkeypatch) -> None:
    requested: list[str] = []
    real_get_context = multiprocessing.get_context

    monkeypatch.setattr(
        worker_process.multiprocessing,
        "get_all_start_methods",
        lambda: ["fork", "forkserver", "spawn"],
    )

    def tracked(method=None):  # type: ignore[no-untyped-def]
        requested.append(str(method))
        return real_get_context(method)

    monkeypatch.setattr(worker_process.multiprocessing, "get_context", tracked)
    monkeypatch.setattr(worker_process, "main_module_is_importable", lambda: True)

    assert isolated_worker_context().get_start_method() == "spawn"
    assert requested == ["spawn"]


def test_all_killable_worker_families_share_isolated_default() -> None:
    methods = {
        _fs_worker_context().get_start_method(),
        _file_write_worker_context().get_start_method(),
        _docs_worker_context().get_start_method(),
        _plugin_worker_context().get_start_method(),
    }

    assert len(methods) == 1
    if _safe_method_available():
        assert methods <= {"forkserver", "spawn"}


def test_bounded_stat_is_safe_while_another_thread_is_live(tmp_path: Path) -> None:
    target = tmp_path / "threaded-stat.txt"
    target.write_text("ok", encoding="utf-8")
    stop = threading.Event()
    ready = threading.Event()

    def hold_thread() -> None:
        ready.set()
        stop.wait(timeout=5.0)

    thread = threading.Thread(target=hold_thread, daemon=True)
    thread.start()
    assert ready.wait(timeout=1.0)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            result = stat_path_contained_bounded(target, timeout_seconds=5.0)
    finally:
        stop.set()
        thread.join(timeout=1.0)

    assert result.exists is True
    assert result.kind == "file"
    assert result.size == 2


def test_nonimportable_single_thread_entrypoint_fails_closed_before_threaded_fork(
    monkeypatch,
) -> None:
    monkeypatch.setattr(worker_process, "main_module_is_importable", lambda: False)

    with pytest.raises(WorkerContextUnavailableError, match="no safe multiprocessing context"):
        isolated_worker_context()


def test_nonimportable_multithreaded_entrypoint_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(worker_process, "main_module_is_importable", lambda: False)

    with pytest.raises(WorkerContextUnavailableError, match="no safe multiprocessing context"):
        isolated_worker_context()


def test_python_c_bounded_stat_uses_fork_or_fails_closed_then_allows_direct_mode(
    tmp_path: Path,
) -> None:
    if "fork" not in multiprocessing.get_all_start_methods():
        pytest.skip("fork is unavailable on this platform")
    target = tmp_path / "python-c-stat.txt"
    target.write_text("ok", encoding="utf-8")
    code = (
        "from micromax_editor.file_access import stat_path_contained_bounded; "
        "from micromax_editor.worker_process import isolated_worker_context,"
        "WorkerContextUnavailableError; "
        "\ntry:\n"
        " m=isolated_worker_context().get_start_method(); "
        f"r=stat_path_contained_bounded({str(target)!r}, timeout_seconds=2.0)\n"
        "except WorkerContextUnavailableError:\n"
        " m='no-safe-context'; "
        f"r=stat_path_contained_bounded({str(target)!r}, timeout_seconds=0)\n"
        "print(m, r.kind, r.size)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        env={
            **os.environ,
            "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")
            + os.pathsep
            + os.environ.get("PYTHONPATH", ""),
        },
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "no-safe-context file 2"


@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), -float("inf"), True, "not-a-timeout"],
)
def test_worker_timeout_normalizer_replaces_nonfinite_or_malformed_values(value: object) -> None:
    assert worker_process.normalize_worker_timeout_seconds(value, default=2.5) == 2.5


def test_worker_timeout_normalizer_preserves_explicit_direct_mode() -> None:
    assert (
        worker_process.normalize_worker_timeout_seconds(
            None,
            default=5.0,
            none_disables=True,
        )
        == 0.0
    )
    assert (
        worker_process.normalize_worker_timeout_seconds(
            0.0,
            default=5.0,
            none_disables=True,
        )
        == 0.0
    )
    assert (
        worker_process.normalize_worker_timeout_seconds(
            -1.0,
            default=5.0,
            none_disables=True,
        )
        == -1.0
    )


def test_worker_teardown_replaces_infinite_join_deadline() -> None:
    joins: list[float | None] = []

    class Process:
        def __init__(self) -> None:
            self.alive = True

        def is_alive(self) -> bool:
            return self.alive

        def terminate(self) -> None:
            pass

        def kill(self) -> None:
            self.alive = False

        def join(self, timeout: float | None = None) -> None:
            joins.append(timeout)

    process = Process()
    worker_process.terminate_worker_process(process, join_timeout=float("inf"))  # type: ignore[arg-type]

    assert joins == [0.2, 0.2]


def test_direct_filesystem_worker_api_replaces_infinite_deadline(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.write_text("witness", encoding="utf-8")

    result = stat_path_contained_bounded(
        target,
        timeout_seconds=float("inf"),
        worker_context=_spawn_context(),
    )

    assert result.exists is True
    assert result.kind == "file"
    assert result.size == 7


def test_worker_result_channel_round_trips_payload_larger_than_socket_buffer() -> None:
    payload = b"x" * (3 * 1024 * 1024)
    proc, channel = worker_process.create_one_shot_worker(
        _spawn_context(),
        target=_worker_publish,
        args=(payload,),
        max_result_bytes=len(payload) + 1024 * 1024,
    )

    result = worker_process.collect_worker_result(
        proc,
        channel,
        timeout_seconds=10.0,
        operation="large framed result",
        require_clean_exit=True,
    )

    assert result == payload


def test_after_start_readiness_is_excluded_from_result_deadline() -> None:
    parent_ready, child_ready = worker_process.socket.socketpair()
    parent_ready.settimeout(5.0)
    proc, channel = worker_process.create_one_shot_worker(
        _spawn_context(),
        target=_worker_ready_then_publish,
        args=(child_ready, ("ok", "ready")),
    )
    observed_pids: list[int | None] = []

    def delayed_ready(worker_pid: int | None) -> None:
        observed_pids.append(worker_pid)
        child_ready.close()
        assert parent_ready.recv(1) == b"R"
        time.sleep(0.15)
        parent_ready.sendall(b"G")

    started = time.monotonic()
    try:
        result = worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=0.05,
            operation="target-ready witness",
            require_clean_exit=True,
            after_start=delayed_ready,
        )
    finally:
        child_ready.close()
        parent_ready.close()

    assert result == ("ok", "ready")
    assert len(observed_pids) == 1
    assert isinstance(observed_pids[0], int)
    assert time.monotonic() - started >= 0.15


def test_partial_worker_frame_cannot_outlive_parent_deadline() -> None:
    cleaned: list[int | None] = []
    proc, channel = worker_process.create_one_shot_worker(
        _spawn_context(),
        target=_worker_publish_partial_frame,
        args=(1024 * 1024, 60.0),
        max_result_bytes=2 * 1024 * 1024,
    )

    started = time.monotonic()
    with pytest.raises(worker_process.WorkerResultTimeoutError, match="timed out"):
        worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=0.1,
            operation="partial frame",
            abnormal_cleanup=cleaned.append,
        )

    assert time.monotonic() - started < 2.0
    assert len(cleaned) == 1
    assert isinstance(cleaned[0], int)


def test_partial_worker_frame_followed_by_exit_fails_promptly() -> None:
    proc, channel = worker_process.create_one_shot_worker(
        _spawn_context(),
        target=_worker_publish_partial_frame,
        args=(1024 * 1024, 0.0),
        max_result_bytes=2 * 1024 * 1024,
    )

    started = time.monotonic()
    with pytest.raises(worker_process.WorkerResultProtocolError, match="incomplete result frame"):
        worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=10.0,
            operation="partial exit",
        )

    assert time.monotonic() - started < 2.0


def test_oversized_declared_result_is_rejected_before_body_read() -> None:
    proc, channel = worker_process.create_one_shot_worker(
        _spawn_context(),
        target=_worker_publish_partial_frame,
        args=(10 * 1024 * 1024, 60.0),
        max_result_bytes=1024,
    )

    started = time.monotonic()
    with pytest.raises(worker_process.WorkerResultTooLargeError, match="exceeds 1024 bytes"):
        worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=2.0,
            operation="oversized frame",
        )

    assert time.monotonic() - started < 2.0


def test_invalid_or_trailing_pickle_data_fails_closed() -> None:
    bad_payloads = (
        b"not-a-pickle",
        __import__("pickle").dumps("first") + __import__("pickle").dumps("second"),
    )
    for payload in bad_payloads:
        proc, channel = worker_process.create_one_shot_worker(
            _spawn_context(),
            target=_worker_publish_raw_frame,
            args=(payload, 0.0),
            max_result_bytes=1024,
        )
        with pytest.raises(worker_process.WorkerResultProtocolError):
            worker_process.collect_worker_result(
                proc,
                channel,
                timeout_seconds=2.0,
                operation="invalid frame",
            )


def test_worker_crash_is_classified_from_eof_without_spending_deadline() -> None:
    proc, channel = worker_process.create_one_shot_worker(
        _spawn_context(),
        target=_worker_exit_without_result,
    )

    started = time.monotonic()
    with pytest.raises(worker_process.WorkerResultProtocolError, match="exited without result"):
        worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=10.0,
            operation="crashing worker",
        )

    assert time.monotonic() - started < 5.0


def test_result_from_nonexiting_worker_is_not_accepted() -> None:
    proc, channel = worker_process.create_one_shot_worker(
        _spawn_context(),
        target=_worker_publish_then_linger,
        args=(("ok", "witness"), 60.0),
    )

    with pytest.raises(worker_process.WorkerResultProcessError, match="did not exit"):
        worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=2.0,
            join_timeout=0.05,
            operation="lingering worker",
            require_clean_exit=True,
        )


def test_start_failure_closes_channel_and_process_handle() -> None:
    state = {"closed": False}

    class Process:
        def start(self) -> None:
            raise OSError("worker start failed")

        def is_alive(self) -> bool:
            return False

        def close(self) -> None:
            state["closed"] = True

    channel = worker_process.create_worker_result_channel(max_bytes=1024)

    with pytest.raises(worker_process.WorkerResultStartError, match="worker start failed"):
        worker_process.collect_worker_result(
            Process(),  # type: ignore[arg-type]
            channel,
            timeout_seconds=1.0,
            operation="start witness",
        )

    assert state["closed"] is True
    assert channel.receiver.fileno() == -1
    assert channel.sender._socket.fileno() == -1  # type: ignore[attr-defined]


def test_partial_start_failure_reclaims_live_child_and_runs_cleanup() -> None:
    state = {"alive": True, "terminated": False, "closed": False}
    cleaned: list[int | None] = []

    class Process:
        pid = 4242

        def start(self) -> None:
            raise OSError("partial worker start failed")

        def is_alive(self) -> bool:
            return bool(state["alive"])

        def terminate(self) -> None:
            state["terminated"] = True
            state["alive"] = False

        def join(self, timeout: float | None = None) -> None:
            del timeout

        def close(self) -> None:
            state["closed"] = True

    channel = worker_process.create_worker_result_channel(max_bytes=1024)

    with pytest.raises(worker_process.WorkerResultStartError, match="partial worker start failed"):
        worker_process.collect_worker_result(
            Process(),  # type: ignore[arg-type]
            channel,
            timeout_seconds=1.0,
            operation="partial start witness",
            abnormal_cleanup=cleaned.append,
        )

    assert state == {"alive": False, "terminated": True, "closed": True}
    assert cleaned == [4242]
    assert channel.receiver.fileno() == -1
    assert channel.sender._socket.fileno() == -1  # type: ignore[attr-defined]


def test_process_construction_failure_closes_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[worker_process.WorkerResultChannel] = []
    real_create = worker_process.create_worker_result_channel

    def tracked_create(**kwargs):  # type: ignore[no-untyped-def]
        channel = real_create(**kwargs)
        created.append(channel)
        return channel

    class Context:
        def Process(self, **_kwargs):  # noqa: N802, ANN001, ANN201
            raise OSError("construction failed")

    monkeypatch.setattr(worker_process, "create_worker_result_channel", tracked_create)

    proc, channel = worker_process.create_one_shot_worker(
        Context(),  # type: ignore[arg-type]
        target=_worker_exit_without_result,
    )
    with pytest.raises(worker_process.WorkerResultStartError, match="construction failed"):
        worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=1.0,
            startup_timeout_seconds=0.2,
            operation="construction witness",
        )

    assert len(created) == 1
    assert created[0].receiver.fileno() == -1
    assert created[0].sender._socket.fileno() == -1  # type: ignore[attr-defined]


def test_blocked_worker_construction_times_out_and_late_child_is_reclaimed() -> None:
    construction_entered = threading.Event()
    release_construction = threading.Event()
    cleanup_finished = threading.Event()
    cleaned: list[int | None] = []
    state = {
        "alive": False,
        "started": False,
        "terminated": False,
        "closed": False,
    }

    class LateProcess:
        pid = 8181
        exitcode = 0

        def start(self) -> None:
            state["started"] = True
            state["alive"] = True

        def is_alive(self) -> bool:
            return bool(state["alive"])

        def terminate(self) -> None:
            state["terminated"] = True
            state["alive"] = False

        def kill(self) -> None:
            state["alive"] = False

        def join(self, timeout: float | None = None) -> None:
            del timeout

        def close(self) -> None:
            state["closed"] = True
            cleanup_finished.set()

    class BlockingContext:
        def get_start_method(self) -> str:
            return "spawn"

        def Process(self, **_kwargs):  # noqa: N802, ANN001, ANN201
            construction_entered.set()
            release_construction.wait(timeout=5.0)
            return LateProcess()

    proc, channel = worker_process.create_one_shot_worker(
        BlockingContext(),  # type: ignore[arg-type]
        target=_worker_exit_without_result,
    )

    started_at = time.monotonic()
    try:
        with pytest.raises(
            worker_process.WorkerResultStartTimeoutError,
            match="startup timed out",
        ):
            worker_process.collect_worker_result(
                proc,
                channel,
                timeout_seconds=1.0,
                startup_timeout_seconds=0.05,
                operation="blocked construction",
                abnormal_cleanup=cleaned.append,
            )
        assert time.monotonic() - started_at < 0.5
        assert construction_entered.wait(timeout=0.5)

        second_calls: list[str] = []

        class SecondContext:
            def get_start_method(self) -> str:
                return "spawn"

            def Process(self, **_kwargs):  # noqa: N802, ANN001, ANN201
                second_calls.append("constructed")
                return LateProcess()

        second_proc, second_channel = worker_process.create_one_shot_worker(
            SecondContext(),  # type: ignore[arg-type]
            target=_worker_exit_without_result,
        )
        with pytest.raises(
            worker_process.WorkerResultStartTimeoutError,
            match="earlier unresolved start",
        ):
            worker_process.collect_worker_result(
                second_proc,
                second_channel,
                timeout_seconds=1.0,
                startup_timeout_seconds=0.05,
                operation="blocked retry",
            )
        assert second_calls == []
        assert second_channel.receiver.fileno() == -1
    finally:
        release_construction.set()

    assert cleanup_finished.wait(timeout=1.0)
    assert state == {
        "alive": False,
        "started": True,
        "terminated": True,
        "closed": True,
    }
    assert cleaned == [8181]
    assert channel.receiver.fileno() == -1
    assert worker_process._WORKER_START_GATE.acquire(timeout=0.1)  # type: ignore[attr-defined]
    worker_process._WORKER_START_GATE.release()  # type: ignore[attr-defined]


def test_blocked_process_start_times_out_without_leaking_caller_ownership() -> None:
    start_entered = threading.Event()
    release_start = threading.Event()
    cleanup_finished = threading.Event()
    state = {"alive": False, "terminated": False, "closed": False}

    class BlockingProcess:
        pid = 9191
        exitcode = 0

        def start(self) -> None:
            start_entered.set()
            release_start.wait(timeout=5.0)
            state["alive"] = True

        def is_alive(self) -> bool:
            return bool(state["alive"])

        def terminate(self) -> None:
            state["terminated"] = True
            state["alive"] = False

        def kill(self) -> None:
            state["alive"] = False

        def join(self, timeout: float | None = None) -> None:
            del timeout

        def close(self) -> None:
            state["closed"] = True
            cleanup_finished.set()

    class Context:
        def get_start_method(self) -> str:
            return "spawn"

        def Process(self, **_kwargs):  # noqa: N802, ANN001, ANN201
            return BlockingProcess()

    proc, channel = worker_process.create_one_shot_worker(
        Context(),  # type: ignore[arg-type]
        target=_worker_exit_without_result,
    )
    try:
        with pytest.raises(worker_process.WorkerResultStartTimeoutError):
            worker_process.collect_worker_result(
                proc,
                channel,
                timeout_seconds=1.0,
                startup_timeout_seconds=0.05,
                operation="blocked start",
            )
        assert start_entered.wait(timeout=0.5)
        # Ownership moved to the still-running starter; the caller did not race
        # it by closing the shared process/channel objects in its ``finally``.
        assert channel.receiver.fileno() >= 0
    finally:
        release_start.set()

    assert cleanup_finished.wait(timeout=1.0)
    assert state == {"alive": False, "terminated": True, "closed": True}
    assert channel.receiver.fileno() == -1


def test_deadline_owned_starter_rejects_explicit_fork_context() -> None:
    if "fork" not in multiprocessing.get_all_start_methods():
        pytest.skip("fork is unavailable on this platform")

    proc, channel = worker_process.create_one_shot_worker(
        multiprocessing.get_context("fork"),
        target=_worker_exit_without_result,
    )
    with pytest.raises(worker_process.WorkerResultStartError, match="cannot use fork"):
        worker_process.collect_worker_result(
            proc,
            channel,
            timeout_seconds=1.0,
            startup_timeout_seconds=0.1,
            operation="fork witness",
        )
    assert channel.receiver.fileno() == -1


def test_startup_budget_is_one_absolute_deadline_across_gate_and_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [100.0]
    observed: dict[str, float | int] = {}

    class Gate:
        def acquire(self, timeout: float = -1.0) -> bool:
            observed["gate_timeout"] = float(timeout)
            clock[0] += 3.0
            return True

        def release(self) -> None:
            observed["gate_releases"] = int(observed.get("gate_releases", 0)) + 1

    class PendingEvent:
        def wait(self, timeout: float | None = None) -> bool:
            observed["event_timeout"] = -1.0 if timeout is None else float(timeout)
            return False

        def is_set(self) -> bool:
            return False

    class Thread:
        ident: int | None = None

        def __init__(self, **_kwargs: object) -> None:
            pass

        def start(self) -> None:
            self.ident = 7
            clock[0] += 2.0

    class Process:
        start_method = "spawn"

    class Channel:
        pass

    attempt = worker_process._WorkerStartAttempt(  # type: ignore[attr-defined]
        Process(),  # type: ignore[arg-type]
        Channel(),  # type: ignore[arg-type]
        operation="absolute deadline",
        abnormal_cleanup=None,
    )
    attempt._done = PendingEvent()  # type: ignore[attr-defined]
    monkeypatch.setattr(worker_process, "_WORKER_START_GATE", Gate())
    monkeypatch.setattr(worker_process.threading, "Thread", Thread)
    monkeypatch.setattr(worker_process.time, "monotonic", lambda: clock[0])

    with pytest.raises(
        worker_process.WorkerResultStartTimeoutError,
        match="startup timed out after 10s",
    ):
        attempt.wait(timeout_seconds=10.0)

    assert observed["gate_timeout"] == pytest.approx(10.0)
    assert observed["event_timeout"] == pytest.approx(5.0)
    assert attempt.caller_owns_resources is False


def test_start_completion_after_absolute_deadline_is_not_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    observed = {"gate_releases": 0, "started": False}

    class Gate:
        def acquire(self, timeout: float = -1.0) -> bool:
            assert timeout == pytest.approx(10.0)
            return True

        def release(self) -> None:
            observed["gate_releases"] += 1

    class Process:
        start_method = "spawn"
        pid = 5151

        def start(self) -> None:
            observed["started"] = True
            clock[0] = 10.25

    class Channel:
        pass

    class Thread:
        ident: int | None = None

        def __init__(self, *, target, **_kwargs: object) -> None:  # type: ignore[no-untyped-def]
            self._target = target

        def start(self) -> None:
            self.ident = 8
            self._target()

    attempt = worker_process._WorkerStartAttempt(  # type: ignore[attr-defined]
        Process(),  # type: ignore[arg-type]
        Channel(),  # type: ignore[arg-type]
        operation="late boundary",
        abnormal_cleanup=None,
    )
    monkeypatch.setattr(worker_process, "_WORKER_START_GATE", Gate())
    monkeypatch.setattr(worker_process.threading, "Thread", Thread)
    monkeypatch.setattr(worker_process.time, "monotonic", lambda: clock[0])

    with pytest.raises(
        worker_process.WorkerResultStartTimeoutError,
        match="startup timed out after 10s",
    ):
        attempt.wait(timeout_seconds=10.0)

    assert observed == {"gate_releases": 1, "started": True}
    assert attempt.caller_owns_resources is True
