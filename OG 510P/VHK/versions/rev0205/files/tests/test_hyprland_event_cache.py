from __future__ import annotations


def _reset_hypr_cache(mod) -> None:
    mod._HYPR_META_CACHE.clear()
    mod._HYPR_META_ORDER.clear()
    mod._HYPR_LAST_ACTIVE.update({
        "ts_addr": 0.0,
        "address": None,
        "ts_ct": 0.0,
        "class": None,
        "title": None,
    })


def test_hypr_closewindow_falls_back_to_cached_openwindow(monkeypatch):
    import vhk.system.wm_events as wm

    _reset_hypr_cache(wm)
    monkeypatch.setattr(wm, "_hypr_find_client", lambda address: None)

    open_ev = wm.WmEvent(
        wm="hyprland",
        kind="new",
        name="openwindow",
        data="0xabc,2: web,Firefox,Docs",
    )
    info_open = wm.window_info_from_event(open_ev)
    assert info_open is not None
    assert info_open.get("address") == "0xabc"
    assert info_open.get("class") == "Firefox"
    assert info_open.get("title") == "Docs"
    assert info_open.get("workspace") == "2: web"

    close_ev = wm.WmEvent(wm="hyprland", kind="close", name="closewindow", data="0xabc")
    info_close = wm.window_info_from_event(close_ev)
    assert info_close is not None
    # closewindow payload only provides the address; we should still see metadata.
    assert info_close.get("address") == "0xabc"
    assert info_close.get("class") == "Firefox"
    assert info_close.get("title") == "Docs"
    assert info_close.get("workspace") == "2: web"


def test_hypr_activewindowv2_pairs_with_activewindow_for_cache(monkeypatch):
    import vhk.system.wm_events as wm

    _reset_hypr_cache(wm)
    monkeypatch.setattr(wm, "_hypr_find_client", lambda address: None)

    # Address arrives first (v2).
    ev_addr = wm.WmEvent(wm="hyprland", kind="focus", name="activewindowv2", data="0xdef")
    wm.window_info_from_event(ev_addr)

    # Class/title arrives separately.
    ev_ct = wm.WmEvent(wm="hyprland", kind="focus", name="activewindow", data="Alacritty,Shell")
    wm.window_info_from_event(ev_ct)

    close_ev = wm.WmEvent(wm="hyprland", kind="close", name="closewindow", data="0xdef")
    info_close = wm.window_info_from_event(close_ev)
    assert info_close is not None
    assert info_close.get("address") == "0xdef"
    assert info_close.get("class") == "Alacritty"
    assert info_close.get("title") == "Shell"


def test_hypr_movewindow_updates_workspace_cache(monkeypatch):
    import vhk.system.wm_events as wm

    _reset_hypr_cache(wm)
    monkeypatch.setattr(wm, "_hypr_find_client", lambda address: None)

    open_ev = wm.WmEvent(wm="hyprland", kind="new", name="openwindow", data="0xbeef,1: main,Code,project")
    wm.window_info_from_event(open_ev)

    move_ev = wm.WmEvent(wm="hyprland", kind="workspace", name="movewindow", data="0xbeef,3: dev")
    wm.window_info_from_event(move_ev)

    close_ev = wm.WmEvent(wm="hyprland", kind="close", name="closewindow", data="0xbeef")
    info_close = wm.window_info_from_event(close_ev)
    assert info_close is not None
    assert info_close.get("workspace") == "3: dev"
