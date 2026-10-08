from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


def _write_blank(path: Path) -> Path:
    img = Image.new("RGB", (100, 80), color=(0, 0, 0))
    img.save(path)
    return path


def test_ocr_read_spans_word_and_find(monkeypatch, tmp_path: Path):
    from vhk.core.models import Region
    from vhk.vision import ocr as ocr_mod

    img_path = _write_blank(tmp_path / "x.png")

    def fake_image_to_data(_img, lang="eng", config=None, output_type=None):  # noqa: ARG001
        # Mimic pytesseract.Output.DICT structure.
        return {
            "level": [1, 5, 5, 5],
            "block_num": [0, 1, 1, 1],
            "par_num": [0, 1, 1, 1],
            "line_num": [0, 1, 1, 1],
            "word_num": [0, 1, 2, 3],
            "left": [0, 10, 30, 50],
            "top": [0, 5, 5, 5],
            "width": [0, 10, 10, 10],
            "height": [0, 10, 10, 10],
            "conf": [-1, 80, 95, -1],
            "text": ["", "Hello", "WORLD", "BLOCK"],
        }

    monkeypatch.setattr(ocr_mod.pytesseract, "image_to_data", fake_image_to_data)

    spans = ocr_mod.ocr_read_spans_file(img_path, level="word")
    assert [s.text for s in spans] == ["Hello", "WORLD"]

    # Region offsets should add (x,y) to returned coords.
    spans2 = ocr_mod.ocr_read_spans_file(img_path, level="word", region=Region(x=7, y=9, w=50, h=50))
    assert spans2[0].x == 10 + 7
    assert spans2[0].y == 5 + 9

    m = ocr_mod.ocr_find_text_file(img_path, pattern="world", match="contains", case_sensitive=False)
    assert m.text == "WORLD"
    assert m.conf == 95


def test_ocr_read_spans_line_grouping(monkeypatch, tmp_path: Path):
    from vhk.vision import ocr as ocr_mod

    img_path = _write_blank(tmp_path / "x.png")

    def fake_image_to_data(_img, lang="eng", config=None, output_type=None):  # noqa: ARG001
        return {
            "level": [5, 5, 5],
            "block_num": [1, 1, 1],
            "par_num": [1, 1, 1],
            "line_num": [1, 1, 2],
            "word_num": [1, 2, 1],
            "left": [10, 30, 10],
            "top": [5, 5, 25],
            "width": [10, 10, 10],
            "height": [10, 10, 10],
            "conf": [90, 80, 70],
            "text": ["Hello", "World", "OK"],
        }

    monkeypatch.setattr(ocr_mod.pytesseract, "image_to_data", fake_image_to_data)

    spans = ocr_mod.ocr_read_spans_file(img_path, level="line")
    assert len(spans) == 2
    texts = sorted([s.text for s in spans])
    assert "Hello World" in texts
    assert "OK" in texts

    m = ocr_mod.ocr_find_text_file(img_path, pattern="hello world", level="line", match="contains")
    assert m.text.lower() == "hello world"


def test_ocr_find_text_strategy_best_conf(monkeypatch, tmp_path: Path):
    from vhk.vision import ocr as ocr_mod

    img_path = _write_blank(tmp_path / "x.png")

    def fake_image_to_data(_img, lang="eng", config=None, output_type=None):  # noqa: ARG001
        return {
            "level": [5, 5],
            "block_num": [1, 1],
            "par_num": [1, 1],
            "line_num": [1, 1],
            "word_num": [1, 2],
            "left": [50, 10],
            "top": [5, 5],
            "width": [10, 10],
            "height": [10, 10],
            "conf": [50, 99],
            "text": ["OK", "OK"],
        }

    monkeypatch.setattr(ocr_mod.pytesseract, "image_to_data", fake_image_to_data)

    m_first = ocr_mod.ocr_find_text_file(img_path, pattern="OK", match_strategy="first", scan_order="tlbr")
    # first in scan order is x=10 (second row item)
    assert m_first.x == 10

    m_best = ocr_mod.ocr_find_text_file(img_path, pattern="OK", match_strategy="best_conf")
    assert m_best.conf == 99


