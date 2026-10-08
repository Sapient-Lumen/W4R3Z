from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from vhk.core.models import Region
from vhk.system.session import detect_backend


_GEOM_RE = re.compile(r"^(?P<w>\d+)x(?P<h>\d+)\+(?P<x>\d+)\+(?P<y>\d+)$")


def parse_geometry(geom: str) -> Region:
    """Parse 'WxH+X+Y' into a Region."""

    m = _GEOM_RE.match(geom.strip())
    if not m:
        raise ValueError(f"Invalid geometry: {geom!r}")
    return Region(
        x=int(m.group("x")),
        y=int(m.group("y")),
        w=int(m.group("w")),
        h=int(m.group("h")),
    )


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


def select_region() -> Region:
    """Ask the user to select a region on screen.

    Uses slop if installed.

    Returns
    -------
    Region

    Raises
    ------
    RuntimeError if slop is not installed or selection was cancelled.
    """

    if detect_backend() == "wayland":
        slurp = _which("slurp")
        if not slurp:
            raise RuntimeError("Region selection on Wayland requires 'slurp'.")

        # slurp default format: "%x,%y %wx%h".
        cmd = [slurp]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError("Region selection cancelled")

        geom = proc.stdout.strip()
        # Example: "10,20 300x400"
        m = re.match(r"^(?P<x>\d+),(?P<y>\d+)\s+(?P<w>\d+)x(?P<h>\d+)$", geom)
        if not m:
            raise RuntimeError(f"Unexpected slurp output: {geom!r}")
        return Region(x=int(m.group("x")), y=int(m.group("y")), w=int(m.group("w")), h=int(m.group("h")))

    slop = _which("slop")
    if not slop:
        raise RuntimeError("Region selection requires 'slop' (Select Operation).")

    # Output X Y W H (easy to parse, avoids eval).
    cmd = [slop, "-f", "%x %y %w %h"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("Region selection cancelled")

    parts = proc.stdout.strip().split()
    if len(parts) != 4:
        raise RuntimeError(f"Unexpected slop output: {proc.stdout!r}")

    x, y, w, h = (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
    return Region(x=x, y=y, w=w, h=h)
