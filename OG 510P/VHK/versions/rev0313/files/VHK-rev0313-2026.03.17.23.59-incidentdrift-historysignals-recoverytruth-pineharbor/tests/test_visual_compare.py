from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.project.loader import load_project
from vhk.core.runner import Runner
from vhk.vision.compare import visual_compare_file


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_visual_compare_uses_exclude_areas(tmp_path: Path):
    base = np.zeros((20, 20, 3), dtype=np.uint8)
    cur = base.copy()
    cur[5:10, 5:10] = (0, 255, 0)

    base_path = tmp_path / "baseline.png"
    cur_path = tmp_path / "current.png"
    cv2.imwrite(str(base_path), base)
    cv2.imwrite(str(cur_path), cur)

    base_path.with_suffix(".json").write_text(
        json.dumps(
            {
                "tags": [],
                "area": [
                    {"type": "match", "xpos": 0, "ypos": 0, "width": 20, "height": 20},
                    {"type": "exclude", "xpos": 5, "ypos": 5, "width": 5, "height": 5},
                ],
            }
        )
    )

    diff = visual_compare_file(cur_path, base_path)
    assert diff.changed_pixels == 0
    assert diff.change_ratio == 0.0


def test_visual_assert_verify_and_wait_for_region_change(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "VisualAssert",
                        "baseline_path": "assets/base_ok.png",
                        "max_changed_pixels": 0,
                        "max_change_ratio": 0.0,
                        "out_ok": "assert_ok",
                    },
                    {
                        "type": "VisualVerify",
                        "baseline_path": "assets/base_ok.png",
                        "max_changed_pixels": 0,
                        "max_change_ratio": 0.0,
                        "out_ok": "verify_ok",
                    },
                    {
                        "type": "WaitForRegionChange",
                        "region": {"x": 0, "y": 0, "w": 20, "h": 20},
                        "min_changed_pixels": 10,
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 4,
                        "out_change_ratio": "ratio",
                    },
                ],
            }
        },
    )

    base = np.zeros((20, 20, 3), dtype=np.uint8)
    changed = base.copy()
    changed[0:4, 0:4] = 255

    cv2.imwrite(str(proj / "assets" / "base_ok.png"), base)

    frames = [base, base, base, changed]
    state = {"i": 0}

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):
        idx = state["i"]
        img = frames[idx] if idx < len(frames) else frames[-1]
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["assert_ok"] is True
    assert res.vars["verify_ok"] is True
    assert res.vars["ratio"] > 0.0
    assert Path(res.vars["baseline_screenshot"]).exists()


def test_visual_assert_fails_on_difference(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "VisualAssert",
                        "baseline_path": "assets/base.png",
                        "max_changed_pixels": 0,
                        "max_change_ratio": 0.0,
                    }
                ],
            }
        },
    )

    base = np.zeros((10, 10, 3), dtype=np.uint8)
    bad = base.copy()
    bad[1, 1] = 255
    cv2.imwrite(str(proj / "assets" / "base.png"), base)

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), bad)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert not res.ok
    assert "VisualAssert failed" in (res.error or "")
    assert Path(res.vars["last_visual_diff"]).exists()
