from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_image_cursor_avoid_parks_and_restores(tmp_path: Path, monkeypatch):
    # Needle exists but screen is blank -> timeout. We verify the cursor guard
    # parks the cursor before capture and restores it even when timing out.
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    blank = np.zeros((80, 100, 3), dtype=np.uint8)

    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), blank)
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    # Fake cursor position + display size.
    from vhk.system.cursor_pos import CursorPos
    from vhk.system.display import ScreenSize

    monkeypatch.setattr(runner_mod.cursor_pos_mod, "get_cursor_pos", lambda: CursorPos(x=50, y=60, backend="fake"))
    monkeypatch.setattr(runner_mod.display_mod, "get_virtual_screen_size", lambda: ScreenSize(width=100, height=80, backend="fake"))

    calls = []

    def fake_move(*, x: int, y: int, **kwargs):
        calls.append((int(x), int(y)))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForImage",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.9,
                        "timeout_ms": 5,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 1,
                        "cursor_avoid": "corner",
                        "cursor_corner": "br",
                        "cursor_margin": 3,
                        "cursor_restore": True,
                    }
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}))

    project = load_project(proj)
    res = Runner(project).run("m")
    assert not res.ok

    # br with margin 3 on 100x80 => (96, 76)
    assert calls[0] == (96, 76)
    assert calls[-1] == (50, 60)


def test_wait_for_image_debug_on_timeout_writes_annotated(tmp_path: Path, monkeypatch):
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    blank = np.zeros((80, 100, 3), dtype=np.uint8)

    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), blank)
        return path

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForImage",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.99,
                        "timeout_ms": 5,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 1,
                        "debug_on_timeout": True,
                        "out_debug_screenshot": "dbg",
                    }
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}))

    project = load_project(proj)
    res = Runner(project).run("m")
    assert not res.ok
    assert "dbg" in res.vars
    p = Path(res.vars["dbg"]).expanduser()
    assert p.exists()
    assert p.name.endswith("_annotated.png")
