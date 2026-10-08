from __future__ import annotations

"""Hyprland socket2 helpers.

Hyprland exposes an event stream via a UNIX stream socket commonly referred to as
"socket2". The wiki documents the path convention:

    $XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock

and the line format:

    EVENT>>DATA\n
For example, the `event` dispatcher emits:

    custom>>yourdata

This module provides:
- best-effort path discovery
- a tiny parser for the `EVENT>>DATA` stream
- a bridge that forwards Hyprland `custom>>...` events into the VHK bus (UNIX
  datagram socket) so users can trigger macros without glue scripts.
"""

import json
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from vhk.system.event_bus import emit_bus_event


@dataclass
class HyprSocket2Event:
    event: str
    data: str
    raw: str


def get_hypr_socket2_path(
    *,
    xdg_runtime_dir: str | None = None,
    instance_signature: str | None = None,
) -> Path:
    """Return the socket2 path using environment conventions.

    Raises FileNotFoundError if the environment doesn't look like Hyprland.
    """

    xdg = xdg_runtime_dir or os.environ.get("XDG_RUNTIME_DIR")
    sig = instance_signature or os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not xdg or not sig:
        raise FileNotFoundError("Hyprland socket2 path requires XDG_RUNTIME_DIR and HYPRLAND_INSTANCE_SIGNATURE")
    return Path(xdg) / "hypr" / sig / ".socket2.sock"


def iter_socket2_events(sock_path: Path, *, bufsize: int = 1024 * 64) -> Iterator[HyprSocket2Event]:
    """Yield parsed socket2 events from a connected UNIX stream socket."""

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(str(sock_path))
        f = s.makefile("r", encoding="utf-8", errors="replace")
        for line in f:
            raw = line.rstrip("\r\n")
            if not raw:
                continue
            if ">>" in raw:
                ev, data = raw.split(">>", 1)
                yield HyprSocket2Event(event=ev.strip(), data=data, raw=raw)
            else:
                yield HyprSocket2Event(event=raw.strip(), data="", raw=raw)
    finally:
        try:
            s.close()
        except Exception:
            pass


def _best_effort_parse(data: str) -> Any:
    """Parse JSON when it looks like JSON; else return the original string."""

    txt = (data or "").strip()
    if not txt:
        return ""
    if txt[0] in "{[\"" or txt in ("true", "false", "null") or txt[0].isdigit() or txt[0] == "-":
        try:
            return json.loads(txt)
        except Exception:
            return data
    return data


def bridge_hypr_custom_to_bus(
    *,
    hypr_socket2: Path,
    bus_socket: Path,
    bus_event: str = "hypr.custom",
    max_events: int | None = None,
) -> int:
    """Forward Hyprland `custom>>...` socket2 events into the VHK bus.

    Returns the number of forwarded events.

    If the custom payload is JSON, it will be decoded and emitted as the bus
    data directly. This lets you use VHK's bus dispatch watcher format:

        custom payload: {"macro": "foo", "vars": {"x": 1}}

    without wrapping.
    """

    n = 0
    for ev in iter_socket2_events(hypr_socket2):
        if ev.event != "custom":
            continue
        payload = _best_effort_parse(ev.data)
        emit_bus_event(bus_socket, bus_event, payload)
        n += 1
        if max_events is not None and n >= max_events:
            break
    return n
