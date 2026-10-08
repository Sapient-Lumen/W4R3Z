from __future__ import annotations

import os
from pathlib import Path
import signal
import time
from types import SimpleNamespace

import pytest

from micromax_editor import editor as editor_module
from micromax_editor.editor import Editor
from micromax_editor.host_process import BoundedProcessResult
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor import open_url_child
from micromax_editor import open_url_process


def _call_host(ed: Editor, name: str) -> None:
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<test>")


@pytest.mark.parametrize(
    ("opened", "expected"),
    [(True, 0), (False, 1)],
)
def test_open_url_child_reports_browser_result(monkeypatch, opened: bool, expected: int) -> None:
    calls: list[tuple[str, int]] = []

    def fake_open(url: str, *, new: int = 0) -> bool:
        calls.append((url, new))
        return opened

    monkeypatch.setattr(open_url_child.webbrowser, "open", fake_open)

    assert open_url_child.main(["https://example.invalid/child"]) == expected
    assert calls == [("https://example.invalid/child", 2)]


def test_open_url_child_contains_browser_exception(monkeypatch, capsys) -> None:
    def fail_open(_url: str, *, new: int = 0) -> bool:
        raise RuntimeError(f"launcher failed at mode {new}")

    monkeypatch.setattr(open_url_child.webbrowser, "open", fail_open)

    assert open_url_child.main(["https://example.invalid/failure"]) == 1
    assert "launcher failed at mode 2" in capsys.readouterr().err


def test_open_url_parent_uses_isolated_bounded_child(monkeypatch) -> None:
    seen: dict[str, object] = {}

    def fake_run(argv: list[str], **kwargs: object) -> BoundedProcessResult:
        seen["argv"] = list(argv)
        seen.update(kwargs)
        return BoundedProcessResult(0, "", "")

    monkeypatch.setattr(open_url_process, "run_argv_bounded", fake_run)

    result = open_url_process.open_external_url_bounded(
        "https://example.invalid/path",
        timeout_seconds=3.5,
        max_output_bytes=1234,
        python_executable="/trusted/python",
    )

    argv = seen["argv"]
    assert isinstance(argv, list)
    assert argv[0:3] == ["/trusted/python", "-I", "-S"]
    assert Path(argv[3]).name == "open_url_child.py"
    assert Path(argv[3]).is_absolute()
    assert argv[4] == "https://example.invalid/path"
    assert seen["timeout_seconds"] == 3.5
    assert seen["max_output_bytes"] == 1234
    assert seen["label"] == "open-url helper"
    assert result.ok is True


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), -float("inf"), True])
def test_open_url_parent_replaces_nonfinite_or_boolean_deadlines(monkeypatch, timeout: object) -> None:
    seen: list[float] = []

    def fake_run(_argv: list[str], **kwargs: object) -> BoundedProcessResult:
        seen.append(float(kwargs["timeout_seconds"]))
        return BoundedProcessResult(0, "", "")

    monkeypatch.setattr(open_url_process, "run_argv_bounded", fake_run)

    result = open_url_process.open_external_url_bounded(
        "https://example.invalid/finite",
        timeout_seconds=timeout,
    )

    assert result.ok is True
    assert seen == [open_url_process.DEFAULT_OPEN_URL_TIMEOUT_SECONDS]


def test_editor_default_open_url_routes_through_bounded_helper(monkeypatch) -> None:
    seen: list[tuple[str, float]] = []

    def fake_open(url: str, *, timeout_seconds: object) -> SimpleNamespace:
        seen.append((url, float(timeout_seconds)))
        return SimpleNamespace(ok=True)

    monkeypatch.setattr(editor_module, "open_external_url_bounded", fake_open)
    ed = Editor()
    ed.options.set("cap.open-url", "true")
    ed._open_url_timeout_seconds = 2.25

    assert ed.open_url("https://example.invalid/default") is True
    assert ed._open_url_fn is None
    assert seen == [("https://example.invalid/default", 2.25)]


def _kill_test_process(pid: int) -> None:
    try:
        os.kill(int(pid), signal.SIGKILL)
    except ProcessLookupError:
        pass


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


