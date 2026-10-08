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

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_text_vanish_require_seen_and_stable(tmp_path: Path, monkeypatch):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForTextVanish",
                    "pattern": "LOADING",
                    "match": "contains",
                    "timeout_ms": 200,
                    "poll_ms": 0,
                    "jitter_ms": 0,
                    "max_attempts": 10,
                    "require_seen": True,
                    "stable_attempts": 2,
                    "out_text": "t",
                    "out_seen": "seen",
                    "out_last_text": "last_text",
                    "out_last_present": "last_present",
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):  # noqa: ARG001
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imwrite(str(path), img)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)

    state = {"i": 0}

    def fake_ocr(path: Path, lang="eng", **_kwargs):  # noqa: ARG001
        state["i"] += 1
        # First two scans: pattern present
        if state["i"] <= 2:
            return "... LOADING ..."
        # Then vanish
        return "done"

    monkeypatch.setattr(runner_mod, "ocr_read_text_file", fake_ocr)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["seen"] is True
    assert "LOADING" in res.vars["last_text"]
    assert res.vars["last_present"] is False


def test_wait_for_text_accepts_scan_rate_hz(tmp_path: Path, monkeypatch):
    """Regression: WaitForText should accept scan_rate_hz and runner should honor it."""

    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForText",
                    "pattern": "READY",
                    "match": "contains",
                    "timeout_ms": 200,
                    "scan_rate_hz": 1000,
                    "poll_ms": 999,
                    "jitter_ms": 0,
                    "max_attempts": 3,
                    "out_text": "t",
                    "out_found": "found",
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)

    import vhk.core.runner as runner_mod

    def fake_capture(path: Path, region=None):  # noqa: ARG001
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imwrite(str(path), img)
        return path

    monkeypatch.setattr(runner_mod.screenshot_mod, "capture", fake_capture)
    monkeypatch.setattr(runner_mod, "ocr_read_text_file", lambda _path, **_kw: "READY")

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["found"] is True
    assert res.vars["t"] == "READY"
