from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from vhk.core.models import Region
from vhk.system.session import detect_backend


@dataclass
class ScreenshotBackend:
    name: str
    exe: str
    converter_exe: str | None = None


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        if fp.exists() and os.access(fp, os.X_OK):
            return str(fp)
    return None


def choose_backend() -> ScreenshotBackend | None:
    """Pick a screenshot backend.

    Preference order:
    - grim (Wayland)
    - maim (fast, region-friendly)
    - scrot (scriptable X11 fallback)
    - import (ImageMagick)
    - xwd + ImageMagick convert/magick pipeline
    """

    if detect_backend() == "wayland":
        grim = _which("grim")
        if grim:
            return ScreenshotBackend(name="grim", exe=grim)
        return None

    maim = _which("maim")
    if maim:
        return ScreenshotBackend(name="maim", exe=maim)

    scrot = _which("scrot")
    if scrot:
        return ScreenshotBackend(name="scrot", exe=scrot)

    imp = _which("import")
    if imp:
        return ScreenshotBackend(name="import", exe=imp)

    xwd = _which("xwd")
    converter = _which("magick") or _which("convert")
    if xwd and converter:
        return ScreenshotBackend(name="xwd+convert", exe=xwd, converter_exe=converter)

    return None


def _png32_path(path: Path) -> str:
    if path.suffix.lower() == ".png":
        return f"PNG32:{path}"
    return str(path)


def capture(path: Path, region: Optional[Region] = None) -> Path:
    """Capture a screenshot.

    Parameters
    ----------
    path:
        Output path. Parent directories are created.
    region:
        Optional capture rectangle.

    Returns
    -------
    Path to the written file.
    """

    backend = choose_backend()
    if not backend:
        raise RuntimeError(
            "No screenshot backend found. Install 'grim' (Wayland), 'maim'/'scrot' (X11), ImageMagick 'import', or 'xwd' + ImageMagick."
        )

    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    if backend.name == "grim":
        # grim expects geometry like: "<x>,<y> <width>x<height>"
        cmd = [backend.exe]
        if region:
            cmd += ["-g", f"{region.x},{region.y} {region.w}x{region.h}"]
        cmd += [str(path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Screenshot failed via {backend.name}: {proc.stderr.strip()}")
    elif backend.name == "maim":
        # Geometry: WxH+X+Y
        cmd = [backend.exe]
        if region:
            cmd += ["-g", f"{region.w}x{region.h}+{region.x}+{region.y}"]
        cmd += [str(path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Screenshot failed via {backend.name}: {proc.stderr.strip()}")
    elif backend.name == "scrot":
        cmd = [backend.exe, "-z", "-F", str(path)]
        if region:
            cmd[1:1] = ["-a", f"{region.x},{region.y},{region.w},{region.h}"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Screenshot failed via {backend.name}: {proc.stderr.strip()}")
    elif backend.name == "import":
        # ImageMagick `import` can do whole-screen (-window root) and crop.
        # Use PNG32 when writing PNGs so transparent areas don't turn black.
        cmd = [backend.exe, "-window", "root"]
        if region:
            cmd += ["-crop", f"{region.w}x{region.h}+{region.x}+{region.y}"]
        cmd += [_png32_path(path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Screenshot failed via {backend.name}: {proc.stderr.strip()}")
    else:
        # xwd whole-screen dump piped into ImageMagick for PNG output.
        xwd_cmd = [backend.exe, "-root", "-silent"]
        conv = backend.converter_exe or "convert"
        convert_cmd = [conv, "xwd:-"]
        if region:
            convert_cmd += ["-crop", f"{region.w}x{region.h}+{region.x}+{region.y}", "+repage"]
        convert_cmd += [_png32_path(path)]

        xwd_proc = subprocess.Popen(xwd_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        conv_proc = subprocess.run(convert_cmd, stdin=xwd_proc.stdout, capture_output=True)
        if xwd_proc.stdout:
            xwd_proc.stdout.close()
        xwd_stderr = xwd_proc.stderr.read().decode(errors="replace").strip() if xwd_proc.stderr else ""
        xwd_rc = xwd_proc.wait()
        if xwd_rc != 0:
            raise RuntimeError(f"Screenshot failed via xwd: {xwd_stderr}")
        if conv_proc.returncode != 0:
            stderr = conv_proc.stderr.decode(errors="replace").strip() if isinstance(conv_proc.stderr, bytes) else str(conv_proc.stderr).strip()
            raise RuntimeError(f"Screenshot failed via xwd+convert: {stderr}")

    if not path.exists():
        raise RuntimeError(f"Screenshot tool reported success but file missing: {path}")

    return path
