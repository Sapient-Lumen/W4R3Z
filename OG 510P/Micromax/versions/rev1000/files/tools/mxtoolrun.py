#!/usr/bin/env python3
"""Shared subprocess, timing, and handoff-summary helpers for Micromax tools.

The short-window runners should be easy to inspect and refactor.  Keep the
platform-sensitive child-process teardown and timestamp formatting here so
``mxtimely`` and ``mxrelease`` can focus on their testing policy rather than
copying process-control boilerplate.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandResult:
    """Captured child-process result with wall-clock and monotonic timing."""

    label: str
    argv: list[str]
    returncode: int
    elapsed_seconds: float
    timeout_seconds: float
    timed_out: bool
    output: str
    started_at_utc: str
    finished_at_utc: str

    def as_json(self, *, include_output: bool = False) -> dict[str, object]:
        """Return a compact JSON row for evidence manifests."""

        payload: dict[str, object] = {
            "label": self.label,
            "argv": list(self.argv),
            "returncode": int(self.returncode),
            "elapsed_seconds": round(float(self.elapsed_seconds), 3),
            "timeout_seconds": round(float(self.timeout_seconds), 3),
            "timed_out": bool(self.timed_out),
            "started_at_utc": self.started_at_utc,
            "finished_at_utc": self.finished_at_utc,
            "output_tail": tail_text(self.output),
        }
        if include_output:
            payload["output"] = self.output
        return payload


def utc_now() -> str:
    """Return a stable UTC timestamp for machine-readable evidence."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def format_duration(seconds: float | int | None) -> str:
    """Return a compact human duration string."""

    if seconds is None:
        return "0.00s"
    value = max(0.0, float(seconds))
    if value < 60:
        return f"{value:.2f}s"
    minutes, secs = divmod(int(round(value)), 60)
    if minutes < 60:
        return f"{minutes}m{secs:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m{secs:02d}s"


def tail_text(text: str, *, max_lines: int = 80, max_chars: int = 12000) -> str:
    """Return a bounded diagnostic tail for console and manifest evidence."""

    lines = str(text or "").splitlines()
    if len(lines) > max_lines:
        lines = [f"... output truncated to last {max_lines} lines ...", *lines[-max_lines:]]
    out = "\n".join(lines).strip()
    if len(out) > max_chars:
        out = "... output truncated to last characters ...\n" + out[-max_chars:]
    return out


def human_command(argv: list[str]) -> str:
    """Return a copy/paste-friendly shell-ish command line."""

    try:
        import shlex

        return " ".join(shlex.quote(str(part)) for part in argv)
    except Exception:
        return " ".join(str(part) for part in argv)


def isolated_python_env(root: Path, *, include_src: bool = True) -> dict[str, str]:
    """Return the deterministic Python child environment used by test tools."""

    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    # Some hosted Python images warm unrelated spreadsheet helpers at startup.
    # Disable that unrelated startup path when the host supports the knob.
    env.setdefault("CUA_DD_PYTHON_TOOL_WARM_SPREADSHEET_RUNTIME", "0")
    if include_src:
        src = str(root / "src")
        parts = [part for part in env.get("PYTHONPATH", "").split(os.pathsep) if part]
        if src not in parts:
            env["PYTHONPATH"] = os.pathsep.join([src, *parts]) if parts else src
    return env


def process_group_kwargs() -> dict[str, Any]:
    """Return Popen kwargs that isolate child process groups when supported."""

    if os.name == "posix":
        return {"start_new_session": True}
    creationflags = int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) or 0)
    return {"creationflags": creationflags} if creationflags else {}


def confirmed_child_process_group_id(proc: subprocess.Popen[Any]) -> int | None:
    """Return a confirmed POSIX child process group id, never a guessed PID."""

    if os.name != "posix":
        return None
    pid = getattr(proc, "pid", None)
    if not isinstance(pid, int) or pid <= 0:
        return None
    try:
        pgid = os.getpgid(pid)
    except (OSError, ProcessLookupError):
        return None
    return int(pgid) if int(pgid) == int(pid) else None


def _signal_process_group_or_child(proc: subprocess.Popen[Any], sig: int, *, pgid: int | None) -> None:
    if os.name == "posix" and isinstance(pgid, int) and pgid > 0:
        try:
            os.killpg(pgid, sig)
            return
        except (OSError, ProcessLookupError):
            pass
    if sig == signal.SIGTERM:
        try:
            proc.terminate()
        except (OSError, ProcessLookupError):
            pass
    else:
        try:
            proc.kill()
        except (OSError, ProcessLookupError):
            pass


def _posix_ppid_map() -> dict[int, int]:
    """Return a Linux /proc snapshot of child pid -> parent pid.

    This is a best-effort fallback for tool children that create their own
    process groups.  ``Popen(start_new_session=True)`` lets the outer runner kill
    its direct child group, but a nested supervisor such as ``mxdoctor`` may also
    put pytest children in fresh sessions.  Those children are no longer in the
    outer process group, yet they are still descendants at timeout time.
    """

    if os.name != "posix":
        return {}
    proc_root = Path("/proc")
    if not proc_root.exists():
        return {}
    mapping: dict[int, int] = {}
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            pid = int(entry.name)
            status = (entry / "status").read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for line in status.splitlines():
            if line.startswith("PPid:"):
                try:
                    mapping[pid] = int(line.split()[1])
                except (IndexError, ValueError):
                    pass
                break
    return mapping


