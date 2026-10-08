from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.cursor_pos import CursorPos


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_mousemove_smoothing_absolute(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # Arrange: a macro that moves from current (0,0) to (100, 50) in 4 steps.
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "MouseMove", "x": 100, "y": 50, "duration_ms": 80, "smooth_steps": 4, "easing": "linear"},
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(runner_mod.cursor_pos_mod, "get_cursor_pos", lambda: CursorPos(x=0, y=0, backend="test"))

    moves: list[tuple[int, int]] = []

    def fake_move(*, x=None, y=None, dx=None, dy=None, relative=False):
        assert relative is False
        moves.append((int(x), int(y)))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.time, "sleep", lambda *_args, **_kwargs: None)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    assert moves == [(25, 12), (50, 25), (75, 38), (100, 50)]


def test_mousemove_smoothing_relative(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "MouseMove", "dx": 10, "dy": 0, "relative": True, "duration_ms": 80, "smooth_steps": 4},
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)

    import vhk.core.runner as runner_mod

    deltas: list[tuple[int, int]] = []

    def fake_move(*, x=None, y=None, dx=None, dy=None, relative=False):
        assert relative is True
        deltas.append((int(dx), int(dy)))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.time, "sleep", lambda *_args, **_kwargs: None)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    # Cumulative rounding should preserve total dx.
    assert sum(dx for dx, _ in deltas) == 10
    assert deltas == [(2, 0), (3, 0), (3, 0), (2, 0)]


def test_mousedrag_smoothing_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "MouseDrag", "x1": 0, "y1": 0, "x2": 100, "y2": 0, "button": 1, "duration_ms": 80, "smooth_steps": 4},
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)

    import vhk.core.runner as runner_mod

    calls: list[tuple[str, tuple]] = []

    def fake_move(*, x=None, y=None, dx=None, dy=None, relative=False):
        calls.append(("move", (int(x), int(y), bool(relative))))

    def fake_click(button=1, *, down=False, up=False, clearmodifiers=False):
        calls.append(("click", (int(button), bool(down), bool(up))))

    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", fake_move)
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", fake_click)
    monkeypatch.setattr(runner_mod.time, "sleep", lambda *_args, **_kwargs: None)

    project = load_project(proj)
    res = Runner(project).run("m")
    assert res.ok

    # First move to x1,y1, then down, then intermediate moves, then up.
    assert calls[0] == ("move", (0, 0, False))
    assert calls[1] == ("click", (1, True, False))
    assert calls[-1] == ("click", (1, False, True))

    path = [c for c in calls if c[0] == "move"]
    # Includes the initial move to (0,0) plus the 4 smoothed points.
    assert path == [
        ("move", (0, 0, False)),
        ("move", (25, 0, False)),
        ("move", (50, 0, False)),
        ("move", (75, 0, False)),
        ("move", (100, 0, False)),
    ]
