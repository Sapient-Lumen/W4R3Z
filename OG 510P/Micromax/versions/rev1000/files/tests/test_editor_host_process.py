from __future__ import annotations

import os
import signal
import sys
import threading
import time
from contextlib import suppress
from pathlib import Path

import pytest

from micromax_editor import host_process
from micromax_editor.host_process import run_argv_bounded


def test_run_argv_bounded_limits_stdout_before_return() -> None:
    result = run_argv_bounded(
        [sys.executable, "-S", "-c", "import sys; sys.stdout.write('x' * 4096)"],
        timeout_seconds=1.0,
        max_output_bytes=32,
        label="test process",
    )

    assert result.returncode == 125
    assert len(result.stdout.encode("utf-8")) <= 32
    assert "test process: output exceeded process output budget 32 bytes" in result.stderr


def test_run_argv_bounded_pipes_input_text() -> None:
    result = run_argv_bounded(
        [sys.executable, "-S", "-c", "import sys; sys.stdout.write(sys.stdin.read().upper())"],
        input_text="abc",
        timeout_seconds=1.0,
        max_output_bytes=1024,
        label="test process",
    )

    assert result.returncode == 0
    assert result.stdout == "ABC"
    assert result.stderr == ""


def test_run_argv_bounded_timeout_uses_diagnostic() -> None:
    result = run_argv_bounded(
        [sys.executable, "-S", "-c", "import time; time.sleep(5)"],
        timeout_seconds=0.2,
        max_output_bytes=1024,
        label="test process",
    )

    assert result.returncode == 124
    assert result.timed_out is True
    assert "test process: timed out after" in result.stderr


@pytest.mark.skipif(os.name != "posix", reason="signal escalation proof is POSIX-specific")
def test_run_argv_bounded_timeout_escalates_past_ignored_sigterm() -> None:
    source = (
        "import signal,time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "print('ready', flush=True); time.sleep(30)"
    )

    started = time.monotonic()
    result = run_argv_bounded(
        [sys.executable, "-S", "-c", source],
        timeout_seconds=0.2,
        max_output_bytes=1024,
        label="stubborn process",
    )

    assert result.returncode == 124
    assert result.timed_out is True
    assert result.stdout == "ready\n"
    assert time.monotonic() - started < 1.5
    assert _micromax_process_threads() == []


def test_process_deadline_normalizer_rejects_nonfinite_and_boolean_values() -> None:
    from micromax_editor.host_process import _finite_timeout_seconds

    assert _finite_timeout_seconds(float("nan"), default=1.25) == 1.25
    assert _finite_timeout_seconds(float("inf"), default=1.25) == 1.25
    assert _finite_timeout_seconds(-float("inf"), default=1.25) == 1.25
    assert _finite_timeout_seconds(True, default=1.25) == 1.25
    assert _finite_timeout_seconds(0, default=1.25) == 0.05
    assert _finite_timeout_seconds(0.5, default=1.25) == 0.5


def test_exact_pipe_holder_signal_uses_pidfd_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    pipe_ids = frozenset({(10, 20)})
    events: list[tuple[object, ...]] = []
    pidfd = os.open(os.devnull, os.O_RDONLY)

    def holds_pipe(pid: int, identities: frozenset[tuple[int, int]]) -> bool:
        events.append(("revalidate", pid, identities))
        return True

    def open_pidfd(pid: int, flags: int = 0) -> int:
        events.append(("open", pid, flags))
        return pidfd

    monkeypatch.setattr(host_process, "_pid_holds_pipe_ids", holds_pipe)
    monkeypatch.setattr(host_process, "_linux_pid_start_time", lambda _pid: "77")
    monkeypatch.setattr(
        host_process.os,
        "pidfd_open",
        open_pidfd,
        raising=False,
    )
    monkeypatch.setattr(
        host_process.signal,
        "pidfd_send_signal",
        lambda fd, sig, info=None, flags=0: events.append(
            ("signal", fd, sig, info, flags)
        ),
        raising=False,
    )

    assert host_process._signal_pipe_holder_pid(
        12345,
        signal.SIGTERM,
        pipe_ids=pipe_ids,
    ) is True
    assert events == [
        ("revalidate", 12345, pipe_ids),
        ("open", 12345, 0),
        ("revalidate", 12345, pipe_ids),
        ("signal", pidfd, int(signal.SIGTERM), None, 0),
    ]
    with pytest.raises(OSError):
        os.fstat(pidfd)


