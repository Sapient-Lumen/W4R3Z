from __future__ import annotations

import json
import socket
import struct
import threading
import time
from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.i3.ipc import EVENT_MASK, GET_TREE, MAGIC, SUBSCRIBE, I3Connection
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
                # Keep open until stop.
                while not self._stop.is_set():
                    time.sleep(0.01)
                return

            # Other message types not needed for these tests.
            payload = json.dumps([]).encode("utf-8")
            reply_hdr = MAGIC + struct.pack("=II", len(payload), msg_type)
            conn.sendall(reply_hdr + payload)


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_i3_subscribe_yields_timeout(tmp_path: Path):
    tree = {"type": "root", "nodes": [], "floating_nodes": []}
    sock_path = tmp_path / "i3.sock"
    srv = FakeI3Server(sock_path, tree)
    srv.start()

    try:
        i3 = I3Connection(socket_path=str(sock_path), timeout=0.2)
        it = i3.subscribe(["window"], timeout=0.05, yield_timeouts=True)
        name, payload = next(it)
        assert name == "timeout"
        assert payload is None
        it.close()
    finally:
        srv.stop()


def test_wait_for_window_uses_ipc_events_and_sets_workspace(tmp_path: Path, monkeypatch):
    # Initial tree: a terminal on workspace 1.
    tree0 = {
        "type": "root",
        "nodes": [
            {
                "type": "workspace",
                "name": "1",
                "nodes": [
                    {
                        "type": "con",
                        "id": 10,
                        "name": "term",
                        "window_properties": {"class": "Alacritty", "title": "term"},
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

    # Macro waits for class "Firefox".
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForWindow",
                    "selector": {"class": "Firefox", "workspace": "1"},
                    "timeout_ms": 2000,
                    "poll_ms": 1000,
                    "use_events": True,
                    "focus": False,
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    monkeypatch.setenv("I3SOCK", str(sock_path))

    def later():
        # After a short delay, add Firefox and send a window event.
        time.sleep(0.08)
        tree1 = {
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
        srv.set_tree(tree1)
        srv.send_window_event({"change": "new", "container": {"id": 55}})

    threading.Thread(target=later, daemon=True).start()

    try:
        res = Runner(project).run("m")
        assert res.ok
        assert res.vars["i3_con_id"] == 55
        assert res.vars["i3_workspace"] == "1"
        assert isinstance(res.vars["i3_window"], dict)
    finally:
        srv.stop()


def test_wait_for_window_hyprland_clients_polling(tmp_path: Path, monkeypatch):
    # This is a pure unit test: monkeypatch hyprctl_json to simulate clients appearing.
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForWindow",
                    "selector": {"class": "kitty", "title": "Work", "title_regex": False},
                    "timeout_ms": 500,
                    "poll_ms": 50,
                    "focus": False,
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "test")

    calls = {"n": 0}

    def fake_hyprctl_json(subcommand: str):
        calls["n"] += 1
        if subcommand == "clients":
            if calls["n"] < 3:
                return []
            return [
                {
                    "address": "0xabc",
                    "class": "kitty",
                    "title": "Work",
                    "workspace": {"name": "2"},
                    "urgent": False,
                }
            ]
        if subcommand == "activewindow":
            return {"address": "0xabc"}
        raise RuntimeError("unexpected")

    import vhk.system.hyprctl as hyprctl_mod

    monkeypatch.setattr(hyprctl_mod, "hyprctl_json", fake_hyprctl_json)

    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["i3_con_id"] == "0xabc"
    assert res.vars["i3_workspace"] == "2"



def test_wait_for_window_hyprland_can_match_stateful_selector(tmp_path: Path, monkeypatch):
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForWindow",
                    "selector": {"class": "mpv", "floating": True, "fullscreen": True, "visible": True},
                    "timeout_ms": 500,
                    "poll_ms": 50,
                    "focus": False,
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "test")

    calls = {"n": 0}

    def fake_hyprctl_json(subcommand: str):
        calls["n"] += 1
        if subcommand == "clients":
            if calls["n"] < 3:
                return [{"address": "0xaaa", "class": "mpv", "title": "video", "workspace": {"name": "2"}, "floating": 0, "fullscreen": 0, "mapped": 1, "hidden": 0}]
            return [
                {
                    "address": "0xabc",
                    "class": "mpv",
                    "title": "video",
                    "workspace": {"name": "2"},
                    "floating": 1,
                    "fullscreenmode": 2,
                    "mapped": 1,
                    "hidden": 0,
                }
            ]
        if subcommand == "activewindow":
            return {"address": "0xabc"}
        raise RuntimeError("unexpected")

    import vhk.system.hyprctl as hyprctl_mod

    monkeypatch.setattr(hyprctl_mod, "hyprctl_json", fake_hyprctl_json)

    res = Runner(project).run("m")
    assert res.ok
    assert res.vars["i3_con_id"] == "0xabc"
    assert res.vars["i3_workspace"] == "2"



class FakeHyprSocket2Server:
    def __init__(self, sock_path: Path):
        self.sock_path = sock_path
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self.sock_path.exists():
            self.sock_path.unlink()
        self.sock_path.parent.mkdir(parents=True, exist_ok=True)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()
        deadline = time.time() + 2
        while not self.sock_path.exists() and time.time() < deadline:
            time.sleep(0.01)

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def send_once_after(self, line: str, delay_s: float = 0.05) -> None:
        def later():
            time.sleep(delay_s)
            try:
                # One-shot connect to trigger accept path if server isn't yet connected.
                pass
            except Exception:
                pass
            self._send_line = line

        threading.Thread(target=later, daemon=True).start()

    def _serve(self) -> None:
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(str(self.sock_path))
        srv.listen(5)
        srv.settimeout(0.1)
        send_line: str | None = None
        try:
            while not self._stop.is_set():
                try:
                    conn, _ = srv.accept()
                except socket.timeout:
                    continue
                with conn:
                    # Wait for a line to be scheduled.
                    deadline = time.time() + 2
                    while not self._stop.is_set() and time.time() < deadline:
                        send_line = getattr(self, '_send_line', None)
                        if send_line:
                            break
                        time.sleep(0.01)
                    if send_line:
                        conn.sendall((send_line + "\n").encode("utf-8"))
                        # Keep the socket open a bit longer.
                        time.sleep(0.05)
        finally:
            try:
                srv.close()
            except Exception:
                pass


def test_wait_for_window_hyprland_socket2_events(tmp_path: Path, monkeypatch):
    """WaitForWindow on Hyprland should use socket2 as a wakeup mechanism when enabled."""

    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForWindow",
                    "selector": {"class": "kitty", "title": "Work", "title_regex": False},
                    "timeout_ms": 1500,
                    "poll_ms": 5000,
                    "use_events": True,
                    "focus": False,
                }
            ],
        }
    }

    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    runtime = tmp_path / 'run'
    monkeypatch.setenv('XDG_RUNTIME_DIR', str(runtime))
    monkeypatch.setenv('HYPRLAND_INSTANCE_SIGNATURE', 'sig')

    sock_path = runtime / 'hypr' / 'sig' / '.socket2.sock'
    srv = FakeHyprSocket2Server(sock_path)
    srv.start()

    ready = threading.Event()

    def fake_hyprctl_json(subcommand: str):
        if subcommand == 'clients':
            if not ready.is_set():
                return []
            return [
                {
                    'address': '0xabc',
                    'class': 'kitty',
                    'title': 'Work',
                    'workspace': {'name': '2'},
                    'urgent': False,
                }
            ]
        if subcommand == 'activewindow':
            return {'address': '0xabc'}
        raise RuntimeError('unexpected')

    import vhk.system.hyprctl as hyprctl_mod
    monkeypatch.setattr(hyprctl_mod, 'hyprctl_json', fake_hyprctl_json)

    # If we fall back to poll-based sleep, this will fail.
    import vhk.core.runner as runner_mod

    orig_sleep = time.sleep

    def no_big_sleep(seconds: float):
        # Allow tiny sleeps used for error backoff, but not a full poll sleep.
        if seconds > 0.2:
            raise AssertionError(f'unexpected sleep: {seconds}')
        orig_sleep(seconds)

    monkeypatch.setattr(runner_mod.time, 'sleep', no_big_sleep)

    def later():
        time.sleep(0.08)
        ready.set()
        srv._send_line = 'activewindowv2>>0xabc'

    threading.Thread(target=later, daemon=True).start()

    try:
        res = Runner(project).run('m')
        assert res.ok
        assert res.vars['i3_con_id'] == '0xabc'
        assert res.vars['i3_workspace'] == '2'
    finally:
        srv.stop()
