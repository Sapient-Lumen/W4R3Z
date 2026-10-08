from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
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


def test_bus_watcher_runs_macro_on_matching_event(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "bus_watchers": [{"name": "w", "event": "ping", "macro": "hit"}],
        "macros": {"hit": "macros/hit.yaml"},
    }
    macros = {
        "hit": {
            "name": "hit",
            "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "${bus_event}:${bus_text}\n"}],
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
            out["stats"] = run_bus_watcher(project, "w", max_events=1)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    # Wait for the socket to appear (bound).
    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    emit_bus_event(sock, "ping", {"status": "ok"})

    t.join(timeout=2)
    assert out["exc"] is None
    assert out["stats"] is not None
    assert out["stats"].events_seen == 1
    assert out["stats"].macro_runs == 1

    assert (proj / "data" / "out.txt").read_text().strip() == 'ping:{"status": "ok"}'


def test_bus_watcher_can_gate_on_focused_window(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "bus_watchers": [
            {
                "name": "w",
                "event": "ping",
                "macro": "hit",
                "when": {"class": "Firefox"},
            }
        ],
        "macros": {"hit": "macros/hit.yaml"},
    }
    macros = {
        "hit": {
            "name": "hit",
            "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "${window_class}:${bus_event}\n"}],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    # First event: active window is terminal (skip). Second: firefox (run).
    infos = iter(
        [
            ({"id": 1, "class": "Alacritty", "title": "term"}, "i3"),
            ({"id": 2, "class": "Firefox", "title": "web"}, "i3"),
        ]
    )

    import vhk.core.bus_watchers as bw

    monkeypatch.setattr(bw, "get_active_window_info", lambda: next(infos))

    sock = get_bus_socket_path(proj, configured=project.settings.bus_socket)

    out = {"stats": None, "exc": None}

    def watcher():
        try:
            out["stats"] = run_bus_watcher(project, "w", max_events=2)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    emit_bus_event(sock, "ping", "one")
    emit_bus_event(sock, "ping", "two")

    t.join(timeout=2)
    assert out["exc"] is None
    assert out["stats"] is not None
    assert out["stats"].events_seen == 2
    assert out["stats"].macro_runs == 1

    assert (proj / "data" / "out.txt").read_text().strip() == "Firefox:ping"
