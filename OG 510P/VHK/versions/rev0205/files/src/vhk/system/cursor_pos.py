from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from vhk.system.session import detect_backend


@dataclass(frozen=True)
class CursorPos:
    x: int
    y: int
    backend: str


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


_NUM_RE = re.compile(r"-?\d+")


def _parse_two_ints(text: str) -> tuple[int, int] | None:
    nums = _NUM_RE.findall(text or "")
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    return None


def _parse_shell_xy(stdout: str) -> tuple[int, int] | None:
    # xdotool/kdotool style: X=10\nY=20
    x = y = None
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        if line.startswith("X="):
            try:
                x = int(line.split("=", 1)[1].strip())
            except Exception:
                x = None
        elif line.startswith("Y="):
            try:
                y = int(line.split("=", 1)[1].strip())
            except Exception:
                y = None
    if x is not None and y is not None:
        return int(x), int(y)
    return None


def _is_kde_like_session() -> bool:
    cd = (os.environ.get("XDG_CURRENT_DESKTOP") or "").strip().lower()
    ds = (os.environ.get("DESKTOP_SESSION") or "").strip().lower()
    if "kde" in cd or "plasma" in cd:
        return True
    if "plasma" in ds or "kde" in ds:
        return True
    if os.environ.get("KDE_FULL_SESSION"):
        return True
    return False


def get_cursor_pos() -> CursorPos:
    """Best-effort global cursor position.

    Notes
    -----
    Wayland does not provide a generic global cursor position API due to its
    security model. This function therefore uses compositor/tool-specific
    helpers when present.

    Current backend preference:
    - X11: xdotool
    - Wayland+Hyprland: hyprctl cursorpos
    - Wayland+wlroots: wl-find-cursor -p
    """

    desktop = detect_backend()

    if desktop != "wayland":
        xd = _which("xdotool")
        if not xd:
            raise RuntimeError("Cursor position requires xdotool on X11.")
        proc = subprocess.run([xd, "getmouselocation", "--shell"], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip() or "xdotool getmouselocation failed")
        x = y = None
        for line in (proc.stdout or "").splitlines():
            if line.startswith("X="):
                try:
                    x = int(line.split("=", 1)[1].strip())
                except Exception:
                    pass
            if line.startswith("Y="):
                try:
                    y = int(line.split("=", 1)[1].strip())
                except Exception:
                    pass
        if x is None or y is None:
            parsed = _parse_two_ints(proc.stdout)
            if parsed:
                x, y = parsed
        if x is None or y is None:
            raise RuntimeError("Could not parse xdotool cursor position output")
        return CursorPos(x=int(x), y=int(y), backend="xdotool")

    # Wayland
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        hyprctl = _which("hyprctl")
        if hyprctl:
            proc = subprocess.run([hyprctl, "cursorpos"], capture_output=True, text=True)
            if proc.returncode == 0:
                parsed = _parse_two_ints(proc.stdout)
                if parsed:
                    x, y = parsed
                    return CursorPos(x=x, y=y, backend="hyprctl")

    # KDE Plasma (KWin): kdotool can query global cursor position without root.
    kd = _which("kdotool")
    if kd and _is_kde_like_session():
        proc = subprocess.run([kd, "getmouselocation", "--shell"], capture_output=True, text=True)
        if proc.returncode == 0:
            parsed = _parse_shell_xy(proc.stdout)
            if parsed:
                x, y = parsed
                return CursorPos(x=x, y=y, backend="kdotool")

    wl_find = _which("wl-find-cursor")
    if wl_find:
        emulate = os.environ.get("VHK_WL_FIND_CURSOR_EMULATE")
        cmd = [wl_find]
        if emulate:
            cmd += ["-e", emulate]
        cmd.append("-p")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip() or "wl-find-cursor failed")
        parsed = _parse_two_ints(proc.stdout)
        if not parsed:
            raise RuntimeError("Could not parse wl-find-cursor output")
        x, y = parsed
        return CursorPos(x=x, y=y, backend="wl-find-cursor")

    raise RuntimeError(
        "No cursor position backend found. On Hyprland install hyprctl (bundled). "
        "On wlroots compositors, install wl-find-cursor. X11 sessions need xdotool."
    )
