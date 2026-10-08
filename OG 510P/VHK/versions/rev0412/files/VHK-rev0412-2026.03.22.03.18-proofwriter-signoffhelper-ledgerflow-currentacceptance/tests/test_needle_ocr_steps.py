from __future__ import annotations

import json
from pathlib import Path

import pytest


def _write_blank_png(path: Path, *, w: int = 80, h: int = 60) -> Path:
    import cv2
    import numpy as np

    img = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return path


def test_ocr_needle_text_uses_needle_ocr_area(monkeypatch, tmp_path: Path):
    import yaml

    from vhk.core.runner import Runner
    from vhk.project.loader import load_project

    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    # Minimal needle: match area starts at (5,2); OCR area starts at (2,1).
    needle_png = proj / "assets" / "n.png"
    _write_blank_png(needle_png, w=40, h=30)

    (proj / "assets" / "n.json").write_text(
        json.dumps(
            {
                "area": [
                    {"type": "match", "xpos": 5, "ypos": 2, "width": 10, "height": 5},
                    {"type": "ocr", "xpos": 2, "ypos": 1, "width": 6, "height": 3},
                ],
                "tags": [],
            }
        )
        + "\n"
    )

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "OcrNeedleText",
                        "needle_path": "assets/n.png",
                        "threshold": 0.5,
                        # Use a capture region so outputs are screen-absolute.
                        "region": "50x50+100+200",
                        "out_text": "txt",
                        "out_match_x": "mx",
                        "out_match_y": "my",
                        "out_ocr_x": "ox",
                        "out_ocr_y": "oy",
                        "out_ocr_w": "ow",
                        "out_ocr_h": "oh",
                    }
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}})
    )

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):  # noqa: ARG001
        # We don't need a real crop; image_search_file is mocked.
        return _write_blank_png(path, w=80, h=60)

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    # Pretend the needle match was found at (10,5) in the *captured* image.
    from vhk.vision.match import ImageMatch

    def fake_image_search_file(*_a, **_kw):  # noqa: ARG001
        return ImageMatch(x=10, y=5, score=0.9, w=20, h=10, scale=1.0)

    monkeypatch.setattr(runner_mod, "image_search_file", fake_image_search_file)

    calls = {}

    def fake_ocr_read_text_file(_path: Path, *, region=None, **_kw):  # noqa: ARG001
        calls["region"] = region
        return "HELLO"

    monkeypatch.setattr(runner_mod, "ocr_read_text_file", fake_ocr_read_text_file)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    # OCR should be done relative to the union bbox of match areas.
    # min_x/min_y = (5,2), so OCR area (2,1) becomes (-3,-1) relative.
    assert calls["region"].x == 7
    assert calls["region"].y == 4
    assert calls["region"].w == 6
    assert calls["region"].h == 3

    # Outputs should be screen-absolute (capture region offset applied).
    assert res.vars["mx"] == 110
    assert res.vars["my"] == 205
    assert res.vars["ox"] == 107
    assert res.vars["oy"] == 204
    assert res.vars["ow"] == 6
    assert res.vars["oh"] == 3
    assert res.vars["txt"] == "HELLO"


def test_wait_for_needle_text_stable_attempts(monkeypatch, tmp_path: Path):
    import yaml

    from vhk.core.runner import Runner
    from vhk.project.loader import load_project

    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    needle_png = proj / "assets" / "n.png"
    _write_blank_png(needle_png, w=40, h=30)

    # No OCR areas: wait step should fall back to match bbox OCR.
    (proj / "assets" / "n.json").write_text(
        json.dumps(
            {
                "area": [{"type": "match", "xpos": 0, "ypos": 0, "width": 10, "height": 10}],
                "tags": [],
            }
        )
        + "\n"
    )

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForNeedleText",
                        "needle_path": "assets/n.png",
                        "threshold": 0.5,
                        "pattern": "OK",
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 5,
                        "stable_attempts": 2,
                        "stable_ms": 0,
                        "out_found": "found",
                        "out_text": "txt",
                    }
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}})
    )

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):  # noqa: ARG001
        return _write_blank_png(path, w=80, h=60)

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    from vhk.vision.match import ImageMatch

    def fake_image_search_file(*_a, **_kw):  # noqa: ARG001
        return ImageMatch(x=1, y=2, score=0.9, w=10, h=10, scale=1.0)

    monkeypatch.setattr(runner_mod, "image_search_file", fake_image_search_file)

    seq = ["NO", "OK", "OK"]

    def fake_ocr_read_text_file(_path: Path, **_kw):  # noqa: ARG001
        return seq.pop(0) if seq else "OK"

    monkeypatch.setattr(runner_mod, "ocr_read_text_file", fake_ocr_read_text_file)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["found"] is True
    assert res.vars["txt"] == "OK"
