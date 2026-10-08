from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def test_pixel_get_color_screen_captures_minimal_region(tmp_path: Path, monkeypatch):
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)

    # Fake capture: ensure we get a 1x1 region and write a 1x1 PNG.
    import vhk.core.runner as runner_mod

    seen = {}

    def fake_capture(path: Path, region=None):
        assert region is not None
        seen["region"] = region
        img = np.zeros((1, 1, 3), dtype=np.uint8)
        # BGR=(3,2,1) => RGB=(1,2,3)
        img[0, 0] = (3, 2, 1)
        cv2.imwrite(str(path), img)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "PixelGetColor", "x": 10, "y": 20, "out_hex": "c"},
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
    assert res.vars["c"] == "#010203"

    r = seen.get("region")
    assert (r.x, r.y, r.w, r.h) == (10, 20, 1, 1)
