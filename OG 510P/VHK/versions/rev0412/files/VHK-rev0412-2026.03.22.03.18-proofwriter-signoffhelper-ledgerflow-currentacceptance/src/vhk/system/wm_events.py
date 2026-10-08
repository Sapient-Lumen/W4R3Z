from __future__ import annotations

import os
import socket
import time
from dataclasses import dataclass
from typing import Any, Iterator

from vhk.i3.ipc import I3Connection, discover_socket_path
from vhk.system.active_window import detect_compositor, get_active_window_info, get_active_window_snapshot, get_window_list_snapshot
from vhk.system.hyprctl import HyprctlError, hyprctl_json


@dataclass
class WmEvent:
    wm: str
    kind: str  # focus | workspace | title | urgent | new | close | geometry | custom
    name: str  # raw event name
    data: Any


def _geometry_payload_from_i3_container(container: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(container, dict):
        return None

    rect = container.get("rect") or {}
    if not isinstance(rect, dict):
        rect = {}
    out_rect = {
        "x": int(rect.get("x") or 0),
        "y": int(rect.get("y") or 0),
        "w": int(rect.get("width") or rect.get("w") or 0),
        "h": int(rect.get("height") or rect.get("h") or 0),
    }

    client = None
    wr = container.get("window_rect") or {}
    if isinstance(wr, dict) and all(k in wr for k in ("x", "y", "width", "height")):
        client = {
            "x": out_rect["x"] + int(wr.get("x") or 0),
            "y": out_rect["y"] + int(wr.get("y") or 0),
            "w": int(wr.get("width") or 0),
            "h": int(wr.get("height") or 0),
        }

    return {"rect": out_rect, "client": client}


def _geometry_signature_from_snapshot(snapshot: dict[str, Any]) -> tuple[object, tuple[int, int, int, int] | None]:
    identity = snapshot.get("address") or snapshot.get("id") or snapshot.get("class") or snapshot.get("app_id")
    geom = snapshot.get("geometry") if isinstance(snapshot.get("geometry"), dict) else None
    rect = None
    if isinstance(geom, dict):
        rect_obj = geom.get("rect") if isinstance(geom.get("rect"), dict) else None
        if isinstance(rect_obj, dict):
            try:
                rect = (
                    int(rect_obj.get("x") or 0),
                    int(rect_obj.get("y") or 0),
                    int(rect_obj.get("w") or rect_obj.get("width") or 0),
                    int(rect_obj.get("h") or rect_obj.get("height") or 0),
                )
            except Exception:
                rect = None
    return identity, rect


def _geometry_reason(old_rect: tuple[int, int, int, int] | None, new_rect: tuple[int, int, int, int] | None) -> str:
    if old_rect is None or new_rect is None:
        return "geometry"
    moved = old_rect[:2] != new_rect[:2]
    resized = old_rect[2:] != new_rect[2:]
    if moved and resized:
        return "geometry"
    if moved:
        return "move"
    if resized:
        return "resize"
    return "geometry"


def _hypr_socket2_path() -> str:
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if not sig or not xdg:
        raise RuntimeError("HYPRLAND_INSTANCE_SIGNATURE/XDG_RUNTIME_DIR not set")
    return os.path.join(xdg, "hypr", sig, ".socket2.sock")


def _iter_hypr_socket2_lines(path: str) -> Iterator[str]:
    """Yield newline-delimited lines from Hyprland socket2."""

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(None)
    s.connect(path)

    buf = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                yield line.decode("utf-8", errors="replace").strip()
    finally:
        try:
            s.close()
        except Exception:
            pass


_HYPR_CLIENTS_CACHE: dict[str, Any] = {"ts": 0.0, "clients": None}

# Hyprland socket2 event payloads can be lossy.
# Notably, `closewindow` and `kill` only provide a window address.
# To make automation and watchers more useful (e.g. "on close" triggers that
# still need class/title/workspace), we maintain a small best-effort metadata
# cache keyed by window address.
_HYPR_META_CACHE: dict[str, dict[str, Any]] = {}
_HYPR_META_ORDER: list[str] = []
_HYPR_META_TTL_S: float = 10 * 60.0  # 10 minutes
_HYPR_META_MAX: int = 2048

# Hyprland emits both `activewindowv2` (address) and `activewindow` (class,title).
# These are often adjacent; we use a short pairing window to attribute class/title
# to an address without calling hyprctl.
_HYPR_LAST_ACTIVE: dict[str, Any] = {
    "ts_addr": 0.0,
    "address": None,
    "ts_ct": 0.0,
    "class": None,
    "title": None,
}


def _hypr_norm_addr(address: str | None) -> str:
    return (address or "").strip().lower()


def _hypr_meta_prune(now: float | None = None) -> None:
    now = time.time() if now is None else float(now)
    # Drop expired entries.
    expired: list[str] = []
    for addr, meta in list(_HYPR_META_CACHE.items()):
        ts = float(meta.get("ts") or 0.0)
        if ts and (now - ts) > _HYPR_META_TTL_S:
            expired.append(addr)
    for addr in expired:
        _HYPR_META_CACHE.pop(addr, None)

    # Enforce max size (rough FIFO; good enough).
    while len(_HYPR_META_CACHE) > _HYPR_META_MAX and _HYPR_META_ORDER:
        a = _HYPR_META_ORDER.pop(0)
        _HYPR_META_CACHE.pop(a, None)


def _hypr_meta_put(address: str | None, meta: dict[str, Any]) -> None:
    addr = _hypr_norm_addr(address)
    if not addr:
        return
    now = time.time()
    _hypr_meta_prune(now)

    cur = _HYPR_META_CACHE.get(addr) or {"address": addr}
    cur.update({k: v for k, v in meta.items() if v is not None})
    cur["address"] = addr
    cur["ts"] = now
    _HYPR_META_CACHE[addr] = cur
    _HYPR_META_ORDER.append(addr)


def _hypr_meta_get(address: str | None) -> dict[str, Any] | None:
    addr = _hypr_norm_addr(address)
    if not addr:
        return None
    _hypr_meta_prune()
    meta = _HYPR_META_CACHE.get(addr)
    if not meta:
        return None
    # Return a shallow copy so callers can safely mutate.
    return dict(meta)


def _hypr_update_cache_from_raw_event(ev_name: str, data: str) -> None:
    """Update Hyprland address->metadata cache from raw socket2 event lines."""

    name = (ev_name or "").strip()
    payload = (data or "").strip()

    # openwindow: WINDOWADDRESS,WORKSPACENAME,WINDOWCLASS,WINDOWTITLE
    if name == "openwindow":
        parts = payload.split(",", 3)
        addr = parts[0].strip() if len(parts) >= 1 else ""
        ws = parts[1].strip() if len(parts) >= 2 else None
        cls = parts[2].strip() if len(parts) >= 3 else None
        title = parts[3].strip() if len(parts) == 4 else None
        _hypr_meta_put(addr, {"workspace": ws or None, "class": cls or None, "title": title or None})
        return

    # movewindow: WINDOWADDRESS,WORKSPACENAME
    if name in {"movewindow", "movewindowv2"}:
        parts = payload.split(",")
        addr = parts[0].strip() if len(parts) >= 1 else ""
        # v2 includes WORKSPACEID as parts[1]
        ws = parts[-1].strip() if len(parts) >= 2 else None
        _hypr_meta_put(addr, {"workspace": ws or None})
        return

    # windowtitlev2: WINDOWADDRESS,WINDOWTITLE
    if name.lower() in {"windowtitle", "windowtitlev2"} or name in {"windowTitle", "windowTitlev2"}:
        if "," in payload:
            addr, title = payload.split(",", 1)
            _hypr_meta_put(addr.strip(), {"title": (title or "").strip() or None})
        return

    # urgent: WINDOWADDRESS
    if name == "urgent":
        _hypr_meta_put(payload, {"urgent": True})
        return

    # activewindowv2: WINDOWADDRESS
    if name == "activewindowv2":
        _HYPR_LAST_ACTIVE["ts_addr"] = time.time()
        _HYPR_LAST_ACTIVE["address"] = payload.strip() or None
        return

    # activewindow: WINDOWCLASS,WINDOWTITLE
    if name == "activewindow":
        cls = None
        title = None
        if "," in payload:
            cls, title = payload.split(",", 1)
            cls = cls.strip() or None
            title = title.strip() or None
        _HYPR_LAST_ACTIVE["ts_ct"] = time.time()
        _HYPR_LAST_ACTIVE["class"] = cls
        _HYPR_LAST_ACTIVE["title"] = title

        # Pair against the most recent address.
        addr = _HYPR_LAST_ACTIVE.get("address")
        ts_addr = float(_HYPR_LAST_ACTIVE.get("ts_addr") or 0.0)
        if addr and (time.time() - ts_addr) <= 0.75:
            _hypr_meta_put(str(addr), {"class": cls, "title": title})
        return

    # closewindow/kill only carry address; no metadata to update here.
    return


def _hypr_clients_cached(ttl_s: float = 0.4) -> list[dict[str, Any]]:
    now = time.time()
    if _HYPR_CLIENTS_CACHE["clients"] is not None and (now - float(_HYPR_CLIENTS_CACHE["ts"])) <= ttl_s:
        return _HYPR_CLIENTS_CACHE["clients"]

    data = hyprctl_json("clients")
    if not isinstance(data, list):
        raise HyprctlError("hyprctl clients did not return a list")

    _HYPR_CLIENTS_CACHE["ts"] = now
    _HYPR_CLIENTS_CACHE["clients"] = data
    return data


def _hypr_find_client(address: str) -> dict[str, Any] | None:
    addr = (address or "").strip().lower()
    if not addr:
        return None

    try:
        for c in _hypr_clients_cached():
            a = str(c.get("address") or "").strip().lower()
            if a == addr:
                return c
    except HyprctlError:
        return None
    except Exception:
        return None

    return None


def window_info_from_event(ev: WmEvent) -> dict[str, Any] | None:
    """Best-effort extract of a window info dict from an event."""

    if ev.wm in {"i3", "sway"}:
        if ev.name != "window" or not isinstance(ev.data, dict):
            return None
        c = ev.data.get("container") or {}
        if not isinstance(c, dict):
            return None
        wp = c.get("window_properties") or {}
        if not isinstance(wp, dict):
            wp = {}

        title = wp.get("title") or c.get("name")
        info: dict[str, Any] = {
            "id": c.get("id") or c.get("window"),
            "app_id": c.get("app_id"),
            "class": wp.get("class"),
            "instance": wp.get("instance"),
            "window_role": wp.get("window_role") or wp.get("role"),
            "title": title,
            "urgent": c.get("urgent"),
            "focused": c.get("focused"),
        }
        geom = _geometry_payload_from_i3_container(c)
        if geom is not None:
            info["geometry"] = geom
        return info

    if ev.wm == "hyprland":
        name = (ev.name or "").strip()
        data = (str(ev.data) if ev.data is not None else "").strip()

        # Always update cache opportunistically; this is cheap for most events
        # and helps closewindow/kill watchers.
        try:
            _hypr_update_cache_from_raw_event(name, data)
        except Exception:
            pass

        address: str | None = None
        title: str | None = None
        cls: str | None = None

        if name == "activewindow":
            if "," in data:
                cls, title = data.split(",", 1)
                cls = cls.strip() or None
                title = title.strip() or None
        elif name == "activewindowv2":
            address = data
        elif name.lower() in {"windowtitle", "windowtitlev2"} or name in {"windowTitle", "windowTitlev2"}:
            if "," in data:
                address, title = data.split(",", 1)
                address = (address or "").strip() or None
                title = (title or "").strip() or None
            else:
                address = data
        elif name == "urgent":
            address = data
        elif name == "openwindow":
            # Format: WINDOWADDRESS,WORKSPACENAME,WINDOWCLASS,WINDOWTITLE
            parts = data.split(",", 3)
            if len(parts) >= 1:
                address = parts[0].strip() or None
            if len(parts) >= 2:
                # Workspace name is useful even if the client cache is stale.
                pass
            if len(parts) >= 3:
                cls = parts[2].strip() or None
            if len(parts) == 4:
                title = parts[3].strip() or None
        elif name in {"closewindow", "kill"}:
            address = data

        client = _hypr_find_client(address or "") if address else None
        if client is not None:
            wsv = client.get("workspace")
            ws_name = None
            if isinstance(wsv, dict):
                ws_name = wsv.get("name")
            elif isinstance(wsv, str):
                ws_name = wsv

            info2: dict[str, Any] = {
                "address": client.get("address"),
                "pid": client.get("pid"),
                "class": client.get("class") or client.get("initialClass") or cls,
                "initialClass": client.get("initialClass"),
                "title": client.get("title") or client.get("initialTitle") or title,
                "workspace": ws_name,
                "urgent": bool(client.get("urgent")) if "urgent" in client else None,
            }
            at = client.get("at")
            size = client.get("size")
            if isinstance(at, list) and len(at) >= 2 and isinstance(size, list) and len(size) >= 2:
                try:
                    info2["geometry"] = {
                        "rect": {"x": int(at[0]), "y": int(at[1]), "w": int(size[0]), "h": int(size[1])},
                        "client": None,
                    }
                except Exception:
                    pass
            return info2

        # Client lookup can fail for closewindow/kill because the client may
        # already be unmapped. Fall back to cached metadata.
        cached = _hypr_meta_get(address)
        if cached is not None:
            # Merge best-effort parsed values.
            if cls and not cached.get("class"):
                cached["class"] = cls
            if title and not cached.get("title"):
                cached["title"] = title
            return cached

        if address or title or cls:
            info3 = {"address": address, "class": cls, "title": title}
            if name == "openwindow":
                parts = data.split(",", 3)
                if len(parts) >= 2:
                    ws = parts[1].strip()
                    if ws:
                        info3["workspace"] = ws
            return info3

    if ev.wm in {"x11", "kwin", "unknown"} and isinstance(ev.data, dict):
        return dict(ev.data)

    return None


def workspace_from_event(ev: WmEvent) -> str | None:
    """Best-effort workspace name extraction for a WM event."""

    if ev.wm in {"i3", "sway"}:
        if ev.name == "workspace" and isinstance(ev.data, dict):
            current = ev.data.get("current") or {}
            if isinstance(current, dict):
                name = str(current.get("name") or "").strip()
                if name:
                    return name
            old = ev.data.get("old") or {}
            if isinstance(old, dict):
                name = str(old.get("name") or "").strip()
                if name:
                    return name
        info = window_info_from_event(ev) or {}
        name = str(info.get("workspace") or "").strip()
        return name or None

    if ev.wm == "hyprland":
        raw = str(ev.data or "").strip()
        if not raw:
            return None
        if ev.name in {"workspace", "workspacev2", "movewindow", "movewindowv2"}:
            if "," in raw:
                return (raw.split(",")[-1].strip() or None)
            return raw or None
        if ev.name in {"focusedmon", "focusedmonv2"}:
            if "," in raw:
                return (raw.split(",")[-1].strip() or None)
            return None
        info = window_info_from_event(ev) or {}
        name = str(info.get("workspace") or "").strip()
        return name or None

    return None


def event_context_from_wm_event(ev: WmEvent) -> tuple[dict[str, Any], str]:
    """Resolve the best-effort window context for a WM event."""

    info: dict[str, Any]
    wm = ev.wm
    if ev.kind in {"title", "urgent", "new", "close", "geometry", "custom"}:
        info = window_info_from_event(ev) or {}
        if (not info) and ev.kind in {"title", "urgent"}:
            try:
                info, wm = get_active_window_info()
            except Exception:
                info, wm = {}, ev.wm
    else:
        try:
            info, wm = get_active_window_info()
        except Exception:
            info, wm = {}, ev.wm

    workspace = workspace_from_event(ev)
    if workspace and not info.get("workspace"):
        info = dict(info)
        info["workspace"] = workspace
    return info, wm


def _snapshot_event_row_key(row: dict[str, Any]) -> str | None:
    for key in ("address", "id"):
        value = row.get(key)
        if value is not None:
            s = str(value).strip()
            if s:
                return s.lower()
    cls = str(row.get("class") or row.get("app_id") or "").strip()
    title = str(row.get("title") or "").strip()
    pid = row.get("pid")
    if cls or title or pid is not None:
        return f"{cls.lower()}::{title}::{pid}"
    return None


def iter_wm_events(*, kinds: set[str] | None = None, poll_ms: int = 200) -> Iterator[WmEvent]:
    """Yield WM events (best-effort).

    Supported kinds: focus, workspace, title, urgent, new, close, geometry, custom.

    This iterator automatically reconnects if the compositor drops the IPC
    connection (i3 restart, Hyprland reload, etc.).
    """

    kinds = kinds or {"focus"}
    wm = detect_compositor() or "unknown"

    if wm in {"i3", "sway"}:
        need_window = bool({"focus", "title", "urgent", "new", "close", "geometry"} & kinds)
        need_workspace = "workspace" in kinds
        subs: list[str] = []
        if need_window:
            subs.append("window")
        if need_workspace:
            subs.append("workspace")
        if not subs:
            return

        backoff = 0.25
        while True:
            try:
                conn = I3Connection(socket_path=discover_socket_path())
                for name, payload in conn.subscribe(subs):
                    if name == "window" and need_window and isinstance(payload, dict):
                        change = payload.get("change")
                        if change == "focus" and "focus" in kinds:
                            yield WmEvent(wm=wm, kind="focus", name=name, data=payload)
                        elif change == "title" and "title" in kinds:
                            yield WmEvent(wm=wm, kind="title", name=name, data=payload)
                        elif change == "urgent" and "urgent" in kinds:
                            yield WmEvent(wm=wm, kind="urgent", name=name, data=payload)
                        elif change == "new" and "new" in kinds:
                            yield WmEvent(wm=wm, kind="new", name=name, data=payload)
                        elif change == "close" and "close" in kinds:
                            yield WmEvent(wm=wm, kind="close", name=name, data=payload)
                        elif change in {"move", "floating", "fullscreen_mode"} and "geometry" in kinds:
                            yield WmEvent(wm=wm, kind="geometry", name=name, data=payload)
                    elif name == "workspace" and need_workspace and isinstance(payload, dict):
                        if payload.get("change") == "focus":
                            yield WmEvent(wm=wm, kind="workspace", name=name, data=payload)
                backoff = 0.25
            except GeneratorExit:
                return
            except KeyboardInterrupt:
                raise
            except Exception:
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 5.0)
                continue

    if wm == "hyprland":
        try:
            path = _hypr_socket2_path()
        except Exception:
            path = None

        if path is not None and "geometry" not in kinds:
            backoff = 0.25
            while True:
                try:
                    for line in _iter_hypr_socket2_lines(path):
                        if not line or ">>" not in line:
                            continue
                        ev, data = line.split(">>", 1)
                        ev = ev.strip()
                        data = data.strip()

                        # Keep cache warm even when the caller only requested
                        # a subset of kinds (e.g. close-only watchers). Hyprland
                        # socket2 emits all events; we can opportunistically
                        # capture metadata from openwindow/title/move events.
                        try:
                            _hypr_update_cache_from_raw_event(ev, data)
                        except Exception:
                            pass

                        if "focus" in kinds and ev in {"activewindow", "activewindowv2"}:
                            yield WmEvent(wm=wm, kind="focus", name=ev, data=data)
                        elif "workspace" in kinds and ev in {"workspace", "workspacev2"}:
                            yield WmEvent(wm=wm, kind="workspace", name=ev, data=data)
                        elif "title" in kinds and (ev.lower() in {"windowtitle", "windowtitlev2"} or ev in {"windowTitle", "windowTitlev2"}):
                            yield WmEvent(wm=wm, kind="title", name=ev, data=data)
                        elif "urgent" in kinds and ev == "urgent":
                            yield WmEvent(wm=wm, kind="urgent", name=ev, data=data)
                        elif "new" in kinds and ev == "openwindow":
                            yield WmEvent(wm=wm, kind="new", name=ev, data=data)
                        elif "close" in kinds and ev in {"closewindow", "kill"}:
                            yield WmEvent(wm=wm, kind="close", name=ev, data=data)
                        elif "custom" in kinds and ev == "custom":
                            yield WmEvent(wm=wm, kind="custom", name=ev, data=data)
                    backoff = 0.25
                except GeneratorExit:
                    return
                except KeyboardInterrupt:
                    raise
                except Exception:
                    time.sleep(backoff)
                    backoff = min(backoff * 2.0, 5.0)
                    continue

    # Fallback: polling. Generic X11 / KWin / unknown backends can still surface
    # focus changes and active-window title transitions via active-window probes,
    # and can infer best-effort new/close transitions by diffing window-list
    # snapshots between polls. Active-window geometry changes are also exposed
    # here as best-effort ``geometry`` events, which is the most portable Linux
    # lane outside compositor-specific scripting APIs.
    if not ({"focus", "title", "new", "close", "geometry"} & kinds):
        return

    primed = False
    prev_focus_sig = None
    prev_title_sig: tuple[object, object] | None = None
    prev_geometry_sig: tuple[object, tuple[int, int, int, int] | None] | None = None
    current_snapshot: dict[str, Any] = {}
    prev_rows: dict[str, dict[str, Any]] | None = None
    pending: list[WmEvent] = []
    sleep_s = max(0, int(poll_ms)) / 1000.0
    while True:
        if pending:
            yield pending.pop(0)
            continue

        try:
            if "geometry" in kinds:
                current_snapshot, active_wm = get_active_window_snapshot(include_geometry=True)
                info = dict(current_snapshot)
            else:
                info, active_wm = get_active_window_info()
        except Exception:
            info, active_wm = {}, wm
            current_snapshot = {}
        focus_sig = info.get("id") or info.get("address") or (info.get("class"), info.get("title"))
        title_sig = (info.get("id") or info.get("address") or info.get("class"), info.get("title"))
        geometry_sig = _geometry_signature_from_snapshot(current_snapshot or info) if "geometry" in kinds else None

        rows_map: dict[str, dict[str, Any]] | None = None
        rows_wm = active_wm or wm
        if {"new", "close"} & kinds:
            try:
                rows, rows_wm2 = get_window_list_snapshot(include_geometry=False, focused_first=False)
                if rows_wm2:
                    rows_wm = rows_wm2
                rows_map = {}
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    key = _snapshot_event_row_key(row)
                    if key is None or key in rows_map:
                        continue
                    rows_map[key] = dict(row)
            except Exception:
                rows_map = None

        if not primed:
            primed = True
            prev_focus_sig = focus_sig
            prev_title_sig = title_sig
            prev_geometry_sig = geometry_sig
            prev_rows = rows_map
            time.sleep(sleep_s)
            continue

        if "focus" in kinds and focus_sig != prev_focus_sig:
            prev_focus_sig = focus_sig
            prev_title_sig = title_sig
            prev_rows = rows_map if rows_map is not None else prev_rows
            yield WmEvent(wm=active_wm or rows_wm or wm, kind="focus", name="poll", data=focus_sig)
            time.sleep(sleep_s)
            continue

        if "title" in kinds and prev_title_sig is not None and title_sig[0] == prev_title_sig[0] and title_sig[1] != prev_title_sig[1]:
            prev_focus_sig = focus_sig
            prev_title_sig = title_sig
            prev_geometry_sig = geometry_sig
            prev_rows = rows_map if rows_map is not None else prev_rows
            yield WmEvent(wm=active_wm or rows_wm or wm, kind="title", name="poll", data=title_sig)
            time.sleep(sleep_s)
            continue

        if (
            "geometry" in kinds
            and prev_geometry_sig is not None
            and geometry_sig is not None
            and geometry_sig[0] == prev_geometry_sig[0]
            and geometry_sig[1] is not None
            and prev_geometry_sig[1] is not None
            and geometry_sig[1] != prev_geometry_sig[1]
        ):
            reason = _geometry_reason(prev_geometry_sig[1], geometry_sig[1])
            payload = dict(current_snapshot or info)
            payload["geometry_reason"] = reason
            payload["old_geometry"] = {
                "rect": {
                    "x": int(prev_geometry_sig[1][0]),
                    "y": int(prev_geometry_sig[1][1]),
                    "w": int(prev_geometry_sig[1][2]),
                    "h": int(prev_geometry_sig[1][3]),
                }
            }
            prev_focus_sig = focus_sig
            prev_title_sig = title_sig
            prev_geometry_sig = geometry_sig
            prev_rows = rows_map if rows_map is not None else prev_rows
            yield WmEvent(wm=active_wm or rows_wm or wm, kind="geometry", name="poll", data=payload)
            time.sleep(sleep_s)
            continue

        if rows_map is not None and prev_rows is not None:
            closed_rows = [dict(prev_rows[key]) for key in prev_rows.keys() if key not in rows_map]
            new_rows = [dict(rows_map[key]) for key in rows_map.keys() if key not in prev_rows]
            prev_rows = rows_map
            prev_focus_sig = focus_sig
            prev_title_sig = title_sig
            prev_geometry_sig = geometry_sig

            queued: list[WmEvent] = []
            if "close" in kinds:
                queued.extend(WmEvent(wm=rows_wm or active_wm or wm, kind="close", name="poll", data=row) for row in closed_rows)
            if "new" in kinds:
                queued.extend(WmEvent(wm=rows_wm or active_wm or wm, kind="new", name="poll", data=row) for row in new_rows)
            if queued:
                pending.extend(queued[1:])
                yield queued[0]
                continue
        elif rows_map is not None:
            prev_rows = rows_map

        prev_focus_sig = focus_sig
        prev_title_sig = title_sig
        prev_geometry_sig = geometry_sig
        time.sleep(sleep_s)
