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


def test_bus_daemon_reload_via_bus_event(tmp_path: Path, monkeypatch):
    manifest = {
        "name": "p",
        "settings": {"event_log": False, "bus_reload_event": "vhk.reload"},
        "bus_watchers": [
            {"name": "hotkeys", "event": "hotkey", "macro": "a"},
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
            out["stats"] = run_bus_daemon(project, max_events=2)
        except Exception as exc:
            out["exc"] = exc

    t = threading.Thread(target=daemon, daemon=True)
    t.start()

    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    # Change the macro on disk.
    (proj / "macros" / "a.yaml").write_text(
        yaml.safe_dump({"name": "a", "steps": [{"type": "AppendFile", "path": "data/out.txt", "text": "B\n"}]})
    )

    # Trigger reload and then the actual hotkey event.
    emit_bus_event(sock, "vhk.reload", {"why": "test"})
    emit_bus_event(sock, "hotkey", {"x": 1})

    t.join(timeout=2)

    assert out["exc"] is None
    assert out["stats"] is not None
    assert (proj / "data" / "out.txt").read_text().strip() == "B"