def test_exact_pipe_holder_signal_revalidates_numeric_pid_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[tuple[object, ...]] = []
    monkeypatch.setattr(host_process.os, "pidfd_open", None, raising=False)
    monkeypatch.setattr(host_process.signal, "pidfd_send_signal", None, raising=False)
    def start_time(pid: int) -> str:
        events.append(("start", pid))
        return "77"

    def holds_pipe(pid: int, identities: frozenset[tuple[int, int]]) -> bool:
        events.append(("holds", pid, identities))
        return True

    monkeypatch.setattr(host_process, "_linux_pid_start_time", start_time)
    monkeypatch.setattr(host_process, "_pid_holds_pipe_ids", holds_pipe)
    monkeypatch.setattr(
        host_process.os,
        "kill",
        lambda pid, sig: events.append(("kill", pid, sig)),
    )

    assert host_process._signal_pipe_holder_pid(
        12345,
        signal.SIGTERM,
        pipe_ids=frozenset({(10, 20)}),
    ) is True
    assert events[-1] == ("kill", 12345, signal.SIGTERM)
    assert sum(1 for event in events if event[0] == "start") == 3
    assert sum(1 for event in events if event[0] == "holds") == 2


def test_exact_pipe_holder_batch_signals_every_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[int] = []
    def signal_holder(
        pid: int,
        _sig: int,
        *,
        pipe_ids: frozenset[tuple[int, int]],
    ) -> bool:
        seen.append(pid)
        return bool(pipe_ids)

    monkeypatch.setattr(host_process, "_signal_pipe_holder_pid", signal_holder)

    assert host_process._signal_pipe_holder_pids(
        (9, 7, 5),
        signal.SIGTERM,
        pipe_ids=frozenset({(10, 20)}),
    ) is True
    assert seen == [9, 7, 5]


