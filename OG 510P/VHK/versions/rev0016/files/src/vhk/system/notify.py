from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

Urgency = Literal["low", "normal", "critical"]


@dataclass
class NotifyBackend:
    name: str
    exe: str


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        if fp.exists() and os.access(fp, os.X_OK):
            return str(fp)
    return None


def choose_backend() -> NotifyBackend | None:
    # Prefer dunstify when available (more features), otherwise notify-send.
    dunstify = _which("dunstify")
    if dunstify:
        return NotifyBackend(name="dunstify", exe=dunstify)
    ns = _which("notify-send")
    if ns:
        return NotifyBackend(name="notify-send", exe=ns)
    return None


def send(summary: str, body: Optional[str] = None, urgency: Urgency = "normal") -> None:
    backend = choose_backend()
    if not backend:
        raise RuntimeError("No notification backend found. Install 'notify-send' (libnotify-bin) or 'dunstify'.")

    cmd = [backend.exe]
    # Both dunstify and notify-send support --urgency.
    cmd += ["--urgency", urgency]
    cmd += [summary]
    if body is not None:
        cmd += [body]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Notification failed via {backend.name}: {proc.stderr.strip()}")
