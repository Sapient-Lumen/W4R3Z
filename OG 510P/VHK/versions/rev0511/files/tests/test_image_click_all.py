from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, *, macro: dict) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    (proj / "macros" / "m.yaml").write_text(yaml.safe_dump(macro))
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": False, "dry_run": True},
                "macros": {"m": "macros/m.yaml"},
            }
        )
    )
    return proj


def test_wait_for_image_all_screen_step(tmp_path: Path, monkeypatch):
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    frame = np.zeros((80, 100, 3), dtype=np.uint8)
    frame[10:20, 30:40] = 255
    frame[40:50, 60:70] = 255

    proj = _write_project(
        tmp_path,
        macro={
            "name": "m",
            "steps": [
                {
                    "type": "WaitForImageAll",
                    "needle_path": "assets/needle.png",
                    "threshold": 0.9,
                    "min_count": 2,
                    "max_results": 10,
                    "out_matches": "ms",
                    "out_count": "n",
                    "timeout_ms": 200,
                    "poll_ms": 1,
                }
            ],
        },
    )
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), frame)
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["n"] == 2
    got = {(m["x"], m["y"]) for m in res.vars["ms"]}
    assert got == {(30, 10), (60, 40)}


def test_click_image_all_centers(tmp_path: Path, monkeypatch):
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    frame = np.zeros((80, 100, 3), dtype=np.uint8)
    frame[10:20, 30:40] = 255
    frame[40:50, 60:70] = 255

    proj = _write_project(
        tmp_path,
        macro={
            "name": "m",
            "steps": [
                {
                    "type": "ClickImageAll",
                    "needle_path": "assets/needle.png",
                    "threshold": 0.9,
                    "min_count": 2,
                    "max_results": 10,
                    "out_clicks": "clicks",
                    "out_clicked_count": "clicked",
                    "timeout_ms": 200,
                    "poll_ms": 1,
                }
            ],
        },
    )
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), frame)
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["clicked"] == 2
    pts = {(c["x"], c["y"]) for c in res.vars["clicks"]}
    assert pts == {(35, 15), (65, 45)}


def test_click_image_all_respects_needle_click_point(tmp_path: Path, monkeypatch):
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255
    frame = np.zeros((40, 50, 3), dtype=np.uint8)
    frame[10:20, 30:40] = 255

    proj = _write_project(
        tmp_path,
        macro={
            "name": "m",
            "steps": [
                {
                    "type": "ClickImageAll",
                    "needle_path": "assets/needle.png",
                    "threshold": 0.9,
                    "min_count": 1,
                    "max_results": 5,
                    "click_point_id": "cp",
                    "out_clicks": "clicks",
                    "timeout_ms": 200,
                    "poll_ms": 1,
                }
            ],
        },
    )
    needle_png = proj / "assets" / "needle.png"
    cv2.imwrite(str(needle_png), needle)
    import json

    (needle_png.with_suffix(".json")).write_text(
        json.dumps(
            {
                "area": [
                    {
                        "type": "match",
                        "xpos": 0,
                        "ypos": 0,
                        "width": 10,
                        "height": 10,
                        "click_point": {"id": "cp", "xpos": 1, "ypos": 2},
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), frame)
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["clicks"][0]["x"] == 31
    assert res.vars["clicks"][0]["y"] == 12
