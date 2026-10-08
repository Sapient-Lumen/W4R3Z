from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import Any

from vhk.core.models import I3WindowSelector
from vhk.i3.ipc import I3Connection, discover_socket_path
from vhk.i3.tree import find_first
from vhk.system.hyprctl import HyprctlError, hyprctl_json
from vhk.system.session import detect_backend


class ActiveWindowProbeError(RuntimeError):
    """Raised when VHK cannot query the active window."""


_XPROP_HEX_RE = re.compile(r"0x[0-9a-fA-F]+")


def get_active_window_geometry() -> tuple[dict[str, int], dict[str, int] | None, str]:
    """Return (rect, client_rect, wm) for the currently active window.

    rect is the outer window/container rectangle in absolute screen coordinates.
    client_rect is the client/content rectangle in absolute screen coordinates
    when available.

    This is primarily used for AHK-style coordinate translation (CoordMode).

    Notes
    -----
    - For i3/sway, `rect` is absolute. `window_rect` is relative to `rect` and
      typically excludes decorations; we convert it into an absolute client_rect.
    - For Hyprland, `hyprctl activewindow -j` exposes `at` and `size`, which we
      treat as the best available window rectangle.
    - For generic X11 sessions, we use EWMH properties (via xprop) and
      xdotool/xwininfo to approximate an outer rect. When available, we apply
      `_NET_FRAME_EXTENTS` (or `_GTK_FRAME_EXTENTS`) to derive a best-effort
      client rect.
    """

    wm = detect_compositor() or "unknown"

    if wm in {"i3", "sway"}:
        socket_path = discover_socket_path()
        tree = I3Connection(socket_path=socket_path).get_tree()
        match = find_first(tree, I3WindowSelector(focused=True))
        if not match:
            raise ActiveWindowProbeError("focused window not found in i3/sway tree")

        node = match.node
        rect = node.get("rect") or {}
        if not isinstance(rect, dict):
            rect = {}
        out_rect = {
            "x": int(rect.get("x") or 0),
            "y": int(rect.get("y") or 0),
            "w": int(rect.get("width") or rect.get("w") or 0),
            "h": int(rect.get("height") or rect.get("h") or 0),
        }

        wr = node.get("window_rect") or {}
        if isinstance(wr, dict) and all(k in wr for k in ("x", "y", "width", "height")):
            client = {
                "x": out_rect["x"] + int(wr.get("x") or 0),
                "y": out_rect["y"] + int(wr.get("y") or 0),
                "w": int(wr.get("width") or 0),
                "h": int(wr.get("height") or 0),
            }
        else:
            client = None

        return out_rect, client, wm

    if wm == "hyprland":
        try:
            raw = hyprctl_json("activewindow")
        except HyprctlError as exc:
            raise ActiveWindowProbeError(str(exc))

        at = raw.get("at")
        size = raw.get("size")
        if not (isinstance(at, list) and len(at) >= 2 and isinstance(size, list) and len(size) >= 2):
            raise ActiveWindowProbeError("hyprctl activewindow did not include 'at'/'size' fields")

        rect = {"x": int(at[0]), "y": int(at[1]), "w": int(size[0]), "h": int(size[1])}
        # Hyprland does not currently provide an explicit client vs outer rect
        # split in this API.
        return rect, None, wm

    if wm == "kwin":
        try:
            from vhk.system import kdotool as kdotool_mod

            # kdotool runs a transient KWin script per invocation; under load
            # this can take a couple seconds.
            geom = kdotool_mod.get_active_window_geometry(timeout_s=3.0)
        except Exception as exc:
            raise ActiveWindowProbeError(str(exc))

        if not geom:
            raise ActiveWindowProbeError("kdotool did not return active window geometry")

        rect = {"x": int(geom.x), "y": int(geom.y), "w": int(geom.w), "h": int(geom.h)}
        # KWin does not expose a distinct client_rect through kdotool.
        return rect, None, wm

    if wm == "x11" or (wm == "unknown" and detect_backend() == "x11"):
        rect, client = _x11_active_window_geometry()
        return rect, client, "x11"

    raise ActiveWindowProbeError("unsupported compositor for active window geometry")


