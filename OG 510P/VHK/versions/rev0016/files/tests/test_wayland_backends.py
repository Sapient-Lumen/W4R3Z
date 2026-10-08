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
