from __future__ import annotations

"""XDG GlobalShortcuts portal helpers (experimental).

This is the closest thing Wayland currently has to a *permissioned* global hotkey
API. It is surfaced via xdg-desktop-portal and implemented by DE-specific portal
backends.

- Portal interface: org.freedesktop.portal.GlobalShortcuts (version 2)
- Preferred trigger format: freedesktop "Shortcuts" specification

We keep this implementation dependency-light by using external DBus tools
(gdbus + dbus-monitor) rather than Python DBus bindings.

Caveats
-------
- BindShortcuts typically shows an interactive UI.
- BindShortcuts requires a parent_window identifier (may be empty depending on
  backend; see portal "Window Identifiers" docs).
- Backend support varies across DEs and versions.
"""

import json
import re
import secrets
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Iterator


_SERVICE = "org.freedesktop.portal.Desktop"
_OBJ = "/org/freedesktop/portal/desktop"


@dataclass(frozen=True)
class ShortcutSpec:
    shortcut_id: str
    description: str
    preferred_trigger: str | None = None


@dataclass(frozen=True)
class ShortcutSignal:
    kind: str  # Activated | Deactivated
    session_handle: str
    shortcut_id: str
    timestamp: int
    options: dict[str, Any]


# --- shortcuts-spec conversion ----------------------------------------------

_MOD_TO_SPEC = {
    "ctrl": "CTRL",
    "control": "CTRL",
    "alt": "ALT",
    "shift": "SHIFT",
    "logo": "LOGO",
    "super": "LOGO",
    "meta": "LOGO",
    "mod4": "LOGO",
    "num": "NUM",
}

_KEY_SYM = {
    "enter": "Return",
    "return": "Return",
    "esc": "Escape",
    "escape": "Escape",
    "tab": "Tab",
    "space": "space",
    "backspace": "BackSpace",
    "delete": "Delete",
    "insert": "Insert",
    "home": "Home",
    "end": "End",
    "pageup": "Page_Up",
    "pagedown": "Page_Down",
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
}


def _normalize_key_name(name: str) -> str:
    s = name.strip()
    if s.startswith("<") and s.endswith(">"):
        s = s[1:-1]
    s = s.replace("_", "").replace("-", "")
    return s.lower()


def vhk_hotkey_to_shortcuts_spec(keys: str) -> str | None:
    """Convert VHK/i3-style chords like "Mod4+Shift+p" to shortcuts-spec.

    Returns None if the chord can't be parsed.

    Shortcuts spec (draft) uses modifiers {CTRL, ALT, SHIFT, NUM, LOGO} and
    keysyms from xkbcommon without the XKB_KEY_ prefix.
    """

    parts = [p for p in re.split(r"[+ ]", keys.replace("/", "+")) if p]
    if not parts:
        return None

    key = parts[-1]
    mods_raw = parts[:-1]

    mods: list[str] = []
    for m in mods_raw:
        mm = _MOD_TO_SPEC.get(m.strip().lower())
        if mm and mm not in mods:
            mods.append(mm)

    k_norm = _normalize_key_name(key)

    # f1..f12
    if k_norm.startswith("f") and k_norm[1:].isdigit():
        k_out = f"F{int(k_norm[1:])}"
    elif len(k_norm) == 1 and k_norm.isalnum():
        k_out = k_norm
    else:
        k_out = _KEY_SYM.get(k_norm, key)

    # Spec requires alphanumerical + underscore only for identifiers.
    k_out = re.sub(r"[^A-Za-z0-9_]", "", str(k_out))
    if not k_out:
        return None

    if mods:
        return "+".join(mods + [k_out])
    return k_out


# --- portal request helpers --------------------------------------------------

_RESPONSE_CODE_RE = re.compile(r"\buint32\s+(\d+)\b")


