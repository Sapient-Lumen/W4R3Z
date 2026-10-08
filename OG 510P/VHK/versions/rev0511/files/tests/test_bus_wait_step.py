from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.event_bus import emit_bus_event


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_bus_event_matches_pattern_and_condition(tmp_path: Path):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForBusEvent",
                    "socket_path": ".vhk/wait.sock",
                    "event": "hotkey",
                    "pattern": '"macro": "hit"',
                    "condition": "bus_data['vars']['x'] == 7",
                    "timeout_ms": 1000,
                }
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)
    sock = proj / ".vhk" / "wait.sock"

    def later() -> None:
        deadline = time.time() + 1.0
        while not sock.exists() and time.time() < deadline:
            time.sleep(0.01)
        emit_bus_event(sock, "noise", {"macro": "hit", "vars": {"x": 7}})
        emit_bus_event(sock, "hotkey", {"macro": "miss", "vars": {"x": 7}})
        emit_bus_event(sock, "hotkey", {"macro": "hit", "vars": {"x": 3}})
        emit_bus_event(sock, "hotkey", {"macro": "hit", "vars": {"x": 7}, "binding": "M-h"})

    threading.Thread(target=later, daemon=True).start()
    res = Runner(project).run("m")
    assert res.ok, res.error
    assert res.vars["bus_event"] == "hotkey"
    assert res.vars["bus_data"]["binding"] == "M-h"
    assert '"macro": "hit"' in res.vars["bus_text"]
    assert isinstance(res.vars["bus_raw"], str)
    assert isinstance(res.vars["bus_ts"], float)


def test_wait_for_bus_event_accepts_plain_text_protocol(tmp_path: Path):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForBusEvent",
                    "socket_path": ".vhk/raw.sock",
                    "event": "reload",
                    "pattern": "manual",
                    "timeout_ms": 1000,
                }
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)
    sock = proj / ".vhk" / "raw.sock"

    def later() -> None:
        deadline = time.time() + 1.0
        while not sock.exists() and time.time() < deadline:
            time.sleep(0.01)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            s.connect(str(sock))
            s.send(b"reload\tmanual-test")
        finally:
            s.close()

    threading.Thread(target=later, daemon=True).start()
    res = Runner(project).run("m")
    assert res.ok, res.error
    assert res.vars["bus_event"] == "reload"
    assert res.vars["bus_data"] == "manual-test"
    assert res.vars["bus_text"] == "manual-test"


def test_wait_for_bus_event_times_out(tmp_path: Path):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForBusEvent",
                    "socket_path": ".vhk/timeout.sock",
                    "event": "never",
                    "timeout_ms": 50,
                }
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    res = Runner(project).run("m")
    assert not res.ok
    assert "WaitForBusEvent timed out" in (res.error or "")
