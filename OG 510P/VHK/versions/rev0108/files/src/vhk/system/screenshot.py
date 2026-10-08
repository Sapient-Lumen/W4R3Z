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
    supports_geometry: bool = True


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


def choose_backend() -> ScreenshotBackend | None:
    """Pick a screenshot backend.

    Preference order:
    - grim (Wayland; wlroots)
    - (opt-in) portal (Wayland/X11; interactive; via VHK_SCREENSHOT_BACKEND=portal)
    - spectacle (Wayland/KDE; best-effort)
    - gnome-screenshot (Wayland/GNOME; best-effort)
    - maim (fast, region-friendly)
    - scrot (scriptable X11 fallback)
    - import (ImageMagick)
    - xwd + ImageMagick convert/magick pipeline
    """

    forced = os.environ.get("VHK_SCREENSHOT_BACKEND")
    if forced:
        forced = forced.strip().lower()
        # Allow explicit backend forcing without changing auto-detection.
        if forced == "portal":
            gdbus = _which("gdbus")
            if gdbus:
                return ScreenshotBackend(name="portal", exe=gdbus, supports_geometry=False)
            return None
        if forced in {"grim", "spectacle", "gnome-screenshot", "maim", "scrot", "import"}:
            exe = _which(forced)
            if exe:
                return ScreenshotBackend(
                    name=forced,
                    exe=exe,
                    supports_geometry=(forced in {"grim", "maim", "scrot", "import"}),
                )
            return None
        if forced in {"xwd+convert", "xwd"}:
            xwd = _which("xwd")
            converter = _which("magick") or _which("convert")
            if xwd and converter:
                return ScreenshotBackend(name="xwd+convert", exe=xwd, converter_exe=converter, supports_geometry=True)
            return None

    if detect_backend() == "wayland":
        grim = _which("grim")
        if grim:
            return ScreenshotBackend(name="grim", exe=grim, supports_geometry=True)

        spectacle = _which("spectacle")
        if spectacle:
            # Spectacle supports background capture to a file.
            # Region capture exists, but is interactive, so we treat geometry
            # cropping as an internal fallback.
            return ScreenshotBackend(name="spectacle", exe=spectacle, supports_geometry=False)

        gnome_ss = _which("gnome-screenshot")
        if gnome_ss:
            # gnome-screenshot is not installed by default on some GNOME
            # releases, but when present it can capture to a file.
            return ScreenshotBackend(name="gnome-screenshot", exe=gnome_ss, supports_geometry=False)

        return None

    maim = _which("maim")
    if maim:
        return ScreenshotBackend(name="maim", exe=maim, supports_geometry=True)

    scrot = _which("scrot")
    if scrot:
        return ScreenshotBackend(name="scrot", exe=scrot, supports_geometry=True)

    imp = _which("import")
    if imp:
        return ScreenshotBackend(name="import", exe=imp, supports_geometry=True)

    xwd = _which("xwd")
    converter = _which("magick") or _which("convert")
    if xwd and converter:
        return ScreenshotBackend(name="xwd+convert", exe=xwd, converter_exe=converter, supports_geometry=True)

    return None


def _png32_path(path: Path) -> str:
    if path.suffix.lower() == ".png":
        return f"PNG32:{path}"
    return str(path)