def _gvariant_dict(options: dict[str, object]) -> str:
    parts: list[str] = []
    for k, v in options.items():
        if isinstance(v, bool):
            parts.append(f"'{k}': <{'true' if v else 'false'}>")
        elif isinstance(v, (int, float)):
            parts.append(f"'{k}': <{v}>")
        else:
            s = str(v)
            s = s.replace("\\", "\\\\").replace("'", "\\'")
            parts.append(f"'{k}': <'{s}'>")
    return "{" + ", ".join(parts) + "}"


def _spawn_response_monitor() -> subprocess.Popen[str]:
    exe = shutil.which("dbus-monitor")
    if exe:
        cmd = [exe, "--session", "interface='org.freedesktop.portal.Request',member='Response'"]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    gdbus = shutil.which("gdbus")
    if not gdbus:
        raise RuntimeError("Need gdbus or dbus-monitor")

    cmd = [gdbus, "monitor", "--session", "--dest", _SERVICE]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)


def _wait_for_response_text(proc: subprocess.Popen[str], *, token: str, timeout_s: float) -> str:
    if not proc.stdout:
        raise RuntimeError("monitor process missing stdout")

    deadline = time.monotonic() + max(0.1, timeout_s)
    buf: list[str] = []
    saw_header = False

    try:
        while time.monotonic() < deadline:
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.01)
                continue
            line = line.rstrip("\n")

            if token not in line and not saw_header:
                continue

            if not saw_header:
                if "Response" not in line:
                    continue
                saw_header = True
                buf = [line]
            else:
                buf.append(line)

            text = "\n".join(buf)
            if _RESPONSE_CODE_RE.search(text):
                # Heuristic: once we saw a response code and token, return.
                # Callers do additional key extraction.
                return text + "\n"

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


def _parse_response_code(text: str) -> int | None:
    m = _RESPONSE_CODE_RE.search(text)
    if m:
        return int(m.group(1))

    # gdbus monitor may show `Response (0, {...})`.
    m = re.search(r"\bResponse\s*\(\s*(\d+)\s*,", text)
    if m:
        return int(m.group(1))
    return None


def _extract_dict_string(text: str, key: str) -> str | None:
    # dbus-monitor style dict entry
    if f'string "{key}"' in text:
        mm = re.search(rf"string \"{re.escape(key)}\"[\s\S]*?variant\s+(?:string|object path)\s+\"([^\"]+)\"", text)
        if mm:
            return mm.group(1)

    # gdbus monitor inline dict style: {'session_handle': <'/path'>}
    mm = re.search(rf"'{re.escape(key)}'\s*:\s*<\s*'([^']+)'\s*>", text)
    if mm:
        return mm.group(1)

    mm = re.search(rf"'{re.escape(key)}'\s*:\s*<\s*o\s+'([^']+)'\s*>", text)
    if mm:
        return mm.group(1)

    return None


