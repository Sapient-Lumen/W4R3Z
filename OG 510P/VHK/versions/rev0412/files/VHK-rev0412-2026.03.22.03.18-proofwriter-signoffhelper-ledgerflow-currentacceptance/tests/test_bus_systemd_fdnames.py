from __future__ import annotations

import os
import socket
from pathlib import Path

import pytest

from vhk.system.event_bus import emit_bus_event, iter_bus_events


def _fd_is_open(fd: int) -> bool:
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


def _stash_fd(fd: int) -> int | None:
    if _fd_is_open(fd):
        return os.dup(fd)
    return None


def _restore_fd(fd: int, saved: int | None) -> None:
    if saved is None:
        return
    try:
        os.dup2(saved, fd)
    finally:
        try:
            os.close(saved)
        except Exception:
            pass


def test_iter_bus_events_selects_named_systemd_fd(monkeypatch, tmp_path: Path):
    sock1 = tmp_path / "bus1.sock"
    sock2 = tmp_path / "bus2.sock"

    s1 = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s2 = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s1.bind(str(sock1))
    s2.bind(str(sock2))

    old3 = _stash_fd(3)
    old4 = _stash_fd(4)

    try:
        # Duplicate the bound socket fds into fd 3 and 4.
        dupfd = os.dup(s1.fileno())
        os.dup2(dupfd, 3)
        os.close(dupfd)

        dupfd = os.dup(s2.fileno())
        os.dup2(dupfd, 4)
        os.close(dupfd)

        monkeypatch.setenv("LISTEN_PID", str(os.getpid()))
        monkeypatch.setenv("LISTEN_FDS", "2")
        monkeypatch.setenv("LISTEN_FDNAMES", "other:vhk-bus")

        it = iter_bus_events(sock2, timeout_s=0.5, use_systemd=True, fdname="vhk-bus")
        try:
            emit_bus_event(sock2, "ping", {"ok": True})
            ev = next(it)
            assert ev.name == "ping"
            assert ev.data == {"ok": True}
        finally:
            try:
                it.close()
            except Exception:
                pass

    finally:
        try:
            s1.close()
        except Exception:
            pass
        try:
            s2.close()
        except Exception:
            pass
        _restore_fd(3, old3)
        _restore_fd(4, old4)


def test_iter_bus_events_named_fd_not_found_raises(monkeypatch, tmp_path: Path):
    sock1 = tmp_path / "bus1.sock"

    s1 = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s1.bind(str(sock1))

    old3 = _stash_fd(3)

    try:
        dupfd = os.dup(s1.fileno())
        os.dup2(dupfd, 3)
        os.close(dupfd)

        monkeypatch.setenv("LISTEN_PID", str(os.getpid()))
        monkeypatch.setenv("LISTEN_FDS", "1")
        monkeypatch.setenv("LISTEN_FDNAMES", "not-it")

        with pytest.raises(RuntimeError):
            _ = iter_bus_events(sock1, timeout_s=0.5, use_systemd=True, fdname="vhk-bus")
            # iter_bus_events returns an iterator; force open by advancing.
            next(_)

    finally:
        try:
            s1.close()
        except Exception:
            pass
        _restore_fd(3, old3)