def detect_compositor() -> str | None:
    """Best-effort compositor detection.

    We keep this intentionally minimal and environment-based; VHK should work even
    when no compositor-specific tooling is available.

    Returned values are used as a dispatch key for "how to query active window
    information".
    """

    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return "hyprland"
    if os.environ.get("SWAYSOCK"):
        return "sway"
    if os.environ.get("I3SOCK"):
        return "i3"

    xcd = (os.environ.get("XDG_CURRENT_DESKTOP") or "").lower()
    if "hyprland" in xcd:
        return "hyprland"
    if "sway" in xcd:
        return "sway"
    if "i3" in xcd:
        return "i3"

    # KDE Plasma: treat Wayland sessions as KWin.
    if detect_backend() == "wayland":
        if "kde" in xcd or "plasma" in xcd or os.environ.get("KDE_FULL_SESSION"):
            return "kwin"

    # If we're in an X11 session (not Wayland+XWayland), we can fall back to
    # EWMH/xprop tooling.
    if detect_backend() == "x11" and os.environ.get("DISPLAY"):
        return "x11"

    return None


def _regex_match(value: str, pattern: str, regex: bool) -> bool:
    if regex:
        return re.search(pattern, value or "") is not None
    return value == pattern


def _selector_matches_hypr_active(selector: I3WindowSelector, info: dict[str, Any]) -> bool:
    # Hyprland doesn't expose i3's instance/role/urgent fields.
    if selector.instance is not None:
        return False
    if selector.window_role is not None:
        return False
    if selector.urgent is not None:
        return False

    title = str(info.get("title") or "")
    if selector.title is not None:
        if not _regex_match(title, selector.title, selector.title_regex):
            return False

    cls = str(info.get("class") or "")
    initial_cls = str(info.get("initialClass") or "")

    if selector.wm_class is not None:
        if selector.wm_class not in {cls, initial_cls}:
            return False

    if selector.app_id is not None:
        cand = initial_cls or cls
        if not _regex_match(cand, selector.app_id, selector.app_id_regex):
            return False

    if selector.workspace is not None:
        ws = None
        wsv = info.get("workspace")
        if isinstance(wsv, dict):
            ws = wsv.get("name")
        elif isinstance(wsv, str):
            ws = wsv
        if ws != selector.workspace:
            return False

    if selector.focused is not None:
        # activewindow is, by definition, focused.
        if bool(selector.focused) is not True:
            return False

    return True


def selector_matches_info(selector: I3WindowSelector, info: dict[str, Any], wm: str) -> bool:
    """Match a selector against a shallow active-window info dict.

    This is used by window watchers and `--require-window` gates to avoid extra
    IPC round-trips when we already have the window info.

    wm should be one of: i3, sway, hyprland, x11, unknown.
    """

    if wm == "hyprland":
        return _selector_matches_hypr_active(selector, info)

    # i3/sway/x11 info from get_active_window_info.
    if selector.app_id is not None:
        if not _regex_match(str(info.get("app_id") or ""), selector.app_id, selector.app_id_regex):
            return False

    if selector.title is not None:
        if not _regex_match(str(info.get("title") or ""), selector.title, selector.title_regex):
            return False

    if selector.wm_class is not None:
        if str(info.get("class") or "") != selector.wm_class:
            return False

    if selector.instance is not None:
        if str(info.get("instance") or "") != selector.instance:
            return False

    if selector.window_role is not None:
        if str(info.get("window_role") or "") != selector.window_role:
            return False

    if selector.workspace is not None:
        if str(info.get("workspace") or "") != selector.workspace:
            return False

    if selector.urgent is not None:
        if bool(info.get("urgent")) != bool(selector.urgent):
            return False

    if selector.focused is not None:
        if bool(info.get("focused")) != bool(selector.focused):
            return False

    return True


