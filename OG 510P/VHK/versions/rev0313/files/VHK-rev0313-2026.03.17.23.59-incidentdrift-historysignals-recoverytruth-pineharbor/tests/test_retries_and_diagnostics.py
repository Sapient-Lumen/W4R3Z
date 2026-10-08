from __future__ import annotations

import json
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


def test_retry_count_retries_a_failing_step(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": True}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "VisualAssert",
                        "baseline_path": "assets/base.png",
                        "max_changed_pixels": 0,
                        "retry_count": 1,
                        "retry_delay_ms": 0,
                    }
                ],
            }
        },
    )

    base = np.zeros((10, 10, 3), dtype=np.uint8)
    bad = base.copy()
    bad[0, 0] = 255
    cv2.imwrite(str(proj / "assets" / "base.png"), base)

    import vhk.core.runner as runner_mod

    state = {"i": 0}

    def fake_capture(path: Path, region=None):
        img = bad if state["i"] == 0 else base
        cv2.imwrite(str(path), img)
        state["i"] += 1
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.event_log
    events = [json.loads(line) for line in Path(res.event_log).read_text().splitlines()]
    assert any(e["type"] == "step_retry" for e in events)


def test_continue_on_error_keeps_macro_running(tmp_path: Path, monkeypatch):
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
                        "continue_on_error": True,
                    },
                    {"type": "SetVar", "name": "after", "value": "still running"},
                ],
            }
        },
    )

    base = np.zeros((10, 10, 3), dtype=np.uint8)
    bad = base.copy()
    bad[0, 0] = 255
    cv2.imwrite(str(proj / "assets" / "base.png"), base)

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), bad)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.vars["after"] == "still running"
    assert res.vars["last_error"]["step_type"] == "VisualAssert"
    assert res.vars["errors"]


def test_wait_attempts_and_error_artifacts_use_last_capture(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": True, "screenshot_on_error": True, "trace_wait_attempts": True},
            "macros": {"m": "macros/m.yaml"},
        },
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForText",
                        "pattern": "READY",
                        "timeout_ms": 20,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 2,
                    }
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    cap = np.zeros((12, 12, 3), dtype=np.uint8)
    cap[:, :] = (10, 20, 30)

    def fake_capture(path: Path, region=None):
        cv2.imwrite(str(path), cap)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)
    monkeypatch.setattr(runner_mod, "ocr_read_text_file", lambda path, lang="eng", **_kwargs: "nope")

    res = Runner(load_project(proj)).run("m")
    assert not res.ok
    assert res.event_log

    events = [json.loads(line) for line in Path(res.event_log).read_text().splitlines()]
    attempts = [e for e in events if e["type"] == "wait_attempt" and e.get("kind") == "text"]
    assert len(attempts) == 2

    step_end = next(e for e in events if e["type"] == "step_end" and e["ok"] is False)
    screenshot = Path(step_end["screenshot"])
    error_context = Path(step_end["error_context"])
    assert screenshot.exists()
    assert error_context.exists()

    saved = cv2.imread(str(screenshot), cv2.IMREAD_COLOR)
    assert saved is not None
    assert saved.shape[:2] == cap.shape[:2]
