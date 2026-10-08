from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vhk.core.models import I3WindowSelector
from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_get_window_list_step_populates_windows_and_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "GetWindowList", "include_geometry": True},
                {"type": "Return", "value_expr": "str(window_count) + '|' + windows[0].title + '|' + str(windows[0].geometry.rect.x)"},
            ],
        }
    }
    proj_dir = _write_project(tmp_path, manifest, macros)
    proj = load_project(proj_dir)

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(
        runner_mod.active_window_mod,
        "get_window_list_snapshot",
        lambda **kwargs: (
            [
                {
                    "id": "0x1",
                    "title": "Firefox",
                    "class": "Firefox",
                    "workspace": "1",
                    "focused": True,
                    "geometry": {"rect": {"x": 10, "y": 20, "w": 300, "h": 200}, "client": None},
                },
                {"id": "0x2", "title": "Alacritty", "class": "Alacritty", "workspace": "2", "focused": False},
            ],
            "x11",
        ),
    )

    res = Runner(proj).run("m")
    assert res.ok is True
    assert res.vars["wm"] == "x11"
    assert res.vars["window_count"] == 2
    assert res.vars["windows"][0]["title"] == "Firefox"
    assert res.vars["return_value"] == "2|Firefox|10"


def test_get_window_list_snapshot_hyprland_marks_focus_and_filters(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(aw, "detect_compositor", lambda: "hyprland")

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
                    "xwayland": False,
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
                    "xwayland": False,
                },
            ]
        if subcommand == "activewindow":
            return {"address": "0xdef"}
        raise AssertionError(subcommand)

    monkeypatch.setattr(aw, "hyprctl_json", fake_hyprctl)

    windows, wm = aw.get_window_list_snapshot(
        include_geometry=True,
        selector=I3WindowSelector(wm_class="Alacritty"),
    )
    assert wm == "hyprland"
    assert len(windows) == 1
    assert windows[0]["class"] == "Alacritty"
    assert windows[0]["focused"] is True
    assert windows[0]["geometry"]["rect"]["x"] == 100



def test_get_window_list_snapshot_kwin_uses_kdotool_search(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.active_window as aw
    from vhk.system import kdotool as kd

    monkeypatch.setattr(aw, "detect_compositor", lambda: "kwin")
    monkeypatch.setattr(kd, "search_windows", lambda **kwargs: ["{win-a}", "{win-b}"])
    monkeypatch.setattr(kd, "get_active_window_id", lambda **kwargs: "{win-b}")
    monkeypatch.setattr(
        kd,
        "get_window_info",
        lambda wid, **kwargs: {
            "id": wid,
            "class": "org.kde.AppB" if wid == "{win-b}" else "org.kde.AppA",
            "app_id": "org.kde.AppB" if wid == "{win-b}" else "org.kde.AppA",
            "title": "B" if wid == "{win-b}" else "A",
            "pid": 22 if wid == "{win-b}" else 11,
        },
    )

    class _Geom:
        def __init__(self, x, y, w, h):
            self.x = x
            self.y = y
            self.w = w
            self.h = h

    monkeypatch.setattr(kd, "get_window_geometry", lambda wid, **kwargs: _Geom(1, 2, 300, 200) if wid == "{win-b}" else _Geom(5, 6, 100, 80))

    windows, wm = aw.get_window_list_snapshot(include_geometry=True)
    assert wm == "kwin"
    assert [row["id"] for row in windows] == ["{win-b}", "{win-a}"]
    assert windows[0]["focused"] is True
    assert windows[0]["geometry"]["rect"]["w"] == 300
