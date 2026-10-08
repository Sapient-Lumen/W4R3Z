from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

from vhk.system.event_bus import iter_bus_events
from vhk.system.hypr_socket2 import bridge_hypr_custom_to_bus


def test_bridge_hypr_custom_to_bus(tmp_path: Path):
    bus_sock = tmp_path / "bus.sock"
    hypr_sock = tmp_path / "hypr.socket2.sock"

    # Start a bus listener that captures two events.
    got: list[tuple[str, object]] = []

    def listen():
        it = iter_bus_events(bus_sock, force_unlink=True)
        try:
            for _ in range(2):
                ev = next(it)
                got.append((ev.name, ev.data))
        finally:
            try:
                it.close()
            except Exception:
                pass

    t_listen = threading.Thread(target=listen, daemon=True)
    t_listen.start()

    deadline = time.time() + 2
    while not bus_sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    # Fake Hyprland socket2 server.
    def serve_socket2():
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.bind(str(hypr_sock))
            s.listen(1)
            conn, _ = s.accept()
            with conn:
                conn.sendall(b'custom>>{"macro":"a","vars":{"x":1}}\n')
                conn.sendall(b'workspace>>2\n')
                conn.sendall(b'custom>>hello\n')
        finally:
            try:
                s.close()
            except Exception:
                pass

    t_srv = threading.Thread(target=serve_socket2, daemon=True)
    t_srv.start()

    # Run the bridge (stop after forwarding 2 custom events).
    out = {"n": 0, "exc": None}

    def bridge():
        try:
            out["n"] = bridge_hypr_custom_to_bus(hypr_socket2=hypr_sock, bus_socket=bus_sock, bus_event="hypr.custom", max_events=2)
        except Exception as exc:
            out["exc"] = exc

    t_bridge = threading.Thread(target=bridge, daemon=True)
    t_bridge.start()

    t_bridge.join(timeout=2)
    t_listen.join(timeout=2)

    assert out["exc"] is None
    assert out["n"] == 2

    assert len(got) == 2
    assert got[0][0] == "hypr.custom"
    assert isinstance(got[0][1], dict)
    assert got[0][1].get("macro") == "a"
    assert got[1] == ("hypr.custom", "hello")