def active_window_matches(selector: I3WindowSelector) -> tuple[bool, str]:
    """Return (matches, wm).

    wm is one of: i3, sway, hyprland, x11, unknown.
    """

    wm = detect_compositor() or "unknown"

    if wm in {"i3", "sway"}:
        socket_path = discover_socket_path()
        tree = I3Connection(socket_path=socket_path).get_tree()

        sel2 = selector.model_copy()
        sel2.focused = True
        match = find_first(tree, sel2)
        return (match is not None), wm

    if wm == "hyprland":
        try:
            info = hyprctl_json("activewindow")
        except HyprctlError as exc:
            raise ActiveWindowProbeError(str(exc))
        return _selector_matches_hypr_active(selector, info), wm

    if wm == "kwin":
        info, _ = get_active_window_info()
        return selector_matches_info(selector, info, "kwin"), wm

    if wm == "x11" or (wm == "unknown" and detect_backend() == "x11"):
        info, _ = get_active_window_info()
        return selector_matches_info(selector, info, "x11"), "x11"

    raise ActiveWindowProbeError("unsupported compositor for active window probing")


def get_active_window_info() -> tuple[dict[str, Any], str]:
    """Return (info, wm) for the currently active (focused) window.

    This is a lightweight, cross-compositor analogue to AHK's "Window Spy":
    it's intended to help users build `when:` selectors and `--require-window`
    JSON payloads.

    The returned info object is intentionally shallow and composed of fields
    that map cleanly to :class:`~vhk.core.models.I3WindowSelector`.

    On X11 we rely on EWMH properties (xprop). Some WMs may not expose every
    property, so fields such as `workspace` may be missing.
    """

    wm = detect_compositor() or "unknown"

    if wm in {"i3", "sway"}:
        socket_path = discover_socket_path()
        tree = I3Connection(socket_path=socket_path).get_tree()
        match = find_first(tree, I3WindowSelector(focused=True))
        if not match:
            raise ActiveWindowProbeError("focused window not found in i3/sway tree")

        node = match.node
        wp = node.get("window_properties") or {}
        info: dict[str, Any] = {
            "id": node.get("id") or node.get("window"),
            "app_id": node.get("app_id"),
            "class": wp.get("class"),
            "instance": wp.get("instance"),
            "window_role": wp.get("window_role") or wp.get("role"),
            "title": wp.get("title") or node.get("name"),
            "workspace": match.workspace,
            "urgent": node.get("urgent"),
            "focused": node.get("focused"),
        }
        return info, wm

    if wm == "hyprland":
        try:
            raw = hyprctl_json("activewindow")
        except HyprctlError as exc:
            raise ActiveWindowProbeError(str(exc))
        ws_name = None
        wsv = raw.get("workspace")
        if isinstance(wsv, dict):
            ws_name = wsv.get("name")
        elif isinstance(wsv, str):
            ws_name = wsv

        info2: dict[str, Any] = {
            "address": raw.get("address"),
            "pid": raw.get("pid"),
            "class": raw.get("class") or raw.get("initialClass"),
            "initialClass": raw.get("initialClass"),
            "title": raw.get("title") or raw.get("initialTitle"),
            "workspace": ws_name,
            # activewindow is, by definition, focused.
            "focused": True,
        }
        return info2, wm

    if wm == "kwin":
        try:
            from vhk.system import kdotool as kdotool_mod

            # Use a slightly more forgiving timeout than the historical default
            # to reduce flakiness on loaded systems.
            info = kdotool_mod.get_active_window_info(timeout_s=3.0)
        except Exception as exc:
            raise ActiveWindowProbeError(str(exc))

        if not info:
            raise ActiveWindowProbeError("kdotool did not return active window info")

        out: dict[str, Any] = {
            "id": info.get("id"),
            "pid": info.get("pid"),
            "class": info.get("class"),
            "app_id": info.get("app_id") or info.get("class"),
            "title": info.get("title"),
            "focused": True,
        }
        return out, wm

    if wm == "x11" or (wm == "unknown" and detect_backend() == "x11"):
        return _x11_active_window_info(), "x11"

    raise ActiveWindowProbeError("unsupported compositor for active window probing")


