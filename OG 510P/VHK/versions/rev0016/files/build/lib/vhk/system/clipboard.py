from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from vhk.system.session import detect_backend

Selection = Literal["clipboard", "primary"]


@dataclass
class ClipboardBackend:
    name: str
    exe_copy: str
    exe_paste: str


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        if fp.exists() and os.access(fp, os.X_OK):
            return str(fp)
    return None


def choose_backend() -> ClipboardBackend | None:
    if detect_backend() == "wayland":
        wl_copy = _which("wl-copy")
        wl_paste = _which("wl-paste")
        if wl_copy and wl_paste:
            return ClipboardBackend(name="wl-clipboard", exe_copy=wl_copy, exe_paste=wl_paste)

    xclip = _which("xclip")
    if xclip:
        return ClipboardBackend(name="xclip", exe_copy=xclip, exe_paste=xclip)
    xsel = _which("xsel")
    if xsel:
        return ClipboardBackend(name="xsel", exe_copy=xsel, exe_paste=xsel)
    return None


def read(selection: Selection = "clipboard") -> str:
    backend = choose_backend()
    if not backend:
        raise RuntimeError("No clipboard tool found. Install 'wl-clipboard' (Wayland) or 'xclip'/'xsel' (X11).")

    if backend.name == "wl-clipboard":
        cmd = [backend.exe_paste]
        if selection == "primary":
            cmd.append("--primary")
    elif backend.name == "xclip":
        cmd = [backend.exe_paste, "-o", "-selection", selection]
    else:
        cmd = [backend.exe_paste, f"--{selection}", "--output"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Clipboard read failed via {backend.name}: {proc.stderr.strip()}")
    return proc.stdout


def write(text: str, selection: Selection = "clipboard") -> None:
    backend = choose_backend()
    if not backend:
        raise RuntimeError("No clipboard tool found. Install 'wl-clipboard' (Wayland) or 'xclip'/'xsel' (X11).")

    if backend.name == "wl-clipboard":
        cmd = [backend.exe_copy]
        if selection == "primary":
            cmd.append("--primary")
    elif backend.name == "xclip":
        cmd = [backend.exe_copy, "-i", "-selection", selection]
    else:
        cmd = [backend.exe_copy, f"--{selection}", "--input"]

    proc = subprocess.run(cmd, input=text, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Clipboard write failed via {backend.name}: {proc.stderr.strip()}")
