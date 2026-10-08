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
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


def choose_keyboard_backend() -> InputBackend | None:
    """Choose a keyboard backend."""

    forced = _forced_backend("VHK_KEYBOARD_BACKEND") or _forced_backend("VHK_INPUT_BACKEND")
    if forced:
        exe = _choose_exe(forced)
        if exe:
            return InputBackend(name=forced, exe=exe)
        return None

    if detect_backend() == "wayland":
        # GNOME/Mutter commonly does not expose the virtual-keyboard protocol
        # required by wtype. Prefer uinput-based helpers there unless the user
        # explicitly forces wtype.
        if _is_gnome_like_session():
            dc = _which("dotoolc")
            if dc:
                return InputBackend(name="dotoolc", exe=dc)
            dt = _which("dotool")
            if dt:
                return InputBackend(name="dotool", exe=dt)
            yd = _which("ydotool")
            if yd:
                return InputBackend(name="ydotool", exe=yd)
            wt = _which("wtype")
            if wt:
                return InputBackend(name="wtype", exe=wt)
            return None

        wt = _which("wtype")
        if wt:
            return InputBackend(name="wtype", exe=wt)
        dc = _which("dotoolc")
        if dc:
            return InputBackend(name="dotoolc", exe=dc)
        dt = _which("dotool")
        if dt:
            return InputBackend(name="dotool", exe=dt)
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

    forced = _forced_backend("VHK_POINTER_BACKEND") or _forced_backend("VHK_INPUT_BACKEND")
    if forced:
        exe = _choose_exe(forced)
        if exe:
            return InputBackend(name=forced, exe=exe)
        return None

    if detect_backend() == "wayland":
        dc = _which("dotoolc")
        if dc:
            return InputBackend(name="dotoolc", exe=dc)
        dt = _which("dotool")
        if dt:
            return InputBackend(name="dotool", exe=dt)
        # ydotool supports both keyboard and pointer injection via uinput, but
        # its absolute mousemove is known to be flaky across setups.
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


def _run(
    cmd: list[str],
    *,
    stdin: str | bytes | None = None,
    text: bool = True,
    env: dict[str, str] | None = None,
) -> None:
    kwargs = {"capture_output": True, "text": text, "input": stdin}
    if env is not None:
        kwargs["env"] = env
    proc = subprocess.run(cmd, **kwargs)
    if proc.returncode != 0:
        stderr = proc.stderr.strip() if isinstance(proc.stderr, str) else (proc.stderr.decode(errors="replace").strip() if proc.stderr else "")
        raise RuntimeError(f"Input command failed: {' '.join(cmd)}\n{stderr}")


def _is_gnome_like_session() -> bool:
    """Heuristic: detect GNOME/Mutter-like sessions.

    wtype relies on the zwp_virtual_keyboard_v1 protocol, which GNOME/Mutter
    typically does not expose. Rather than selecting wtype and failing at
    runtime, prefer uinput helpers (dotool/ydotool) by default.
    """

    cd = (os.environ.get("XDG_CURRENT_DESKTOP") or "").strip().lower()
    ds = (os.environ.get("DESKTOP_SESSION") or "").strip().lower()
    if "gnome" in cd or "ubuntu:gnome" in cd:
        return True
    if "gnome" in ds:
        return True
    if os.environ.get("GNOME_DESKTOP_SESSION_ID"):
        return True
    return False


# --- backend overrides + socket helpers -------------------------------------

# Users sometimes need to force a specific toolchain in mixed/XWayland sessions
# or on desktops like GNOME/Mutter where some protocols are not exposed.
#
# Supported values (case-insensitive):
# - VHK_INPUT_BACKEND: affects both keyboard + pointer
# - VHK_KEYBOARD_BACKEND: keyboard override
# - VHK_POINTER_BACKEND: pointer override
#
# Values: auto | xdotool | wtype | ydotool | dotool | dotoolc | xvkbd


