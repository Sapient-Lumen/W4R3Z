from __future__ import annotations

from collections import deque

from vhk.system.wm_events import iter_wm_events



def test_polling_window_events_focus_waits_for_actual_transition(monkeypatch) -> None:
    import vhk.system.wm_events as wm_mod

    sequence = deque([
        ({"id": "0x1", "class": "Firefox", "title": "Docs"}, "x11"),
        ({"id": "0x1", "class": "Firefox", "title": "Docs"}, "x11"),
        ({"id": "0x2", "class": "kitty", "title": "shell"}, "x11"),
    ])

    monkeypatch.setattr(wm_mod, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(wm_mod.time, "sleep", lambda _s: None)

    def fake_get_active_window_info():
        if len(sequence) > 1:
            return sequence.popleft()
        return sequence[0]

    monkeypatch.setattr(wm_mod, "get_active_window_info", fake_get_active_window_info)

    it = iter_wm_events(kinds={"focus"}, poll_ms=1)
    ev = next(it)
    assert ev.kind == "focus"
    assert ev.name == "poll"
    assert ev.data == "0x2"



def test_polling_window_events_can_detect_active_title_changes(monkeypatch) -> None:
    import vhk.system.wm_events as wm_mod

    sequence = deque([
        ({"id": "0x1", "class": "Firefox", "title": "Inbox"}, "x11"),
        ({"id": "0x1", "class": "Firefox", "title": "Inbox"}, "x11"),
        ({"id": "0x1", "class": "Firefox", "title": "Compose"}, "x11"),
    ])

    monkeypatch.setattr(wm_mod, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(wm_mod.time, "sleep", lambda _s: None)

    def fake_get_active_window_info():
        if len(sequence) > 1:
            return sequence.popleft()
        return sequence[0]

    monkeypatch.setattr(wm_mod, "get_active_window_info", fake_get_active_window_info)

    it = iter_wm_events(kinds={"title"}, poll_ms=1)
    ev = next(it)
    assert ev.kind == "title"
    assert ev.name == "poll"
    assert ev.data == ("0x1", "Compose")


def test_polling_window_events_can_detect_closed_windows(monkeypatch) -> None:
    import vhk.system.wm_events as wm_mod

    rows_seq = deque([
        ([{"id": "0x1", "class": "Firefox", "title": "Docs"}, {"id": "0x2", "class": "kitty", "title": "shell"}], "x11"),
        ([{"id": "0x2", "class": "kitty", "title": "shell"}], "x11"),
    ])

    monkeypatch.setattr(wm_mod, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(wm_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(wm_mod, "get_active_window_info", lambda: ({"id": "0x2", "class": "kitty", "title": "shell"}, "x11"))

    def fake_get_window_list_snapshot(*, include_geometry=False, focused_first=True):
        assert include_geometry is False
        assert focused_first is False
        if len(rows_seq) > 1:
            return rows_seq.popleft()
        return rows_seq[0]

    monkeypatch.setattr(wm_mod, "get_window_list_snapshot", fake_get_window_list_snapshot)

    it = iter_wm_events(kinds={"close"}, poll_ms=1)
    ev = next(it)
    assert ev.kind == "close"
    assert ev.name == "poll"
    assert ev.data["id"] == "0x1"
    assert ev.data["class"] == "Firefox"



def test_polling_window_events_can_detect_new_windows(monkeypatch) -> None:
    import vhk.system.wm_events as wm_mod

    rows_seq = deque([
        ([{"id": "0x2", "class": "kitty", "title": "shell"}], "x11"),
        ([{"id": "0x2", "class": "kitty", "title": "shell"}, {"id": "0x3", "class": "Firefox", "title": "Docs"}], "x11"),
    ])

    monkeypatch.setattr(wm_mod, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(wm_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(wm_mod, "get_active_window_info", lambda: ({"id": "0x2", "class": "kitty", "title": "shell"}, "x11"))

    def fake_get_window_list_snapshot(*, include_geometry=False, focused_first=True):
        assert include_geometry is False
        assert focused_first is False
        if len(rows_seq) > 1:
            return rows_seq.popleft()
        return rows_seq[0]

    monkeypatch.setattr(wm_mod, "get_window_list_snapshot", fake_get_window_list_snapshot)

    it = iter_wm_events(kinds={"new"}, poll_ms=1)
    ev = next(it)
    assert ev.kind == "new"
    assert ev.name == "poll"
    assert ev.data["id"] == "0x3"
    assert ev.data["class"] == "Firefox"


def test_polling_window_events_can_detect_active_window_geometry_changes(monkeypatch) -> None:
    import vhk.system.wm_events as wm_mod

    sequence = deque([
        ({
            "id": "0x1",
            "class": "Firefox",
            "title": "Docs",
            "geometry": {"rect": {"x": 10, "y": 20, "w": 800, "h": 600}, "client": None},
        }, "x11"),
        ({
            "id": "0x1",
            "class": "Firefox",
            "title": "Docs",
            "geometry": {"rect": {"x": 10, "y": 20, "w": 800, "h": 600}, "client": None},
        }, "x11"),
        ({
            "id": "0x1",
            "class": "Firefox",
            "title": "Docs",
            "geometry": {"rect": {"x": 70, "y": 45, "w": 900, "h": 620}, "client": None},
        }, "x11"),
    ])

    monkeypatch.setattr(wm_mod, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(wm_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(wm_mod, "get_window_list_snapshot", lambda **kwargs: ([{"id": "0x1", "class": "Firefox", "title": "Docs"}], "x11"))

    def fake_get_active_window_snapshot(*, include_geometry=True, require_geometry=False):
        assert include_geometry is True
        if len(sequence) > 1:
            return sequence.popleft()
        return sequence[0]

    monkeypatch.setattr(wm_mod, "get_active_window_snapshot", fake_get_active_window_snapshot)
    monkeypatch.setattr(wm_mod, "get_active_window_info", lambda: ({"id": "0x1", "class": "Firefox", "title": "Docs"}, "x11"))

    it = iter_wm_events(kinds={"geometry"}, poll_ms=1)
    ev = next(it)
    assert ev.kind == "geometry"
    assert ev.name == "poll"
    assert ev.data["id"] == "0x1"
    assert ev.data["geometry_reason"] == "geometry"
    assert ev.data["geometry"]["rect"] == {"x": 70, "y": 45, "w": 900, "h": 620}
    assert ev.data["old_geometry"]["rect"] == {"x": 10, "y": 20, "w": 800, "h": 600}
