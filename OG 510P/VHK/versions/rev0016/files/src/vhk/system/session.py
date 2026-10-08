from __future__ import annotations

"""Session / desktop backend detection.

VHK started life as an i3+X11 automation tool, but many users run i3-like
workflows on Wayland (sway, river, etc). The surrounding ecosystem has largely
standardized on:

- grim + slurp for screenshots/region selection
- wl-copy + wl-paste for clipboard
- wtype (virtual keyboard) for key typing
- ydotool (uinput) for mouse and keyboard injection (requires ydotoold)

This module provides a single place to decide which *desktop backend* we are
targeting.
"""

import os
from typing import Literal


DesktopBackend = Literal["auto", "x11", "wayland"]


_preferred: DesktopBackend = "auto"


def set_preferred_backend(value: DesktopBackend) -> None:
    """Set a preferred backend for the current process.

    This is intended to be set by the Runner based on project settings.
    """

    global _preferred
    _preferred = value


def _env_override() -> DesktopBackend | None:
    v = (os.environ.get("VHK_BACKEND") or "").strip().lower()
    if v in {"auto", "x11", "wayland"}:
        return v  # type: ignore[return-value]
    return None


def detect_backend() -> DesktopBackend:
    """Resolve the effective backend.

    Priority:
      1) Project/runtime preferred backend (set_preferred_backend)
      2) VHK_BACKEND env var
      3) Heuristic from XDG_SESSION_TYPE / WAYLAND_DISPLAY

    Notes
    -----
    Some Wayland compositors still set DISPLAY (XWayland). We treat
    XDG_SESSION_TYPE=wayland as authoritative.
    """

    if _preferred != "auto":
        return _preferred

    v = _env_override()
    if v:
        return v

    if (os.environ.get("XDG_SESSION_TYPE") or "").lower() == "wayland":
        return "wayland"

    if os.environ.get("WAYLAND_DISPLAY") and not os.environ.get("DISPLAY"):
        return "wayland"

    return "x11"
