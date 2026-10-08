from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        if fp.exists() and os.access(fp, os.X_OK):
            return str(fp)
    return None


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"Command failed: {' '.join(cmd)}")


def open_target(target: str) -> None:
    """Open a file path or URL with the desktop's preferred application.

    Notes
    -----
    We intentionally use xdg-open as the Linux baseline because it delegates to
    the user's configured handlers for files and URLs.
    """

    exe = _which("xdg-open")
    if not exe:
        raise RuntimeError("Missing dependency: xdg-open")
    _run([exe, target])



def compose_email(
    to: list[str] | str,
    *,
    cc: list[str] | str | None = None,
    bcc: list[str] | str | None = None,
    subject: str | None = None,
    body: str | None = None,
    attachments: list[str] | str | None = None,
    utf8: bool = True,
) -> None:
    """Open the user's preferred mail composer with prefilled fields."""

    exe = _which("xdg-email")
    if not exe:
        raise RuntimeError("Missing dependency: xdg-email")

    def _as_list(v: list[str] | str | None) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return [str(x) for x in v]

    cmd = [exe]
    if utf8:
        cmd.append("--utf8")
    for addr in _as_list(cc):
        cmd += ["--cc", addr]
    for addr in _as_list(bcc):
        cmd += ["--bcc", addr]
    if subject is not None:
        cmd += ["--subject", subject]
    if body is not None:
        cmd += ["--body", body]
    for path in _as_list(attachments):
        cmd += ["--attach", path]
    cmd += _as_list(to)
    if len(cmd) <= 1:
        raise ValueError("ComposeEmail requires at least one recipient")
    _run(cmd)
