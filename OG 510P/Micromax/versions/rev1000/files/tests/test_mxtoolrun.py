from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import mxtoolrun  # noqa: E402


def test_format_duration_keeps_short_and_long_values_readable() -> None:
    assert mxtoolrun.format_duration(1.234) == "1.23s"
    assert mxtoolrun.format_duration(65) == "1m05s"


def test_isolated_python_env_prepends_src_and_disables_host_pytest(monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", raising=False)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(["/elsewhere"]))

    env = mxtoolrun.isolated_python_env(ROOT)

    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(ROOT / "src")


def test_run_captured_records_output_and_timing() -> None:
    result = mxtoolrun.run_captured(
        [sys.executable, "-c", "print('toolrun-ok')"],
        cwd=ROOT,
        env=mxtoolrun.isolated_python_env(ROOT),
        timeout_seconds=5,
        label="smoke",
    )

    assert result.returncode == 0
    assert result.timed_out is False
    assert "toolrun-ok" in result.output
    assert result.elapsed_seconds >= 0
    assert result.as_json()["output_tail"] == "toolrun-ok"


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


def test_run_captured_timeout_reaps_detached_grandchild(tmp_path: Path) -> None:
    pidfile = tmp_path / "grandchild.pid"
    script = (
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

    result = mxtoolrun.run_captured(
        [sys.executable, "-S", "-c", script],
        cwd=ROOT,
        env=mxtoolrun.isolated_python_env(ROOT),
        timeout_seconds=0.5,
        label="detached-grandchild",
    )

    assert result.returncode == 124
    assert result.timed_out is True
    child_pid = int(pidfile.read_text(encoding="utf-8"))
    for _ in range(30):
        if not _pid_alive(child_pid):
            break
        import time

        time.sleep(0.1)
    assert not _pid_alive(child_pid)

