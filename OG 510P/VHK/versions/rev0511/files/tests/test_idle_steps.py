from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.session import set_preferred_backend


@pytest.fixture(autouse=True)
def _reset_backend():
    set_preferred_backend("auto")
    yield
    set_preferred_backend("auto")


def _mkexe(tmp_path: Path, name: str) -> Path:
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)
    return p


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_get_idle_ms_prefers_xprintidle_on_x11(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("x11")
    _mkexe(tmp_path, "xprintidle")
    monkeypatch.setenv("PATH", str(tmp_path))

    import vhk.system.idle as idle_mod

    def fake_run(cmd, capture_output=True, text=True):
        assert cmd == [str(tmp_path / "xprintidle")]

        class R:
            returncode = 0
            stdout = "4321\n"
            stderr = ""

        return R()

    monkeypatch.setattr(idle_mod.subprocess, "run", fake_run)
    sample = idle_mod.get_idle_ms()
    assert sample.ms == 4321
    assert sample.backend == "x11"
    assert sample.source == "xprintidle"


def test_get_idle_ms_uses_mutter_idle_monitor_on_wayland(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "gdbus")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    import vhk.system.idle as idle_mod

    def fake_run(cmd, capture_output=True, text=True):
        assert cmd[:4] == [str(tmp_path / "gdbus"), "call", "--session", "--dest"]

        class R:
            returncode = 0
            stdout = "(uint64 9876,)\n"
            stderr = ""

        return R()

    monkeypatch.setattr(idle_mod.subprocess, "run", fake_run)
    sample = idle_mod.get_idle_ms()
    assert sample.ms == 9876
    assert sample.backend == "wayland"
    assert sample.source == "mutter-idle-monitor"


def test_wait_for_idle_retries_until_threshold(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.idle as idle_mod

    values = iter(
        [
            idle_mod.IdleSample(100, "x11", "xprintidle"),
            idle_mod.IdleSample(450, "x11", "xprintidle"),
            idle_mod.IdleSample(1200, "x11", "xprintidle"),
        ]
    )
    monkeypatch.setattr(idle_mod, "get_idle_ms", lambda: next(values))

    attempts: list[tuple[int, int, bool]] = []
    sample = idle_mod.wait_for_idle(
        1000,
        timeout_ms=100,
        poll_ms=0,
        max_attempts=5,
        on_attempt=lambda attempt, cur, ok: attempts.append((attempt, cur.ms, ok)),
    )
    assert sample.ms == 1200
    assert attempts == [(1, 100, False), (2, 450, False), (3, 1200, True)]


def test_wait_for_idle_times_out(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.idle as idle_mod

    monkeypatch.setattr(idle_mod, "get_idle_ms", lambda: idle_mod.IdleSample(50, "x11", "xprintidle"))
    with pytest.raises(TimeoutError):
        idle_mod.wait_for_idle(1000, timeout_ms=10, poll_ms=0, max_attempts=2)


def test_runner_get_idle_ms_and_wait_for_idle_steps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "GetIdleMs", "out_ms": "before_ms", "out_backend": "before_backend", "out_source": "before_source"},
                {"type": "WaitForIdle", "minimum_ms": 1000, "poll_ms": 0, "max_attempts": 1, "out_ms": "after_idle_ms", "out_backend": "after_idle_backend", "out_source": "after_idle_source"},
                {"type": "WaitForUserActivity", "maximum_ms": 1500, "armed_after_ms": 5000, "poll_ms": 0, "max_attempts": 1, "out_ms": "after_active_ms", "out_backend": "after_active_backend", "out_source": "after_active_source"},
                {"type": "Return", "value_expr": "str(after_active_ms)"},
            ],
        }
    }
    proj_dir = _write_project(tmp_path, manifest, macros)
    proj = load_project(proj_dir)

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.idle_mod, "get_idle_ms", lambda: runner_mod.idle_mod.IdleSample(123, "x11", "xprintidle"))
    monkeypatch.setattr(runner_mod.idle_mod, "wait_for_idle", lambda *a, **k: runner_mod.idle_mod.IdleSample(1500, "x11", "xprintidle"))
    monkeypatch.setattr(runner_mod.idle_mod, "wait_for_user_activity", lambda *a, **k: runner_mod.idle_mod.IdleSample(80, "x11", "xprintidle"))

    res = Runner(proj).run("m")
    assert res.ok is True
    assert res.vars["before_ms"] == 123
    assert res.vars["before_backend"] == "x11"
    assert res.vars["before_source"] == "xprintidle"
    assert res.vars["after_idle_ms"] == 1500
    assert res.vars["after_idle_backend"] == "x11"
    assert res.vars["after_idle_source"] == "xprintidle"
    assert res.vars["after_active_ms"] == 80
    assert res.vars["after_active_backend"] == "x11"
    assert res.vars["after_active_source"] == "xprintidle"
    assert res.vars["return_value"] == "80"


def test_wait_for_user_activity_returns_when_idle_drops(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.idle as idle_mod

    values = iter(
        [
            idle_mod.IdleSample(6200, "x11", "xprintidle"),
            idle_mod.IdleSample(7100, "x11", "xprintidle"),
            idle_mod.IdleSample(40, "x11", "xprintidle"),
        ]
    )
    monkeypatch.setattr(idle_mod, "get_idle_ms", lambda: next(values))

    attempts: list[tuple[int, int, bool, bool]] = []
    sample = idle_mod.wait_for_user_activity(
        1500,
        armed_after_ms=5000,
        timeout_ms=100,
        poll_ms=0,
        max_attempts=5,
        on_attempt=lambda attempt, cur, armed, ok: attempts.append((attempt, cur.ms, armed, ok)),
    )
    assert sample.ms == 40
    assert attempts == [(1, 6200, True, False), (2, 7100, True, False), (3, 40, True, True)]


def test_wait_for_user_activity_can_return_immediately_when_already_active(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.idle as idle_mod

    monkeypatch.setattr(idle_mod, "get_idle_ms", lambda: idle_mod.IdleSample(120, "x11", "xprintidle"))
    sample = idle_mod.wait_for_user_activity(1500, timeout_ms=10, poll_ms=0, max_attempts=1)
    assert sample.ms == 120


def test_wait_for_user_activity_times_out_when_never_returns(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.idle as idle_mod

    monkeypatch.setattr(idle_mod, "get_idle_ms", lambda: idle_mod.IdleSample(6000, "x11", "xprintidle"))
    with pytest.raises(TimeoutError):
        idle_mod.wait_for_user_activity(1500, armed_after_ms=5000, timeout_ms=10, poll_ms=0, max_attempts=2)
