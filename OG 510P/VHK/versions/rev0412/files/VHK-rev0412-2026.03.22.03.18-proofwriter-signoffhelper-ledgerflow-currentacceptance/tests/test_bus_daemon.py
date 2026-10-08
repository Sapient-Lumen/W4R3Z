from __future__ import annotations

import threading
import time
from pathlib import Path

import yaml

from vhk.project.loader import load_project
from vhk.core.bus_watchers import run_bus_daemon
from vhk.system.event_bus import emit_bus_event, get_bus_socket_path


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "data").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_bus_daemon_runs_multiple_watchers_and_consume(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "bus_watchers": [
            {"name": "a", "event": "hotkey", "macro": "a", "consume": True},
            {"name": "b", "event": "hotkey", "macro": "b"},
        ],
        "macros": {"a": "macros/a.yaml", "b": "macros/b.yaml"},
    }
    macros = {
        "a": {"name": "a", "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "A\n"}]},
        "b": {"name": "b", "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "B\n"}]},
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    sock = get_bus_socket_path(proj, configured=project.settings.bus_socket)

    out = {"stats": None, "exc": None}

    def daemon():
        try:
            out["stats"] = run_bus_daemon(project, max_events=1)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=daemon, daemon=True)
    t.start()

    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    emit_bus_event(sock, "hotkey", {"x": 1})
    t.join(timeout=2)

    assert out["exc"] is None
    assert out["stats"] is not None
    # consume=True on watcher a, so b should not run.
    assert (proj / "data" / "out.txt").read_text().strip() == "A"


def test_bus_daemon_can_run_both_watchers_when_not_consuming(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "bus_watchers": [
            {"name": "a", "event": "hotkey", "macro": "a"},
            {"name": "b", "event": "hotkey", "macro": "b"},
        ],
        "macros": {"a": "macros/a.yaml", "b": "macros/b.yaml"},
    }
    macros = {
        "a": {"name": "a", "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "A\n"}]},
        "b": {"name": "b", "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "B\n"}]},
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    sock = get_bus_socket_path(proj, configured=project.settings.bus_socket)

    out = {"stats": None, "exc": None}

    def daemon():
        try:
            out["stats"] = run_bus_daemon(project, max_events=1)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=daemon, daemon=True)
    t.start()

    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    emit_bus_event(sock, "hotkey", {"x": 1})
    t.join(timeout=2)

    assert out["exc"] is None
    assert out["stats"] is not None
    assert (proj / "data" / "out.txt").read_text().splitlines() == ["A", "B"]


def test_bus_daemon_stop_event_exits(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False},
        "bus_watchers": [
            {"name": "a", "event": "hotkey", "macro": "a"},
        ],
        "macros": {"a": "macros/a.yaml"},
    }
    macros = {
        "a": {"name": "a", "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "A\n"}]},
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    sock = get_bus_socket_path(proj, configured=project.settings.bus_socket)

    out = {"stats": None, "exc": None}

    def daemon():
        try:
            out["stats"] = run_bus_daemon(project, max_events=None)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=daemon, daemon=True)
    t.start()

    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    emit_bus_event(sock, "hotkey", {"x": 1})
    emit_bus_event(sock, "vhk.stop", {"why": "test"})

    t.join(timeout=2)
    assert not t.is_alive(), "busd did not stop after vhk.stop"
    assert out["exc"] is None
    assert (proj / "data" / "out.txt").read_text().strip() == "A"
