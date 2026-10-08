from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


class HyprctlError(RuntimeError):
    """Raised when hyprctl cannot be executed or its output cannot be parsed."""


def _run(cmd: list[str], *, timeout: float = 2.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def hyprctl_available() -> bool:
    return shutil.which("hyprctl") is not None


def hyprctl_json(subcommand: str) -> Any:
    """Call hyprctl and parse JSON output.

    Hyprland documents JSON output via the `-j` flag, e.g.:

        hyprctl -j activewindow

    Some older snippets use:

        hyprctl activewindow -j

    We try both.
    """

    hyprctl = shutil.which("hyprctl")
    if not hyprctl:
        raise HyprctlError("hyprctl not found")

    last_err: Exception | None = None
    for cmd in ([hyprctl, "-j", subcommand], [hyprctl, subcommand, "-j"]):
        try:
            proc = _run(cmd)
        except Exception as exc:
            last_err = exc
            continue
        if proc.returncode != 0:
            last_err = RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"hyprctl exited {proc.returncode}")
            continue
        try:
            return json.loads(proc.stdout)
        except Exception as exc:
            last_err = exc
            continue

    raise HyprctlError(f"hyprctl JSON probe failed for '{subcommand}': {last_err}")


def hyprctl_dispatch(dispatcher: str, arg: str | None = None, *, timeout: float = 2.0) -> str:
    """Run a hyprctl dispatcher command (non-JSON).

    Example:
        hyprctl dispatch focuswindow "address:0x..."
    """

    hyprctl = shutil.which("hyprctl")
    if not hyprctl:
        raise HyprctlError("hyprctl not found")

    cmd = [hyprctl, "dispatch", dispatcher]
    if arg is not None:
        cmd.append(arg)

    try:
        proc = _run(cmd, timeout=timeout)
    except Exception as exc:
        raise HyprctlError(str(exc))
    if proc.returncode != 0:
        raise HyprctlError(proc.stderr.strip() or proc.stdout.strip() or f"hyprctl exited {proc.returncode}")
    return (proc.stdout or "").strip()