def test_ocr_fuzzy_match_in_spans():
    from vhk.vision.ocr import OcrSpan, ocr_find_text_in_spans

    spans = [
        OcrSpan(text="RE4DY", x=0, y=0, w=1, h=1, conf=80.0),
        OcrSpan(text="NOT READY", x=10, y=0, w=1, h=1, conf=90.0),
    ]

    m = ocr_find_text_in_spans(spans, pattern="READY", match="fuzzy", fuzzy_threshold=0.8)
    assert m.text == "RE4DY"


def test_screen_wait_for_text_box_and_click_text(monkeypatch, tmp_path: Path):
    import yaml
    import numpy as np
    import cv2

    from vhk.core.runner import Runner
    from vhk.project.loader import load_project
    from vhk.vision.ocr import OcrSpan

    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForTextBox",
                        "pattern": "READY",
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 3,
                        "out_found": "found",
                        "out_x": "x",
                        "out_y": "y",
                        "out_w": "w",
                        "out_h": "h",
                    },
                    {
                        "type": "ClickText",
                        "pattern": "OK",
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 3,
                        "offset_x": 1,
                        "offset_y": 2,
                        "out_click_x": "cx",
                        "out_click_y": "cy",
                    },
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}))

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):  # noqa: ARG001
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imwrite(str(path), img)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    calls = []

    def fake_move(x=None, y=None, **_):
        calls.append(("move", x, y))

    def fake_click(button, **_):
        calls.append(("click", button))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", fake_click)

    state = {"i": 0}

    def fake_read_spans(_path: Path, lang="eng", region=None, level="word", **_kwargs):  # noqa: ARG001
        state["i"] += 1
        # Attempts: 1 (wait) -> no; 2 (wait) -> yes; 3 (click) -> no; 4 (click) -> yes.
        if state["i"] == 1:
            return [OcrSpan(text="nope", x=0, y=0, w=1, h=1, conf=10.0)]
        if state["i"] == 2:
            return [OcrSpan(text="system READY", x=3, y=4, w=10, h=6, conf=88.0)]
        if state["i"] == 3:
            return [OcrSpan(text="waiting", x=0, y=0, w=1, h=1, conf=10.0)]
        return [OcrSpan(text="OK", x=10, y=20, w=8, h=10, conf=99.0)]

    monkeypatch.setattr(runner_mod, "ocr_read_spans_file", fake_read_spans)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["found"] is True
    assert res.vars["x"] == 3
    assert res.vars["y"] == 4
    # Click center: x=10 + 4 + 1 = 15, y=20 + 5 + 2 = 27
    assert res.vars["cx"] == 15
    assert res.vars["cy"] == 27
    assert calls[0] == ("move", 15, 27)
    assert calls[1][0] == "click"


def test_screen_click_text_all(monkeypatch, tmp_path: Path):
    import yaml
    import numpy as np
    import cv2

    from vhk.core.runner import Runner
    from vhk.project.loader import load_project
    from vhk.vision.ocr import OcrSpan

    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "ClickTextAll",
                        "pattern": "OK",
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 1,
                        "offset_x": 1,
                        "offset_y": 2,
                        "out_clicked_count": "n",
                        "out_last_click_x": "lx",
                        "out_last_click_y": "ly",
                    }
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}))

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):  # noqa: ARG001
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imwrite(str(path), img)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    calls = []

    def fake_move(x=None, y=None, **_):
        calls.append(("move", x, y))

    def fake_click(button, **_):
        calls.append(("click", button))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", fake_click)

    def fake_read_spans(_path: Path, lang="eng", region=None, level="word", **_kwargs):  # noqa: ARG001
        return [
            OcrSpan(text="OK", x=10, y=20, w=8, h=10, conf=99.0),
            OcrSpan(text="OK", x=0, y=0, w=4, h=4, conf=50.0),
        ]

    monkeypatch.setattr(runner_mod, "ocr_read_spans_file", fake_read_spans)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["n"] == 2
    # Scan-order clicks top-left first: bbox at (0,0,w=4,h=4) -> center (2,2) + offsets -> (3,4)
    assert calls[0] == ("move", 3, 4)
    assert calls[1] == ("click", 1)
    # Second click: bbox at (10,20,w=8,h=10) -> center (14,25) + offsets -> (15,27)
    assert calls[2] == ("move", 15, 27)
    assert calls[3] == ("click", 1)
    assert res.vars["lx"] == 15
    assert res.vars["ly"] == 27
