from __future__ import annotations

"""XDG Desktop Portal helpers (best-effort).

VHK's core automation flow prefers compositor-native screenshot tooling like
grim/maim/scrot. However, some Wayland environments intentionally restrict
silent screen capture, and the supported cross-DE mechanism is the
XDG Desktop Portal API.

This module implements a *minimal*, CLI-oriented bridge to the screenshot
portal using only external DBus client tools (no extra Python dependencies).

Important caveats:
  - Portal screenshot capture is typically *interactive* (user confirmation).
  - The portal chooses the final storage location and returns a URI.
  - Region capture is not part of the portal API; callers can crop after.
"""

import os
import re
import secrets
import shutil
import subprocess
import selectors
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


_SERVICE = "org.freedesktop.portal.Desktop"
_OBJ = "/org/freedesktop/portal/desktop"


@dataclass(frozen=True)
class PortalResponse:
    response: int
    uri: str | None = None
    # Used by PickColor
    color: tuple[float, float, float] | None = None


def _gvariant_dict(options: dict[str, object]) -> str:
    """Build a GVariant dict literal for gdbus.

    Examples:
        { 'handle_token': <'abc'>, 'interactive': <true> }
    """

    parts: list[str] = []
    for k, v in options.items():
        if isinstance(v, bool):
            parts.append(f"'{k}': <{'true' if v else 'false'}>")
        elif isinstance(v, (int, float)):
            parts.append(f"'{k}': <{v}>")
        else:
            # Strings and everything else treated as string.
            s = str(v)
            s = s.replace("\\", "\\\\").replace("'", "\\'")
            parts.append(f"'{k}': <'{s}'>")
    return "{" + ", ".join(parts) + "}"


def _uri_to_path(uri: str) -> Path:
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme not in {"file", ""}:
        raise RuntimeError(f"Portal returned non-file URI: {uri}")
    path = urllib.parse.unquote(parsed.path)
    if not path:
        raise RuntimeError(f"Portal returned empty URI path: {uri}")
    return Path(path)


def _parse_response_text(text: str) -> PortalResponse | None:
    # Response code
    m = re.search(r"\buint32\s+(\d+)\b", text)
    if not m:
        m = re.search(r"\bResponse\s*\(\s*(\d+)\s*,", text)
    if not m:
        return None
    code = int(m.group(1))

    # uri
    uri: str | None = None
    # Most common dbus-monitor style:
    #   string "uri" ... variant string "file:///..."
    if "string \"uri\"" in text:
        mm = re.search(r"string \"uri\"[\s\S]*?variant\s+string\s+\"([^\"]+)\"", text)
        if mm:
            uri = mm.group(1)
    if not uri:
        # gdbus monitor style might inline as {'uri': <'file:///...'>}
        mm = re.search(r"'uri'\s*:\s*<\s*'([^']+)'\s*>", text)
        if mm:
            uri = mm.group(1)
    if not uri:
        # Loose fallback: first file://... we see
        mm = re.search(r"(file://[^\s\"']+)", text)
        if mm:
            uri = mm.group(1)

    # color
    color: tuple[float, float, float] | None = None
    if "string \"color\"" in text or "color" in text:
        # dbus-monitor typically prints doubles line by line.
        doubles = re.findall(r"\bdouble\s+([0-9]*\.?[0-9]+)\b", text)
        if len(doubles) >= 3:
            color = (float(doubles[0]), float(doubles[1]), float(doubles[2]))

    return PortalResponse(response=code, uri=uri, color=color)


def _monitor_lines(*, use_gdbus: bool) -> subprocess.Popen[str]:
    if use_gdbus:
        exe = shutil.which("gdbus")
        if not exe:
            raise RuntimeError("gdbus is required for portal capture")
        # Monitor all signals from the portal service so we can filter by token.
        cmd = [exe, "monitor", "--session", "--dest", _SERVICE]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    exe = shutil.which("dbus-monitor")
    if not exe:
        raise RuntimeError("dbus-monitor is required for portal capture")
    # dbus-monitor supports match rules; filter for the Response signal.
    cmd = [exe, "--session", "interface='org.freedesktop.portal.Request',member='Response'"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)


