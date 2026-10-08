from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.project.loader import load_project
from vhk.core.runner import Runner


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_region_stable_rolls_baseline_until_stable(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForRegionStable",
                        "region": {"x": 0, "y": 0, "w": 20, "h": 20},
                        "max_changed_pixels": 0,
                        "max_change_ratio": 0.0,
                        "rolling_baseline": True,
                        "timeout_ms": 200,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 8,
                        "stable_attempts": 1,
                        "out_ok": "ok",
                        "out_change_ratio": "ratio",
                    }
                ],
            }
        },
    )

    base = np.zeros((20, 20, 3), dtype=np.uint8)
    c1 = base.copy()
    c1[0:4, 0:4] = 255
    c2 = base.copy()
    c2[4:8, 4:8] = 255
    stable = base.copy()

    # First call: baseline capture. Subsequent calls: attempts.
    frames = [base, c1, c2, stable, stable]
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
    assert res.vars["ok"] is True
    assert float(res.vars["ratio"]) == 0.0
    assert Path(res.vars["baseline_screenshot"]).exists()


def test_wait_for_region_stable_timeout_writes_diff(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForRegionStable",
                        "region": {"x": 0, "y": 0, "w": 20, "h": 20},
                        "max_changed_pixels": 0,
                        "max_change_ratio": 0.0,
                        "rolling_baseline": True,
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 3,
                        "debug_on_timeout": True,
                        "out_visual_diff": "diff",
                    }
                ],
            }
        },
    )

    base = np.zeros((20, 20, 3), dtype=np.uint8)
    c1 = base.copy()
    c1[0:4, 0:4] = 255
    c2 = base.copy()
    c2[4:8, 4:8] = 255

    frames = [base, c1, c2, c1]
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
    assert not res.ok
    assert "WaitForRegionStable" in (res.error or "")
    assert "diff" in res.vars
    assert Path(res.vars["diff"]).exists()