def _forced_backend(env_var: str) -> str | None:
    v = (os.environ.get(env_var) or "").strip().lower()
    if not v or v == "auto":
        return None
    return v


def _choose_exe(name: str) -> str | None:
    # Backend names are also executable names for our supported tools.
    if name == "dotoolc":
        return _which("dotoolc")
    if name == "dotool":
        return _which("dotool")
    if name == "ydotool":
        return _which("ydotool")
    if name == "wtype":
        return _which("wtype")
    if name == "xdotool":
        return _which("xdotool")
    if name == "xvkbd":
        return _which("xvkbd")
    return None


def choose_ydotool_socket(env: dict[str, str] | None = None) -> str | None:
    """Best-effort choice of YDOTOOL_SOCKET.

    Packaging conventions differ: some setups run ydotoold as root with a
    /tmp socket, while others run it as a user service under XDG_RUNTIME_DIR.

    VHK keeps this logic in one place so users don't need to memorize distro-
    specific defaults.
    """

    env_map = os.environ if env is None else env
    forced = (env_map.get("YDOTOOL_SOCKET") or "").strip()
    if forced:
        return forced

    xdg_runtime = (env_map.get("XDG_RUNTIME_DIR") or "").strip()
    if not xdg_runtime:
        try:
            xdg_runtime = f"/run/user/{os.getuid()}"
        except Exception:
            xdg_runtime = ""

    candidates: list[str] = []
    if xdg_runtime:
        candidates.append(str(Path(xdg_runtime) / ".ydotool_socket"))
    candidates.append("/tmp/.ydotool_socket")

    for c in candidates:
        p = Path(c)
        try:
            if p.exists():
                return str(p)
        except Exception:
            continue
    return None


def _ydotool_env() -> dict[str, str] | None:
    sock = choose_ydotool_socket()
    if not sock:
        return None
    env = dict(os.environ)
    env["YDOTOOL_SOCKET"] = sock
    return env


def _ydotool_pixel_scale(env_map: dict[str, str] | None = None) -> float:
    """Scale factor applied to ydotool cursor deltas/coordinates.

    Some ydotool setups report mismatched coordinate scaling (for example, a
    "half-resolution" effect where 10px becomes 20px, or vice versa). Keeping
    this as a knob makes projects portable while still allowing a single env
    tweak per machine.

    Environment
    -----------
    VHK_YDOTOOL_PIXEL_SCALE
        A float. Use 0.5 when the cursor moves twice as far, 2.0 when it moves
        half as far.
    """

    m = os.environ if env_map is None else env_map
    raw = (m.get("VHK_YDOTOOL_PIXEL_SCALE") or "").strip()
    if not raw:
        return 1.0
    try:
        v = float(raw)
    except Exception:
        return 1.0
    if v == 0:
        return 1.0
    return float(v)


def _ydotool_absolute_method(env_map: dict[str, str] | None = None) -> str:
    """Return the ydotool absolute-move strategy.

    ydotool's `mousemove --absolute X Y` is reported broken on some systems.
    VHK defaults to a conservative workaround that still supports multi-monitor
    layouts: reset to (0,0) with an absolute move, then move relatively.

    Environment
    -----------
    VHK_YDOTOOL_ABSOLUTE_METHOD
        - "reset_relative" (default): `--absolute 0 0` then relative move.
        - "native": use `mousemove --absolute X Y` directly.
        - "cursor_relative": compute delta from a cursor-pos backend and use
          a relative move (best-effort; falls back to reset_relative).
    """

    m = os.environ if env_map is None else env_map
    raw = (m.get("VHK_YDOTOOL_ABSOLUTE_METHOD") or "").strip().lower()
    if not raw:
        return "reset_relative"
    raw = raw.replace("+", "_").replace("-", "_").replace(" ", "_")
    if raw in {"native", "direct"}:
        return "native"
    if raw in {"cursor_relative", "cursor", "delta"}:
        return "cursor_relative"
    if raw in {"reset_relative", "reset", "workaround", "resetrel"}:
        return "reset_relative"
    return "reset_relative"