def _x11_active_window_id() -> int:
    if detect_backend() != "x11":
        raise ActiveWindowProbeError("x11 backend not active")

    xd = shutil.which("xdotool")
    if xd:
        proc = subprocess.run([xd, "getactivewindow"], capture_output=True, text=True)
        if proc.returncode == 0 and (proc.stdout or "").strip().isdigit():
            return int(proc.stdout.strip())

    xp = shutil.which("xprop")
    if not xp:
        raise ActiveWindowProbeError("xprop not found (required for X11 active-window probing)")

    proc = subprocess.run([xp, "-root", "_NET_ACTIVE_WINDOW"], capture_output=True, text=True)
    if proc.returncode != 0:
        raise ActiveWindowProbeError((proc.stderr or proc.stdout).strip() or "xprop _NET_ACTIVE_WINDOW failed")

    m = _XPROP_HEX_RE.search(proc.stdout or "")
    if not m:
        raise ActiveWindowProbeError("could not parse _NET_ACTIVE_WINDOW")
    return int(m.group(0), 16)


def _parse_kv_shell(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _x11_get_outer_rect(win_id: int) -> dict[str, int]:
    xd = shutil.which("xdotool")
    if xd:
        proc = subprocess.run([xd, "getwindowgeometry", "--shell", str(win_id)], capture_output=True, text=True)
        if proc.returncode == 0:
            kv = _parse_kv_shell(proc.stdout)
            if {"X", "Y", "WIDTH", "HEIGHT"}.issubset(kv.keys()):
                return {
                    "x": int(kv["X"]),
                    "y": int(kv["Y"]),
                    "w": int(kv["WIDTH"]),
                    "h": int(kv["HEIGHT"]),
                }

    xwi = shutil.which("xwininfo")
    if not xwi:
        raise ActiveWindowProbeError("need xdotool or xwininfo for X11 window geometry")

    hex_id = f"0x{win_id:x}"
    proc = subprocess.run([xwi, "-id", hex_id], capture_output=True, text=True)
    if proc.returncode != 0:
        raise ActiveWindowProbeError((proc.stderr or proc.stdout).strip() or "xwininfo failed")

    x = y = w = h = None
    for raw in (proc.stdout or "").splitlines():
        line = raw.strip()
        if line.startswith("Absolute upper-left X:"):
            x = int(line.split(":", 1)[1].strip())
        elif line.startswith("Absolute upper-left Y:"):
            y = int(line.split(":", 1)[1].strip())
        elif line.startswith("Width:"):
            w = int(line.split(":", 1)[1].strip())
        elif line.startswith("Height:"):
            h = int(line.split(":", 1)[1].strip())

    if x is None or y is None or w is None or h is None:
        raise ActiveWindowProbeError("could not parse xwininfo geometry")

    return {"x": x, "y": y, "w": w, "h": h}


def _parse_extents_line(line: str) -> tuple[int, int, int, int] | None:
    # _NET_FRAME_EXTENTS(CARDINAL) = 5, 5, 19, 5
    if "=" not in line:
        return None
    rhs = line.split("=", 1)[1]
    nums = [n.strip() for n in rhs.split(",") if n.strip()]
    if len(nums) < 4:
        return None
    try:
        left, right, top, bottom = (int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3]))
        return left, right, top, bottom
    except Exception:
        return None


