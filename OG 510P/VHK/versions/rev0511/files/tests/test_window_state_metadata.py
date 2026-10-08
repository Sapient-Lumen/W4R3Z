from __future__ import annotations

import subprocess

from vhk.system.cursor_pos import CursorPos


def _cp(args: list[str], rc: int, out: str = "", err: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=args, returncode=rc, stdout=out, stderr=err)


def test_get_window_list_snapshot_i3like_includes_state_fields(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(aw, "detect_compositor", lambda: "sway")
    monkeypatch.setattr(aw, "discover_socket_path", lambda: "/tmp/fake-sway.sock")

    class _Conn:
        def __init__(self, socket_path: str):
            self.socket_path = socket_path

        def get_tree(self):
            return {
                "type": "root",
                "nodes": [
                    {
                        "type": "workspace",
                        "name": "1:web",
                        "nodes": [
                            {
                                "id": 42,
                                "type": "con",
                                "name": "Mozilla Firefox",
                                "app_id": "firefox",
                                "pid": 1001,
                                "focused": True,
                                "urgent": False,
                                "visible": True,
                                "sticky": False,
                                "floating": "user_on",
                                "fullscreen_mode": 2,
                                "rect": {"x": 10, "y": 20, "width": 900, "height": 700},
                                "window_rect": {"x": 0, "y": 0, "width": 900, "height": 700},
                                "window_properties": {"class": "Firefox", "title": "Mozilla Firefox"},
                                "nodes": [],
                                "floating_nodes": [],
                            }
                        ],
                        "floating_nodes": [],
                    }
                ],
                "floating_nodes": [],
            }

    monkeypatch.setattr(aw, "I3Connection", _Conn)
    monkeypatch.setattr(aw, "get_process_name", lambda pid: "firefox" if int(pid) == 1001 else None)

    windows, wm = aw.get_window_list_snapshot(include_geometry=True)
    assert wm == "sway"
    assert len(windows) == 1
    row = windows[0]
    assert row["visible"] is True
    assert row["floating"] is True
    assert row["fullscreen"] is True
    assert row["fullscreen_mode"] == 2
    assert row["sticky"] is False
    assert row["process_name"] == "firefox"


def test_get_window_list_snapshot_hyprland_includes_state_fields(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(aw, "detect_compositor", lambda: "hyprland")
    monkeypatch.setattr(aw, "get_process_name", lambda pid: "steam" if int(pid) == 222 else None)

    def fake_hyprctl(subcommand: str):
        if subcommand == "clients":
            return [
                {
                    "address": "0xdef",
                    "pid": 222,
                    "class": "steam",
                    "initialClass": "steam",
                    "title": "Friends List",
                    "initialTitle": "Friends List",
                    "workspace": {"id": 2, "name": "2"},
                    "at": [100, 200],
                    "size": [800, 500],
                    "mapped": 1,
                    "hidden": 0,
                    "floating": 1,
                    "pinned": 0,
                    "fullscreen": 1,
                    "fullscreenmode": 1,
                    "xwayland": 1,
                }
            ]
        if subcommand == "activewindow":
            return {"address": "0xdef"}
        raise AssertionError(subcommand)

    monkeypatch.setattr(aw, "hyprctl_json", fake_hyprctl)

    windows, wm = aw.get_window_list_snapshot(include_geometry=True)
    assert wm == "hyprland"
    assert len(windows) == 1
    row = windows[0]
    assert row["mapped"] is True
    assert row["hidden"] is False
    assert row["visible"] is True
    assert row["floating"] is True
    assert row["pinned"] is False
    assert row["fullscreen"] is True
    assert row["fullscreen_mode"] == 1
    assert row["process_name"] == "steam"


def test_get_window_at_cursor_skips_non_visible_rows():
    import vhk.system.active_window as aw

    rows = [
        {
            "id": "0x1",
            "title": "Hidden parent",
            "visible": False,
            "focused": True,
            "geometry": {"rect": {"x": 0, "y": 0, "w": 500, "h": 500}, "client": None},
        },
        {
            "id": "0x2",
            "title": "Visible popup",
            "visible": True,
            "focused": False,
            "geometry": {"rect": {"x": 100, "y": 100, "w": 120, "h": 90}, "client": None},
        },
    ]

    row = aw._choose_window_at_point(rows, 110, 110)
    assert row is not None
    assert row["id"] == "0x2"


def test_active_window_x11_info_includes_state_fields(monkeypatch):
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
                        '_NET_WM_PID(CARDINAL) = 4242',
                        '_NET_WM_DESKTOP(CARDINAL) = 0',
                        '_NET_WM_STATE(ATOM) = _NET_WM_STATE_FULLSCREEN, _NET_WM_STATE_STICKY',
                        '',
                    ]
                ),
            )
        if cmd[:2] == ["/bin/xprop", "-root"] and "_NET_DESKTOP_NAMES" in cmd:
            return _cp(cmd, 0, '_NET_DESKTOP_NAMES(UTF8_STRING) = "Web", "Chat"\n')
        if cmd[:2] == ["/bin/xprop", "-root"] and "_NET_CURRENT_DESKTOP" in cmd:
            return _cp(cmd, 0, '_NET_CURRENT_DESKTOP(CARDINAL) = 0\n')
        if cmd[:2] == ["/bin/xprop", "-root"] and "_NET_ACTIVE_WINDOW" in cmd:
            return _cp(cmd, 0, '_NET_ACTIVE_WINDOW(WINDOW): window id # 0x3039\n')
        return _cp(cmd, 1, "", "unexpected")

    monkeypatch.setattr(aw.subprocess, "run", fake_run)

    info, wm = aw.get_active_window_info()
    assert wm == "x11"
    assert info["workspace"] == "Web"
    assert info["fullscreen"] is True
    assert info["sticky"] is True
    assert info["visible"] is True
    assert info["minimized"] is False


def test_get_window_at_cursor_snapshot_preserves_state_fields(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(aw, "detect_compositor", lambda: "hyprland")
    monkeypatch.setattr(aw, "get_cursor_pos", lambda: CursorPos(x=160, y=120, backend="hyprctl"))
    monkeypatch.setattr(
        aw,
        "get_window_list_snapshot",
        lambda **kwargs: (
            [
                {
                    "id": "0xaaa",
                    "title": "Hidden parent",
                    "class": "Firefox",
                    "workspace": "1:web",
                    "focused": True,
                    "visible": False,
                    "geometry": {"rect": {"x": 0, "y": 0, "w": 500, "h": 400}, "client": None},
                },
                {
                    "id": "0xbbb",
                    "title": "Popup",
                    "class": "Firefox",
                    "workspace": "1:web",
                    "focused": False,
                    "visible": True,
                    "floating": True,
                    "fullscreen": False,
                    "geometry": {"rect": {"x": 120, "y": 90, "w": 120, "h": 100}, "client": None},
                },
            ],
            "hyprland",
        ),
    )

    window, wm, cursor = aw.get_window_at_cursor_snapshot(include_geometry=True)
    assert wm == "hyprland"
    assert cursor.backend == "hyprctl"
    assert window is not None
    assert window["id"] == "0xbbb"
    assert window["visible"] is True
    assert window["floating"] is True
    assert window["fullscreen"] is False
