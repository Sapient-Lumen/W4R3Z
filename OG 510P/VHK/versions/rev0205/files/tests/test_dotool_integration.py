from __future__ import annotations

from pathlib import Path

import pytest

from vhk.system import display as display_mod
from vhk.system import input as input_mod


def _mkexe(tmp_path: Path, name: str) -> None:
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)


def test_choose_keyboard_backend_on_gnome_prefers_uinput_helpers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "wtype")
    _mkexe(tmp_path, "dotoolc")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")

    kb = input_mod.choose_keyboard_backend()
    assert kb is not None
    assert kb.name == "dotoolc"


def test_dotool_reset_modifiers_uses_keyup_calls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "dotoolc")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    calls: list[dict] = []

    def fake_run(cmd, capture_output=True, text=True, input=None, env=None):
        calls.append({"cmd": cmd, "input": input})

        class R:
            returncode = 0
            stderr = ""
            stdout = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.reset_modifiers()
    sent = [c["input"].strip() for c in calls if c.get("input")]
    assert sent == ["keyup shift", "keyup ctrl", "keyup alt", "keyup super"]


def test_dotool_mouse_move_click_and_wheel(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "dotoolc")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)

    monkeypatch.setattr(display_mod, "get_virtual_screen_size", lambda **_: display_mod.ScreenSize(1000, 1000, "test"))

    calls: list[dict] = []

    def fake_run(cmd, capture_output=True, text=True, input=None, env=None):
        calls.append({"cmd": cmd, "input": input})

        class R:
            returncode = 0
            stderr = ""
            stdout = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.mouse_move(x=100, y=200)
    input_mod.mouse_move(dx=5, dy=-3, relative=True)
    input_mod.mouse_click(1)
    input_mod.mouse_click(1, down=True)
    input_mod.mouse_click(1, up=True)
    input_mod.mouse_wheel(3, axis="vertical")
    input_mod.mouse_wheel(-2, axis="horizontal")

    sent = [c["input"].strip() for c in calls if c.get("input")]
    assert sent[0].startswith("mouseto ")
    assert "0.100000" in sent[0] and "0.200000" in sent[0]
    assert sent[1] == "mousemove 5 -3"
    assert sent[2] == "click left"
    assert sent[3] == "buttondown left"
    assert sent[4] == "buttonup left"
    assert sent[5] == "wheel 3"
    assert sent[6] == "hwheel -2"


def test_dotool_typedelay_is_emitted_for_delay_ms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "dotoolc")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")

    calls: list[dict] = []

    def fake_run(cmd, capture_output=True, text=True, input=None, env=None):
        calls.append({"cmd": cmd, "input": input})

        class R:
            returncode = 0
            stderr = ""
            stdout = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    input_mod.type_text("hi", delay_ms_per_char=25)
    assert calls
    script = (calls[-1]["input"] or "")
    assert script.startswith("typedelay 25\n")
    assert script.rstrip().endswith("typedelay 0")