def _dotool_send(cmdline: str, *, use_client: bool = False) -> None:
    """Send a dotool command line to dotool/dotoolc."""

    exe = _which("dotoolc") if use_client else _which("dotool")
    if not exe:
        raise RuntimeError("dotool backend requested but dotool/dotoolc was not found in PATH")
    _run([exe], stdin=(cmdline.rstrip("\n") + "\n"))


def _dotool_button_name(button: int) -> str:
    m = {1: "left", 2: "middle", 3: "right"}
    if int(button) not in m:
        raise ValueError("dotool supports buttons 1(left),2(middle),3(right)")
    return m[int(button)]


_DOTOOL_KEY_SYNONYMS: dict[str, str] = {
    # X11-ish keysyms -> dotool-friendly tokens
    "shiftl": "shift",
    "shiftr": "shift",
    "controll": "ctrl",
    "controlr": "ctrl",
    "altl": "alt",
    "altr": "alt",
    "superl": "super",
    "superr": "super",
    "metal": "super",
    "metar": "super",
    "return": "enter",
    "escape": "esc",
}


def _dotool_key_name(key_name: str) -> str:
    n = _normalize_key_name(key_name)
    return _DOTOOL_KEY_SYNONYMS.get(n, key_name)


def _dotool_script_for_type(text: str) -> str:
    """Build a dotool script that types arbitrary text.

    dotool's `type` command consumes the remainder of a line, so newlines must
    be expressed explicitly.
    """

    lines = text.splitlines()
    parts: list[str] = []
    for i, line in enumerate(lines):
        parts.append(f"type {line}")
        if i != len(lines) - 1:
            parts.append("key enter")
    if text.endswith("\n"):
        parts.append("key enter")
    return "\n".join(parts) + "\n"


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


# --- ydotool keycode mapping -------------------------------------------------

# ydotool's `key` command expects Linux input-event-codes keycodes with
# explicit press/release state, e.g. "28:1 28:0" for Enter.
# See: /usr/include/linux/input-event-codes.h

_YDOTOOL_MOD_KEYCODES: dict[str, int] = {
    "ctrl": 29,  # KEY_LEFTCTRL
    "shift": 42,  # KEY_LEFTSHIFT
    "alt": 56,  # KEY_LEFTALT
    "logo": 125,  # KEY_LEFTMETA
}


