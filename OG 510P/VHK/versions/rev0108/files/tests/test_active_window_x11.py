from __future__ import annotations

import subprocess

import pytest

from vhk.core.models import I3WindowSelector


def _cp(args: list[str], rc: int, out: str = "", err: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=args, returncode=rc, stdout=out, stderr=err)


def test_active_window_x11_geometry_uses_frame_extents(monkeypatch):
    import vhk.system.active_window as aw

    # Ensure detect_backend() is x11 and compositor detection doesn't pick i3/sway/hyprland.
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("SWAYSOCK", raising=False)
    monkeypatch.delenv("I3SOCK", raising=False)
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)

    def fake_which(name: str):
        # Pretend we have all the relevant tools.
        return f"/bin/{name}"

    monkeypatch.setattr(aw.shutil, "which", fake_which)

    def fake_run(cmd, capture_output=True, text=True, **kwargs):
        cmd = list(cmd)
        if cmd[:2] == ["/bin/xdotool", "getactivewindow"]:
            return _cp(cmd, 0, "12345\n")
        if cmd[:3] == ["/bin/xdotool", "getwindowgeometry", "--shell"]:
            # xdotool(1) --shell format
            return _cp(cmd, 0, "WINDOW=12345\nX=10\nY=20\nWIDTH=300\nHEIGHT=200\nSCREEN=0\n")
        if cmd[:3] == ["/bin/xprop", "-id", "0x3039"] and "_NET_FRAME_EXTENTS" in cmd:
            return _cp(cmd, 0, "_NET_FRAME_EXTENTS(CARDINAL) = 5, 5, 19, 5\n")
        if cmd[:2] == ["/bin/xprop", "-root"] and "_NET_DESKTOP_NAMES" in cmd:
            return _cp(cmd, 0, '_NET_DESKTOP_NAMES(UTF8_STRING) = "1", "2"\n')
        if cmd[:2] == ["/bin/xprop", "-root"] and "_NET_ACTIVE_WINDOW" in cmd:
            return _cp(cmd, 0, "_NET_ACTIVE_WINDOW(WINDOW): window id # 0x3039\n")
        return _cp(cmd, 1, "", "unexpected")

    monkeypatch.setattr(aw.subprocess, "run", fake_run)

    rect, client, wm = aw.get_active_window_geometry()
    assert wm == "x11"
    assert rect == {"x": 10, "y": 20, "w": 300, "h": 200}
    assert client == {"x": 15, "y": 39, "w": 290, "h": 176}


def test_active_window_x11_info_and_match(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("SWAYSOCK", raising=False)
    monkeypatch.delenv("I3SOCK", raising=False)
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)

    monkeypatch.setattr(aw.shutil, "which", lambda name: f"/bin/{name}")

    def fake_run(cmd, capture_output=True, text=True, **kwargs):
        cmd = list(cmd)
        if cmd[:2] == ["/bin/xdotool", "getactivewindow"]:
            return _cp(cmd, 0, "12345\n")
        if cmd[:3] == ["/bin/xprop", "-id", "0x3039"] and "WM_CLASS" in cmd:
            return _cp(
                cmd,
                0,
                "\n".join(
                    [
                        'WM_CLASS(STRING) = "Navigator", "Firefox"',
                        '_NET_WM_NAME(UTF8_STRING) = "Mozilla Firefox"',
                        'WM_WINDOW_ROLE(STRING) = "browser"',
                        "_NET_WM_PID(CARDINAL) = 4242",
                        "_NET_WM_DESKTOP(CARDINAL) = 0",
                        "",
                    ]
                ),
            )
        if cmd[:2] == ["/bin/xprop", "-root"] and "_NET_DESKTOP_NAMES" in cmd:
            return _cp(cmd, 0, '_NET_DESKTOP_NAMES(UTF8_STRING) = "Web", "Chat"\n')
        if cmd[:2] == ["/bin/xprop", "-root"] and "_NET_ACTIVE_WINDOW" in cmd:
            return _cp(cmd, 0, "_NET_ACTIVE_WINDOW(WINDOW): window id # 0x3039\n")
        return _cp(cmd, 1, "", "unexpected")

    monkeypatch.setattr(aw.subprocess, "run", fake_run)

    info, wm = aw.get_active_window_info()
    assert wm == "x11"
    assert info["class"] == "Firefox"
    assert info["instance"] == "Navigator"
    assert info["title"] == "Mozilla Firefox"
    assert info["window_role"] == "browser"
    assert info["workspace"] == "Web"

    ok, wm2 = aw.active_window_matches(I3WindowSelector(wm_class="Firefox", title="Mozilla Firefox"))
    assert wm2 == "x11"
    assert ok

    bad, _ = aw.active_window_matches(I3WindowSelector(wm_class="Alacritty"))
    assert bad is False