def test_exact_linux_cleanup_does_not_broaden_empty_scan_to_process_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Process:
        pass

    monkeypatch.setattr(
        host_process,
        "_linux_pipe_holder_discovery_available",
        lambda _pipe_ids: True,
    )
    monkeypatch.setattr(host_process, "_linux_pipe_holder_pids", lambda _pipe_ids: ())

    def unexpected_group_signal(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("exact Linux cleanup broadened to a process group")

    monkeypatch.setattr(host_process, "_signal_process_tree_or_child", unexpected_group_signal)

    host_process._terminate_lingering_capture_owners(
        Process(),  # type: ignore[arg-type]
        pgid=12345,
        pipe_ids=frozenset({(10, 20)}),
    )


def _pid_is_live(pid: int) -> bool:
    proc_stat = Path(f"/proc/{pid}/stat")
    try:
        fields = proc_stat.read_text(encoding="utf-8", errors="replace").split()
    except OSError:
        fields = []
    if len(fields) >= 3 and fields[2] == "Z":
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _kill_test_process(pid: int) -> None:
    try:
        os.killpg(int(pid), signal.SIGKILL)
        return
    except (OSError, ProcessLookupError):
        pass
    with suppress(OSError, ProcessLookupError):
        os.kill(int(pid), signal.SIGKILL)


def _background_parent_program(
    marker: Path,
    *,
    detach_stdio: bool,
    new_session: bool,
) -> str:
    child = (
        "import os,time; from pathlib import Path; "
        f"Path({str(marker)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    kwargs = f", start_new_session={new_session!r}"
    if detach_stdio:
        kwargs += (
            ", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, "
            "stderr=subprocess.DEVNULL"
        )
    return (
        "import subprocess,sys,time; from pathlib import Path; "
        f"marker=Path({str(marker)!r}); "
        f"subprocess.Popen([sys.executable,'-S','-c',{child!r}]{kwargs}); "
        "deadline=time.monotonic()+1.0; "
        "\nwhile not marker.exists() and time.monotonic()<deadline: time.sleep(0.01)"
    )


def _wait_until_dead(pid: int, *, timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout
    while _pid_is_live(pid) and time.monotonic() < deadline:
        time.sleep(0.02)


def _micromax_process_threads() -> list[str]:
    return sorted(
        thread.name
        for thread in threading.enumerate()
        if thread.name.startswith("micromax-process-")
    )


@pytest.mark.skipif(os.name != "posix", reason="process-group proof is POSIX-specific")
def test_run_argv_bounded_kills_background_descendant_holding_capture_pipes(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "inherited-pipes.pid"

    started = time.monotonic()
    result = run_argv_bounded(
        [
            sys.executable,
            "-S",
            "-c",
            _background_parent_program(
                marker,
                detach_stdio=False,
                new_session=False,
            ),
        ],
        timeout_seconds=2.0,
        max_output_bytes=1024,
        label="test process",
    )
    elapsed = time.monotonic() - started

    assert result.returncode == 0
    assert marker.is_file()
    pid = int(marker.read_text(encoding="utf-8"))
    try:
        _wait_until_dead(pid)
        assert _pid_is_live(pid) is False
        assert elapsed < 2.0
        assert _micromax_process_threads() == []
    finally:
        _kill_test_process(pid)


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/self/fd").is_dir(),
    reason="escaped capture-pipe owner proof requires Linux /proc",
)
def test_run_argv_bounded_kills_new_session_descendant_holding_capture_pipes(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "escaped-inherited-pipes.pid"

    result = run_argv_bounded(
        [
            sys.executable,
            "-S",
            "-c",
            _background_parent_program(
                marker,
                detach_stdio=False,
                new_session=True,
            ),
        ],
        timeout_seconds=2.0,
        max_output_bytes=1024,
        label="test process",
    )

    assert result.returncode == 0
    assert marker.is_file()
    pid = int(marker.read_text(encoding="utf-8"))
    try:
        _wait_until_dead(pid)
        assert _pid_is_live(pid) is False
        assert _micromax_process_threads() == []
    finally:
        _kill_test_process(pid)


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/self/fd").is_dir(),
    reason="escaped stdin-pipe owner proof requires Linux /proc",
)
def test_run_argv_bounded_releases_blocked_stdin_writer_after_parent_exit(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "escaped-stdin-owner.pid"
    child = (
        "import os,time; from pathlib import Path; "
        f"Path({str(marker)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    parent = (
        "import subprocess,sys,time; from pathlib import Path; "
        f"marker=Path({str(marker)!r}); "
        f"subprocess.Popen([sys.executable,'-S','-c',{child!r}], start_new_session=True); "
        "deadline=time.monotonic()+1.0; "
        "\nwhile not marker.exists() and time.monotonic()<deadline: time.sleep(0.01)"
    )

    started = time.monotonic()
    result = run_argv_bounded(
        [sys.executable, "-S", "-c", parent],
        input_text="x" * 2_000_000,
        timeout_seconds=2.0,
        max_output_bytes=1024,
        label="stdin owner",
    )
    elapsed = time.monotonic() - started

    assert result.returncode == 0
    assert marker.is_file()
    pid = int(marker.read_text(encoding="utf-8"))
    try:
        _wait_until_dead(pid)
        assert _pid_is_live(pid) is False
        assert elapsed < 2.0
        assert _micromax_process_threads() == []
    finally:
        _kill_test_process(pid)


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/self/fd").is_dir(),
    reason="exact sibling ownership proof requires Linux /proc",
)
def test_run_argv_bounded_preserves_detached_sibling_of_capture_pipe_holder(
    tmp_path: Path,
) -> None:
    holder_marker = tmp_path / "capture-holder.pid"
    detached_marker = tmp_path / "detached-sibling.pid"
    holder = (
        "import os,time; from pathlib import Path; "
        f"Path({str(holder_marker)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    detached = (
        "import os,time; from pathlib import Path; "
        f"Path({str(detached_marker)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    parent = (
        "import subprocess,sys,time; from pathlib import Path; "
        f"a=Path({str(holder_marker)!r}); b=Path({str(detached_marker)!r}); "
        f"subprocess.Popen([sys.executable,'-S','-c',{holder!r}]); "
        f"subprocess.Popen([sys.executable,'-S','-c',{detached!r}], "
        "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, "
        "stderr=subprocess.DEVNULL); "
        "deadline=time.monotonic()+1.0; "
        "\nwhile (not a.exists() or not b.exists()) and time.monotonic()<deadline: "
        "time.sleep(0.01)"
    )

    result = run_argv_bounded(
        [sys.executable, "-S", "-c", parent],
        timeout_seconds=2.0,
        max_output_bytes=1024,
        label="mixed background siblings",
    )

    assert result.returncode == 0
    assert holder_marker.is_file()
    assert detached_marker.is_file()
    holder_pid = int(holder_marker.read_text(encoding="utf-8"))
    detached_pid = int(detached_marker.read_text(encoding="utf-8"))
    try:
        _wait_until_dead(holder_pid)
        assert _pid_is_live(holder_pid) is False
        assert _pid_is_live(detached_pid) is True
        assert _micromax_process_threads() == []
    finally:
        _kill_test_process(holder_pid)
        _kill_test_process(detached_pid)


@pytest.mark.skipif(os.name != "posix", reason="background-child proof is POSIX-specific")
def test_run_argv_bounded_leaves_stdio_detached_background_descendant_alive(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "detached-stdio.pid"

    result = run_argv_bounded(
        [
            sys.executable,
            "-S",
            "-c",
            _background_parent_program(
                marker,
                detach_stdio=True,
                new_session=True,
            ),
        ],
        timeout_seconds=2.0,
        max_output_bytes=1024,
        label="test process",
    )

    assert result.returncode == 0
    assert marker.is_file()
    pid = int(marker.read_text(encoding="utf-8"))
    try:
        assert _pid_is_live(pid) is True
        assert _micromax_process_threads() == []
    finally:
        _kill_test_process(pid)


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/self/status").is_file(),
    reason="escaped-descendant teardown proof requires Linux /proc",
)
def test_run_argv_bounded_timeout_kills_descendant_in_fresh_session(tmp_path: Path) -> None:
    marker = tmp_path / "escaped.pid"
    child_code = (
        "import subprocess,sys,time; "
        "p=subprocess.Popen([sys.executable,'-S','-c',"
        "'import time; time.sleep(30)'], start_new_session=True); "
        f"open({str(marker)!r},'w',encoding='utf-8').write(str(p.pid)); "
        "time.sleep(30)"
    )

    result = run_argv_bounded(
        [sys.executable, "-S", "-c", child_code],
        timeout_seconds=0.5,
        max_output_bytes=1024,
        label="escaped descendant",
    )

    assert result.returncode == 124
    assert marker.is_file()
    pid = int(marker.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        try:
            fields = Path(f"/proc/{pid}/stat").read_text(
                encoding="utf-8", errors="replace"
            ).split()
        except OSError:
            break
        if len(fields) >= 3 and fields[2] == "Z":
            break
        time.sleep(0.02)
    else:
        with suppress(ProcessLookupError):
            os.killpg(pid, 9)
        pytest.fail("escaped descendant survived bounded-process teardown")


def test_run_argv_bounded_constructor_timeout_returns_and_late_process_is_reclaimed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    constructor_entered = threading.Event()
    release_constructor = threading.Event()
    cleanup_finished = threading.Event()
    state = {"alive": True, "terminated": False}

    class LateProcess:
        stdin = None
        stdout = None
        stderr = None
        pid = None
        returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode if not state["alive"] else None

        def terminate(self) -> None:
            state["terminated"] = True
            state["alive"] = False
            self.returncode = -int(signal.SIGTERM)

        def kill(self) -> None:
            state["alive"] = False
            self.returncode = -int(signal.SIGKILL)

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            cleanup_finished.set()
            return int(self.returncode or 0)

    process = LateProcess()

    def blocked_popen(*_args: object, **_kwargs: object) -> LateProcess:
        constructor_entered.set()
        release_constructor.wait(timeout=5.0)
        return process

    monkeypatch.setattr(host_process.subprocess, "Popen", blocked_popen)

    started = time.monotonic()
    try:
        result = run_argv_bounded(
            ["ignored"],
            timeout_seconds=0.05,
            max_output_bytes=1024,
            label="blocked constructor",
        )
        elapsed = time.monotonic() - started
        assert result.returncode == 124
        assert result.timed_out is True
        assert "startup timed out after 0.05s" in result.stderr
        assert elapsed < 0.5
        assert constructor_entered.wait(timeout=0.5)
        assert state == {"alive": True, "terminated": False}
    finally:
        release_constructor.set()

    assert cleanup_finished.wait(timeout=1.0)
    assert state == {"alive": False, "terminated": True}


def test_run_argv_bounded_constructor_and_execution_share_one_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [100.0]
    observed: dict[str, float] = {}

    class SlowStartedProcess:
        stdin = None
        stdout = None
        stderr = None
        pid = None

        def __init__(self) -> None:
            self.returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            self.returncode = -int(signal.SIGTERM)

        def kill(self) -> None:
            self.returncode = -int(signal.SIGKILL)

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            return int(self.returncode or 0)

    process = SlowStartedProcess()

    def delayed_start(factory, *, cleanup, deadline, timeout_seconds, operation):  # type: ignore[no-untyped-def]
        del factory, cleanup, timeout_seconds, operation
        observed["deadline"] = float(deadline)
        clock[0] += 0.06
        return process

    monkeypatch.setattr(host_process, "start_subprocess_with_deadline", delayed_start)
    monkeypatch.setattr(host_process.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        host_process.time,
        "sleep",
        lambda seconds: clock.__setitem__(0, clock[0] + float(seconds)),
    )

    result = run_argv_bounded(
        ["ignored"],
        timeout_seconds=0.10,
        max_output_bytes=1024,
        label="shared deadline",
    )

    assert observed["deadline"] == pytest.approx(100.10)
    assert clock[0] == pytest.approx(100.10)
    assert result.returncode == 124
    assert result.timed_out is True
    assert "shared deadline: timed out after 0.1s" in result.stderr


def test_started_process_is_reclaimed_when_capture_handoff_is_interrupted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = object()
    cleaned: list[object] = []

    monkeypatch.setattr(
        host_process,
        "start_subprocess_with_deadline",
        lambda *_args, **_kwargs: process,
    )

    def interrupted_capture(*_args: object, **_kwargs: object) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(host_process, "_capture_started_process", interrupted_capture)
    monkeypatch.setattr(host_process, "_cleanup_abandoned_popen", cleaned.append)

    with pytest.raises(KeyboardInterrupt):
        host_process._run_captured_process(  # type: ignore[attr-defined]
            lambda: process,  # type: ignore[return-value]
            stdin_bytes=None,
            timeout_value=1.0,
            output_limit=1024,
            label="interrupted capture",
            output_budget_name="test budget",
        )

    assert cleaned == [process]


def test_partial_capture_thread_start_reclaims_started_threads_and_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    created: list[PartialThread] = []

    class PartialThread:
        def __init__(self, **_kwargs: object) -> None:
            self.ident: int | None = None
            self.alive = False
            self.index = len(created)
            created.append(self)

        def start(self) -> None:
            if self.index == 1:
                events.append("second-start-interrupted")
                raise KeyboardInterrupt
            self.ident = 101 + self.index
            self.alive = True
            events.append(f"start-{self.index}")

        def is_alive(self) -> bool:
            return self.alive

        def join(self, timeout: float | None = None) -> None:
            del timeout
            events.append(f"join-{self.index}")
            self.alive = False

    class Process:
        stdout = object()
        stderr = object()
        stdin = None
        pid = None
        returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            events.append("wait")
            return int(self.returncode or -9)

    process = Process()

    monkeypatch.setattr(host_process.threading, "Thread", PartialThread)
    monkeypatch.setattr(
        host_process,
        "_confirmed_child_process_group_id",
        lambda _process: None,
    )
    monkeypatch.setattr(
        host_process,
        "_process_pipe_ids",
        lambda _process: frozenset(),
    )

    def terminate(_process: object, **_kwargs: object) -> None:
        events.append("terminate")
        process.returncode = -9

    monkeypatch.setattr(host_process, "terminate_process_tree", terminate)
    monkeypatch.setattr(
        host_process,
        "_close_process_streams",
        lambda _process: events.append("close"),
    )

    with pytest.raises(KeyboardInterrupt):
        host_process._capture_started_process(  # type: ignore[attr-defined]
            process,  # type: ignore[arg-type]
            stdin_bytes=None,
            timeout_value=1.0,
            deadline=time.monotonic() + 1.0,
            output_limit=1024,
            label="partial capture start",
            output_budget_name="test budget",
        )

    assert events == [
        "start-0",
        "second-start-interrupted",
        "terminate",
        "join-0",
        "close",
        "wait",
    ]
    assert created[0].alive is False
    assert created[1].ident is None
