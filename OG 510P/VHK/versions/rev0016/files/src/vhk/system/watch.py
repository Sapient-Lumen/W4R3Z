from __future__ import annotations

import os
import random
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from vhk.system.session import detect_backend


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        if fp.exists() and os.access(fp, os.X_OK):
            return str(fp)
    return None


@dataclass
class FileState:
    exists: bool
    mtime_ns: int | None
    size: int | None


def file_state(path: str | Path) -> FileState:
    p = Path(path).expanduser()
    if not p.exists():
        return FileState(False, None, None)
    st = p.stat()
    return FileState(True, int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9))), int(st.st_size))


def wait_for_file(path: str | Path, *, condition: str = "exists", timeout_ms: int = 10_000, poll_ms: int = 200, max_poll_ms: int = 1000, jitter_ms: int = 30, max_attempts: int | None = None, on_attempt=None) -> FileState:
    p = Path(path).expanduser()
    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    baseline = file_state(p)
    ino = _which("inotifywait")

    while time.time() <= deadline:
        attempt += 1
        cur = file_state(p)
        ok = False
        if condition == "exists":
            ok = cur.exists
        elif condition == "missing":
            ok = not cur.exists
        elif condition == "changed":
            ok = cur != baseline
        else:
            raise ValueError(f"Unsupported file wait condition: {condition}")

        if on_attempt is not None:
            on_attempt(attempt, cur, ok, helper=("inotifywait" if ino else None))
        if ok:
            return cur
        if max_attempts is not None and attempt >= max_attempts:
            break

        if ino and condition in {"exists", "missing", "changed"}:
            timeout_left = max(0.05, deadline - time.time())
            watch_target = p if p.exists() else p.parent
            cmd = [ino, "--quiet", "--timeout", str(max(1, int(timeout_left + 0.999))), "-e", "modify", "-e", "close_write", "-e", "move", "-e", "create", "-e", "delete", "-e", "attrib", str(watch_target)]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_left + 0.2)
            except subprocess.TimeoutExpired:
                pass
        else:
            if poll > 0:
                jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForFile timed out after {timeout_ms}ms ({condition})")


def wait_for_clipboard_change(read_func, *, selection: str = "clipboard", initial_text: str | None = None, timeout_ms: int = 10_000, poll_ms: int = 200, max_poll_ms: int = 1000, jitter_ms: int = 30, max_attempts: int | None = None, on_attempt=None) -> str:
    baseline = initial_text if initial_text is not None else read_func(selection=selection)
    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    clipnotify = _which("clipnotify") if detect_backend() == "x11" else None

    while time.time() <= deadline:
        attempt += 1
        cur = read_func(selection=selection)
        changed = cur != baseline
        if on_attempt is not None:
            on_attempt(attempt, cur, changed, helper=("clipnotify" if clipnotify else None))
        if changed:
            return cur
        if max_attempts is not None and attempt >= max_attempts:
            break

        if clipnotify:
            cmd = [clipnotify]
            if selection == "primary":
                cmd += ["-s", "PRIMARY"]
            timeout_left = max(0.05, deadline - time.time())
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_left)
            except subprocess.TimeoutExpired:
                pass
        else:
            if poll > 0:
                jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForClipboardChange timed out after {timeout_ms}ms")



def wait_for_new_file(directory: str | Path, *, pattern: str = "*", timeout_ms: int = 10_000, poll_ms: int = 200, max_poll_ms: int = 1000, jitter_ms: int = 30, max_attempts: int | None = None, on_attempt=None) -> Path:
    root = Path(directory).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")

    baseline = {p.resolve() for p in root.glob(pattern)}
    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    ino = _which("inotifywait")

    while time.time() <= deadline:
        attempt += 1
        current = sorted((p for p in root.glob(pattern)), key=lambda p: (p.stat().st_mtime_ns, p.name))
        new_files = [p for p in current if p.resolve() not in baseline]
        found = new_files[-1] if new_files else None
        if on_attempt is not None:
            on_attempt(attempt, found, bool(found), helper=("inotifywait" if ino else None))
        if found is not None:
            return found
        if max_attempts is not None and attempt >= max_attempts:
            break

        if ino:
            timeout_left = max(0.05, deadline - time.time())
            cmd = [ino, "--quiet", "--timeout", str(max(1, int(timeout_left + 0.999))), "-e", "close_write", "-e", "move", "-e", "create", str(root)]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_left + 0.2)
            except subprocess.TimeoutExpired:
                pass
        else:
            if poll > 0:
                jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForNewFile timed out after {timeout_ms}ms in {root}")
