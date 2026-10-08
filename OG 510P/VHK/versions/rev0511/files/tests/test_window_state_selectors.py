from __future__ import annotations

from vhk.core.models import I3WindowSelector


def test_selector_matches_info_matches_state_fields_x11():
    import vhk.system.active_window as aw

    info = {
        "class": "Firefox",
        "title": "Mozilla Firefox",
        "workspace": "1:web",
        "focused": True,
        "visible": True,
        "fullscreen": True,
        "sticky": False,
        "minimized": False,
    }

    assert aw.selector_matches_info(I3WindowSelector(fullscreen=True, visible=True), info, "x11") is True
    assert aw.selector_matches_info(I3WindowSelector(fullscreen=False), info, "x11") is False
    assert aw.selector_matches_info(I3WindowSelector(minimized=False), info, "x11") is True
    assert aw.selector_matches_info(I3WindowSelector(sticky=True), info, "x11") is False



def test_selector_matches_info_matches_hyprland_focus_and_state_fields():
    import vhk.system.active_window as aw

    info = {
        "address": "0xabc",
        "class": "steam",
        "initialClass": "steam",
        "title": "Friends List",
        "initialTitle": "Friends List",
        "workspace": {"id": 2, "name": "2"},
        "pid": 222,
        "focused": False,
        "mapped": 1,
        "hidden": 0,
        "floating": 1,
        "pinned": 1,
        "fullscreenmode": 2,
    }

    selector = I3WindowSelector(
        wm_class="steam",
        workspace="2",
        focused=False,
        visible=True,
        floating=True,
        pinned=True,
        fullscreen=True,
        fullscreen_mode=2,
    )
    assert aw.selector_matches_info(selector, info, "hyprland") is True
    assert aw.selector_matches_info(I3WindowSelector(focused=True), info, "hyprland") is False
    assert aw.selector_matches_info(I3WindowSelector(hidden=True), info, "hyprland") is False



def test_i3_tree_node_matches_stateful_selector():
    from vhk.i3.tree import node_matches

    node = {
        "id": 55,
        "type": "con",
        "name": "Firefox",
        "app_id": "firefox",
        "pid": 111,
        "focused": True,
        "urgent": False,
        "visible": True,
        "sticky": True,
        "floating": "user_on",
        "fullscreen_mode": 1,
        "window_properties": {"class": "Firefox", "title": "Mozilla Firefox"},
    }

    assert node_matches(node, I3WindowSelector(wm_class="Firefox", visible=True, floating=True, fullscreen=True, sticky=True), "1:web") is True
    assert node_matches(node, I3WindowSelector(floating=False), "1:web") is False
    assert node_matches(node, I3WindowSelector(fullscreen_mode=2), "1:web") is False
    assert node_matches(node, I3WindowSelector(minimized=False), "1:web") is False



def test_get_window_list_snapshot_filters_by_state_hyprland(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(aw, "detect_compositor", lambda: "hyprland")
    monkeypatch.setattr(aw, "get_process_name", lambda pid: {111: "firefox", 222: "mpv"}.get(int(pid)))

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
                    "mapped": 1,
                    "hidden": 0,
                    "floating": 0,
                    "pinned": 0,
                    "fullscreen": 0,
                },
                {
                    "address": "0xdef",
                    "pid": 222,
                    "class": "mpv",
                    "initialClass": "mpv",
                    "title": "video",
                    "initialTitle": "video",
                    "workspace": {"id": 9, "name": "9"},
                    "mapped": 1,
                    "hidden": 0,
                    "floating": 1,
                    "pinned": 1,
                    "fullscreenmode": 2,
                },
            ]
        if subcommand == "activewindow":
            return {"address": "0xdef"}
        raise AssertionError(subcommand)

    monkeypatch.setattr(aw, "hyprctl_json", fake_hyprctl)

    rows, wm = aw.get_window_list_snapshot(
        selector=I3WindowSelector(floating=True, pinned=True, fullscreen=True, visible=True),
        include_geometry=False,
    )
    assert wm == "hyprland"
    assert len(rows) == 1
    assert rows[0]["id"] == "0xdef"
    assert rows[0]["process_name"] == "mpv"
