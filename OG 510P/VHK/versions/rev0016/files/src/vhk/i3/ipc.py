from __future__ import annotations

import json
import os
import socket
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAGIC = b"i3-ipc"

# Message types (subset)
COMMAND = 0
GET_WORKSPACES = 1
SUBSCRIBE = 2
GET_OUTPUTS = 3
GET_TREE = 4


@dataclass
class I3Reply:
    msg_type: int
    payload: Any


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        full = Path(p) / cmd
        if full.exists() and os.access(full, os.X_OK):
            return str(full)
    return None


def _try_xprop_socketpath() -> str | None:
    """Try to read i3's I3_SOCKET_PATH X11 root window property.

    i3 docs note i3 utilities consult this property when I3SOCK is not set.
    """

    xprop = _which("xprop")
    if not xprop:
        return None

    try:
        out = subprocess.check_output([xprop, "-root", "I3_SOCKET_PATH"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return None

    # Example: I3_SOCKET_PATH(STRING) = "/run/user/1000/i3/ipc-socket.1234"
    if "=" not in out:
        return None
    rhs = out.split("=", 1)[1].strip()
    if rhs.startswith('"') and rhs.endswith('"'):
        rhs = rhs[1:-1]
    return rhs or None


def _glob_candidates(user: str) -> list[str]:
    cands: list[str] = []

    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        cands += [str(p) for p in (Path(xdg) / "i3").glob("ipc-socket.*")]
        # sway commonly uses sway-ipc.* directly under XDG_RUNTIME_DIR
        cands += [str(p) for p in Path(xdg).glob("sway-ipc.*")]

    # i3 docs mention /tmp/i3-%u.XXXXXX/ipc-socket.%p
    tmp_root = Path("/tmp")
    for d in tmp_root.glob(f"i3-{user}.*"):
        cands += [str(p) for p in d.glob("ipc-socket.*")]

    return cands


def discover_socket_path() -> str:
    """Best-effort discovery following i3's documented precedence.

    Order:
      1) I3SOCK env var
      2) `i3 --get-socketpath`
      3) X11 root window property I3_SOCKET_PATH (via xprop)
      4) glob common runtime dirs
    """

    if os.environ.get("SWAYSOCK"):
        return os.environ["SWAYSOCK"]
    if os.environ.get("I3SOCK"):
        return os.environ["I3SOCK"]

    sway_bin = _which("sway")
    if sway_bin:
        try:
            out = subprocess.check_output([sway_bin, "--get-socketpath"], text=True).strip()
            if out:
                return out
        except Exception:
            pass

    i3_bin = _which("i3")
    if i3_bin:
        try:
            out = subprocess.check_output([i3_bin, "--get-socketpath"], text=True).strip()
            if out:
                return out
        except Exception:
            pass

    sp = _try_xprop_socketpath()
    if sp:
        return sp

    user = os.environ.get("USER") or ""
    for p in _glob_candidates(user):
        if Path(p).exists():
            return p

    raise RuntimeError("Unable to discover i3/sway IPC socket path (set I3SOCK/SWAYSOCK)")


class I3Connection:
    def __init__(self, socket_path: str | None = None, timeout: float = 2.0):
        self.socket_path = socket_path or discover_socket_path()
        self.timeout = timeout

    def _connect(self) -> socket.socket:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect(self.socket_path)
        return s

    def _send(self, msg_type: int, payload: str = "") -> I3Reply:
        data = payload.encode("utf-8")
        header = MAGIC + struct.pack("=II", len(data), msg_type)
        with self._connect() as s:
            s.sendall(header + data)
            return self._recv(s)

    def _recv(self, s: socket.socket) -> I3Reply:
        hdr = s.recv(len(MAGIC) + 8)
        if len(hdr) != len(MAGIC) + 8:
            raise RuntimeError("Short read from i3 IPC")
        magic = hdr[: len(MAGIC)]
        if magic != MAGIC:
            raise RuntimeError("Bad IPC magic")
        length, msg_type = struct.unpack("=II", hdr[len(MAGIC) :])
        body = b""
        while len(body) < length:
            chunk = s.recv(length - len(body))
            if not chunk:
                break
            body += chunk
        if len(body) != length:
            raise RuntimeError("Short payload from i3 IPC")

        payload_text = body.decode("utf-8")
        try:
            payload = json.loads(payload_text) if payload_text else None
        except json.JSONDecodeError:
            payload = payload_text
        return I3Reply(msg_type=msg_type, payload=payload)

    def command(self, cmd: str) -> Any:
        return self._send(COMMAND, cmd).payload

    def get_tree(self) -> Any:
        return self._send(GET_TREE, "").payload

    def get_workspaces(self) -> Any:
        return self._send(GET_WORKSPACES, "").payload
