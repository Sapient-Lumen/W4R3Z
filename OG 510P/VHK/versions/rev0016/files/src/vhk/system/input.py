from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from vhk.system.session import detect_backend


@dataclass
class InputBackend:
    name: str
    exe: str


TypeTextBackend = Literal["auto", "native", "xvkbd"]
PasteShortcut = Literal["auto", "ctrl+v", "ctrl+shift+v", "shift+insert"]


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        if fp.exists() and os.access(fp, os.X_OK):
            return str(fp)
    return None


def choose_keyboard_backend() -> InputBackend | None:
    """Choose a keyboard backend."""

    if detect_backend() == "wayland":
        wt = _which("wtype")
        if wt:
            return InputBackend(name="wtype", exe=wt)
        yd = _which("ydotool")
        if yd:
            return InputBackend(name="ydotool", exe=yd)
        return None

    xd = _which("xdotool")
    if xd:
        return InputBackend(name="xdotool", exe=xd)
    return None


def choose_xvkbd_backend() -> InputBackend | None:
    """Choose xvkbd when present (X11-only text fallback)."""

    if detect_backend() == "wayland":
        return None
    xv = _which("xvkbd")
    if xv:
        return InputBackend(name="xvkbd", exe=xv)
    return None


def choose_pointer_backend() -> InputBackend | None:
    """Choose a mouse/pointer backend."""

    if detect_backend() == "wayland":
        yd = _which("ydotool")
        if yd:
            return InputBackend(name="ydotool", exe=yd)
        return None

    xd = _which("xdotool")
    if xd:
        return InputBackend(name="xdotool", exe=xd)
    return None


def choose_backend() -> InputBackend | None:
    """Backward-compatible alias used by older CLI code."""

    return choose_keyboard_backend() or choose_pointer_backend() or choose_xvkbd_backend()


def _run(cmd: list[str], *, stdin: str | bytes | None = None, text: bool = True) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=text, input=stdin)
    if proc.returncode != 0:
        stderr = proc.stderr.strip() if isinstance(proc.stderr, str) else (proc.stderr.decode(errors="replace").strip() if proc.stderr else "")
        raise RuntimeError(f"Input command failed: {' '.join(cmd)}\n{stderr}")


_MOD_MAP = {
    "control": "ctrl",
    "ctrl": "ctrl",
    "shift": "shift",
    "alt": "alt",
    "mod1": "alt",
    "super": "logo",
    "meta": "logo",
    "logo": "logo",
    "mod4": "logo",
}


def _parse_chord(keys: str) -> tuple[list[str], str]:
    # Accept either "ctrl+l" or "ctrl+alt+t".
    parts = [p for p in re.split(r"[+ ]", keys.replace("/", "+")) if p]
    if len(parts) == 1 and "/" in keys:
        parts = keys.split("+")
    mods: list[str] = []
    key = parts[-1]
    for p in parts[:-1]:
        m = _MOD_MAP.get(p.lower())
        if m:
            mods.append(m)
    return mods, key


_SPECIAL_KEY_PAT = re.compile(r"<[^>]+>")


def text_looks_paste_friendly(text: str) -> bool:
    """Return True when the text is suitable for clipboard-paste injection.

    Clipboard-based sending is great for long printable text, but not for key
    chord markup like ``<ctrl>+v`` or other pseudo-key tokens.
    """

    return not bool(_SPECIAL_KEY_PAT.search(text))



def key(keys: str, *, clearmodifiers: bool = False) -> None:
    backend = choose_keyboard_backend()
    if not backend:
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype' (Wayland).")

    if backend.name == "xdotool":
        cmd = [backend.exe, "key"]
        if clearmodifiers:
            cmd.append("--clearmodifiers")
        cmd.append(keys)
        _run(cmd)
        return

    if backend.name == "wtype":
        mods, k = _parse_chord(keys)
        cmd = [backend.exe]
        # wtype has no direct equivalent to xdotool's --clearmodifiers.
        for m in mods:
            cmd += ["-M", m]
        cmd += ["-k", k]
        for m in reversed(mods):
            cmd += ["-m", m]
        _run(cmd)
        return

    # ydotool supports chord syntax in a single command (e.g. ctrl+alt+f1).
    cmd = [backend.exe, "key", keys]
    _run(cmd)



