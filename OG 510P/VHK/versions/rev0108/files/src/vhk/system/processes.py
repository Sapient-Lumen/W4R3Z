from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class StartedProcess:
    pid: int
    command: str | list[str]
    shell: bool
    cwd: str | None
    popen: subprocess.Popen[Any]


def start_process(
    command: str | list[str],
    *,
    shell: bool = False,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
) -> StartedProcess:
    cwd2 = str(Path(cwd).expanduser()) if cwd is not None else None
    merged_env = os.environ.copy()
    if env:
        merged_env.update({str(k): str(v) for k, v in env.items()})
    popen = subprocess.Popen(command, shell=shell, cwd=cwd2, env=merged_env or None)
    return StartedProcess(pid=int(popen.pid), command=command, shell=shell, cwd=cwd2, popen=popen)


def process_exists(pid: int) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def wait_for_process_exit(
    pid: int,
    *,
    popen: subprocess.Popen[Any] | None = None,
    timeout_ms: int = 10_000,
    poll_ms: int = 200,
    max_poll_ms: int = 1000,
    jitter_ms: int = 30,
    on_attempt=None,
) -> int | None:
    import random

    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))

    while time.time() <= deadline:
        attempt += 1
        if popen is not None:
            rc = popen.poll()
            exited = rc is not None
        else:
            rc = None
            exited = not process_exists(pid)

        if on_attempt is not None:
            on_attempt(attempt, exited, rc)
        if exited:
            return rc

        if poll > 0:
            jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
            time.sleep(max(0, poll + jitter) / 1000.0)
        poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForProcessExit timed out after {timeout_ms}ms (pid={pid})")


def kill_process(
    pid: int,
    *,
    sig: str | int = "TERM",
    popen: subprocess.Popen[Any] | None = None,
    missing_ok: bool = True,
    wait_ms: int = 0,
) -> bool:
    sig2 = _normalize_signal(sig)
    try:
        if popen is not None and popen.poll() is None:
            popen.send_signal(sig2)
        else:
            os.kill(int(pid), sig2)
    except ProcessLookupError:
        if missing_ok:
            return False
        raise

    if wait_ms > 0:
        try:
            wait_for_process_exit(int(pid), popen=popen, timeout_ms=int(wait_ms), poll_ms=50, max_poll_ms=200, jitter_ms=0)
        except TimeoutError:
            pass
    return True


def _normalize_signal(sig: str | int) -> int:
    if isinstance(sig, int):
        return sig
    s = str(sig).strip().upper()
    if s.isdigit():
        return int(s)
    if not s.startswith("SIG"):
        s = "SIG" + s
    if not hasattr(signal, s):
        raise ValueError(f"Unknown signal: {sig}")
    return int(getattr(signal, s))
