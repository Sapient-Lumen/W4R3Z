from __future__ import annotations

import os
from pathlib import Path

import pytest

from vhk.system import clipboard as clipboard_mod
from vhk.system import input as input_mod
from vhk.system import screenshot as screenshot_mod
from vhk.system.session import set_preferred_backend


@pytest.fixture(autouse=True)
def _reset_backend():
    # Ensure tests don't leak the preferred backend across modules.
    set_preferred_backend("auto")
    yield
    set_preferred_backend("auto")


def _mkexe(tmp_path: Path, name: str) -> None:
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)


def test_choose_screenshot_backend_wayland_prefers_grim(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "grim")
    _mkexe(tmp_path, "maim")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    b = screenshot_mod.choose_backend()
    assert b is not None
    assert b.name == "grim"


def test_choose_screenshot_backend_wayland_falls_back_to_spectacle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "spectacle")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    b = screenshot_mod.choose_backend()
    assert b is not None
    assert b.name == "spectacle"


def test_choose_screenshot_backend_wayland_falls_back_to_gnome_screenshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "gnome-screenshot")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    b = screenshot_mod.choose_backend()
    assert b is not None
    assert b.name == "gnome-screenshot"


def test_choose_screenshot_backend_respects_env_override_portal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "gdbus")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("VHK_SCREENSHOT_BACKEND", "portal")
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    b = screenshot_mod.choose_backend()
    assert b is not None
    assert b.name == "portal"


def test_choose_clipboard_backend_wayland_prefers_wl_clipboard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "wl-copy")
    _mkexe(tmp_path, "wl-paste")
    _mkexe(tmp_path, "xclip")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    b = clipboard_mod.choose_backend()
    assert b is not None
    assert b.name == "wl-clipboard"


def test_wtype_key_chord_builds_expected_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "wtype")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    calls: list[dict] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append({"cmd": cmd, "input": input})
        class R:
            returncode = 0
            stderr = ""
        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.key("ctrl+alt+t")
    assert calls
    assert calls[-1]["cmd"][:1] == [str(tmp_path / "wtype")]
    # wtype: press modifiers, press+release key, release modifiers in reverse.
    assert calls[-1]["cmd"][1:] == ["-M", "ctrl", "-M", "alt", "-k", "t", "-m", "alt", "-m", "ctrl"]


def test_wtype_type_text_uses_stdin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "wtype")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    calls: list[dict] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append({"cmd": cmd, "input": input})
        class R:
            returncode = 0
            stderr = ""
        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.type_text("hello", delay_ms_per_char=12)
    assert calls
    assert calls[-1]["cmd"] == [str(tmp_path / "wtype"), "-d", "12", "-"]
    assert calls[-1]["input"] == "hello"


def test_hyprland_absolute_mouse_move_prefers_hyprctl_dispatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "hyprctl")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "sig")

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)
        class R:
            returncode = 0
            stderr = ""
            stdout = ""
        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.mouse_move(x=100, y=200)
    assert calls
    assert calls[-1] == [str(tmp_path / "hyprctl"), "dispatch", "movecursor", "100", "200"]


def test_hyprland_relative_mouse_move_uses_ydotool_when_available(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "hyprctl")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "sig")

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)
        class R:
            returncode = 0
            stderr = ""
            stdout = ""
        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.mouse_move(dx=5, dy=-3, relative=True)
    assert calls
    assert calls[-1] == [str(tmp_path / "ydotool"), "mousemove", "5", "-3"]


def test_hyprland_relative_mouse_move_falls_back_to_cursorpos_when_no_ydotool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "hyprctl")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "sig")

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)
        class R:
            pass

        r = R()
        r.returncode = 0
        r.stderr = ""
        if cmd[1:] == ["cursorpos"]:
            r.stdout = "100 200\n"
        else:
            r.stdout = "ok\n"
        return r

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.mouse_move(dx=10, dy=20, relative=True)
    # First call should read cursorpos.
    assert calls[0] == [str(tmp_path / "hyprctl"), "cursorpos"]
    # Second should dispatch movecursor to 110,220.
    assert calls[1] == [str(tmp_path / "hyprctl"), "dispatch", "movecursor", "110", "220"]


from vhk.system.session import detect_backend


def test_detect_backend_prefers_wayland_when_both_displays_exist(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("VHK_BACKEND", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    assert detect_backend() == "wayland"


def test_detect_backend_can_still_be_forced_to_x11(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VHK_BACKEND", "x11")
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    assert detect_backend() == "x11"


def test_keydown_falls_back_to_ydotool_when_wtype_lacks_virtual_keyboard_protocol(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "wtype")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)
        class R:
            pass
        r = R()
        if cmd[0].endswith("wtype"):
            r.returncode = 1
            r.stdout = ""
            r.stderr = "Compositor does not support the virtual keyboard protocol"
        else:
            r.returncode = 0
            r.stdout = ""
            r.stderr = ""
        return r

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.key_down("ctrl")
    assert calls[0][0] == str(tmp_path / "wtype")
    assert calls[1] == [str(tmp_path / "ydotool"), "key", "29:1"]


def test_keyup_and_resetmodifiers_work_with_ydotool_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.key_up("ctrl")
    assert calls[-1] == [str(tmp_path / "ydotool"), "key", "29:0"]

    input_mod.reset_modifiers()
    assert calls[-1][0:2] == [str(tmp_path / "ydotool"), "key"]
    # Contains releases for shift/ctrl/alt/logo.
    assert "42:0" in calls[-1]
    assert "29:0" in calls[-1]
    assert "56:0" in calls[-1]
    assert "125:0" in calls[-1]
