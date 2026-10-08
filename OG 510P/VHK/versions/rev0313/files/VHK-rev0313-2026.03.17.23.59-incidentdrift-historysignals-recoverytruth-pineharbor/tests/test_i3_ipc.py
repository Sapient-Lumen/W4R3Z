import json
import socket
import struct
import threading
import time
from pathlib import Path

from vhk.i3.ipc import GET_WORKSPACES, I3Connection, MAGIC


def _serve_once(sock_path: Path):
    if sock_path.exists():
        sock_path.unlink()
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(str(sock_path))
    srv.listen(1)
    conn, _ = srv.accept()
    with conn:
        hdr = conn.recv(len(MAGIC) + 8)
        assert hdr[: len(MAGIC)] == MAGIC
        length, msg_type = struct.unpack("=II", hdr[len(MAGIC) :])
        assert msg_type == GET_WORKSPACES
        body = b""
        while len(body) < length:
            body += conn.recv(length - len(body))
        assert body == b""  # payload empty

        payload = json.dumps([]).encode("utf-8")
        reply_hdr = MAGIC + struct.pack("=II", len(payload), msg_type)
        conn.sendall(reply_hdr + payload)
    srv.close()


def test_i3_ipc_get_workspaces(tmp_path: Path):
    sock_path = tmp_path / "i3.sock"
    t = threading.Thread(target=_serve_once, args=(sock_path,), daemon=True)
    t.start()

    # Wait for server to bind
    deadline = time.time() + 2
    while not sock_path.exists() and time.time() < deadline:
        time.sleep(0.01)

    i3 = I3Connection(socket_path=str(sock_path))
    workspaces = i3.get_workspaces()
    assert workspaces == []

    t.join(timeout=2)
