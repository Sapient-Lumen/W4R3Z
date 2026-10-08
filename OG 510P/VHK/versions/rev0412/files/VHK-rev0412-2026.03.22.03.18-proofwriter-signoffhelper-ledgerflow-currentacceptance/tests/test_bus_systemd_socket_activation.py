from __future__ import annotations

import os
import socket
from pathlib import Path

from vhk.system.event_bus import emit_bus_event, iter_bus_events


def _fd_is_open(fd: int) -> bool:
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


def test_iter_bus_events_uses_systemd_fd(monkeypatch, tmp_path: Path):
    sock_path = tmp_path / "bus.sock"

    # Create and bind a real AF_UNIX datagram socket.
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.bind(str(sock_path))

    old3 = None
    try:
        if _fd_is_open(3):
            old3 = os.dup(3)

        # Duplicate the bound socket fd into fd 3.
        dupfd = os.dup(s.fileno())
        os.dup2(dupfd, 3)
        os.close(dupfd)

        monkeypatch.setenv("LISTEN_PID", str(os.getpid()))
        monkeypatch.setenv("LISTEN_FDS", "1")

        it = iter_bus_events(sock_path, timeout_s=0.5, use_systemd=True)
        try:
            emit_bus_event(sock_path, "ping", {"x": 1})
            ev = next(it)
            assert ev.name == "ping"
            assert ev.data == {"x": 1}
        finally:
            try:
                it.close()
            except Exception:
                pass

    finally:
        try:
            s.close()
        except Exception:
            pass
        try:
            if sock_path.exists():
                sock_path.unlink()
        except Exception:
            pass

        # Restore fd 3 if it was previously in use.
        if old3 is not None:
            try:
                os.dup2(old3, 3)
            finally:
                try:
                    os.close(old3)
                except Exception:
                    pass