def _posix_descendant_pids(pid: int) -> list[int]:
    """Return known descendant pids for ``pid`` from a single /proc snapshot."""

    if os.name != "posix" or pid <= 0:
        return []
    ppid = _posix_ppid_map()
    children: dict[int, list[int]] = {}
    for child, parent in ppid.items():
        children.setdefault(parent, []).append(child)
    out: list[int] = []
    stack = list(children.get(int(pid), ()))
    seen: set[int] = set()
    while stack:
        child = stack.pop()
        if child in seen:
            continue
        seen.add(child)
        out.append(child)
        stack.extend(children.get(child, ()))
    return out


def _signal_descendant_process_groups(proc: subprocess.Popen[Any], sig: int, *, parent_pgid: int | None) -> None:
    """Signal descendants that escaped the direct child process group.

    This deliberately avoids guessing beyond current descendants of the tool
    child.  It never signals the runner's own process group, and it deduplicates
    process groups so a pytest child that created a new session is signaled once.
    """

    if os.name != "posix":
        return
    pid = getattr(proc, "pid", None)
    if not isinstance(pid, int) or pid <= 0:
        return
    try:
        own_pgid = os.getpgrp()
    except OSError:
        own_pgid = None
    protected_pgids = {value for value in (own_pgid, parent_pgid) if isinstance(value, int) and value > 0}
    signaled_groups: set[int] = set()
    for child_pid in sorted(_posix_descendant_pids(pid), reverse=True):
        if child_pid in {os.getpid(), os.getppid(), pid}:
            continue
        try:
            child_pgid = os.getpgid(child_pid)
        except (OSError, ProcessLookupError):
            continue
        if child_pgid > 0 and child_pgid not in protected_pgids:
            if child_pgid in signaled_groups:
                continue
            try:
                os.killpg(child_pgid, sig)
                signaled_groups.add(child_pgid)
                continue
            except (OSError, ProcessLookupError):
                pass
        try:
            os.kill(child_pid, sig)
        except (OSError, ProcessLookupError):
            pass


def _signal_process_tree_or_child(proc: subprocess.Popen[Any], sig: int, *, pgid: int | None) -> None:
    """Signal escaped descendant groups first, then the direct child/group."""

    _signal_descendant_process_groups(proc, sig, parent_pgid=pgid)
    _signal_process_group_or_child(proc, sig, pgid=pgid)


def terminate_process(proc: subprocess.Popen[Any], *, pgid: int | None = None, timeout: float = 3.0) -> None:
    """Best-effort child and escaped-grandchild teardown after timeout/interruption."""

    if proc.poll() is not None:
        _signal_descendant_process_groups(proc, signal.SIGTERM, parent_pgid=pgid)
        return
    _signal_process_tree_or_child(proc, signal.SIGTERM, pgid=pgid)
    try:
        proc.wait(timeout=max(0.1, float(timeout)))
    except subprocess.TimeoutExpired:
        _signal_process_tree_or_child(proc, signal.SIGKILL, pgid=pgid)
        try:
            proc.wait(timeout=max(0.1, float(timeout)))
        except subprocess.TimeoutExpired:
            pass


def _heartbeat_line(label: str, *, elapsed: float, timeout_seconds: float) -> str:
    return f"{label}: still running elapsed={format_duration(elapsed)} timeout={format_duration(timeout_seconds)}"


def run_captured(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_seconds: float,
    label: str,
    heartbeat_seconds: float = 0.0,
    heartbeat_prefix: str = "",
) -> CommandResult:
    """Run a child with captured output, timeout teardown, and optional heartbeat.

    The implementation intentionally returns one compact result row.  Callers can
    decide whether a nonzero status is acceptable, print captured tails, or store
    the row inside a richer manifest.
    """

    timeout_value = max(0.1, float(timeout_seconds))
    heartbeat_value = max(0.0, float(heartbeat_seconds))
    started_at = utc_now()
    started = time.monotonic()
    proc = subprocess.Popen(
        [str(part) for part in argv],
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **process_group_kwargs(),
    )
    pgid = confirmed_child_process_group_id(proc)
    deadline = started + timeout_value
    next_heartbeat = started + heartbeat_value if heartbeat_value else float("inf")
    output = ""
    timed_out = False
    returncode = 0

    while True:
        now = time.monotonic()
        remaining = deadline - now
        if remaining <= 0:
            timed_out = True
            terminate_process(proc, pgid=pgid)
            try:
                output, _ = proc.communicate(timeout=1)
            except Exception:
                output = output or ""
            returncode = 124
            break
        wait_for = remaining
        if heartbeat_value:
            wait_for = min(wait_for, max(0.05, next_heartbeat - now))
        try:
            output, _ = proc.communicate(timeout=max(0.05, wait_for))
            returncode = int(proc.returncode or 0)
            break
        except subprocess.TimeoutExpired:
            now = time.monotonic()
            if heartbeat_value and now >= next_heartbeat:
                prefix = f"{heartbeat_prefix}: " if heartbeat_prefix else ""
                print(prefix + _heartbeat_line(label, elapsed=now - started, timeout_seconds=timeout_value), flush=True)
                next_heartbeat = now + heartbeat_value
            continue

    elapsed = time.monotonic() - started
    return CommandResult(
        label=label,
        argv=[str(part) for part in argv],
        returncode=int(returncode),
        elapsed_seconds=round(float(elapsed), 3),
        timeout_seconds=round(float(timeout_value), 3),
        timed_out=bool(timed_out),
        output=output or "",
        started_at_utc=started_at,
        finished_at_utc=utc_now(),
    )