def _grim_scale_args() -> list[str]:
    """Return grim `-s` arguments for consistent capture scaling.

    grim captures in *layout coordinates* when you pass `-g`, but its output
    image can be scaled by an output scale factor. By default grim uses the
    highest output scale, which can cause captured image pixels to not match
    the coordinate space expected by input backends.

    VHK defaults to `-s 1` to keep screenshot pixels aligned with layout
    coordinates (and therefore the coordinate space used by most Wayland input
    helpers). Override with:

    - `VHK_GRIM_SCALE=auto` to omit `-s` and use grim defaults
    - `VHK_GRIM_SCALE=<float>` to force a specific scale factor
    """

    raw = os.environ.get("VHK_GRIM_SCALE")
    if raw is None or raw.strip() == "":
        raw = "1"
    v = raw.strip().lower()
    if v in {"auto", "default", "max"}:
        return []
    try:
        f = float(v)
    except Exception:
        return []
    if f <= 0:
        return []
    # Preserve the user's formatting where possible (grim accepts real numbers).
    return ["-s", raw.strip()]


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
        forced = os.environ.get("VHK_SCREENSHOT_BACKEND")
        if forced:
            raise RuntimeError(
                f"Forced screenshot backend '{forced}' was not available. "
                "Ensure the corresponding tool is installed and on PATH."
            )
        raise RuntimeError(
            "No screenshot backend found. Install 'grim' (Wayland), 'maim'/'scrot' (X11), ImageMagick 'import', or 'xwd' + ImageMagick."
        )

    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    if backend.name == "grim":
        # grim expects geometry like: "<x>,<y> <width>x<height>"
        # By default grim scales the output image to the highest output scale.
        # We default to `-s 1` for coordinate-consistent automation.
        cmd = [backend.exe, *_grim_scale_args()]
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
        if backend.name == "portal":
            # Portal screenshots are typically interactive and return a URI.
            # We copy the portal output into the requested path.
            import tempfile

            from PIL import Image

            from vhk.system.portal import save_portal_screenshot

            full_path = path
            tmp_path: Path | None = None
            if region is not None:
                fd, tmp_name = tempfile.mkstemp(prefix="vhk_portal_fullshot_", suffix=path.suffix or ".png")
                os.close(fd)
                tmp_path = Path(tmp_name)
                full_path = tmp_path

            save_portal_screenshot(full_path)

            if region is not None:
                try:
                    with Image.open(full_path) as im:
                        crop = im.crop((region.x, region.y, region.x + region.w, region.y + region.h))
                        crop.save(path)
                finally:
                    if tmp_path and tmp_path.exists():
                        tmp_path.unlink(missing_ok=True)
        elif backend.name in {"spectacle", "gnome-screenshot"}:
            # These backends do not accept a geometry rectangle directly.
            # We capture full-screen, then crop with Pillow when a region is
            # requested.
            import tempfile

            from PIL import Image

            full_path = path
            tmp_path: Path | None = None
            if region is not None:
                fd, tmp_name = tempfile.mkstemp(prefix="vhk_fullshot_", suffix=path.suffix or ".png")
                os.close(fd)
                tmp_path = Path(tmp_name)
                full_path = tmp_path

            if backend.name == "spectacle":
                # background mode, no notify, save to path
                cmd = [backend.exe, "--background", "--nonotify", "--fullscreen", "--output", str(full_path)]
            else:
                # gnome-screenshot -f writes to a file
                cmd = [backend.exe, "-f", str(full_path)]

            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(f"Screenshot failed via {backend.name}: {proc.stderr.strip()}")

            if region is not None:
                try:
                    with Image.open(full_path) as im:
                        crop = im.crop((region.x, region.y, region.x + region.w, region.y + region.h))
                        crop.save(path)
                finally:
                    if tmp_path and tmp_path.exists():
                        tmp_path.unlink(missing_ok=True)
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


def capture_interactive_region(path: Path) -> Path:
    """Capture a screenshot of a user-selected region.

    This is intended for CLI tooling (capture-needle / capture-baseline) where
    an interactive selection UX is acceptable.

    Backends (best-effort):
    - Wayland/KDE: spectacle --background --region --output <file>
    - Wayland/GNOME: gnome-screenshot --area -f <file>
    - X11: scrot --select --file <file>
    """

    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    def _run(cmd: list[str]) -> None:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip() or "selection cancelled")

    if detect_backend() == "wayland":
        spectacle = _which("spectacle")
        if spectacle:
            _run([spectacle, "--background", "--nonotify", "--region", "--output", str(path)])
            if path.exists():
                return path
            raise RuntimeError("spectacle reported success but output file missing")

        gnome_ss = _which("gnome-screenshot")
        if gnome_ss:
            _run([gnome_ss, "--area", "-f", str(path)])
            if path.exists():
                return path
            raise RuntimeError("gnome-screenshot reported success but output file missing")

        raise RuntimeError("No interactive region capture backend found on Wayland (try 'spectacle' or 'gnome-screenshot').")

    scrot = _which("scrot")
    if scrot:
        # Debian's scrot uses '-s/--select' for interactive selection.
        _run([scrot, "--select", "--overwrite", "--silent", "--file", str(path)])
        if path.exists():
            return path
        raise RuntimeError("scrot reported success but output file missing")

    raise RuntimeError("No interactive region capture backend found (install 'scrot' on X11).")
