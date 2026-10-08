from __future__ import annotations

import json
import socket
import struct
import threading
import time
from pathlib import Path

import yaml

from vhk.core.runner import Runner
from vhk.i3.ipc import EVENT_MASK, GET_TREE, MAGIC, SUBSCRIBE
from vhk.project.loader import load_project


WINDOW_EVENT = EVENT_MASK | 3


def _read_exact(conn: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return buf


class FakeI3Server:
    def __init__(self, sock_path: Path, tree: dict):
        self.sock_path = sock_path
        self._tree = tree
        self._lock = threading.Lock()
        self._subs: list[socket.socket] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self.sock_path.exists():
            self.sock_path.unlink()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()
        deadline = time.time() + 2
        while not self.sock_path.exists() and time.time() < deadline:
            time.sleep(0.01)

    def stop(self) -> None:
        self._stop.set()
        with self._lock:
            for s in list(self._subs):
                try:
                    s.close()
                except Exception:
                    pass
            self._subs.clear()
        if self._thread:
            self._thread.join(timeout=2)

    def set_tree(self, tree: dict) -> None:
        with self._lock:
            self._tree = tree

    def send_window_event(self, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        hdr = MAGIC + struct.pack("=II", len(data), WINDOW_EVENT)
        with self._lock:
            subs = list(self._subs)
        for s in subs:
            try:
                s.sendall(hdr + data)
            except Exception:
                pass

    def _serve(self) -> None:
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(str(self.sock_path))
        srv.listen(5)
        srv.settimeout(0.1)
        try:
            while not self._stop.is_set():
                try:
                    conn, _ = srv.accept()
                except socket.timeout:
                    continue
                t = threading.Thread(target=self._handle_conn, args=(conn,), daemon=True)
                t.start()
        finally:
            try:
                srv.close()
            except Exception:
                pass

    def _handle_conn(self, conn: socket.socket) -> None:
        with conn:
            hdr = _read_exact(conn, len(MAGIC) + 8)
            if len(hdr) != len(MAGIC) + 8:
                return
            assert hdr[: len(MAGIC)] == MAGIC
            length, msg_type = struct.unpack("=II", hdr[len(MAGIC) :])
            _ = _read_exact(conn, length)

            if msg_type == GET_TREE:
                with self._lock:
                    payload = json.dumps(self._tree).encode("utf-8")
                reply_hdr = MAGIC + struct.pack("=II", len(payload), msg_type)
                conn.sendall(reply_hdr + payload)
                return

            if msg_type == SUBSCRIBE:
                payload = json.dumps({"success": True}).encode("utf-8")
                reply_hdr = MAGIC + struct.pack("=II", len(payload), msg_type)
                conn.sendall(reply_hdr + payload)
                with self._lock:
                    self._subs.append(conn)
                while not self._stop.is_set():
                    time.sleep(0.01)


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_window_vanish_uses_events(tmp_path: Path, monkeypatch):
    tree0 = {
        "type": "root",
        "nodes": [
            {
                "type": "workspace",
                "name": "1",
                "nodes": [
                    {
                        "type": "con",
                        "id": 55,
                        "name": "Firefox",
                        "urgent": False,
                        "focused": True,
                        "window_properties": {"class": "Firefox", "title": "web"},
                        "nodes": [],
                        "floating_nodes": [],
                    }
                ],
                "floating_nodes": [],
            }
        ],
        "floating_nodes": [],
    }

    sock_path = tmp_path / "i3.sock"
    srv = FakeI3Server(sock_path, tree0)
    srv.start()

    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForWindowVanish",
                    "selector": {"class": "Firefox", "workspace": "1"},
                    "timeout_ms": 2000,
                    "poll_ms": 1000,
                    "use_events": True,
                    "require_seen": True,
                    "out_seen": "seen",
                    "out_last_con_id": "last_id",
                    "out_last_workspace": "last_ws",
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    monkeypatch.setenv("I3SOCK", str(sock_path))

    def later():
        time.sleep(0.08)
        tree1 = {
            "type": "root",
            "nodes": [
                {"type": "workspace", "name": "1", "nodes": [], "floating_nodes": []},
            ],
            "floating_nodes": [],
        }
        srv.set_tree(tree1)
        srv.send_window_event({"change": "close", "container": {"id": 55}})

    threading.Thread(target=later, daemon=True).start()

    try:
        res = Runner(project).run("m")
        assert res.ok
        assert res.vars["seen"] is True
        assert res.vars["last_id"] == 55
        assert res.vars["last_ws"] == "1"
    finally:
        srv.stop()



def test_wait_for_window_vanish_x11_uses_snapshot_fallback(tmp_path: Path, monkeypatch) -> None:
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForWindowVanish",
                    "selector": {"class": "Firefox", "title": "Docs"},
                    "timeout_ms": 500,
                    "poll_ms": 10,
                    "use_events": False,
                    "require_seen": True,
                    "out_seen": "seen",
                    "out_last_con_id": "last_id",
                    "out_last_workspace": "last_ws",
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    import vhk.system.active_window as aw
    import vhk.core.runner as runner_mod

    rows_seq = [
        ([{"id": "0x4040", "class": "Firefox", "title": "Docs", "workspace": "Web", "focused": True}], "x11"),
        ([], "x11"),
    ]
    calls = {"count": 0}

    def fake_snapshot(*, selector=None, include_geometry=False, focused_first=True):
        assert include_geometry is False
        calls["count"] += 1
        if calls["count"] <= len(rows_seq):
            return rows_seq[calls["count"] - 1]
        return rows_seq[-1]

    monkeypatch.setattr(aw, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(aw, "get_window_list_snapshot", fake_snapshot)
    monkeypatch.setattr(runner_mod, "I3Connection", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("i3 path should not be used for x11 vanish waits")))

    res = Runner(project).run("m")
    assert res.ok is True
    assert res.vars["seen"] is True
    assert res.vars["last_id"] == "0x4040"
    assert res.vars["last_ws"] == "Web"