def _wait_for_response(proc: subprocess.Popen[str], *, token: str, timeout_s: float) -> PortalResponse:
    if not proc.stdout:
        raise RuntimeError("monitor process missing stdout")

    deadline = time.monotonic() + max(0.1, timeout_s)
    buf: list[str] = []
    saw_header = False

    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)

    try:
        while time.monotonic() < deadline:
            remaining = max(0.0, deadline - time.monotonic())
            events = sel.select(timeout=min(0.25, remaining))
            if not events:
                continue

            line = proc.stdout.readline()
            if not line:
                break
            line = line.rstrip("\n")

            if token not in line and not saw_header:
                continue

            if not saw_header:
                if "Response" not in line:
                    continue
                saw_header = True
                buf = [line]
            else:
                # dbus-monitor blocks have indented arg lines; gdbus monitor may
                # be one-line, but we keep buffering until we can parse.
                buf.append(line)

            parsed = _parse_response_text("\n".join(buf))
            if parsed is not None:
                return parsed

            # Stop buffering when a new top-level message begins.
            if saw_header and line.startswith("signal time=") and len(buf) > 1:
                # New signal header without having parsed; reset.
                saw_header = token in line and "Response" in line
                buf = [line] if saw_header else []

    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=1)
        except Exception:
            pass

    raise RuntimeError(f"Timed out waiting for portal response (token={token})")


def _call_portal_method(method: str, *, options: dict[str, object], timeout_s: float) -> PortalResponse:
    gdbus = shutil.which("gdbus")
    if not gdbus:
        raise RuntimeError("gdbus is required for portal capture")

    # Prefer dbus-monitor when present since it's widely documented and its
    # output includes type hints. Fall back to gdbus monitor otherwise.
    use_gdbus = shutil.which("dbus-monitor") is None

    token = str(options.get("handle_token") or "")
    if not token:
        raise RuntimeError("handle_token missing")

    mon = _monitor_lines(use_gdbus=use_gdbus)

    # Fire request.
    variant = _gvariant_dict(options)
    cmd = [
        gdbus,
        "call",
        "--session",
        "--dest",
        _SERVICE,
        "--object-path",
        _OBJ,
        "--method",
        method,
        "",
        variant,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        try:
            mon.terminate()
        except Exception:
            pass
        raise RuntimeError((proc.stderr or proc.stdout).strip() or "portal request failed")

    resp = _wait_for_response(mon, token=token, timeout_s=timeout_s)
    return resp


def portal_screenshot_uri(*, interactive: bool = True, modal: bool = True, timeout_s: float = 90.0) -> PortalResponse:
    """Request a screenshot via the XDG screenshot portal.

    This will commonly show a permission prompt / UI.
    """

    token = "vhk_ss_" + secrets.token_hex(8)
    token = token.replace("-", "_")

    opts: dict[str, object] = {"handle_token": token, "modal": modal, "interactive": interactive}
    return _call_portal_method("org.freedesktop.portal.Screenshot.Screenshot", options=opts, timeout_s=timeout_s)


def portal_pick_color(*, modal: bool = True, timeout_s: float = 90.0) -> PortalResponse:
    token = "vhk_color_" + secrets.token_hex(8)
    token = token.replace("-", "_")
    opts: dict[str, object] = {"handle_token": token, "modal": modal}
    return _call_portal_method("org.freedesktop.portal.Screenshot.PickColor", options=opts, timeout_s=timeout_s)


def save_portal_screenshot(out_path: Path, *, interactive: bool = True, modal: bool = True, timeout_s: float = 90.0) -> tuple[Path, str]:
    """Take a portal screenshot and copy it to a chosen output path."""

    resp = portal_screenshot_uri(interactive=interactive, modal=modal, timeout_s=timeout_s)
    if resp.response != 0:
        raise RuntimeError(f"Portal screenshot cancelled/failed (response={resp.response})")
    if not resp.uri:
        raise RuntimeError("Portal screenshot succeeded but no uri was returned")

    src = _uri_to_path(resp.uri)
    if not src.exists():
        raise RuntimeError(f"Portal returned uri but file is missing: {resp.uri}")

    out_path = out_path.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != out_path:
        out_path.write_bytes(src.read_bytes())
    return out_path, resp.uri


def rgb01_to_hex(rgb: tuple[float, float, float]) -> str:
    def clamp(x: float) -> int:
        return max(0, min(255, int(round(x * 255.0))))

    r, g, b = (clamp(c) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"
