from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.cursor_pos import CursorPos


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_get_window_at_cursor_step_populates_window_and_cursor_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "GetWindowAtCursor", "include_geometry": True},
                {"type": "Return", "value_expr": "str(window_found) + '|' + window_title + '|' + str(cursor_x) + ',' + str(cursor_y)"},
            ],
        }
    }
    proj_dir = _write_project(tmp_path, manifest, macros)
    proj = load_project(proj_dir)

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(
        runner_mod.active_window_mod,
        "get_window_at_cursor_snapshot",
        lambda **kwargs: (
            {
                "id": "0x2",
                "title": "Terminal",
                "class": "Alacritty",
                "workspace": "2",
                "focused": False,
                "pid": 888,
                "process_name": "alacritty",
                "geometry": {"rect": {"x": 100, "y": 200, "w": 600, "h": 400}, "client": None},
            },
            "x11",
            CursorPos(x=123, y=456, backend="xdotool"),
        ),
    )

    res = Runner(proj).run("m")
    assert res.ok is True
    assert res.vars["wm"] == "x11"
    assert res.vars["window_found"] is True
    assert res.vars["window"]["title"] == "Terminal"
    assert res.vars["cursor_x"] == 123
    assert res.vars["cursor_y"] == 456
    assert res.vars["cursorpos_backend"] == "xdotool"
    assert res.vars["window_focused"] is False
    assert res.vars["window_pid"] == 888
    assert res.vars["window_process"] == "alacritty"
    assert res.vars["return_value"] == "True|Terminal|123,456"


def test_get_window_at_cursor_snapshot_hyprland_uses_cursor_and_geometry(monkeypatch: pytest.MonkeyPatch):
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
                    "title": "Firefox",
                    "class": "Firefox",
                    "workspace": "1:web",
                    "focused": True,
                    "geometry": {"rect": {"x": 0, "y": 0, "w": 500, "h": 400}, "client": None},
                },
                {
                    "id": "0xbbb",
                    "title": "Popup",
                    "class": "Firefox",
                    "workspace": "1:web",
                    "focused": False,
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
    # Smaller containing popup should win over the larger focused parent.
    assert window["id"] == "0xbbb"
    assert window["geometry"]["rect"]["w"] == 120



def test_get_window_at_cursor_snapshot_x11_prefers_pointer_window_id(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(aw, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(aw, "get_cursor_pos", lambda: CursorPos(x=50, y=50, backend="xdotool"))
    monkeypatch.setattr(aw, "_x11_pointer_window_id", lambda: 0x2)
    monkeypatch.setattr(
        aw,
        "get_window_list_snapshot",
        lambda **kwargs: (
            [
                {
                    "id": "0x1",
                    "title": "Background",
                    "class": "Firefox",
                    "focused": True,
                    "geometry": {"rect": {"x": 0, "y": 0, "w": 500, "h": 500}, "client": None},
                },
                {
                    "id": "0x2",
                    "title": "Palette",
                    "class": "Rofi",
                    "focused": False,
                    "geometry": {"rect": {"x": 0, "y": 0, "w": 500, "h": 500}, "client": None},
                },
            ],
            "x11",
        ),
    )

    window, wm, cursor = aw.get_window_at_cursor_snapshot(include_geometry=False)
    assert wm == "x11"
    assert cursor.backend == "xdotool"
    assert window is not None
    assert window["id"] == "0x2"
    assert "geometry" not in window