def key_down(key_name: str, *, clearmodifiers: bool = False) -> None:
    backend = choose_keyboard_backend()
    if not backend:
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype' (Wayland).")

    if backend.name == "xdotool":
        cmd = [backend.exe, "keydown"]
        if clearmodifiers:
            cmd.append("--clearmodifiers")
        cmd.append(key_name)
        _run(cmd)
        return

    if backend.name == "wtype":
        m = _MOD_MAP.get(key_name.lower())
        if m:
            cmd = [backend.exe, "-M", m]
        else:
            cmd = [backend.exe, "-P", key_name]
        _run(cmd)
        return

    raise RuntimeError("KeyDown/KeyUp are not supported via ydotool backend yet; use Key or install wtype.")



def key_up(key_name: str, *, clearmodifiers: bool = False) -> None:
    backend = choose_keyboard_backend()
    if not backend:
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype' (Wayland).")

    if backend.name == "xdotool":
        cmd = [backend.exe, "keyup"]
        if clearmodifiers:
            cmd.append("--clearmodifiers")
        cmd.append(key_name)
        _run(cmd)
        return

    if backend.name == "wtype":
        m = _MOD_MAP.get(key_name.lower())
        if m:
            cmd = [backend.exe, "-m", m]
        else:
            cmd = [backend.exe, "-p", key_name]
        _run(cmd)
        return

    raise RuntimeError("KeyDown/KeyUp are not supported via ydotool backend yet; use Key or install wtype.")





def reset_modifiers() -> None:
    """Best-effort explicit release of common modifiers.

    This is intentionally separate from xdotool's --clearmodifiers behavior.
    It is useful after hotkey-triggered automation when the author wants to
    deliberately release modifier state before the next action.
    """

    backend = choose_keyboard_backend()
    if not backend:
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype' (Wayland).")

    modifiers = ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Super_L", "Super_R"]

    if backend.name == "xdotool":
        for key_name in modifiers:
            _run([backend.exe, "keyup", key_name])
        return

    if backend.name == "wtype":
        for name in ["shift", "ctrl", "alt", "logo"]:
            _run([backend.exe, "-m", name])
        return

    raise RuntimeError("ResetModifiers is not supported via ydotool backend yet; install wtype or use explicit KeyUp steps.")
def type_text(
    text: str,
    *,
    delay_ms_per_char: int = 0,
    clearmodifiers: bool = False,
    backend: TypeTextBackend = "auto",
) -> str:
    """Type text using the chosen backend and return the backend name used."""

    chosen = backend
    if chosen == "auto":
        # Prefer the normal keyboard backend when present; xvkbd is our X11-only
        # fallback when typing exists but xdotool is missing or unreliable.
        if choose_keyboard_backend() is not None:
            chosen = "native"
        elif choose_xvkbd_backend() is not None:
            chosen = "xvkbd"
        else:
            chosen = "native"

    if chosen == "xvkbd":
        xv = choose_xvkbd_backend()
        if not xv:
            raise RuntimeError("No xvkbd backend found. Install 'xvkbd' or choose backend='native'.")
        with tempfile.NamedTemporaryFile(prefix="vhk_xvkbd_", suffix=".txt", delete=False) as tmp:
            tmp.write(text.encode("utf-16"))
            tmp_path = tmp.name
        try:
            cmd = [xv.exe, "-file", tmp_path, "-utf16"]
            if delay_ms_per_char:
                cmd += ["-delay", str(int(delay_ms_per_char))]
            _run(cmd)
        finally:
            try:
                os.unlink(tmp_path)
            except FileNotFoundError:
                pass
        return "xvkbd"

    kb = choose_keyboard_backend()
    if not kb:
        xv = choose_xvkbd_backend()
        if xv:
            return type_text(text, delay_ms_per_char=delay_ms_per_char, clearmodifiers=clearmodifiers, backend="xvkbd")
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11), 'wtype' (Wayland), or 'xvkbd' (X11 fallback).")

    if kb.name == "xdotool":
        cmd = [kb.exe, "type"]
        if clearmodifiers:
            cmd.append("--clearmodifiers")
        if delay_ms_per_char:
            cmd += ["--delay", str(int(delay_ms_per_char))]
        cmd.append(text)
        _run(cmd)
        return "xdotool"

    if kb.name == "wtype":
        cmd = [kb.exe]
        if delay_ms_per_char:
            cmd += ["-d", str(int(delay_ms_per_char))]
        cmd.append("-")
        _run(cmd, stdin=text)
        return "wtype"

    # ydotool
    cmd = [kb.exe, "type", text]
    _run(cmd)
    return "ydotool"



