from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vhk.system.session import detect_backend


@dataclass
class CursorBackend:
    name: str
    exe: str


@dataclass
class CursorHandle:
    backend: str
    process: Any


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


def choose_backend() -> CursorBackend | None:
    """Choose a cursor-hide helper.

    Today this is intentionally X11-only. There is no generic Wayland equivalent.
    Preference order:
    - unclutter / unclutter-xfixes for explicit hide/show lifecycle control
    - xbanish for hide-on-typing support (not used for manual hide/show)
    """

    if detect_backend() == "wayland":
        return None

    for cmd in ("unclutter", "unclutter-xfixes"):
        exe = _which(cmd)
        if exe:
            return CursorBackend(name="unclutter", exe=exe)

    exe = _which("xbanish")
    if exe:
        return CursorBackend(name="xbanish", exe=exe)

    return None


def _spawn_unclutter(exe: str):
    # Try xfixes-style CLI first, then legacy unclutter flags.
    candidates = [
        [exe, "--timeout", "0", "--start-hidden"],
        [exe, "-idle", "0", "-root"],
    ]

    last_err = ""
    for cmd in candidates:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        time.sleep(0.05)
        rc = proc.poll()
        if rc is None:
            return proc

        try:
            stderr = proc.stderr.read() if proc.stderr else ""
        except Exception:
            stderr = ""
        last_err = stderr.strip() or f"exit code {rc}"

    raise RuntimeError(f"Cursor helper failed to start via {exe}: {last_err}")


def hide_cursor() -> CursorHandle:
    """Hide the cursor until `show_cursor()` is called.

    Returns a handle the caller should keep around and later pass to
    `show_cursor()`. This is best-effort and currently X11-only.
    """

    backend = choose_backend()
    if not backend:
        raise RuntimeError("No cursor helper found. Install 'unclutter'/'unclutter-xfixes' or 'xbanish' (X11).")

    if backend.name == "unclutter":
        proc = _spawn_unclutter(backend.exe)
        return CursorHandle(backend="unclutter", process=proc)

    # xbanish is not a true manual hide/show helper, but it is still useful to
    # start as a session companion for hide-on-typing behavior.
    proc = subprocess.Popen([backend.exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return CursorHandle(backend="xbanish", process=proc)


def show_cursor(handle: CursorHandle | None) -> None:
    if handle is None:
        return

    proc = getattr(handle, "process", None)
    if proc is None:
        return

    try:
        proc.terminate()
    except Exception:
        return

    try:
        proc.wait(timeout=1.0)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
