from __future__ import annotations

import json
import os
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator


@dataclass
class BusEvent:
    """A small, local IPC event.

    This is intentionally simple: it is a glue layer that makes it easy for
    other tools (WM configs, scripts, systemd units) to trigger VHK macros
    without embedding VHK logic.

    Transport: a UNIX datagram socket.

    Notes
    -----
    - A UNIX datagram socket path is effectively single-consumer.
    - For long-lived setups, prefer `vhk busd` + cheap emitters (`vhk-emit`).
    - For systemd socket activation, VHK can consume an already-bound
      datagram socket passed in via the standard LISTEN_FDS/LISTEN_PID env.
    """

    name: str
    data: Any
    raw: str
    ts: float


def _hash_project_root(project_root: Path) -> str:
    import hashlib

    return hashlib.sha256(str(project_root.resolve()).encode("utf-8", errors="replace")).hexdigest()[:12]


def get_bus_socket_path(project_root: Path, *, configured: str | None = None) -> Path:
    """Return the bus socket path for a project.

    Resolution order:
      1) explicit `configured` (absolute or project-relative)
      2) env var `VHK_BUS_SOCKET`
      3) XDG_RUNTIME_DIR/vhk/bus_<hash>.sock
      4) <project>/.vhk/bus.sock
    """

    project_root = Path(project_root).resolve()

    if configured:
        p = Path(configured)
        if not p.is_absolute():
            p = project_root / p
        return p

    env = os.environ.get("VHK_BUS_SOCKET")
    if env:
        return Path(env)

    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        return Path(xdg) / "vhk" / f"bus_{_hash_project_root(project_root)}.sock"

    return project_root / ".vhk" / "bus.sock"


def _safe_unlink(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except FileNotFoundError:
        return
    except Exception:
        return


def emit_bus_event(sock_path: Path, name: str, data: Any = None) -> None:
    """Emit an event to the local bus."""

    payload = json.dumps({"name": str(name), "data": data}, ensure_ascii=False)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        s.connect(str(sock_path))
        s.send(payload.encode("utf-8"))
    finally:
        try:
            s.close()
        except Exception:
            pass


def event_text(ev: BusEvent) -> str:
    """Return a human-readable text representation of a bus event payload."""

    if isinstance(ev.data, str):
        return ev.data
    if ev.data is None:
        return ""
    try:
        return json.dumps(ev.data, ensure_ascii=False)
    except Exception:
        return str(ev.data)


def _decode_bus_event(raw_b: bytes, *, ts: float | None = None) -> BusEvent:
    raw = raw_b.decode("utf-8", errors="replace")
    ts = time.time() if ts is None else float(ts)

    name = "message"
    data: Any = None
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict) and "name" in obj:
            name = str(obj.get("name") or "message")
            data = obj.get("data")
        else:
            name = "message"
            data = obj
    except Exception:
        txt = raw.strip("\r\n")
        if "\t" in txt:
            n, rest = txt.split("\t", 1)
            name = (n or "message").strip() or "message"
            data = rest
        elif txt:
            name = txt
            data = None

    return BusEvent(name=name, data=data, raw=raw, ts=ts)


def _systemd_listen_fds_with_names(*, unset_env: bool = True) -> list[tuple[int, str | None]]:
    """Return (fd, name) tuples passed by systemd socket activation.

    This follows the sd-daemon protocol conventions:
      - LISTEN_PID must match this process pid
      - LISTEN_FDS indicates a contiguous range starting at fd 3
      - LISTEN_FDNAMES (optional) is a ':'-separated list of fd names

    Notes
    -----
    The libsystemd helpers expose this as sd_listen_fds_with_names(). The key
    convention is that descriptor names come from the LISTEN_FDNAMES env var
    and can be set from socket units using FileDescriptorName=.

    We follow the common convention of unsetting these environment variables
    after consuming them to avoid surprising child processes.
    """

    try:
        pid = int(os.environ.get("LISTEN_PID", "0") or "0")
        if pid != os.getpid():
            return []
        n = int(os.environ.get("LISTEN_FDS", "0") or "0")
        if n <= 0:
            return []

        names_raw = os.environ.get("LISTEN_FDNAMES")
        names: list[str] = []
        if names_raw:
            # Colon-separated list. If fewer names than fds, remaining fds are unnamed.
            names = names_raw.split(":")

        if unset_env:
            os.environ.pop("LISTEN_PID", None)
            os.environ.pop("LISTEN_FDS", None)
            os.environ.pop("LISTEN_FDNAMES", None)

        start = 3
        out: list[tuple[int, str | None]] = []
        for i in range(n):
            nm = names[i] if i < len(names) and names[i] != "" else None
            out.append((start + i, nm))
        return out
    except Exception:
        return []


