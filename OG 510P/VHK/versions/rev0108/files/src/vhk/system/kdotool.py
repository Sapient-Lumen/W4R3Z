from __future__ import annotations

"""kdotool helpers (KDE Plasma / KWin).

kdotool is an xdotool-like CLI tool that uses KWin's scripting API to query and
control windows on KDE Plasma (Wayland and X11). VHK uses it as a best-effort
provider for:

- Global cursor position on KDE Wayland (via ``kdotool getmouselocation --shell``)
- Active window metadata and geometry (for ``Window Spy`` and ``CoordMode``)

Notes
-----
- kdotool is *not* an input injection tool; it focuses on window queries and
  actions. Use dotool/ydotool/wtype for keyboard/mouse injection.
- Each kdotool invocation loads and runs a transient KWin script. This is fast
  enough for occasional probes but may be too slow for tight polling loops.
"""

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any


def which_kdotool() -> str | None:
    return shutil.which("kdotool")


def run_kdotool(args: list[str], *, timeout_s: float = 3.0) -> str:
    exe = which_kdotool()
    if not exe:
        raise RuntimeError("kdotool not found in PATH")
    proc = subprocess.run([exe, *args], capture_output=True, text=True, timeout=max(0.5, float(timeout_s)))
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip() or "kdotool failed"
        raise RuntimeError(err)
    return proc.stdout or ""


def parse_shell_kv(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


@dataclass(frozen=True)
class WindowGeometry:
    x: int
    y: int
    w: int
    h: int


_POS_RE = re.compile(r"Position:\s*(?P<x>-?\d+)\s*,\s*(?P<y>-?\d+)")
_GEOM_RE = re.compile(r"Geometry:\s*(?P<w>\d+)\s*x\s*(?P<h>\d+)")


def parse_getwindowgeometry(stdout: str) -> WindowGeometry | None:
    """Parse xdotool-like getwindowgeometry output.

    kdotool mimics xdotool's human-readable output (but may omit --shell).
    We parse both patterns conservatively.
    """

    if not stdout:
        return None

    # Prefer shell-like output if present (some tools output X=... Y=...)
    kv = parse_shell_kv(stdout)
    if {"X", "Y", "WIDTH", "HEIGHT"}.issubset(kv.keys()):
        try:
            return WindowGeometry(x=int(kv["X"]), y=int(kv["Y"]), w=int(kv["WIDTH"]), h=int(kv["HEIGHT"]))
        except Exception:
            pass

    x = y = w = h = None
    for raw in stdout.splitlines():
        line = raw.strip()
        m = _POS_RE.search(line)
        if m:
            x = int(m.group("x"))
            y = int(m.group("y"))
        m2 = _GEOM_RE.search(line)
        if m2:
            w = int(m2.group("w"))
            h = int(m2.group("h"))

    if x is None or y is None or w is None or h is None:
        # Loose fallback: first 4 ints in the text.
        nums = re.findall(r"-?\d+", stdout)
        if len(nums) >= 4 and x is None and y is None and w is None and h is None:
            try:
                x, y, w, h = (int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3]))
            except Exception:
                return None

    if x is None or y is None or w is None or h is None:
        return None
    return WindowGeometry(x=int(x), y=int(y), w=int(w), h=int(h))


def get_mouselocation_shell(*, timeout_s: float = 3.0) -> dict[str, str]:
    """Return kv mapping from ``kdotool getmouselocation --shell``."""

    out = run_kdotool(["getmouselocation", "--shell"], timeout_s=timeout_s)
    return parse_shell_kv(out)


def get_active_window_id(*, timeout_s: float = 3.0) -> str | None:
    """Return KWin's internal window UUID for the active window."""

    out = run_kdotool(["getactivewindow", "getwindowid"], timeout_s=timeout_s)
    for raw in (out or "").splitlines():
        line = raw.strip()
        if line:
            return line
    return None


def get_active_window_info(*, timeout_s: float = 3.0) -> dict[str, Any]:
    """Best-effort active window info via kdotool."""

    info: dict[str, Any] = {"focused": True}
    wid = get_active_window_id(timeout_s=timeout_s)
    if wid:
        info["id"] = wid

    try:
        title = run_kdotool(["getactivewindow", "getwindowname"], timeout_s=timeout_s).strip()
        if title:
            info["title"] = title
    except Exception:
        pass

    try:
        cls = run_kdotool(["getactivewindow", "getwindowclassname"], timeout_s=timeout_s).strip()
        if cls:
            # Many callers use either app_id or class selectors.
            info["class"] = cls
            info["app_id"] = cls
    except Exception:
        pass

    try:
        # Some kdotool builds (or wrappers) print plain digits, while others may
        # include extra context. Parse conservatively and retry once on failure.
        pid_text = run_kdotool(["getactivewindow", "getwindowpid"], timeout_s=timeout_s)
        pid_txt = (pid_text or "").strip()

        if pid_txt.isdigit():
            info["pid"] = int(pid_txt)
        else:
            m = re.search(r"\b(\d+)\b", pid_txt)
            if m:
                info["pid"] = int(m.group(1))
            else:
                # Retry once with a slightly longer timeout.
                pid_text2 = run_kdotool(["getactivewindow", "getwindowpid"], timeout_s=max(1.0, float(timeout_s) * 2.0))
                pid_txt2 = (pid_text2 or "").strip()
                if pid_txt2.isdigit():
                    info["pid"] = int(pid_txt2)
                else:
                    m2 = re.search(r"\b(\d+)\b", pid_txt2)
                    if m2:
                        info["pid"] = int(m2.group(1))
    except Exception:
        pass

    return info


def get_active_window_geometry(*, timeout_s: float = 3.0) -> WindowGeometry | None:
    out = run_kdotool(["getactivewindow", "getwindowgeometry"], timeout_s=timeout_s)
    return parse_getwindowgeometry(out)