def _build_evdev_keycodes() -> dict[str, int]:
    m: dict[str, int] = {
        "enter": 28,
        "return": 28,
        "tab": 15,
        "space": 57,
        "esc": 1,
        "escape": 1,
        "backspace": 14,
        "delete": 111,
        "insert": 110,
        "home": 102,
        "end": 107,
        "pageup": 104,
        "pagedown": 109,
        "up": 103,
        "down": 108,
        "left": 105,
        "right": 106,
        "minus": 12,
        "equal": 13,
        "comma": 51,
        "period": 52,
        "slash": 53,
        "semicolon": 39,
        "apostrophe": 40,
        "grave": 41,
        "bracketleft": 26,
        "bracketright": 27,
        "backslash": 43,
    }

    # Digits (US layout scancodes)
    for d, code in zip("1234567890", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
        m[d] = code

    # Letters (US layout scancodes)
    letter_codes = {
        "a": 30,
        "b": 48,
        "c": 46,
        "d": 32,
        "e": 18,
        "f": 33,
        "g": 34,
        "h": 35,
        "i": 23,
        "j": 36,
        "k": 37,
        "l": 38,
        "m": 50,
        "n": 49,
        "o": 24,
        "p": 25,
        "q": 16,
        "r": 19,
        "s": 31,
        "t": 20,
        "u": 22,
        "v": 47,
        "w": 17,
        "x": 45,
        "y": 21,
        "z": 44,
    }
    m.update(letter_codes)

    # Function keys (F1..F12)
    for i, code in enumerate(range(59, 71), start=1):
        m[f"f{i}"] = code

    return m


_EVDEV_KEYCODES = _build_evdev_keycodes()


def _normalize_key_name(name: str) -> str:
    s = name.strip()
    if s.startswith("<") and s.endswith(">"):
        s = s[1:-1]
    s = s.replace("_", "").replace("-", "")
    return s.lower()


def _ydotool_key_sequence(keys: str) -> list[str]:
    """Convert a VHK chord string (ctrl+alt+t) into ydotool keycode events."""

    mods, key_name = _parse_chord(keys)
    key_norm = _normalize_key_name(key_name)

    # De-dupe modifiers while preserving order.
    ordered_mods: list[str] = []
    for m in mods:
        if m not in ordered_mods:
            ordered_mods.append(m)

    # Map modifiers to keycodes.
    mod_codes: list[int] = []
    for m in ordered_mods:
        code = _YDOTOOL_MOD_KEYCODES.get(m)
        if code is not None:
            mod_codes.append(code)

    code = _EVDEV_KEYCODES.get(key_norm)
    if code is None and len(key_norm) == 1:
        code = _EVDEV_KEYCODES.get(key_norm)

    if code is None:
        raise RuntimeError(
            f"ydotool backend needs a Linux evdev keycode mapping for '{key_name}'. "
            "Use wtype/xdotool, or extend VHK's mapping (see /usr/include/linux/input-event-codes.h)."
        )

    seq: list[str] = []
    for mc in mod_codes:
        seq.append(f"{mc}:1")
    seq.append(f"{code}:1")
    seq.append(f"{code}:0")
    for mc in reversed(mod_codes):
        seq.append(f"{mc}:0")
    return seq


def _ydotool_keycode_for_name(key_name: str) -> int:
    """Best-effort evdev keycode lookup for a single key name.

    Used by KeyDown/KeyUp/ResetModifiers on the ydotool backend.

    Notes
    -----
    VHK intentionally ships a small pragmatic mapping for common keys so
    projects can be portable without requiring users to hand-author raw
    keycodes. For anything outside the mapping, users can:
    - use the `Key` step (chords) when possible
    - extend VHK's mapping (see /usr/include/linux/input-event-codes.h)
    """

    key_norm = _normalize_key_name(key_name)

    # Treat common modifier spellings as left-side modifiers.
    if "ctrl" in key_norm or "control" in key_norm:
        return _YDOTOOL_MOD_KEYCODES["ctrl"]
    if "shift" in key_norm:
        return _YDOTOOL_MOD_KEYCODES["shift"]
    if "alt" in key_norm or "mod1" in key_norm:
        return _YDOTOOL_MOD_KEYCODES["alt"]
    if "meta" in key_norm or "super" in key_norm or "logo" in key_norm or "mod4" in key_norm:
        return _YDOTOOL_MOD_KEYCODES["logo"]

    code = _EVDEV_KEYCODES.get(key_norm)
    if code is None and len(key_norm) == 1:
        code = _EVDEV_KEYCODES.get(key_norm)
    if code is None:
        raise RuntimeError(
            f"ydotool backend needs a Linux evdev keycode mapping for '{key_name}'. "
            "Use wtype/xdotool, or extend VHK's mapping (see /usr/include/linux/input-event-codes.h)."
        )
    return int(code)


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
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype'/'dotool'/'ydotool' (Wayland).")

    if backend.name == "xdotool":
        cmd = [backend.exe, "key"]
        if clearmodifiers:
            cmd.append("--clearmodifiers")
        cmd.append(keys)
        _run(cmd)
        return

    if backend.name in {"dotool", "dotoolc"}:
        _dotool_send(f"key {keys}", use_client=(backend.name == "dotoolc"))
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
        try:
            _run(cmd)
        except RuntimeError as exc:
            # Common Wayland footgun: some compositors (notably GNOME/Mutter)
            # do not support the virtual keyboard protocol required by wtype.
            # When ydotool is present, fall back to it for key injection.
            msg = str(exc)
            if "virtual keyboard protocol" in msg.lower():
                dc = _which("dotoolc")
                if dc:
                    _run([dc], stdin=f"key {keys}\n")
                    return
                dt = _which("dotool")
                if dt:
                    _run([dt], stdin=f"key {keys}\n")
                    return
                yd = _which("ydotool")
                if yd:
                    _run([yd, "key", *_ydotool_key_sequence(keys)], env=_ydotool_env())
                    return
            raise
        return

    # (dotool handled above)


    # ydotool: keycodes + press/release states.
    cmd = [backend.exe, "key", *_ydotool_key_sequence(keys)]
    _run(cmd, env=_ydotool_env())



def key_down(key_name: str, *, clearmodifiers: bool = False) -> None:
    backend = choose_keyboard_backend()
    if not backend:
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype'/'dotool'/'ydotool' (Wayland).")

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
        try:
            _run(cmd)
        except RuntimeError as exc:
            msg = str(exc)
            if "virtual keyboard protocol" in msg.lower():
                yd = _which("ydotool")
                if yd:
                    code = _ydotool_keycode_for_name(key_name)
                    _run([yd, "key", f"{code}:1"], env=_ydotool_env())
                    return
            raise
        return

    if backend.name in {"dotool", "dotoolc"}:
        _dotool_send(f"keydown {_dotool_key_name(key_name)}", use_client=(backend.name == "dotoolc"))
        return

    # ydotool
    code = _ydotool_keycode_for_name(key_name)
    _run([backend.exe, "key", f"{code}:1"], env=_ydotool_env())



def key_up(key_name: str, *, clearmodifiers: bool = False) -> None:
    backend = choose_keyboard_backend()
    if not backend:
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype'/'dotool'/'ydotool' (Wayland).")

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
        try:
            _run(cmd)
        except RuntimeError as exc:
            msg = str(exc)
            if "virtual keyboard protocol" in msg.lower():
                yd = _which("ydotool")
                if yd:
                    code = _ydotool_keycode_for_name(key_name)
                    _run([yd, "key", f"{code}:0"], env=_ydotool_env())
                    return
            raise
        return

    if backend.name in {"dotool", "dotoolc"}:
        _dotool_send(f"keyup {_dotool_key_name(key_name)}", use_client=(backend.name == "dotoolc"))
        return

    # ydotool
    code = _ydotool_keycode_for_name(key_name)
    _run([backend.exe, "key", f"{code}:0"], env=_ydotool_env())





def reset_modifiers() -> None:
    """Best-effort explicit release of common modifiers.

    This is intentionally separate from xdotool's --clearmodifiers behavior.
    It is useful after hotkey-triggered automation when the author wants to
    deliberately release modifier state before the next action.
    """

    backend = choose_keyboard_backend()
    if not backend:
        raise RuntimeError("No keyboard backend found. Install 'xdotool' (X11) or 'wtype'/'dotool'/'ydotool' (Wayland).")

    modifiers = ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Super_L", "Super_R"]

    if backend.name == "xdotool":
        for key_name in modifiers:
            _run([backend.exe, "keyup", key_name])
        return

    if backend.name == "wtype":
        for name in ["shift", "ctrl", "alt", "logo"]:
            _run([backend.exe, "-m", name])
        return

    if backend.name in {"dotool", "dotoolc"}:
        # dotool uses key names rather than evdev numeric keycodes.
        for name in ["shift", "ctrl", "alt", "super"]:
            _dotool_send(f"keyup {name}", use_client=(backend.name == "dotoolc"))
        return

    # ydotool: release common modifiers (best-effort).
    seq = []
    for name in ["shift", "ctrl", "alt", "logo"]:
        code = _YDOTOOL_MOD_KEYCODES[name]
        seq.append(f"{code}:0")
    _run([backend.exe, "key", *seq], env=_ydotool_env())
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
        try:
            _run(cmd, stdin=text)
            return "wtype"
        except RuntimeError as exc:
            msg = str(exc)
            if "virtual keyboard protocol" in msg.lower():
                dc = _which("dotoolc")
                if dc:
                    _run([dc], stdin=_dotool_script_for_type(text) if "\n" in text else f"type {text}\n")
                    return "dotoolc"
                dt = _which("dotool")
                if dt:
                    _run([dt], stdin=_dotool_script_for_type(text) if "\n" in text else f"type {text}\n")
                    return "dotool"
                yd = _which("ydotool")
                if yd:
                    _run([yd, "type", text], env=_ydotool_env())
                    return "ydotool"
            raise

    if kb.name in {"dotool", "dotoolc"}:
        script = _dotool_script_for_type(text) if "\n" in text else f"type {text}\n"
        if delay_ms_per_char:
            # dotool supports typedelay/ typehold. typedelay is good enough for
            # mimicking xdotool's --delay style behavior.
            script = f"typedelay {int(delay_ms_per_char)}\n" + script
            # When using the long-lived daemon client, restore to 0 so callers
            # don't accidentally inherit delay for later actions.
            if kb.name == "dotoolc":
                script = script + "typedelay 0\n"
        _run([kb.exe], stdin=script)
        return kb.name

    # ydotool
    cmd = [kb.exe, "type", text]
    _run(cmd, env=_ydotool_env())
    return "ydotool"



def mouse_move(*, x: int | None = None, y: int | None = None, dx: int | None = None, dy: int | None = None, relative: bool = False) -> None:
    # Hyprland exposes an in-compositor cursor mover via `hyprctl dispatch movecursor`.
    # This can be more ergonomic than ydotool for absolute movement because it
    # doesn't require ydotoold/uinput permissions. (Clicking still needs a
    # separate backend.)
    if detect_backend() == "wayland" and os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        hyprctl = _which("hyprctl")
        if hyprctl:
            if not relative:
                if x is None or y is None:
                    raise ValueError("MouseMove absolute requires x and y")
                _run([hyprctl, "dispatch", "movecursor", str(int(x)), str(int(y))])
                return

            # Relative movement: prefer ydotool when present (lower overhead).
            # When ydotool is unavailable, fall back to cursorpos+movecursor.
            if _which("ydotool") is None:
                if dx is None or dy is None:
                    raise ValueError("MouseMove relative requires dx and dy")
                from vhk.system import cursor_pos as cursor_pos_mod

                pos = cursor_pos_mod.get_cursor_pos()
                _run([hyprctl, "dispatch", "movecursor", str(int(pos.x + int(dx))), str(int(pos.y + int(dy)))])
                return

    backend = choose_pointer_backend()
    if not backend:
        raise RuntimeError("No pointer backend found. Install 'xdotool' (X11) or 'ydotool'/'dotool' (Wayland).")

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

    if backend.name in {"dotool", "dotoolc"}:
        # dotool supports:
        # - mousemove X Y (relative delta)
        # - mouseto X Y (normalized coordinates 0..1)
        if relative:
            if dx is None or dy is None:
                raise ValueError("MouseMove relative requires dx and dy")
            _dotool_send(f"mousemove {int(dx)} {int(dy)}", use_client=(backend.name == "dotoolc"))
            return

        if x is None or y is None:
            raise ValueError("MouseMove absolute requires x and y")
        from vhk.system.display import get_virtual_screen_size

        sz = get_virtual_screen_size()
        fx = 0.0 if sz.width <= 1 else float(x) / float(sz.width)
        fy = 0.0 if sz.height <= 1 else float(y) / float(sz.height)
        fx = max(0.0, min(1.0, fx))
        fy = max(0.0, min(1.0, fy))
        _dotool_send(f"mouseto {fx:.6f} {fy:.6f}", use_client=(backend.name == "dotoolc"))
        return

    # ydotool
    env = _ydotool_env()
    scale = _ydotool_pixel_scale()

    def _scaled_i(v: int) -> int:
        return int(round(float(v) * float(scale)))

    if relative:
        if dx is None or dy is None:
            raise ValueError("MouseMove relative requires dx and dy")
        cmd = [backend.exe, "mousemove", str(_scaled_i(int(dx))), str(_scaled_i(int(dy)))]
        _run(cmd, env=env)
        return

    if x is None or y is None:
        raise ValueError("MouseMove absolute requires x and y")

    method = _ydotool_absolute_method()
    if method == "native":
        cmd = [backend.exe, "mousemove", "--absolute", str(_scaled_i(int(x))), str(_scaled_i(int(y)))]
        _run(cmd, env=env)
        return

    if method == "cursor_relative":
        try:
            from vhk.system import cursor_pos as cursor_pos_mod

            pos = cursor_pos_mod.get_cursor_pos()
            cmd = [backend.exe, "mousemove", str(_scaled_i(int(x) - int(pos.x))), str(_scaled_i(int(y) - int(pos.y)))]
            _run(cmd, env=env)
            return
        except Exception:
            # Fall back to reset_relative.
            pass

    # reset_relative: move to the top-left via an absolute command, then move
    # relatively to the target coordinates. This mirrors common user-space
    # workarounds for broken absolute moves.
    _run([backend.exe, "mousemove", "--absolute", "0", "0"], env=env)
    _run([backend.exe, "mousemove", str(_scaled_i(int(x))), str(_scaled_i(int(y)))], env=env)
    return



def mouse_click(button: int = 1, *, down: bool = False, up: bool = False, clearmodifiers: bool = False) -> None:
    backend = choose_pointer_backend()
    if not backend:
        raise RuntimeError("No pointer backend found. Install 'xdotool' (X11) or 'ydotool'/'dotool' (Wayland).")

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

    if backend.name in {"dotool", "dotoolc"}:
        btn = _dotool_button_name(int(button))
        if down:
            _dotool_send(f"buttondown {btn}", use_client=(backend.name == "dotoolc"))
        elif up:
            _dotool_send(f"buttonup {btn}", use_client=(backend.name == "dotoolc"))
        else:
            _dotool_send(f"click {btn}", use_client=(backend.name == "dotoolc"))
        return

    # ydotool uses a compact click encoding:
    # - base 0x40 = press, 0x80 = release, 0xC0 = click (press+release)
    # - low bits encode button index (0=left, 1=right, 2=middle)
    idx_map = {1: 0, 2: 2, 3: 1}
    if int(button) not in idx_map:
        raise ValueError("ydotool click supports buttons 1(left),2(middle),3(right)")
    idx = idx_map[int(button)]
    if down:
        code = hex(0x40 | idx)
    elif up:
        code = hex(0x80 | idx)
    else:
        code = hex(0xC0 | idx)
    cmd = [backend.exe, "click", code]
    _run(cmd, env=_ydotool_env())



def mouse_wheel(clicks: int = 1, *, axis: str = "vertical") -> None:
    backend = choose_pointer_backend()
    if not backend:
        raise RuntimeError("No pointer backend found. Install 'xdotool' (X11) or 'ydotool'/'dotool' (Wayland).")

    n = int(clicks)
    if n == 0:
        return
    axis_norm = axis.lower()
    if axis_norm not in {"vertical", "horizontal"}:
        raise ValueError("MouseWheel axis must be 'vertical' or 'horizontal'")

    if backend.name in {"dotool", "dotoolc"}:
        cmd_name = "wheel" if axis_norm == "vertical" else "hwheel"
        _dotool_send(f"{cmd_name} {n}", use_client=(backend.name == "dotoolc"))
        return

    if backend.name != "xdotool":
        raise RuntimeError("Mouse wheel is supported via xdotool (X11) or dotool (Wayland); ydotool does not currently expose wheel events.")

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
