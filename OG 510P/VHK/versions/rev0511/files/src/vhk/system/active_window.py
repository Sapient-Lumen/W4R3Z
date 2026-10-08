from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from typing import Any

from vhk.core.models import I3WindowSelector
from vhk.i3.ipc import I3Connection, discover_socket_path
from vhk.i3.tree import find_first
from vhk.system.hyprctl import HyprctlError, hyprctl_json
from vhk.system.cursor_pos import CursorPos, get_cursor_pos
from vhk.system.session import detect_backend
from vhk.system.processes import get_process_name


class ActiveWindowProbeError(RuntimeError):
    """Raised when VHK cannot query the active window."""


class WindowFocusError(RuntimeError):
    """Raised when VHK cannot focus a matching window."""


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


def _merge_non_none(dst: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    for key, value in extra.items():
        if value is not None:
            dst[key] = value
    return dst


def _boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s in {"1", "true", "yes", "on", "enabled", "user_on", "fullscreen", "visible"}:
            return True
        if s in {"0", "false", "no", "off", "none", "disabled", "auto_off", "hidden"}:
            return False
    return None


def _i3like_state_fields(node: dict[str, Any]) -> dict[str, Any]:
    fullscreen_mode = None
    if node.get("fullscreen_mode") is not None:
        try:
            fullscreen_mode = int(node.get("fullscreen_mode"))
        except Exception:
            fullscreen_mode = None

    floating_raw = node.get("floating")
    floating = None
    if floating_raw is not None:
        floating = str(floating_raw) not in {"auto_off", "off", "none"}

    visible = None
    if "visible" in node:
        visible = bool(node.get("visible"))

    sticky = None
    if "sticky" in node:
        sticky = bool(node.get("sticky"))

    return {
        "visible": visible,
        "fullscreen": None if fullscreen_mode is None else fullscreen_mode > 0,
        "fullscreen_mode": fullscreen_mode,
        "floating": floating,
        "sticky": sticky,
    }


def _hypr_state_fields(raw: dict[str, Any]) -> dict[str, Any]:
    mapped = _boolish(raw.get("mapped")) if "mapped" in raw else None
    hidden = _boolish(raw.get("hidden")) if "hidden" in raw else None
    floating = _boolish(raw.get("floating")) if "floating" in raw else None
    pinned = _boolish(raw.get("pinned")) if "pinned" in raw else None

    fullscreen = _boolish(raw.get("fullscreen")) if "fullscreen" in raw else None
    fullscreen_mode = None
    for key in ("fullscreenmode", "fullscreenMode"):
        if raw.get(key) is not None:
            try:
                fullscreen_mode = int(raw.get(key))
                break
            except Exception:
                pass
    if fullscreen is None and fullscreen_mode is not None:
        fullscreen = fullscreen_mode > 0

    visible = None
    if mapped is not None and hidden is not None:
        visible = mapped and not hidden
    elif hidden is not None:
        visible = not hidden
    elif mapped is not None:
        visible = mapped

    return {
        "mapped": mapped,
        "hidden": hidden,
        "visible": visible,
        "floating": floating,
        "pinned": pinned,
        "fullscreen": fullscreen,
        "fullscreen_mode": fullscreen_mode,
    }


def _parse_xprop_atom_list(line: str) -> set[str]:
    if "=" not in line:
        return set()
    rhs = line.split("=", 1)[1]
    return set(re.findall(r"_NET_WM_STATE_[A-Z_]+", rhs))


def _x11_current_desktop_index() -> int | None:
    xp = shutil.which("xprop")
    if not xp:
        return None
    proc = subprocess.run([xp, "-root", "_NET_CURRENT_DESKTOP"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return _parse_xprop_int(proc.stdout or "")


def _x11_state_fields_from_atoms(atoms: set[str], *, desktop_idx: int | None, current_desktop_idx: int | None) -> dict[str, Any]:
    minimized = "_NET_WM_STATE_HIDDEN" in atoms
    fullscreen = "_NET_WM_STATE_FULLSCREEN" in atoms
    sticky = "_NET_WM_STATE_STICKY" in atoms

    visible = None
    if desktop_idx is not None or sticky or minimized:
        on_current = sticky or (desktop_idx is not None and current_desktop_idx is not None and desktop_idx == current_desktop_idx)
        visible = (not minimized) and (sticky or on_current or current_desktop_idx is None)

    return {
        "minimized": minimized,
        "fullscreen": fullscreen,
        "sticky": sticky,
        "visible": visible,
    }


def _attach_process_metadata(info: dict[str, Any]) -> dict[str, Any]:
    pid = info.get("pid")
    if pid is None:
        return info
    try:
        pid_i = int(pid)
    except Exception:
        return info
    info["pid"] = pid_i
    if not info.get("process_name"):
        info["process_name"] = get_process_name(pid_i)
    return info


def _regex_match(value: str, pattern: str, regex: bool) -> bool:
    if regex:
        return re.search(pattern, value or "") is not None
    return value == pattern


_STATE_BOOL_FIELDS = (
    "visible",
    "fullscreen",
    "floating",
    "sticky",
    "minimized",
    "hidden",
    "mapped",
    "pinned",
)


def _selector_matches_state_fields(selector: I3WindowSelector, info: dict[str, Any]) -> bool:
    for field in _STATE_BOOL_FIELDS:
        want = getattr(selector, field, None)
        if want is None:
            continue
        got = _boolish(info.get(field))
        if got is None:
            return False
        if got != bool(want):
            return False

    want_mode = getattr(selector, "fullscreen_mode", None)
    if want_mode is not None:
        try:
            got_mode = int(info.get("fullscreen_mode"))
        except Exception:
            return False
        if got_mode != int(want_mode):
            return False

    return True


def _selector_matches_hypr_active(selector: I3WindowSelector, info: dict[str, Any]) -> bool:
    # Hyprland doesn't expose i3's instance/role/urgent fields generically.
    if selector.instance is not None:
        return False
    if selector.window_role is not None:
        return False
    if selector.urgent is not None:
        return False

    title = str(info.get("title") or info.get("initialTitle") or "")
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

    if selector.pid is not None:
        try:
            if int(info.get("pid") or 0) != int(selector.pid):
                return False
        except Exception:
            return False

    if selector.focused is not None:
        if "focused" in info:
            if bool(info.get("focused")) != bool(selector.focused):
                return False
        else:
            # activewindow is, by definition, focused.
            if bool(selector.focused) is not True:
                return False

    normalized = dict(info)
    _merge_non_none(normalized, _hypr_state_fields(info))
    return _selector_matches_state_fields(selector, normalized)


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

    if selector.pid is not None:
        try:
            if int(info.get("pid") or 0) != int(selector.pid):
                return False
        except Exception:
            return False

    if selector.urgent is not None:
        if bool(info.get("urgent")) != bool(selector.urgent):
            return False

    if selector.focused is not None:
        if bool(info.get("focused")) != bool(selector.focused):
            return False

    if not _selector_matches_state_fields(selector, info):
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
            "pid": node.get("pid"),
            "app_id": node.get("app_id"),
            "class": wp.get("class"),
            "instance": wp.get("instance"),
            "window_role": wp.get("window_role") or wp.get("role"),
            "title": wp.get("title") or node.get("name"),
            "workspace": match.workspace,
            "urgent": node.get("urgent"),
            "focused": node.get("focused"),
        }
        _merge_non_none(info, _i3like_state_fields(node))
        return _attach_process_metadata(info), wm

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
        _merge_non_none(info2, _hypr_state_fields(raw))
        if info2.get("visible") is None:
            info2["visible"] = True
        return _attach_process_metadata(info2), wm

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
            "visible": True,
            "minimized": False,
        }
        return _attach_process_metadata(out), wm

    if wm == "x11" or (wm == "unknown" and detect_backend() == "x11"):
        return _attach_process_metadata(_x11_active_window_info()), "x11"

    raise ActiveWindowProbeError("unsupported compositor for active window probing")




def _selector_without_focus(selector: I3WindowSelector) -> I3WindowSelector:
    if getattr(selector, "focused", None) is None:
        return selector
    return selector.model_copy(update={"focused": None})


def _normalize_window_identity(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    lower = s.lower()
    if lower.startswith("0x"):
        try:
            return f"0x{int(lower, 16):x}"
        except Exception:
            return lower
    if s.isdigit():
        try:
            return f"0x{int(s):x}"
        except Exception:
            return lower
    return lower


def _row_identity(row: dict[str, Any]) -> str | None:
    return _normalize_window_identity(row.get("address") or row.get("id"))


def _x11_window_id_arg(window_id: Any) -> str:
    s = str(window_id or "").strip()
    if not s:
        raise WindowFocusError("x11 focus target did not include a window id")
    if s.lower().startswith("0x"):
        try:
            return str(int(s, 16))
        except Exception:
            return s
    return s


def _emit_focus_request(row: dict[str, Any], wm: str, *, timeout_s: float) -> None:
    window_id = row.get("id") or row.get("address")
    if wm in {"i3", "sway"}:
        if window_id is None:
            raise WindowFocusError("i3/sway focus target did not include a con id")
        i3 = I3Connection(socket_path=discover_socket_path())
        i3.command(f"[con_id={window_id}] focus")
        return

    if wm == "hyprland":
        from vhk.system.hyprctl import hyprctl_dispatch

        address = str(row.get("address") or row.get("id") or "").strip()
        if not address:
            raise WindowFocusError("Hyprland focus target did not include an address")
        hyprctl_dispatch("focuswindow", f"address:{address}", timeout=max(0.25, timeout_s))
        return

    if wm == "kwin":
        from vhk.system import kdotool as kdotool_mod

        if not window_id:
            raise WindowFocusError("KWin focus target did not include a window id")
        kdotool_mod.run_kdotool(["windowactivate", str(window_id)], timeout_s=max(0.25, timeout_s))
        return

    if wm == "x11":
        xd = shutil.which("xdotool")
        if xd:
            proc = subprocess.run(
                [xd, "windowactivate", "--sync", _x11_window_id_arg(window_id)],
                capture_output=True,
                text=True,
                timeout=max(0.5, timeout_s),
            )
            if proc.returncode != 0:
                raise WindowFocusError((proc.stderr or proc.stdout).strip() or "xdotool windowactivate failed")
            return

        wmctrl = shutil.which("wmctrl")
        if wmctrl:
            target = str(window_id or "").strip()
            proc = subprocess.run([wmctrl, "-ia", target], capture_output=True, text=True, timeout=max(0.5, timeout_s))
            if proc.returncode != 0:
                raise WindowFocusError((proc.stderr or proc.stdout).strip() or "wmctrl -ia failed")
            return

        raise WindowFocusError("need xdotool or wmctrl for X11 window activation")

    raise WindowFocusError(f"unsupported compositor for window focus: {wm}")


def _target_is_active(row: dict[str, Any], selector: I3WindowSelector) -> tuple[bool, dict[str, Any] | None, str | None]:
    try:
        info, wm = get_active_window_info()
    except Exception:
        return False, None, None

    row_id = _row_identity(row)
    active_id = _normalize_window_identity(info.get("address") or info.get("id"))
    if row_id and active_id and row_id == active_id:
        return True, info, wm

    try:
        if selector_matches_info(selector, info, wm):
            return True, info, wm
    except Exception:
        pass
    return False, info, wm


def focus_window_matching(
    selector: I3WindowSelector,
    *,
    timeout_ms: int = 3000,
    poll_ms: int = 100,
    focused_first: bool = True,
) -> tuple[dict[str, Any], str]:
    """Focus the best-effort first window matching ``selector``.

    This intentionally searches without ``focused=True`` so callers can activate a
    matching window even when it is not active yet.
    """

    search_selector = _selector_without_focus(selector)
    rows, wm = get_window_list_snapshot(selector=search_selector, include_geometry=False, focused_first=focused_first)
    if not rows:
        raise WindowFocusError(f"no window matched selector {search_selector.model_dump(by_alias=True)}")

    row = dict(rows[0])
    matched, _info, _wm = _target_is_active(row, search_selector)
    if matched:
        return row, wm

    timeout_ms = max(0, int(timeout_ms))
    poll_ms = max(10, int(poll_ms))
    _emit_focus_request(row, wm, timeout_s=max(0.25, timeout_ms / 1000.0))

    if timeout_ms <= 0:
        return row, wm

    deadline = time.time() + (timeout_ms / 1000.0)
    while time.time() <= deadline:
        matched, _info, _wm = _target_is_active(row, search_selector)
        if matched:
            return row, wm
        time.sleep(poll_ms / 1000.0)

    raise WindowFocusError(f"window activation did not focus selector {search_selector.model_dump(by_alias=True)}")


def get_active_window_snapshot(*, include_geometry: bool = True, require_geometry: bool = False) -> tuple[dict[str, Any], str]:
    """Return a best-effort active-window snapshot for macros and CLIs.

    The snapshot intentionally mirrors the variable shape used by window watchers:
    a shallow window info dict, plus optional ``geometry`` when the current
    compositor/toolchain can provide it.

    Parameters
    ----------
    include_geometry:
        When true, attach ``geometry={rect, client}`` on a best-effort basis.
    require_geometry:
        When true, geometry probe failures are raised instead of being silently
        downgraded to ``geometry=None``.
    """

    info, wm = get_active_window_info()
    snapshot: dict[str, Any] = _attach_process_metadata(dict(info))
    snapshot["wm"] = wm

    if include_geometry:
        try:
            rect, client, _wm2 = get_active_window_geometry()
            snapshot["geometry"] = {"rect": rect, "client": client} if rect is not None else None
        except Exception as exc:
            if require_geometry:
                raise ActiveWindowProbeError(str(exc))
            snapshot["geometry"] = None

    return snapshot, wm


def _iter_i3_like_windows(tree: dict[str, Any]) -> list[tuple[dict[str, Any], str | None]]:
    rows: list[tuple[dict[str, Any], str | None]] = []
    stack: list[tuple[dict[str, Any], str | None]] = [(tree, None)]
    while stack:
        node, ws = stack.pop()
        ws2 = ws
        if node.get("type") == "workspace":
            ws2 = node.get("name")

        children = list(node.get("nodes") or []) + list(node.get("floating_nodes") or [])
        for child in reversed(children):
            stack.append((child, ws2))

        if children:
            continue

        wp = node.get("window_properties") or {}
        if not (node.get("window") is not None or node.get("app_id") or wp or node.get("pid") or node.get("name")):
            continue

        rows.append((node, ws2))
    return rows



def _snapshot_from_i3_like(node: dict[str, Any], workspace: str | None, wm: str, *, include_geometry: bool) -> dict[str, Any]:
    wp = node.get("window_properties") or {}
    snapshot: dict[str, Any] = {
        "id": node.get("id") or node.get("window"),
        "window": node.get("window"),
        "pid": node.get("pid"),
        "process_name": get_process_name(node.get("pid")),
        "app_id": node.get("app_id"),
        "class": wp.get("class"),
        "instance": wp.get("instance"),
        "window_role": wp.get("window_role") or wp.get("role"),
        "title": wp.get("title") or node.get("name"),
        "workspace": workspace,
        "urgent": node.get("urgent"),
        "focused": bool(node.get("focused")),
        "wm": wm,
    }
    _merge_non_none(snapshot, _i3like_state_fields(node))
    if include_geometry:
        rect = node.get("rect") or {}
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
        snapshot["geometry"] = {"rect": out_rect, "client": client}
    return snapshot



def _hypr_workspace_name(value: Any) -> str | None:
    if isinstance(value, dict):
        name = value.get("name")
        if name is None:
            ident = value.get("id")
            return None if ident is None else str(ident)
        return str(name)
    if value is None:
        return None
    return str(value)



def _parse_wmctrl_list_line(line: str, *, current_desktop_idx: int | None = None) -> dict[str, Any] | None:
    parts = (line or "").split(None, 9)
    if len(parts) < 10:
        return None
    wid, desktop, pid, x, y, w, h, host, wm_class, title = parts
    try:
        rect = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
    except Exception:
        rect = None
    cls = None
    instance = None
    if "." in wm_class:
        instance, cls = wm_class.split(".", 1)
    else:
        cls = wm_class
    desktop_idx = None
    try:
        desktop_idx = int(desktop)
    except Exception:
        desktop_idx = None
    sticky = desktop_idx == -1
    visible = None
    if desktop_idx is not None:
        visible = sticky or (current_desktop_idx is not None and desktop_idx == current_desktop_idx)
    out: dict[str, Any] = {
        "id": wid,
        "workspace": desktop,
        "pid": int(pid) if pid.isdigit() else None,
        "process_name": get_process_name(int(pid)) if pid.isdigit() else None,
        "host": host,
        "class": cls,
        "instance": instance,
        "app_id": cls,
        "title": title,
        "focused": False,
        "wm": "x11",
        "sticky": sticky,
        "visible": visible,
    }
    if rect is not None:
        out["geometry"] = {"rect": rect, "client": None}
    return out



def _x11_list_windows(*, include_geometry: bool) -> list[dict[str, Any]]:
    wmctrl = shutil.which("wmctrl")
    active_id = None
    try:
        active_id = _x11_active_window_id()
    except Exception:
        active_id = None
    current_desktop_idx = _x11_current_desktop_index()

    rows: list[dict[str, Any]] = []
    if wmctrl:
        proc = subprocess.run([wmctrl, "-l", "-p", "-G", "-x"], capture_output=True, text=True)
        if proc.returncode == 0:
            for raw in (proc.stdout or "").splitlines():
                item = _parse_wmctrl_list_line(raw, current_desktop_idx=current_desktop_idx)
                if not item:
                    continue
                if not include_geometry:
                    item.pop("geometry", None)
                wid = str(item.get("id") or "")
                if active_id is not None:
                    item["focused"] = wid.lower() == f"0x{active_id:x}".lower()
                xp = shutil.which("xprop")
                if xp:
                    try:
                        proc_props = subprocess.run([xp, "-id", wid, "_NET_WM_STATE"], capture_output=True, text=True)
                        if proc_props.returncode == 0:
                            atoms: set[str] = set()
                            for prop_line in (proc_props.stdout or "").splitlines():
                                if prop_line.strip().startswith("_NET_WM_STATE"):
                                    atoms = _parse_xprop_atom_list(prop_line)
                                    break
                            desktop_idx = None
                            try:
                                desktop_idx = int(str(item.get("workspace")))
                            except Exception:
                                desktop_idx = None
                            _merge_non_none(item, _x11_state_fields_from_atoms(atoms, desktop_idx=desktop_idx, current_desktop_idx=current_desktop_idx))
                    except Exception:
                        pass
                rows.append(item)
            if rows:
                return rows

    xd = shutil.which("xdotool")
    if not xd:
        raise ActiveWindowProbeError("need wmctrl or xdotool for X11 window enumeration")

    proc = subprocess.run([xd, "search", "."], capture_output=True, text=True)
    if proc.returncode != 0:
        raise ActiveWindowProbeError((proc.stderr or proc.stdout).strip() or "xdotool search failed")

    seen: set[int] = set()
    for raw in (proc.stdout or "").splitlines():
        line = raw.strip()
        if not line or not line.isdigit():
            continue
        wid_int = int(line)
        if wid_int in seen:
            continue
        seen.add(wid_int)
        item: dict[str, Any] = {"id": f"0x{wid_int:x}", "focused": active_id == wid_int, "wm": "x11"}

        proc_name = subprocess.run([xd, "getwindowname", line], capture_output=True, text=True)
        if proc_name.returncode == 0 and (proc_name.stdout or "").strip():
            item["title"] = (proc_name.stdout or "").strip()

        xp = shutil.which("xprop")
        if xp:
            proc_props = subprocess.run([xp, "-id", f"0x{wid_int:x}", "WM_CLASS", "_NET_WM_PID", "_NET_WM_DESKTOP", "_NET_WM_STATE"], capture_output=True, text=True)
            state_atoms: set[str] = set()
            desktop_idx = None
            for prop_line in (proc_props.stdout or "").splitlines():
                line2 = prop_line.strip()
                if line2.startswith("WM_CLASS") and "=" in line2:
                    vals = [chunk.strip().strip('"') for chunk in line2.split("=", 1)[1].split(",")]
                    if vals:
                        item["instance"] = vals[0] or None
                    if len(vals) >= 2:
                        item["class"] = vals[1] or None
                        item["app_id"] = vals[1] or None
                elif line2.startswith("_NET_WM_PID") and "=" in line2:
                    rhs = line2.split("=", 1)[1].strip()
                    if rhs.isdigit():
                        item["pid"] = int(rhs)
                        item["process_name"] = get_process_name(int(rhs))
                elif line2.startswith("_NET_WM_DESKTOP") and "=" in line2:
                    item["workspace"] = line2.split("=", 1)[1].strip()
                    desktop_idx = _parse_xprop_int(line2)
                elif line2.startswith("_NET_WM_STATE"):
                    state_atoms = _parse_xprop_atom_list(line2)
            _merge_non_none(item, _x11_state_fields_from_atoms(state_atoms, desktop_idx=desktop_idx, current_desktop_idx=current_desktop_idx))

        if include_geometry:
            try:
                rect = _x11_get_outer_rect(wid_int)
                client = None
                extents = _x11_get_frame_extents(wid_int)
                if extents is not None:
                    left, right, top, bottom = extents
                    client = {
                        "x": rect["x"] + left,
                        "y": rect["y"] + top,
                        "w": max(0, rect["w"] - left - right),
                        "h": max(0, rect["h"] - top - bottom),
                    }
                item["geometry"] = {"rect": rect, "client": client}
            except Exception:
                item["geometry"] = None
        rows.append(item)

    return rows





def _rect_contains(rect: dict[str, Any] | None, x: int, y: int) -> bool:
    if not isinstance(rect, dict):
        return False
    try:
        rx = int(rect.get("x") or 0)
        ry = int(rect.get("y") or 0)
        rw = int(rect.get("w") or rect.get("width") or 0)
        rh = int(rect.get("h") or rect.get("height") or 0)
    except Exception:
        return False
    return x >= rx and y >= ry and x < (rx + rw) and y < (ry + rh)



def _window_area(row: dict[str, Any]) -> int:
    geom = row.get("geometry")
    rect = geom.get("rect") if isinstance(geom, dict) else None
    if not isinstance(rect, dict):
        return 1 << 60
    try:
        return max(0, int(rect.get("w") or rect.get("width") or 0)) * max(0, int(rect.get("h") or rect.get("height") or 0))
    except Exception:
        return 1 << 60



def _choose_window_at_point(rows: list[dict[str, Any]], x: int, y: int) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for row in rows:
        if row.get("visible") is False:
            continue
        geom = row.get("geometry")
        rect = geom.get("rect") if isinstance(geom, dict) else None
        if _rect_contains(rect, x, y):
            candidates.append(row)
    if not candidates:
        return None
    candidates.sort(
        key=lambda row: (
            _window_area(row),
            0 if bool(row.get("focused")) else 1,
            str(row.get("workspace") or ""),
            str(row.get("title") or ""),
            str(row.get("id") or row.get("address") or ""),
        )
    )
    return dict(candidates[0])



def _normalize_window_id(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s.lower().startswith("0x"):
        try:
            return f"0x{int(s, 16):x}"
        except Exception:
            return s.lower()
    if s.isdigit():
        return f"0x{int(s):x}"
    return s



def _find_window_by_id(rows: list[dict[str, Any]], window_id: Any) -> dict[str, Any] | None:
    want = _normalize_window_id(window_id)
    if want is None:
        return None
    for row in rows:
        row_id = _normalize_window_id(row.get("id") or row.get("address"))
        if row_id == want:
            return dict(row)
    return None

def get_window_list_snapshot(
    *,
    include_geometry: bool = False,
    selector: I3WindowSelector | None = None,
    focused_first: bool = True,
) -> tuple[list[dict[str, Any]], str]:
    """Return a best-effort list of currently open top-level windows."""

    wm = detect_compositor() or "unknown"
    rows: list[dict[str, Any]]

    if wm in {"i3", "sway"}:
        socket_path = discover_socket_path()
        tree = I3Connection(socket_path=socket_path).get_tree()
        rows = [_snapshot_from_i3_like(node, ws, wm, include_geometry=include_geometry) for node, ws in _iter_i3_like_windows(tree)]
    elif wm == "hyprland":
        try:
            raw_clients = hyprctl_json("clients")
        except HyprctlError as exc:
            raise ActiveWindowProbeError(str(exc))
        active_addr = None
        try:
            active = hyprctl_json("activewindow")
            active_addr = active.get("address")
        except Exception:
            active_addr = None
        if not isinstance(raw_clients, list):
            raise ActiveWindowProbeError("hyprctl clients did not return a list")
        rows = []
        for client in raw_clients:
            if not isinstance(client, dict):
                continue
            item: dict[str, Any] = {
                "id": client.get("address"),
                "address": client.get("address"),
                "pid": client.get("pid"),
                "process_name": get_process_name(client.get("pid")),
                "class": client.get("class") or client.get("initialClass"),
                "app_id": client.get("class") or client.get("initialClass"),
                "initialClass": client.get("initialClass"),
                "title": client.get("title") or client.get("initialTitle"),
                "workspace": _hypr_workspace_name(client.get("workspace")),
                "focused": client.get("address") == active_addr,
                "wm": wm,
                "xwayland": client.get("xwayland"),
            }
            _merge_non_none(item, _hypr_state_fields(client))
            if include_geometry:
                at = client.get("at")
                size = client.get("size")
                if isinstance(at, list) and len(at) >= 2 and isinstance(size, list) and len(size) >= 2:
                    item["geometry"] = {"rect": {"x": int(at[0]), "y": int(at[1]), "w": int(size[0]), "h": int(size[1])}, "client": None}
                else:
                    item["geometry"] = None
            rows.append(item)
    elif wm == "kwin":
        try:
            from vhk.system import kdotool as kdotool_mod
        except Exception as exc:
            raise ActiveWindowProbeError(str(exc))
        try:
            ids = kdotool_mod.search_windows(timeout_s=3.0)
        except Exception as exc:
            raise ActiveWindowProbeError(str(exc))
        focused_id = None
        try:
            focused_id = kdotool_mod.get_active_window_id(timeout_s=3.0)
        except Exception:
            focused_id = None
        rows = []
        for wid in ids:
            item = _attach_process_metadata(kdotool_mod.get_window_info(wid, timeout_s=3.0))
            item["focused"] = wid == focused_id
            item["wm"] = wm
            if include_geometry:
                try:
                    geom = kdotool_mod.get_window_geometry(wid, timeout_s=3.0)
                    item["geometry"] = None if geom is None else {"rect": {"x": int(geom.x), "y": int(geom.y), "w": int(geom.w), "h": int(geom.h)}, "client": None}
                except Exception:
                    item["geometry"] = None
            rows.append(item)
    elif wm == "x11" or (wm == "unknown" and detect_backend() == "x11"):
        rows = _x11_list_windows(include_geometry=include_geometry)
        wm = "x11"
    else:
        raise ActiveWindowProbeError("unsupported compositor for window enumeration")

    if selector is not None:
        rows = [row for row in rows if selector_matches_info(selector, row, wm)]

    if focused_first:
        rows = sorted(rows, key=lambda row: (not bool(row.get("focused")), str(row.get("workspace") or ""), str(row.get("title") or "")))

    return rows, wm




def get_window_at_cursor_snapshot(
    *,
    include_geometry: bool = True,
    require_geometry: bool = False,
    require_window: bool = False,
) -> tuple[dict[str, Any] | None, str, CursorPos]:
    """Return a best-effort snapshot of the top-level window under the cursor.

    This is VHK's closest analogue to the "which window is the mouse over?"
    portion of AutoHotkey's Window Spy / MouseGetPos workflow.

    The implementation is intentionally backend-aware:
    - X11 prefers ``xdotool getmouselocation``'s direct window id when present.
    - KDE Wayland prefers kdotool's pointer window stack.
    - i3/sway/Hyprland fall back to cursor-position + window geometry matching.

    The returned tuple is ``(window, wm, cursor)``. ``window`` may be ``None``
    when the pointer is not over a detectable top-level window and
    ``require_window`` is false.
    """

    cursor = get_cursor_pos()
    wm = detect_compositor() or "unknown"

    def _finalize(window: dict[str, Any] | None, wm_name: str) -> tuple[dict[str, Any] | None, str, CursorPos]:
        if window is None:
            if require_window:
                raise ActiveWindowProbeError("no window detected under cursor")
            return None, wm_name, cursor
        out = _attach_process_metadata(dict(window))
        if require_geometry and not out.get("geometry"):
            raise ActiveWindowProbeError("window-under-cursor probe did not provide geometry")
        if not include_geometry:
            out.pop("geometry", None)
        out["wm"] = wm_name
        return out, wm_name, cursor

    if wm == "kwin":
        try:
            from vhk.system import kdotool as kdotool_mod
        except Exception as exc:
            raise ActiveWindowProbeError(str(exc))

        direct_id = None
        try:
            direct_id = kdotool_mod.get_window_under_cursor_id(timeout_s=3.0)
        except Exception:
            direct_id = None

        if direct_id:
            item = kdotool_mod.get_window_info(direct_id, timeout_s=3.0)
            try:
                focused_id = kdotool_mod.get_active_window_id(timeout_s=3.0)
            except Exception:
                focused_id = None
            item["focused"] = direct_id == focused_id
            if include_geometry or require_geometry:
                try:
                    geom = kdotool_mod.get_window_geometry(direct_id, timeout_s=3.0)
                    item["geometry"] = None if geom is None else {"rect": {"x": int(geom.x), "y": int(geom.y), "w": int(geom.w), "h": int(geom.h)}, "client": None}
                except Exception:
                    item["geometry"] = None
            return _finalize(item, wm)

    rows, wm2 = get_window_list_snapshot(include_geometry=True, focused_first=False)

    direct_match = None
    if wm2 == "x11":
        try:
            direct_match = _find_window_by_id(rows, _x11_pointer_window_id())
        except Exception:
            direct_match = None
    elif wm2 == "kwin":
        try:
            from vhk.system import kdotool as kdotool_mod
            direct_match = _find_window_by_id(rows, kdotool_mod.get_window_under_cursor_id(timeout_s=3.0))
        except Exception:
            direct_match = None

    if direct_match is None:
        direct_match = _choose_window_at_point(rows, int(cursor.x), int(cursor.y))

    return _finalize(direct_match, wm2)



def _x11_pointer_window_id() -> int | None:
    xd = shutil.which("xdotool")
    if not xd:
        return None
    proc = subprocess.run([xd, "getmouselocation", "--shell"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    kv = _parse_kv_shell(proc.stdout)
    raw = kv.get("WINDOW")
    if raw is None:
        return None
    raw = raw.strip()
    if raw.lower().startswith("0x"):
        try:
            return int(raw, 16)
        except Exception:
            return None
    if raw.isdigit():
        try:
            return int(raw)
        except Exception:
            return None
    return None

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
            "_NET_WM_STATE",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise ActiveWindowProbeError((proc.stderr or proc.stdout).strip() or "xprop failed")

    instance = cls = title = role = None
    pid = None
    desktop_idx = None
    state_atoms: set[str] = set()

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
        elif line.startswith("_NET_WM_STATE"):
            state_atoms = _parse_xprop_atom_list(line)

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
        "visible": True,
    }
    _merge_non_none(info, _x11_state_fields_from_atoms(state_atoms, desktop_idx=desktop_idx, current_desktop_idx=_x11_current_desktop_index()))
    info["visible"] = True
    info["minimized"] = False
    return info
