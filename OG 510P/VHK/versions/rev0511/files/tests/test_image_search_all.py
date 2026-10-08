from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.vision.match import image_search_all_file


def test_image_search_all_file_two_instances(tmp_path: Path):
    hay = np.zeros((120, 160, 3), dtype=np.uint8)
    hay[10:30, 10:30] = 255
    hay[50:70, 80:100] = 255

    needle = np.zeros((20, 20, 3), dtype=np.uint8)
    needle[:] = 255

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)

    matches = image_search_all_file(
        hay_path,
        needle_path,
        threshold=0.95,
        max_results=10,
        overlap_threshold=0.2,
        sort="scan",
    )
    assert len(matches) == 2
    got = {(m.x, m.y) for m in matches}
    assert got == {(10, 10), (80, 50)}


def test_image_search_all_file_nms_dedup(tmp_path: Path):
    hay = np.zeros((80, 100, 3), dtype=np.uint8)
    hay[30:50, 40:60] = 255

    needle = np.zeros((20, 20, 3), dtype=np.uint8)
    needle[:] = 255

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)

    matches = image_search_all_file(hay_path, needle_path, threshold=0.90, max_results=20)
    assert len(matches) == 1
    assert (matches[0].x, matches[0].y) == (40, 30)


def test_image_search_all_screen_step(tmp_path: Path, monkeypatch):
    # Two matches in the captured frame.
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    frame = np.zeros((80, 100, 3), dtype=np.uint8)
    frame[10:20, 30:40] = 255
    frame[40:50, 60:70] = 255

    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), frame)
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "ImageSearchAll",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.9,
                        "max_results": 10,
                        "out_matches": "ms",
                        "out_screenshot": "shot",
                    }
                ],
            }
        )
    )
    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}})
    )

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    ms = res.vars["ms"]
    assert isinstance(ms, list)
    assert len(ms) == 2
    got = {(m["x"], m["y"]) for m in ms}
    assert got == {(30, 10), (60, 40)}
