
from __future__ import annotations

from vhk.core.models import I3WindowSelector


def test_get_window_list_snapshot_hyprland_includes_process_name_and_pid_filter(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(aw, "detect_compositor", lambda: "hyprland")
    monkeypatch.setattr(aw, "get_process_name", lambda pid: {111: "firefox", 222: "alacritty"}.get(int(pid)))

    def fake_hyprctl(subcommand: str):
        if subcommand == "clients":
            return [
                {
                    "address": "0xabc",
                    "pid": 111,
                    "class": "Firefox",
                    "initialClass": "Firefox",
                    "title": "Mozilla Firefox",
                    "initialTitle": "Mozilla Firefox",
                    "workspace": {"id": 1, "name": "1:web"},
                    "at": [10, 20],
                    "size": [900, 700],
                },
                {
                    "address": "0xdef",
                    "pid": 222,
                    "class": "Alacritty",
                    "initialClass": "Alacritty",
                    "title": "shell",
                    "initialTitle": "shell",
                    "workspace": {"id": 2, "name": "2:term"},
                    "at": [100, 200],
                    "size": [800, 500],
                },
            ]
        if subcommand == "activewindow":
            return {"address": "0xdef"}
        raise AssertionError(subcommand)

    monkeypatch.setattr(aw, "hyprctl_json", fake_hyprctl)

    windows, wm = aw.get_window_list_snapshot(
        include_geometry=False,
        selector=I3WindowSelector(pid=222),
    )
    assert wm == "hyprland"
    assert len(windows) == 1
    assert windows[0]["pid"] == 222
    assert windows[0]["process_name"] == "alacritty"
    assert windows[0]["focused"] is True


def test_selector_matches_info_can_match_pid():
    import vhk.system.active_window as aw

    info = {"class": "Firefox", "title": "Mozilla Firefox", "pid": 4242, "focused": True}
    assert aw.selector_matches_info(I3WindowSelector(pid=4242), info, "x11") is True
    assert aw.selector_matches_info(I3WindowSelector(pid=9999), info, "x11") is False