@pytest.mark.skipif(os.name != "posix", reason="descriptor inheritance proof is POSIX-specific")
def test_successful_background_browser_does_not_inherit_capture_pipes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    marker = tmp_path / "browser-fds"
    browser = tmp_path / "background-browser"
    browser.write_text(
        "#!/bin/sh\n"
        "out=$(readlink /proc/$$/fd/1)\n"
        "err=$(readlink /proc/$$/fd/2)\n"
        f"printf '%s\\n%s\\n%s\\n' \"$$\" \"$out\" \"$err\" > {str(marker)!r}\n"
        "exec /bin/sleep 30\n",
        encoding="utf-8",
    )
    browser.chmod(0o700)
    monkeypatch.setenv("BROWSER", f"{browser} %s &")
    # This regression owns descriptor inheritance, not desktop-browser discovery.
    # Avoid CPython's separate xdg-settings probe, whose unbounded platform call
    # is intentionally contained by the parent deadline but would make this
    # success-path assertion depend on the host desktop.
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

    started = time.monotonic()
    result = open_url_process.open_external_url_bounded(
        "https://example.invalid/background-browser",
        timeout_seconds=4.0,
    )
    elapsed = time.monotonic() - started

    assert result.ok is True, result.reason
    assert elapsed < 4.0
    deadline = time.monotonic() + 2.0
    while not marker.is_file() and time.monotonic() < deadline:
        time.sleep(0.02)
    rows = marker.read_text(encoding="utf-8").splitlines()
    assert len(rows) >= 3
    pid = int(rows[0])
    try:
        assert rows[1:] == [os.devnull, os.devnull]
    finally:
        _kill_test_process(pid)


@pytest.mark.skipif(os.name != "posix", reason="desktop-discovery teardown proof is POSIX-specific")
def test_open_url_parent_deadline_contains_desktop_controller_discovery(
    tmp_path: Path,
    monkeypatch,
) -> None:
    marker = tmp_path / "xdg-settings.pid"
    probe = tmp_path / "xdg-settings"
    probe.write_text(
        "#!/bin/sh\n"
        f"printf '%s' \"$$\" > {str(marker)!r}\n"
        "exec /bin/sleep 30\n",
        encoding="utf-8",
    )
    probe.chmod(0o700)
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":micromax-test")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("TERM", raising=False)
    monkeypatch.setenv("BROWSER", "/bin/true")

    started = time.monotonic()
    result = open_url_process.open_external_url_bounded(
        "https://example.invalid/desktop-discovery",
        timeout_seconds=0.5,
    )
    elapsed = time.monotonic() - started

    assert result.ok is False
    assert result.timed_out is True
    assert elapsed < 5.0
    assert marker.is_file(), "xdg-settings probe did not start before the deadline"
    pid = int(marker.read_text(encoding="utf-8"))
    try:
        deadline = time.monotonic() + 2.0
        while _pid_is_live(pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        assert _pid_is_live(pid) is False
    finally:
        _kill_test_process(pid)


@pytest.mark.skipif(os.name != "posix", reason="process-group liveness proof is POSIX-specific")
def test_open_url_hostcall_times_out_browser_process_and_keeps_vm_live(
    tmp_path: Path,
    monkeypatch,
) -> None:
    marker = tmp_path / "browser.pid"
    browser = tmp_path / "blocking-browser"
    browser.write_text(
        "#!/bin/sh\n"
        f"printf '%s' \"$$\" > {str(marker)!r}\n"
        "exec /bin/sleep 30\n",
        encoding="utf-8",
    )
    browser.chmod(0o700)
    monkeypatch.setenv("BROWSER", str(browser))

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.options.set("cap.open-url", "true")
    ed._open_url_timeout_seconds = 4.0
    ed.vm.stack[:] = ["https://example.invalid/blocking-browser"]

    started = time.monotonic()
    _call_host(ed, "ed.open-url")
    elapsed = time.monotonic() - started

    assert ed.vm.stack == [0]
    assert elapsed < 10.0
    assert marker.is_file(), "browser helper did not start before the deadline"
    pid = int(marker.read_text(encoding="utf-8"))
    try:
        deadline = time.monotonic() + 3.0
        while _pid_is_live(pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        assert _pid_is_live(pid) is False
    finally:
        _kill_test_process(pid)

    ed.vm.stack.clear()
    ed.vm.eval("1 2 +", filename="<post-timeout>")
    assert ed.vm.stack == [3]
