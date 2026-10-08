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
        yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}})
    )
    return proj


def test_wait_for_image_vanish_basic(tmp_path: Path, monkeypatch):
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    blank = np.zeros((80, 100, 3), dtype=np.uint8)
    present = blank.copy()
    present[10:20, 30:40] = 255

    frames = [present, blank, blank]
    state = {"i": 0}

    def fake_capture(path: Path, region=None):
        i = state["i"]
        img = frames[i] if i < len(frames) else frames[-1]
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForImageVanish",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.9,
                        "timeout_ms": 200,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 10,
                        "stable_attempts": 2,
                        "stable_ms": 0,
                        "require_seen": True,
                        "out_seen": "seen",
                        "out_last_score": "score",
                        "out_last_seen_x": "sx",
                        "out_last_seen_y": "sy",
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
    assert res.vars["seen"] is True
    # Last seen match location from the "present" frame.
    assert res.vars["sx"] == 30
    assert res.vars["sy"] == 10
    assert float(res.vars["score"]) < 0.9


def test_wait_for_image_vanish_require_seen_times_out(tmp_path: Path, monkeypatch):
    # If the image is never present and require_seen=true, we should time out
    # rather than immediately succeeding.
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    blank = np.zeros((80, 100, 3), dtype=np.uint8)
    frames = [blank, blank, blank]
    state = {"i": 0}

    def fake_capture(path: Path, region=None):
        i = state["i"]
        img = frames[i] if i < len(frames) else frames[-1]
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForImageVanish",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.9,
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 3,
                        "require_seen": True,
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
    assert not res.ok
    assert "WaitForImageVanish" in (res.error or "")


def test_wait_for_pixel_vanish_basic(tmp_path: Path, monkeypatch):
    blank = np.zeros((50, 60, 3), dtype=np.uint8)
    present = blank.copy()
    # Red pixel at (x=30,y=10) in BGR order.
    present[10, 30] = (0, 0, 255)

    frames = [present, blank, blank]
    state = {"i": 0}

    def fake_capture(path: Path, region=None):
        i = state["i"]
        img = frames[i] if i < len(frames) else frames[-1]
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    proj = _write_project(
        tmp_path,
        macro={
            "name": "m",
            "steps": [
                {
                    "type": "WaitForPixelVanish",
                    "color": "#FF0000",
                    "tolerance": 0.0,
                    "timeout_ms": 200,
                    "poll_ms": 0,
                    "jitter_ms": 0,
                    "max_attempts": 10,
                    "stable_attempts": 2,
                    "stable_ms": 0,
                    "require_seen": True,
                    "out_seen": "seen",
                    "out_last_seen_x": "sx",
                    "out_last_seen_y": "sy",
                }
            ],
        },
    )

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["seen"] is True
    assert res.vars["sx"] == 30
    assert res.vars["sy"] == 10
