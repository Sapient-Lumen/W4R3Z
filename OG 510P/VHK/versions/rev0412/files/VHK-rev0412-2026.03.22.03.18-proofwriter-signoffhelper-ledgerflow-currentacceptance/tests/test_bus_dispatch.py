from __future__ import annotations

import threading
import time
from pathlib import Path

import yaml

from vhk.project.loader import load_project
from vhk.core.bus_watchers import run_bus_watcher
from vhk.system.event_bus import emit_bus_event, get_bus_socket_path


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "data").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_bus_dispatch_runs_target_macro(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
        "macros": {"hit": "macros/hit.yaml"},
    }
    macros = {
        "hit": {
            "name": "hit",
            "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "${dispatch_binding}:${x}\n"}],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    sock = get_bus_socket_path(proj, configured=project.settings.bus_socket)
    out = {"stats": None, "exc": None}

    def watcher():
        try:
            out["stats"] = run_bus_watcher(project, "hotkeys", max_events=1)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    emit_bus_event(sock, "hotkey", {"macro": "hit", "vars": {"x": 3}, "binding": "B"})
    t.join(timeout=2)

    assert out["exc"] is None
    assert out["stats"] is not None
    assert out["stats"].macro_runs == 1
    assert (proj / "data" / "out.txt").read_text().strip() == "B:3"


def test_bus_dispatch_require_window_can_skip(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
        "macros": {"hit": "macros/hit.yaml"},
    }
    macros = {
        "hit": {
            "name": "hit",
            "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "ran\n"}],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    import vhk.core.bus_watchers as bw

    monkeypatch.setattr(bw, "get_active_window_info", lambda: ({"class": "Chromium", "title": "x"}, "i3"))

    sock = get_bus_socket_path(proj, configured=project.settings.bus_socket)
    out = {"stats": None, "exc": None}

    def watcher():
        try:
            out["stats"] = run_bus_watcher(project, "hotkeys", max_events=1)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    emit_bus_event(
        sock,
        "hotkey",
        {
            "macro": "hit",
            "vars": {},
            "binding": "B",
            "require_window": {"class": "Firefox"},
        },
    )

    t.join(timeout=2)
    assert out["exc"] is None
    assert out["stats"] is not None
    assert out["stats"].events_seen == 1
    assert out["stats"].macro_runs == 0
    assert out["stats"].skipped_nonmatching == 1
    assert not (proj / "data" / "out.txt").exists()