def create_session(*, timeout_s: float = 60.0) -> str:
    """Create a GlobalShortcuts session and return its session_handle."""

    gdbus = shutil.which("gdbus")
    if not gdbus:
        raise RuntimeError("gdbus is required for global shortcuts portal")

    handle_token = "vhk_gs_" + secrets.token_hex(8)
    handle_token = handle_token.replace("-", "_")
    session_token = "vhk_sess_" + secrets.token_hex(8)
    session_token = session_token.replace("-", "_")

    opts: dict[str, object] = {"handle_token": handle_token, "session_handle_token": session_token}

    mon = _spawn_response_monitor()
    cmd = [
        gdbus,
        "call",
        "--session",
        "--dest",
        _SERVICE,
        "--object-path",
        _OBJ,
        "--method",
        "org.freedesktop.portal.GlobalShortcuts.CreateSession",
        _gvariant_dict(opts),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        try:
            mon.terminate()
        except Exception:
            pass
        raise RuntimeError((proc.stderr or proc.stdout).strip() or "CreateSession failed")

    text = _wait_for_response_text(mon, token=handle_token, timeout_s=timeout_s)
    code = _parse_response_code(text)
    if code is None:
        raise RuntimeError("Failed to parse portal response")
    if code != 0:
        raise RuntimeError(f"Portal CreateSession cancelled/failed (response={code})")

    sess = _extract_dict_string(text, "session_handle")
    if not sess:
        raise RuntimeError("Portal CreateSession succeeded but no session_handle returned")
    return sess


def bind_shortcuts(
    session_handle: str,
    shortcuts: list[ShortcutSpec],
    *,
    parent_window: str = "",
    timeout_s: float = 120.0,
) -> None:
    """Bind shortcuts for a session.

    Note: this is typically interactive (the portal presents a configuration UI).
    """

    gdbus = shutil.which("gdbus")
    if not gdbus:
        raise RuntimeError("gdbus is required for global shortcuts portal")

    handle_token = "vhk_bind_" + secrets.token_hex(8)
    handle_token = handle_token.replace("-", "_")

    # Build a(sa{sv}) shortcut list literal.
    elems: list[str] = []
    for s in shortcuts:
        vardict: dict[str, object] = {"description": s.description}
        if s.preferred_trigger:
            vardict["preferred_trigger"] = s.preferred_trigger
        elems.append(f"('{s.shortcut_id}', {_gvariant_dict(vardict)})")

    shortcuts_lit = "[" + ", ".join(elems) + "]"
    opts: dict[str, object] = {"handle_token": handle_token}

    mon = _spawn_response_monitor()

    cmd = [
        gdbus,
        "call",
        "--session",
        "--dest",
        _SERVICE,
        "--object-path",
        _OBJ,
        "--method",
        "org.freedesktop.portal.GlobalShortcuts.BindShortcuts",
        session_handle,
        shortcuts_lit,
        parent_window,
        _gvariant_dict(opts),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        try:
            mon.terminate()
        except Exception:
            pass
        raise RuntimeError((proc.stderr or proc.stdout).strip() or "BindShortcuts failed")

    text = _wait_for_response_text(mon, token=handle_token, timeout_s=timeout_s)
    code = _parse_response_code(text)
    if code is None:
        raise RuntimeError("Failed to parse BindShortcuts response")
    if code != 0:
        raise RuntimeError(f"Portal BindShortcuts cancelled/failed (response={code})")




def parse_shortcut_signal_block(text: str, *, session_handle: str) -> ShortcutSignal | None:
    """Parse a dbus-monitor signal block for Activated/Deactivated."""

    m = re.search(r"member=(Activated|Deactivated)", text)
    if not m:
        return None
    kind = m.group(1)

    sess_m = re.search(r"object path\s+\"([^\"]+)\"", text)
    sid_m = re.search(r"\n\s*string\s+\"([^\"]+)\"", text)
    ts_m = re.search(r"\buint64\s+(\d+)\b", text)

    if not sess_m or not sid_m or not ts_m:
        return None
    sess = sess_m.group(1)
    if sess != session_handle:
        return None

    return ShortcutSignal(kind=kind, session_handle=sess, shortcut_id=sid_m.group(1), timestamp=int(ts_m.group(1)), options={})


def iter_shortcut_signals(*, session_handle: str) -> Iterator[ShortcutSignal]:
    """Iterate Activated/Deactivated signals for a session."""

    exe = shutil.which("dbus-monitor")
    if not exe:
        raise RuntimeError("dbus-monitor is required to listen for shortcut signals")

    # Filter only shortcut signals.
    cmd = [
        exe,
        "--session",
        "interface='org.freedesktop.portal.GlobalShortcuts'",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    if not proc.stdout:
        raise RuntimeError("monitor process missing stdout")

    buf: list[str] = []

    def flush() -> ShortcutSignal | None:
        nonlocal buf
        if not buf:
            return None
        text = "\n".join(buf) + "\n"
        buf = []

        return parse_shortcut_signal_block(text, session_handle=session_handle)

    try:
        for line in proc.stdout:
            if not line:
                break
            line = line.rstrip("\n")

            if line.startswith("signal time="):
                out = flush()
                if out is not None:
                    yield out
                buf = [line]
            else:
                if buf:
                    buf.append(line)

    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=1)
        except Exception:
            pass
