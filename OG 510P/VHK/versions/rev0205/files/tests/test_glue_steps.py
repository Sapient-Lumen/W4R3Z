from __future__ import annotations

import threading
import time
from pathlib import Path

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.watch import FileState, wait_for_file


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_file_steps_roundtrip(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "WriteFile", "path": "data/out.txt", "text": "hello"},
                    {"type": "AppendFile", "path": "data/out.txt", "text": "\nworld"},
                    {"type": "WaitForFile", "path": "data/out.txt", "condition": "exists", "timeout_ms": 10, "poll_ms": 0, "max_attempts": 1},
                    {"type": "ReadFile", "path": "data/out.txt", "out_var": "txt"},
                    {"type": "ListDirectory", "path": "data", "pattern": "*.txt", "files_only": True, "out_var": "files"},
                ],
            }
        },
    )

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.vars["txt"] == "hello\nworld"
    assert res.vars["files"] == ["out.txt"]
    assert res.vars["file_exists"] is True


def test_wait_for_file_changed_polling(tmp_path: Path):
    p = tmp_path / "watch.txt"
    p.write_text("one")

    def mutate():
        time.sleep(0.03)
        p.write_text("two")

    t = threading.Thread(target=mutate, daemon=True)
    t.start()
    st = wait_for_file(p, condition="changed", timeout_ms=500, poll_ms=10, max_poll_ms=20, jitter_ms=0)
    t.join(timeout=1)
    assert st == FileState(True, p.stat().st_mtime_ns, p.stat().st_size)


def test_wait_for_clipboard_change_step_uses_watch_helper(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForClipboardChange",
                        "selection": "clipboard",
                        "timeout_ms": 100,
                        "poll_ms": 0,
                        "max_attempts": 1,
                        "out_text": "clip",
                    }
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    seen = {}

    def fake_wait(read_func, **kwargs):
        seen.update(kwargs)
        return "new clipboard text"

    monkeypatch.setattr(runner_mod.watch_mod, "wait_for_clipboard_change", fake_wait)

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.vars["clip"] == "new clipboard text"
    assert seen["selection"] == "clipboard"


def test_wait_for_clipboard_event_step_uses_watch_helper(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForClipboardEvent",
                        "selection": "clipboard",
                        "timeout_ms": 100,
                        "poll_ms": 0,
                        "max_attempts": 1,
                        "out_text": "clip",
                        "out_changed": "changed",
                        "out_event": "evt",
                    }
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    seen = {}

    def fake_wait(read_func, **kwargs):
        seen.update(kwargs)
        return ("new clipboard text", False)

    monkeypatch.setattr(runner_mod.watch_mod, "wait_for_clipboard_event", fake_wait)

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.vars["clip"] == "new clipboard text"
    assert res.vars["changed"] is False
    assert res.vars["evt"] is True
    assert seen["selection"] == "clipboard"


def test_mouse_drag_and_wheel(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "MouseDrag", "x1": 1, "y1": 2, "x2": 30, "y2": 40},
                    {"type": "MouseWheel", "clicks": -2, "axis": "vertical"},
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    calls = []
    monkeypatch.setattr(runner_mod.input_mod, "mouse_move", lambda **kw: calls.append(("move", kw)))
    monkeypatch.setattr(runner_mod.input_mod, "mouse_click", lambda *args, **kw: calls.append(("click", args, kw)))
    monkeypatch.setattr(runner_mod.input_mod, "mouse_wheel", lambda clicks, axis="vertical": calls.append(("wheel", clicks, axis)))

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert calls[0] == ("move", {"x": 1, "y": 2})
    assert calls[1][0] == "click" and calls[1][1] == (1,) and calls[1][2]["down"] is True
    assert calls[2] == ("move", {"x": 30, "y": 40})
    assert calls[3][0] == "click" and calls[3][1] == (1,) and calls[3][2]["up"] is True
    assert calls[4] == ("wheel", -2, "vertical")
