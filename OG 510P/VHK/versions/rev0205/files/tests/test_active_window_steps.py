from __future__ import annotations

from pathlib import Path

import pytest
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


def test_get_active_window_step_populates_watcher_style_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "GetActiveWindow"},
                {"type": "Return", "value_expr": "window.title + '|' + window_class + '|' + wm + '|' + str(window.geometry.rect.x)"},
            ],
        }
    }
    proj_dir = _write_project(tmp_path, manifest, macros)
    proj = load_project(proj_dir)

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(
        runner_mod.active_window_mod,
        "get_active_window_snapshot",
        lambda **kwargs: (
            {
                "wm": "x11",
                "id": 42,
                "pid": 777,
                "class": "Firefox",
                "title": "Mozilla Firefox",
                "workspace": "1",
                "urgent": False,
                "process_name": "firefox",
                "geometry": {"rect": {"x": 10, "y": 20, "w": 300, "h": 200}, "client": {"x": 12, "y": 25, "w": 296, "h": 190}},
            },
            "x11",
        ),
    )

    res = Runner(proj).run("m")
    assert res.ok is True
    assert res.vars["wm"] == "x11"
    assert res.vars["window"]["title"] == "Mozilla Firefox"
    assert res.vars["window_title"] == "Mozilla Firefox"
    assert res.vars["window_class"] == "Firefox"
    assert res.vars["workspace"] == "1"
    assert res.vars["urgent"] is False
    assert res.vars["window_pid"] == 777
    assert res.vars["window_process"] == "firefox"
    assert res.vars["return_value"] == "Mozilla Firefox|Firefox|x11|10"


def test_get_active_window_snapshot_downgrades_missing_geometry(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_active_window_info",
        lambda: ({"class": "Alacritty", "title": "shell", "focused": True}, "sway"),
    )

    def boom():
        raise aw.ActiveWindowProbeError("no geometry")

    monkeypatch.setattr(aw, "get_active_window_geometry", boom)

    snapshot, wm = aw.get_active_window_snapshot(include_geometry=True, require_geometry=False)
    assert wm == "sway"
    assert snapshot["wm"] == "sway"
    assert snapshot["title"] == "shell"
    assert snapshot["geometry"] is None



def test_get_active_window_snapshot_can_require_geometry(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_active_window_info",
        lambda: ({"class": "Alacritty", "title": "shell", "focused": True}, "sway"),
    )
    monkeypatch.setattr(aw, "get_active_window_geometry", lambda: (_ for _ in ()).throw(aw.ActiveWindowProbeError("no geometry")))

    with pytest.raises(aw.ActiveWindowProbeError):
        aw.get_active_window_snapshot(include_geometry=True, require_geometry=True)