def mouse_move(*, x: int | None = None, y: int | None = None, dx: int | None = None, dy: int | None = None, relative: bool = False) -> None:
    backend = choose_pointer_backend()
    if not backend:
        raise RuntimeError("No pointer backend found. Install 'xdotool' (X11) or 'ydotool' (Wayland).")

    if backend.name == "xdotool":
        if relative:
            if dx is None or dy is None:
                raise ValueError("MouseMove relative requires dx and dy")
            cmd = [backend.exe, "mousemove_relative", "--", str(int(dx)), str(int(dy))]
        else:
            if x is None or y is None:
                raise ValueError("MouseMove absolute requires x and y")
            cmd = [backend.exe, "mousemove", str(int(x)), str(int(y))]
        _run(cmd)
        return

    # ydotool
    if relative:
        if dx is None or dy is None:
            raise ValueError("MouseMove relative requires dx and dy")
        cmd = [backend.exe, "mousemove", str(int(dx)), str(int(dy))]
    else:
        if x is None or y is None:
            raise ValueError("MouseMove absolute requires x and y")
        cmd = [backend.exe, "mousemove", "--absolute", str(int(x)), str(int(y))]
    _run(cmd)



def mouse_click(button: int = 1, *, down: bool = False, up: bool = False, clearmodifiers: bool = False) -> None:
    backend = choose_pointer_backend()
    if not backend:
        raise RuntimeError("No pointer backend found. Install 'xdotool' (X11) or 'ydotool' (Wayland).")

    if down and up:
        raise ValueError("MouseClick: choose at most one of down/up")

    if backend.name == "xdotool":
        if down:
            cmd = [backend.exe, "mousedown"]
        elif up:
            cmd = [backend.exe, "mouseup"]
        else:
            cmd = [backend.exe, "click"]

        if clearmodifiers and cmd[-1] == "click":
            cmd.append("--clearmodifiers")

        cmd.append(str(int(button)))
        _run(cmd)
        return

    if down or up:
        raise RuntimeError("ydotool backend currently supports click-only (no down/up).")

    # ydotool uses button codes (0xC0 left, 0xC1 right, 0xC2 middle).
    code_map = {1: "0xC0", 2: "0xC2", 3: "0xC1"}
    if int(button) not in code_map:
        raise ValueError("ydotool click supports buttons 1(left),2(middle),3(right) in this MVP")
    cmd = [backend.exe, "click", code_map[int(button)]]
    _run(cmd)



def mouse_wheel(clicks: int = 1, *, axis: str = "vertical") -> None:
    backend = choose_pointer_backend()
    if not backend:
        raise RuntimeError("No pointer backend found. Install 'xdotool' (X11) or 'ydotool' (Wayland).")

    n = int(clicks)
    if n == 0:
        return
    axis_norm = axis.lower()
    if axis_norm not in {"vertical", "horizontal"}:
        raise ValueError("MouseWheel axis must be 'vertical' or 'horizontal'")

    if backend.name != "xdotool":
        raise RuntimeError("Mouse wheel is currently supported via xdotool only in this MVP.")

    if axis_norm == "vertical":
        button = 4 if n > 0 else 5
    else:
        button = 7 if n > 0 else 6

    cmd = [backend.exe, "click", "--repeat", str(abs(n)), str(button)]
    _run(cmd)



def paste(*, selection: str = "clipboard", shortcut: PasteShortcut = "auto", clearmodifiers: bool = False) -> None:
    """Paste using a chosen shortcut.

    ``auto`` defaults to Ctrl+V for the clipboard selection and Shift+Insert for
    PRIMARY, which mirrors the current VHK behavior while still allowing the
    terminal-friendly Ctrl+Shift+V override.
    """

    sel = str(selection).strip().lower()
    mode = str(shortcut).strip().lower()
    if mode == "auto":
        mode = "ctrl+v" if sel == "clipboard" else "shift+insert"

    if mode == "ctrl+v":
        key("ctrl+v", clearmodifiers=clearmodifiers)
        return
    if mode == "ctrl+shift+v":
        key("ctrl+shift+v", clearmodifiers=clearmodifiers)
        return
    if mode == "shift+insert":
        key("shift+Insert", clearmodifiers=clearmodifiers)
        return
    raise ValueError(f"Unknown paste shortcut: {shortcut}")
