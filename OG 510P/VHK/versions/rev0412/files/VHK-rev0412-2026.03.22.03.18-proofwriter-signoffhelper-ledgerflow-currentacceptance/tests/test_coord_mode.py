from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.core.models import Region
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


def test_coord_mode_pixel_window_translates_regions_and_points(tmp_path: Path, monkeypatch):
    # Frame is a big black canvas with a single red pixel at absolute (130, 210).
    frame = np.zeros((400, 400, 3), dtype=np.uint8)
    frame[210, 130] = (0, 0, 255)  # BGR => #FF0000

    def fake_capture(path: Path, region=None):
        img = frame
        if region is not None:
            img = img[region.y : region.y + region.h, region.x : region.x + region.w]
        cv2.imwrite(str(path), img)
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    # Active window starts at (100,200). Region in the macro is relative to the window.
    def fake_geom():
        return ({"x": 100, "y": 200, "w": 300, "h": 300}, {"x": 102, "y": 205, "w": 296, "h": 290}, "i3")

    monkeypatch.setattr(runner_mod, "get_active_window_geometry", fake_geom)

    reg = Region(x=20, y=5, w=80, h=60)

    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "CoordMode", "target": "pixel", "mode": "window"},
                    {
                        "type": "PixelSearch",
                        "color": "#FF0000",
                        "tolerance": 0,
                        "region": reg.model_dump(),
                        "out_x": "x",
                        "out_y": "y",
                    },
                    {
                        "type": "PixelGetColor",
                        "x": 30,
                        "y": 10,
                        "out_hex": "hex",
                    },
                ],
            }
        },
    )

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    assert res.vars["x"] == 130
    assert res.vars["y"] == 210
    assert res.vars["hex"] == "#FF0000"


def test_coord_mode_mouse_window_translates_mouse_steps(tmp_path: Path, monkeypatch):
    import vhk.core.runner as runner_mod

    moves: list[tuple[int, int]] = []
    clicks: list[int] = []

    def fake_move(*, x=None, y=None, dx=None, dy=None, relative=False):
        assert not relative
        moves.append((int(x), int(y)))

    def fake_click(button=1, *, down=False, up=False, clearmodifiers=False):
        clicks.append(int(button))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", fake_click)

    def fake_geom():
        return ({"x": 100, "y": 200, "w": 300, "h": 300}, {"x": 102, "y": 205, "w": 296, "h": 290}, "i3")

    monkeypatch.setattr(runner_mod, "get_active_window_geometry", fake_geom)

    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "CoordMode", "target": "mouse", "mode": "window"},
                    {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
                ],
            }
        },
    )

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    assert moves == [(110, 220)]
    assert clicks == [1]


def test_coord_mode_mouse_window_translates_multiclick_steps(tmp_path: Path, monkeypatch):
    import vhk.core.runner as runner_mod

    moves: list[tuple[int, int]] = []
    clicks: list[int] = []
    sleeps: list[float] = []

    def fake_move(*, x=None, y=None, dx=None, dy=None, relative=False):
        assert not relative
        moves.append((int(x), int(y)))

    def fake_click(button=1, *, down=False, up=False, clearmodifiers=False):
        clicks.append(int(button))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", fake_click)
    monkeypatch.setattr(runner_mod.time, "sleep", lambda secs: sleeps.append(float(secs)))

    def fake_geom():
        return ({"x": 100, "y": 200, "w": 300, "h": 300}, {"x": 102, "y": 205, "w": 296, "h": 290}, "i3")

    monkeypatch.setattr(runner_mod, "get_active_window_geometry", fake_geom)

    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "CoordMode", "target": "mouse", "mode": "window"},
                    {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1, "clicks": 2, "delay_between_clicks_ms": 25},
                ],
            }
        },
    )

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    assert moves == [(110, 220)]
    assert clicks == [1, 1]
    assert sleeps == [0.025]
