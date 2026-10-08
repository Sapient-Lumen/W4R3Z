from __future__ import annotations

import json
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


def test_wait_for_image_file_and_outputs(tmp_path: Path):
    # Create hay/needle images in assets
    hay = np.zeros((80, 100, 3), dtype=np.uint8)
    hay[10:20, 30:40] = 255
    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:] = 255

    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    cv2.imwrite(str(proj / "assets" / "hay.png"), hay)
    cv2.imwrite(str(proj / "assets" / "needle.png"), needle)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForImageFile",
                        "haystack_path": "assets/hay.png",
                        "needle_path": "assets/needle.png",
                        "threshold": 0.9,
                        "timeout_ms": 50,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "out_x": "x",
                        "out_y": "y",
                        "out_score": "s",
                    }
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "macros": {"m": "macros/m.yaml"}}))

    project = load_project(proj)
    r = Runner(project)
    res = r.run("m")
    assert res.ok
    assert res.vars["x"] == 30
    assert res.vars["y"] == 10
    assert res.vars["s"] >= 0.9


def test_call_macro_returns(tmp_path: Path):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "macros": {"parent": "macros/parent.yaml", "child": "macros/child.yaml"},
    }

    macros = {
        "child": {"name": "child", "steps": [{"type": "SetVar", "name": "rv", "value": "hi ${who}"}]},
        "parent": {
            "name": "parent",
            "steps": [
                {"type": "SetVar", "name": "who", "value": "bob"},
                {"type": "CallMacro", "macro": "child", "args": {"who": "${who}"}, "returns": {"rv": "out"}},
            ],
        },
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)
    res = Runner(project).run("parent")
    assert res.ok
    assert res.vars["out"] == "hi bob"


def test_panic_file_stops_run(tmp_path: Path):
    panic_file = tmp_path / "panic.flag"
    panic_file.write_text("panic")

    manifest = {
        "name": "p",
        "settings": {"event_log": False, "panic_file": str(panic_file)},
        "macros": {"m": "macros/m.yaml"},
    }
    macros = {"m": {"name": "m", "steps": [{"type": "Log", "message": "hello"}]}}
    proj = _write_project(tmp_path, manifest, macros)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert not res.ok
    assert "Panic file" in (res.error or "")
