from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.vision.assets import load_needle, compute_click_offset


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_compute_click_offset_relative_to_union_bbox(tmp_path: Path):
    # Build a needle with two match areas, clickpoint in second.
    img = np.zeros((60, 80, 3), dtype=np.uint8)
    png = tmp_path / "n.png"
    cv2.imwrite(str(png), img)

    meta = {
        "tags": [],
        "area": [
            {"type": "match", "xpos": 10, "ypos": 10, "width": 20, "height": 20},
            {
                "type": "match",
                "xpos": 40,
                "ypos": 10,
                "width": 10,
                "height": 10,
                "click_point": {"xpos": 1, "ypos": 2, "id": "cp"},
            },
        ],
    }
    png.with_suffix(".json").write_text(yaml.safe_dump(meta).replace("'", '"'))
    # The above YAML->JSON hack isn't great; write proper JSON for reliability.
    import json

    png.with_suffix(".json").write_text(json.dumps(meta))

    needle = load_needle(png)
    dx, dy = compute_click_offset(needle, click_point_id="cp")
    # union min_x=10, min_y=10 => (40-10)+1 = 31 ; (10-10)+2 = 2
    assert (dx, dy) == (31, 2)


def test_wait_for_image_screen_and_clickneedle(tmp_path: Path, monkeypatch):
    # Create a needle and two screen frames: first missing, second present.
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    blank = np.zeros((80, 100, 3), dtype=np.uint8)
    present = blank.copy()
    present[10:20, 30:40] = 255

    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    # Add clickpoint metadata at (2,3) inside match area.
    import json

    (proj / "assets" / "needle.json").write_text(
        json.dumps(
            {
                "tags": [],
                "area": [
                    {
                        "type": "match",
                        "xpos": 0,
                        "ypos": 0,
                        "width": 10,
                        "height": 10,
                        "click_point": {"xpos": 2, "ypos": 3},
                    }
                ],
            }
        )
    )

    frames = [blank, present]
    state = {"i": 0}

    def fake_capture(path: Path, region=None):
        i = state["i"]
        img = frames[i] if i < len(frames) else frames[-1]
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    # Patch screenshot capture.
    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    # Patch input functions to record.
    calls = []

    def fake_move(*, x, y, **kwargs):
        calls.append(("move", x, y))

    def fake_click(button, **kwargs):
        calls.append(("click", button, kwargs.get("clearmodifiers", False)))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", fake_click)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForImage",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.9,
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 3,
                        "out_x": "x",
                        "out_y": "y",
                    },
                    {
                        "type": "ClickNeedle",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.9,
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 3,
                        "out_click_x": "cx",
                        "out_click_y": "cy",
                    },
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}))

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    # WaitForImage should find the match (x=30,y=10)
    assert res.vars["x"] == 30
    assert res.vars["y"] == 10

    # ClickNeedle uses clickpoint (2,3) => click at (32,13)
    assert res.vars["cx"] == 32
    assert res.vars["cy"] == 13
    assert calls[0] == ("move", 32, 13)
    assert calls[1][0] == "click"


def test_wait_for_text_and_assert_text(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForText",
                        "pattern": "READY",
                        "match": "contains",
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 3,
                        "out_text": "t",
                        "out_found": "found",
                    },
                    {"type": "AssertText", "pattern": "OK", "match": "regex", "out_text": "t2"},
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    # Fake capture just creates an empty file.
    def fake_capture(path: Path, region=None):
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imwrite(str(path), img)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    # Fake OCR returns READY on second call, then OK.
    state = {"i": 0}

    def fake_ocr(path: Path, lang="eng"):
        state["i"] += 1
        if state["i"] == 1:
            return "not yet"
        if state["i"] == 2:
            return "system READY"
        return "OK"

    monkeypatch.setattr(runner_mod, "ocr_read_text_file", fake_ocr)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["found"] is True
    assert "READY" in res.vars["t"]
    assert res.vars["t2"] == "OK"


def test_step_mode_does_not_block(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {"m": {"name": "m", "steps": [{"type": "Delay", "ms": 0}]}},
    )

    project = load_project(proj)
    r = Runner(project, step_mode=True, input_func=lambda _: "")
    res = r.run("m")
    assert res.ok
