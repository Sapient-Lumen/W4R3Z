from __future__ import annotations

from pathlib import Path

import yaml

import pytest

from vhk.project.loader import load_project
from vhk.core.runner import Runner
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


def test_cursorpos_hyprctl_parses_numbers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "hyprctl")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "abc")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    import vhk.system.cursor_pos as cursor_pos_mod

    def fake_run(cmd, capture_output=True, text=True):
        assert cmd[:2] == [str(tmp_path / "hyprctl"), "cursorpos"]

        class R:
            returncode = 0
            stdout = "123, 456\n"
            stderr = ""

        return R()

    monkeypatch.setattr(cursor_pos_mod.subprocess, "run", fake_run)
    pos = cursor_pos_mod.get_cursor_pos()
    assert (pos.x, pos.y, pos.backend) == (123, 456, "hyprctl")


def test_cursorpos_wl_find_cursor_uses_emulate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "wl-find-cursor")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    monkeypatch.setenv("VHK_WL_FIND_CURSOR_EMULATE", "ydotool mousemove 0 1")

    import vhk.system.cursor_pos as cursor_pos_mod

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = "10 20\n"
            stderr = ""

        return R()

    monkeypatch.setattr(cursor_pos_mod.subprocess, "run", fake_run)
    pos = cursor_pos_mod.get_cursor_pos()
    assert pos.x == 10 and pos.y == 20 and pos.backend == "wl-find-cursor"
    assert calls == [[str(tmp_path / "wl-find-cursor"), "-e", "ydotool mousemove 0 1", "-p"]]


def test_runner_get_cursor_pos_step_sets_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "GetCursorPos"},
                {"type": "Return", "value_expr": "str(cursor_x)"},
            ],
        }
    }
    proj_dir = _write_project(tmp_path, manifest, macros)
    proj = load_project(proj_dir)

    import vhk.system.cursor_pos as cursor_pos_mod

    monkeypatch.setattr(cursor_pos_mod, "get_cursor_pos", lambda: cursor_pos_mod.CursorPos(7, 9, "test"))

    res = Runner(proj).run("m")
    assert res.ok is True
    assert res.vars is not None
    assert res.vars["cursor_x"] == 7
    assert res.vars["cursor_y"] == 9
    assert res.vars["cursorpos_backend"] == "test"
    assert res.vars["return_value"] == "7"


def test_ydotool_key_translates_chord_to_keycodes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    import vhk.system.input as input_mod

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)
    input_mod.key("ctrl+alt+f1")
    assert calls == [[str(tmp_path / "ydotool"), "key", "29:1", "56:1", "59:1", "59:0", "56:0", "29:0"]]


def test_ydotool_mouse_click_supports_down_up(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    import vhk.system.input as input_mod

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)
    input_mod.mouse_click(1, down=True)
    input_mod.mouse_click(1, up=True)
    input_mod.mouse_click(3)
    assert calls == [
        [str(tmp_path / "ydotool"), "click", "0x40"],
        [str(tmp_path / "ydotool"), "click", "0x80"],
        [str(tmp_path / "ydotool"), "click", "0xc1"],
    ]


def test_ydotool_mousemove_absolute_defaults_to_reset_relative(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("VHK_YDOTOOL_ABSOLUTE_METHOD", raising=False)

    import vhk.system.input as input_mod

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None, env=None):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)
    input_mod.mouse_move(x=10, y=20)
    assert calls == [
        [str(tmp_path / "ydotool"), "mousemove", "--absolute", "0", "0"],
        [str(tmp_path / "ydotool"), "mousemove", "10", "20"],
    ]


def test_ydotool_mousemove_absolute_native_can_be_forced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("VHK_YDOTOOL_ABSOLUTE_METHOD", "native")

    import vhk.system.input as input_mod

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None, env=None):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)
    input_mod.mouse_move(x=10, y=20)
    assert calls == [[str(tmp_path / "ydotool"), "mousemove", "--absolute", "10", "20"]]


def test_ydotool_mousemove_respects_pixel_scale(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    set_preferred_backend("wayland")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("VHK_YDOTOOL_PIXEL_SCALE", "0.5")
    monkeypatch.delenv("VHK_YDOTOOL_ABSOLUTE_METHOD", raising=False)

    import vhk.system.input as input_mod

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None, env=None):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)
    input_mod.mouse_move(x=11, y=21)
    # reset_relative: absolute reset + scaled relative move (rounded)
    assert calls == [
        [str(tmp_path / "ydotool"), "mousemove", "--absolute", "0", "0"],
        [str(tmp_path / "ydotool"), "mousemove", "6", "10"],
    ]