def _x11_get_frame_extents(win_id: int) -> tuple[int, int, int, int] | None:
    xp = shutil.which("xprop")
    if not xp:
        return None

    hex_id = f"0x{win_id:x}"
    # Query both: some environments set _GTK_FRAME_EXTENTS but not _NET_FRAME_EXTENTS.
    proc = subprocess.run(
        [xp, "-id", hex_id, "_NET_FRAME_EXTENTS", "_GTK_FRAME_EXTENTS"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None

    net_line = None
    gtk_line = None
    for raw in (proc.stdout or "").splitlines():
        if raw.strip().startswith("_NET_FRAME_EXTENTS"):
            net_line = raw
        elif raw.strip().startswith("_GTK_FRAME_EXTENTS"):
            gtk_line = raw

    if net_line:
        parsed = _parse_extents_line(net_line)
        if parsed is not None:
            return parsed

    if gtk_line:
        parsed = _parse_extents_line(gtk_line)
        if parsed is not None:
            return parsed

    return None


def _x11_active_window_geometry() -> tuple[dict[str, int], dict[str, int] | None]:
    win_id = _x11_active_window_id()
    rect = _x11_get_outer_rect(win_id)

    ext = _x11_get_frame_extents(win_id)
    if not ext:
        return rect, None

    left, right, top, bottom = ext
    cw = rect["w"] - left - right
    ch = rect["h"] - top - bottom
    if cw <= 0 or ch <= 0:
        return rect, None

    client = {"x": rect["x"] + left, "y": rect["y"] + top, "w": cw, "h": ch}
    return rect, client


def _parse_xprop_string_line(line: str) -> str | None:
    # _NET_WM_NAME(UTF8_STRING) = "Mozilla Firefox"
    m = re.search(r'"(.*)"', line)
    if m:
        return m.group(1)
    # Sometimes: WM_NAME = Mozilla Firefox
    if "=" in line:
        rhs = line.split("=", 1)[1].strip()
        if rhs:
            return rhs
    return None


def _parse_xprop_wm_class(line: str) -> tuple[str | None, str | None]:
    # WM_CLASS(STRING) = "Navigator", "Firefox"
    quoted = re.findall(r'"([^"]*)"', line)
    if len(quoted) >= 2:
        return quoted[0], quoted[1]
    if len(quoted) == 1:
        return None, quoted[0]
    return None, None


def _parse_xprop_int(line: str) -> int | None:
    m = re.search(r"\b(\d+)\b", line)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def _x11_desktop_names() -> list[str] | None:
    xp = shutil.which("xprop")
    if not xp:
        return None
    proc = subprocess.run([xp, "-root", "_NET_DESKTOP_NAMES"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return re.findall(r'"([^"]*)"', proc.stdout or "") or None


def _x11_active_window_info() -> dict[str, Any]:
    win_id = _x11_active_window_id()

    xp = shutil.which("xprop")
    if not xp:
        raise ActiveWindowProbeError("xprop not found (required for X11 active-window probing)")

    hex_id = f"0x{win_id:x}"
    proc = subprocess.run(
        [
            xp,
            "-id",
            hex_id,
            "WM_CLASS",
            "_NET_WM_NAME",
            "WM_NAME",
            "WM_WINDOW_ROLE",
            "_NET_WM_PID",
            "_NET_WM_DESKTOP",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise ActiveWindowProbeError((proc.stderr or proc.stdout).strip() or "xprop failed")

    instance = cls = title = role = None
    pid = None
    desktop_idx = None

    for raw in (proc.stdout or "").splitlines():
        line = raw.strip()
        if line.startswith("WM_CLASS"):
            instance, cls = _parse_xprop_wm_class(line)
        elif line.startswith("_NET_WM_NAME"):
            title = _parse_xprop_string_line(line) or title
        elif line.startswith("WM_NAME") and not title:
            title = _parse_xprop_string_line(line) or title
        elif line.startswith("WM_WINDOW_ROLE"):
            role = _parse_xprop_string_line(line) or role
        elif line.startswith("_NET_WM_PID"):
            pid = _parse_xprop_int(line)
        elif line.startswith("_NET_WM_DESKTOP"):
            desktop_idx = _parse_xprop_int(line)

    ws_name: str | None = None
    if desktop_idx is not None:
        names = _x11_desktop_names()
        if names and 0 <= desktop_idx < len(names):
            ws_name = names[desktop_idx]
        else:
            ws_name = str(desktop_idx)

    info: dict[str, Any] = {
        "id": win_id,
        "pid": pid,
        "class": cls,
        "instance": instance,
        "window_role": role,
        "title": title,
        "workspace": ws_name,
        "focused": True,
    }
    return info
