from __future__ import annotations

import os
import shlex
import signal
import sys
import threading
import time
from contextlib import suppress
from pathlib import Path

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.host_process import run_shell_command_bounded
from micromax_editor.micromax_bridge import install_editor_hostcalls

ROOT = Path(__file__).resolve().parents[1]


def _call_host(ed: Editor, name: str) -> None:
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<test>")


def _python_command(source: str) -> str:
    return shlex.join([sys.executable, "-S", "-c", source])


def _enable_shell(ed: Editor) -> None:
    assert ed.exec_command_line("set cap.shell true")


def test_shell_command_input_budget_preserves_operation_argument() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    _enable_shell(ed)
    ed.vm.editor_shell_command_max_bytes = 8

    ed.vm.stack.append("echo too-long")
    with pytest.raises(MicromaxError, match="shell command input budget"):
        _call_host(ed, "ed.shell")

    assert ed.vm.stack == ["echo too-long"]


def test_shell_output_budget_truncates_before_vm_result_budget() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    _enable_shell(ed)
    ed.vm.editor_shell_output_max_bytes = 64
    ed.vm.hostcall_result_max_bytes = 10_000

    ed.vm.stack.append(_python_command("import sys; sys.stdout.write('x' * 4096)"))
    _call_host(ed, "ed.shell")

    code = ed.vm.stack[-3]
    out = ed.vm.stack[-2]
    err = ed.vm.stack[-1]
    assert code == 125
    assert len(out.encode("utf-8")) <= 64
    assert "output exceeded shell output budget 64 bytes" in err


def test_shell_timeout_returns_error_tuple() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    _enable_shell(ed)
    ed.vm.editor_shell_timeout_seconds = 0.2

    ed.vm.stack.append(_python_command("import time; time.sleep(5)"))
    started = time.monotonic()
    _call_host(ed, "ed.shell")

    assert time.monotonic() - started < 3
    assert ed.vm.stack[-3] == 124
    assert "ed.shell: timed out after" in ed.vm.stack[-1]


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    status = Path(f"/proc/{pid}/status")
    if status.exists():
        try:
            for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("State:") and "Z" in line.split():
                    return False
        except Exception:
            pass
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@pytest.mark.skipif(os.name != "posix", reason="requires POSIX fork/session semantics")
def test_bounded_shell_timeout_reaps_detached_grandchild(tmp_path: Path) -> None:
    pidfile = tmp_path / "grandchild.pid"
    source = (
        "import os, pathlib, time\n"
        f"pidfile = pathlib.Path({str(pidfile)!r})\n"
        "child = os.fork()\n"
        "if child == 0:\n"
        "    os.setsid()\n"
        "    time.sleep(30)\n"
        "else:\n"
        "    pidfile.write_text(str(child), encoding='utf-8')\n"
        "    time.sleep(30)\n"
    )

    result = run_shell_command_bounded(
        _python_command(source),
        timeout_seconds=0.3,
        max_output_bytes=1024,
    )

    assert result.returncode == 124
    assert result.timed_out is True
    child_pid = int(pidfile.read_text(encoding="utf-8"))
    for _ in range(30):
        if not _pid_alive(child_pid):
            break
        time.sleep(0.1)
    assert not _pid_alive(child_pid)


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/self/fd").is_dir(),
    reason="escaped capture-pipe owner proof requires Linux /proc",
)
def test_bounded_shell_success_reaps_background_pipe_owner(tmp_path: Path) -> None:
    pidfile = tmp_path / "background-pipe-owner.pid"
    child_source = "import time; time.sleep(30)"
    source = (
        "import subprocess, sys, time\n"
        f"pidfile = {str(pidfile)!r}\n"
        "child = subprocess.Popen("
        f"[sys.executable, '-S', '-c', {child_source!r}], start_new_session=True)\n"
        "open(pidfile, 'w', encoding='utf-8').write(str(child.pid))\n"
        "deadline = time.monotonic() + 1.0\n"
        "while not __import__('pathlib').Path(pidfile).exists() "
        "and time.monotonic() < deadline:\n"
        "    time.sleep(0.01)\n"
    )

    started = time.monotonic()
    result = run_shell_command_bounded(
        _python_command(source),
        timeout_seconds=2.0,
        max_output_bytes=1024,
    )
    elapsed = time.monotonic() - started

    assert result.returncode == 0
    assert pidfile.is_file()
    child_pid = int(pidfile.read_text(encoding="utf-8"))
    try:
        deadline = time.monotonic() + 2.0
        while _pid_alive(child_pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        assert not _pid_alive(child_pid)
        assert elapsed < 2.0
        assert not any(
            thread.name.startswith("micromax-process-")
            for thread in threading.enumerate()
        )
    finally:
        try:
            os.killpg(child_pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            with suppress(OSError, ProcessLookupError):
                os.kill(child_pid, signal.SIGKILL)
