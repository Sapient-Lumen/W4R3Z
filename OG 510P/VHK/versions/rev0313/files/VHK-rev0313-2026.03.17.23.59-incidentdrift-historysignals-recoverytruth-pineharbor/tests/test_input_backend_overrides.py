from __future__ import annotations

from pathlib import Path

import pytest


def _mkexe(tmp_path: Path, name: str):
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)
    return p


@pytest.mark.parametrize("forced,expected", [
    ("dotoolc", "dotoolc"),
    ("dotool", "dotool"),
    ("ydotool", "ydotool"),
])
def test_keyboard_backend_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, forced: str, expected: str):
    _mkexe(tmp_path, "wtype")
    _mkexe(tmp_path, "dotool")
    _mkexe(tmp_path, "dotoolc")
    _mkexe(tmp_path, "ydotool")

    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("VHK_KEYBOARD_BACKEND", forced)

    from vhk.system import input as input_mod

    b = input_mod.choose_keyboard_backend()
    assert b is not None
    assert b.name == expected


def test_keyboard_backend_auto_prefers_wtype_then_dotoolc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "dotool")
    _mkexe(tmp_path, "dotoolc")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    from vhk.system import input as input_mod

    # No wtype => dotoolc
    b = input_mod.choose_keyboard_backend()
    assert b is not None
    assert b.name == "dotoolc"

    # Add wtype => wtype wins
    _mkexe(tmp_path, "wtype")
    b2 = input_mod.choose_keyboard_backend()
    assert b2 is not None
    assert b2.name == "wtype"


def test_pointer_backend_auto_prefers_dotoolc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "dotool")
    _mkexe(tmp_path, "dotoolc")
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    from vhk.system import input as input_mod

    b = input_mod.choose_pointer_backend()
    assert b is not None
    assert b.name == "dotoolc"


def test_keyboard_backend_skips_dotoolc_when_daemon_is_known_inactive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "dotool")
    _mkexe(tmp_path, "dotoolc")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    from vhk.system import input as input_mod

    monkeypatch.setattr(
        input_mod,
        "_wayland_runtime_probes",
        lambda: {
            "dotoold": {"status": "inactive", "daemon_ready": False},
            "wayland_protocols": {"status": "probe_tool_missing"},
            "ydotool_socket": {"status": "tool_missing"},
        },
    )

    b = input_mod.choose_keyboard_backend()
    assert b is not None
    assert b.name == "dotool"


def test_keyboard_backend_skips_wtype_when_virtual_keyboard_is_known_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "wtype")
    _mkexe(tmp_path, "dotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    from vhk.system import input as input_mod

    monkeypatch.setattr(
        input_mod,
        "_wayland_runtime_probes",
        lambda: {
            "dotoold": {"status": "tool_missing", "daemon_ready": False},
            "wayland_protocols": {"status": "ok", "virtual_keyboard": False},
            "ydotool_socket": {"status": "tool_missing"},
        },
    )

    b = input_mod.choose_keyboard_backend()
    assert b is not None
    assert b.name == "dotool"


def test_pointer_backend_skips_ydotool_when_socket_is_known_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    from vhk.system import input as input_mod

    monkeypatch.setattr(
        input_mod,
        "_wayland_runtime_probes",
        lambda: {
            "dotoold": {"status": "tool_missing", "daemon_ready": False},
            "wayland_protocols": {"status": "probe_tool_missing"},
            "ydotool_socket": {"status": "socket_missing"},
        },
    )

    assert input_mod.choose_pointer_backend() is None
