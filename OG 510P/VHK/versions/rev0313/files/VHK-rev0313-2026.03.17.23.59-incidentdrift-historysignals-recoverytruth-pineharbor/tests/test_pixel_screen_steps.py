from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.core.models import Region


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_pixel_and_pixel_search_screen(tmp_path: Path, monkeypatch):
    # Frames: first no match (all black), second has a near-red pixel.
    blank = np.zeros((80, 100, 3), dtype=np.uint8)
    present = blank.copy()
    # Near-red pixel at (x=30,y=10). OpenCV uses BGR.
    present[10, 30] = (5, 5, 250)

    frames = [blank, present]
    state = {"i": 0}

    def fake_capture(path: Path, region=None):
        i = state["i"]
        img = frames[i] if i < len(frames) else frames[-1]
        if region is not None:
            img = img[region.y : region.y + region.h, region.x : region.x + region.w]
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    reg = Region(x=20, y=5, w=50, h=30)

    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForPixel",
                        "color": "#FF0000",
                        "tolerance": 10,
                        "tolerance_mode": "per_channel",
                        "step": 2,
                        "region": reg.model_dump(),
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 6,
                        "out_x": "x1",
                        "out_y": "y1",
                        "out_dist": "d1",
                    },
                    {
                        "type": "PixelSearch",
                        "color": "#FF0000",
                        "tolerance": 10,
                        "tolerance_mode": "per_channel",
                        "region": reg.model_dump(),
                        "out_x": "x2",
                        "out_y": "y2",
                        "out_dist": "d2",
                    },
                ],
            }
        },
    )

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    # Pixel is at absolute (30,10)
    assert res.vars["x1"] == 30
    assert res.vars["y1"] == 10
    assert res.vars["x2"] == 30
    assert res.vars["y2"] == 10
    assert res.vars["d1"] <= 10
    assert res.vars["d2"] <= 10


def test_click_pixel_all_screen(tmp_path: Path, monkeypatch):
    blank = np.zeros((80, 100, 3), dtype=np.uint8)
    present = blank.copy()
    # Two red pixels (BGR)
    present[10, 30] = (0, 0, 255)
    present[20, 60] = (0, 0, 255)

    frames = [blank, present]
    state = {"i": 0}

    def fake_capture(path: Path, region=None):
        i = state["i"]
        img = frames[i] if i < len(frames) else frames[-1]
        if region is not None:
            img = img[region.y : region.y + region.h, region.x : region.x + region.w]
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    clicks = []

    def fake_mouse_move(x: int, y: int):
        clicks.append(("move", int(x), int(y)))

    def fake_mouse_click(button: int, clearmodifiers: bool = False):
        clicks.append(("click", int(button), bool(clearmodifiers)))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_mouse_move)
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", fake_mouse_click)

    reg = Region(x=20, y=5, w=60, h=40)
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "ClickPixelAll",
                        "color": "#FF0000",
                        "tolerance": 0,
                        "tolerance_mode": "per_channel",
                        "region": reg.model_dump(),
                        "min_count": 2,
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 6,
                        "out_matches": "m",
                        "out_clicks": "c",
                    }
                ],
            }
        },
    )

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    # Should have clicked both pixels at absolute positions.
    pts = [(p["x"], p["y"]) for p in res.vars["c"]]
    assert pts == [(30, 10), (60, 20)]
    # Two moves and two clicks.
    assert [c[0] for c in clicks] == ["move", "click", "move", "click"]