def _open_bus_socket(
    sock_path: Path,
    *,
    timeout_s: float | None,
    force_unlink: bool,
    use_systemd: bool,
    fdname: str | None,
) -> tuple[socket.socket, Callable[[], None], bool]:
    """Open a socket for receiving bus datagrams.

    Returns: (socket, cleanup_fn, activated)
      - cleanup_fn handles unlinking the socket path when appropriate
      - activated=True means the socket came from systemd activation
    """

    import errno

    sock_path = Path(sock_path)

    # Prefer systemd-passed sockets when present.
    fds = _systemd_listen_fds_with_names() if use_systemd else []
    if fds:
        chosen_fd = fds[0][0]
        if fdname is not None:
            want = str(fdname)
            for fd, nm in fds:
                if nm == want:
                    chosen_fd = fd
                    break
            else:
                have = ", ".join([(nm or "(unnamed)") for _, nm in fds])
                raise RuntimeError(f"systemd-passed sockets do not include fdname={want!r}; have: {have}")

        s = socket.socket(fileno=chosen_fd)
        if timeout_s is not None:
            s.settimeout(float(timeout_s))

        # Basic sanity checks (best-effort): AF_UNIX + SOCK_DGRAM.
        try:
            stype = s.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
            if stype != socket.SOCK_DGRAM:
                raise RuntimeError(f"systemd-passed fd {chosen_fd} is not SOCK_DGRAM (SO_TYPE={stype})")
        except OSError:
            pass

        def _cleanup() -> None:
            # systemd owns the socket path (RemoveOnStop= can handle cleanup)
            return

        return s, _cleanup, True

    # Normal bind path.
    sock_path.parent.mkdir(parents=True, exist_ok=True)

    if force_unlink:
        _safe_unlink(sock_path)

    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    if timeout_s is not None:
        s.settimeout(float(timeout_s))

    try:
        try:
            s.bind(str(sock_path))
        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                raise RuntimeError(
                    f"Bus socket already in use: {sock_path} (another watcher/daemon may be running). "
                    "Stop it first or pass force_unlink=True if you are sure the socket is stale."
                )
            raise
    except Exception:
        try:
            s.close()
        except Exception:
            pass
        raise

    def _cleanup() -> None:
        _safe_unlink(sock_path)

    return s, _cleanup, False


def wait_for_bus_event(
    sock_path: Path,
    *,
    timeout_s: float,
    recv_buf: int = 65535,
    force_unlink: bool = False,
    use_systemd: bool = False,
    fdname: str | None = None,
    accept: Callable[[BusEvent], bool] | None = None,
) -> BusEvent:
    """Wait for the next bus event accepted by ``accept``.

    This is a one-shot receive helper for macro execution and tests. It uses the
    same bind/systemd activation semantics as :func:`iter_bus_events` but stops
    after the first accepted event or raises ``TimeoutError``.
    """

    if timeout_s < 0:
        raise ValueError("timeout_s must be >= 0")

    s: socket.socket | None = None
    cleanup: Callable[[], None] | None = None
    deadline = time.time() + float(timeout_s)

    try:
        s, cleanup, _activated = _open_bus_socket(
            Path(sock_path), timeout_s=None, force_unlink=force_unlink, use_systemd=use_systemd, fdname=fdname
        )
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError(f"Timed out waiting for bus event on {sock_path}")
            s.settimeout(remaining)
            try:
                raw_b = s.recv(recv_buf)
            except socket.timeout as exc:
                raise TimeoutError(f"Timed out waiting for bus event on {sock_path}") from exc
            ev = _decode_bus_event(raw_b)
            if accept is None or bool(accept(ev)):
                return ev
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass
        if cleanup is not None:
            try:
                cleanup()
            except Exception:
                pass


def iter_bus_events(
    sock_path: Path,
    *,
    recv_buf: int = 65535,
    timeout_s: float | None = None,
    force_unlink: bool = False,
    use_systemd: bool = True,
    fdname: str | None = None,
) -> Iterator[BusEvent]:
    """Yield BusEvent objects from a bound UNIX datagram socket.

    Safety note
    -----------
    A UNIX socket path is effectively single-consumer: only one process can bind
    it at a time.

    Older VHK revisions unlinked the socket path unconditionally before binding.
    That made it easy to accidentally *break* an existing daemon: the second
    process would unlink the path, leaving the first process still bound but no
    longer reachable.

    By default we now refuse to start if the path already exists (likely meaning
    another VHK bus watcher/daemon is running). Use `force_unlink=True` to
    intentionally reclaim a stale socket.

    systemd socket activation
    -------------------------
    If LISTEN_FDS/LISTEN_PID are present and `use_systemd=True`, VHK will consume
    the first passed descriptor (fd 3) by default, or a named fd via LISTEN_FDNAMES and read bus events from that socket.
    """

    s: socket.socket | None = None
    cleanup: Callable[[], None] | None = None

    try:
        s, cleanup, _activated = _open_bus_socket(
            Path(sock_path), timeout_s=timeout_s, force_unlink=force_unlink, use_systemd=use_systemd, fdname=fdname
        )

        while True:
            try:
                raw_b = s.recv(recv_buf)
            except socket.timeout:
                continue
            yield _decode_bus_event(raw_b)

    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass
        if cleanup is not None:
            try:
                cleanup()
            except Exception:
                pass
