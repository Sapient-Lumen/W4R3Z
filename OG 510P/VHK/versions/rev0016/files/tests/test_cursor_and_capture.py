from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.core.models import Region
from vhk.project.loader import load_project
from vhk.system import cursor as cursor_mod
from vhk.system import input as input_mod
from vhk.system import screenshot as screenshot_mod
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


def test_choose_cursor_backend_prefers_unclutter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "unclutter")
    _mkexe(tmp_path, "xbanish")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)

    b = cursor_mod.choose_backend()
    assert b is not None
    assert b.name == "unclutter"


def test_choose_screenshot_backend_x11_prefers_scrot_before_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "scrot")
    _mkexe(tmp_path, "import")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)

    b = screenshot_mod.choose_backend()
    assert b is not None
    assert b.name == "scrot"


def test_capture_scrot_builds_expected_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "scrot")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[cmd.index("-F") + 1])
        out_path.write_bytes(b"png")

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "shot.png"
    screenshot_mod.capture(out, region=Region(x=1, y=2, w=30, h=40))
    assert calls == [[str(tmp_path / "scrot"), "-a", "1,2,30,40", "-z", "-F", str(out)]]
    assert out.exists()


def test_capture_xwd_convert_pipeline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "xwd")
    _mkexe(tmp_path, "convert")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)

    popen_calls: list[list[str]] = []
    run_calls: list[list[str]] = []

    class FakeStdout:
        def close(self):
            pass

    class FakeStderr:
        def read(self):
            return b""

    class FakePopen:
        def __init__(self, cmd, stdout=None, stderr=None):
            popen_calls.append(cmd)
            self.stdout = FakeStdout()
            self.stderr = FakeStderr()

        def poll(self):
            return None

        def wait(self):
            return 0

    def fake_run(cmd, stdin=None, capture_output=True):
        run_calls.append(cmd)
        target = cmd[-1]
        if isinstance(target, str) and target.startswith("PNG32:"):
            target = target.split(":", 1)[1]
        Path(target).write_bytes(b"png")

        class R:
            returncode = 0
            stderr = b""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)
    monkeypatch.setattr(screenshot_mod, "_which", lambda cmd: str(tmp_path / cmd) if (tmp_path / cmd).exists() else None)

    out = tmp_path / "root.png"
    screenshot_mod.capture(out)
    assert popen_calls == [[str(tmp_path / "xwd"), "-root", "-silent"]]
    assert run_calls == [[str(tmp_path / "convert"), "xwd:-", f"PNG32:{out}"]]
    assert out.exists()


def test_reset_modifiers_xdotool_emits_keyup_sequence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "xdotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)
    input_mod.reset_modifiers()
    assert calls == [
        [str(tmp_path / "xdotool"), "keyup", "Shift_L"],
        [str(tmp_path / "xdotool"), "keyup", "Shift_R"],
        [str(tmp_path / "xdotool"), "keyup", "Control_L"],
        [str(tmp_path / "xdotool"), "keyup", "Control_R"],
        [str(tmp_path / "xdotool"), "keyup", "Alt_L"],
        [str(tmp_path / "xdotool"), "keyup", "Alt_R"],
        [str(tmp_path / "xdotool"), "keyup", "Super_L"],
        [str(tmp_path / "xdotool"), "keyup", "Super_R"],
    ]


def test_runner_cursor_setting_and_steps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False, "hide_cursor_during_run": True},
        "macros": {"m": "macros/m.yaml"},
    }
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "CursorShow"},
                {"type": "CursorHide"},
                {"type": "ResetModifiers"},
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    calls: list[tuple[str, str | None]] = []

    class Handle:
        backend = "unclutter"

    monkeypatch.setattr("vhk.core.runner.cursor_mod.hide_cursor", lambda: calls.append(("hide", None)) or Handle())
    monkeypatch.setattr("vhk.core.runner.cursor_mod.show_cursor", lambda handle: calls.append(("show", getattr(handle, "backend", None))))
    monkeypatch.setattr("vhk.core.runner.input_mod.reset_modifiers", lambda: calls.append(("reset", None)))

    res = Runner(project).run("m")
    assert res.ok
    assert calls == [
        ("hide", None),
        ("show", "unclutter"),
        ("hide", None),
        ("reset", None),
        ("show", "unclutter"),
    ]
