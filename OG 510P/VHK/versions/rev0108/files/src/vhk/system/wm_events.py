from __future__ import annotations

import os
import socket
import time
from dataclasses import dataclass
from typing import Any, Iterator

from vhk.i3.ipc import I3Connection, discover_socket_path
from vhk.system.active_window import detect_compositor, get_active_window_info
from vhk.system.hyprctl import HyprctlError, hyprctl_json


@dataclass
class WmEvent:
    wm: str
    kind: str  # focus | workspace | title | urgent | new | close | custom
    name: str  # raw event name
    data: Any


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

    return None


def iter_wm_events(*, kinds: set[str] | None = None, poll_ms: int = 200) -> Iterator[WmEvent]:
    """Yield WM events (best-effort).

    Supported kinds: focus, workspace, title, urgent, new, close, custom.

    This iterator automatically reconnects if the compositor drops the IPC
    connection (i3 restart, Hyprland reload, etc.).
    """

    kinds = kinds or {"focus"}
    wm = detect_compositor() or "unknown"

    if wm in {"i3", "sway"}:
        need_window = bool({"focus", "title", "urgent", "new", "close"} & kinds)
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

        if path is not None:
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

    # Fallback: polling. Only supports focus changes.
    # (new/close/title/workspace events require compositor IPC.)
    if "focus" not in kinds:
        return

    prev = None
    while True:
        try:
            info, _wm = get_active_window_info()
        except Exception:
            info = {}
        sig = info.get("id") or info.get("address") or (info.get("class"), info.get("title"))
        if sig != prev:
            prev = sig
            yield WmEvent(wm=wm, kind="focus", name="poll", data=sig)
        time.sleep(max(0, int(poll_ms)) / 1000.0)
