from __future__ import annotations

"""Display geometry helpers.

Wayland does not provide a single, stable API for "what is the size of the
virtual desktop?". For automation tools, this matters when an input backend
expects normalized coordinates (e.g. dotool's `mouseto` uses 0..1 percentages).

VHK therefore provides a best-effort probe that prefers compositor-native
introspection when available and falls back to X11 tooling when applicable.
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from vhk.system.session import detect_backend


@dataclass(frozen=True)
class ScreenSize:
    width: int
    height: int
    backend: str


_CACHED: ScreenSize | None = None


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


def _clamp_int(v: int) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def _bbox_rects(rects: list[tuple[int, int, int, int]]) -> tuple[int, int] | None:
    '''Return bounding-box width/height for a list of (x,y,w,h) rects.

    Unlike a naive max(x+w), this handles negative coordinates by computing a
    union bounding box (max - min).
    '''

    if not rects:
        return None
    min_x = min(x for x, y, w, h in rects)
    min_y = min(y for x, y, w, h in rects)
    max_x = max(x + w for x, y, w, h in rects)
    max_y = max(y + h for x, y, w, h in rects)
    w = max_x - min_x
    h = max_y - min_y
    if w <= 0 or h <= 0:
        return None
    return w, h


def _probe_hyprland() -> ScreenSize | None:
    if not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return None
    hyprctl = _which("hyprctl")
    if not hyprctl:
        return None
    for cmd in ([hyprctl, "-j", "monitors"], [hyprctl, "monitors", "-j"]):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            continue
        try:
            data = json.loads(proc.stdout or "[]")
        except Exception:
            continue
        rects: list[tuple[int, int, int, int]] = []
        for m in data if isinstance(data, list) else []:
            try:
                x = _clamp_int(m.get("x") or (m.get("at") or [0, 0])[0])
                y = _clamp_int(m.get("y") or (m.get("at") or [0, 0])[1])
                w = _clamp_int(m.get("width") or (m.get("size") or [0, 0])[0])
                h = _clamp_int(m.get("height") or (m.get("size") or [0, 0])[1])
                if w > 0 and h > 0:
                    rects.append((x, y, w, h))
            except Exception:
                continue
        bbox = _bbox_rects(rects)
        if bbox:
            w, h = bbox
            return ScreenSize(width=w, height=h, backend="hyprctl")
    return None


def _probe_i3_sway_ipc() -> ScreenSize | None:
    # Prefer our pure-Python IPC when sway/i3 sockets are present.
    try:
        from vhk.i3.ipc import I3Connection

        conn = I3Connection()
        outs = conn.get_outputs()
        rects: list[tuple[int, int, int, int]] = []
        for o in outs if isinstance(outs, list) else []:
            if isinstance(o, dict) and o.get("active") is True and isinstance(o.get("rect"), dict):
                r = o["rect"]
                rects.append((_clamp_int(r.get("x")), _clamp_int(r.get("y")), _clamp_int(r.get("width")), _clamp_int(r.get("height"))))
        bbox = _bbox_rects(rects)
        if bbox:
            w, h = bbox
            return ScreenSize(width=w, height=h, backend="i3-ipc")
    except Exception:
        return None
    return None


def _gnome_layout_mode_is_logical(layout_mode: int | None) -> bool:
    """Heuristic: does Mutter expose logical or physical coordinate layout?

    Mutter's DisplayConfig docs have historically had some ambiguity around the
    numeric values for layout-mode. In practice, we treat:
      - 2 as logical (mode dimensions divided by logical monitor scale)
      - >2 as logical (future extensions / x11-fractional-scaling paths)
      - 1 as physical

    This matches the doc comment that distinguishes physical vs logical layout
    in GetCurrentState.
    """

    if layout_mode is None:
        return True
    if layout_mode == 1:
        return False
    return True


def parse_gnome_displayconfig_getcurrentstate(text: str) -> ScreenSize | None:
    """Parse `gdbus call ... GetCurrentState` output and derive virtual size.

    Returns ``None`` when the input cannot be parsed.

    This parser is used as an optional Wayland fallback when Hyprland and
    sway/i3 IPC probes are unavailable.
    """

    try:
        from vhk.system.gvariant import gdbus_call_output_to_python

        parsed = gdbus_call_output_to_python(text)
    except Exception:
        return None

    if not isinstance(parsed, tuple) or len(parsed) < 4:
        return None

    _, monitors, logical_monitors, props = parsed[:4]
    if not isinstance(monitors, list) or not isinstance(logical_monitors, list) or not isinstance(props, dict):
        return None

    layout_mode_raw = props.get("layout-mode")
    try:
        layout_mode = int(layout_mode_raw) if layout_mode_raw is not None else None
    except Exception:
        layout_mode = None

    logical_layout = _gnome_layout_mode_is_logical(layout_mode)

    # Build a lookup: physical monitor id -> current mode (w,h)
    current_modes: dict[tuple[str, str, str, str], tuple[int, int]] = {}
    for mon in monitors:
        try:
            mon_id, modes, _mon_props = mon
            if not (isinstance(mon_id, tuple) and len(mon_id) == 4):
                continue
            key = tuple(str(x) for x in mon_id)  # type: ignore[assignment]
            best: tuple[int, int] | None = None
            if isinstance(modes, list):
                for mode in modes:
                    # mode: (id, width, height, refresh, preferred_scale, scales, props)
                    if not (isinstance(mode, tuple) and len(mode) >= 7):
                        continue
                    w = int(mode[1])
                    h = int(mode[2])
                    mode_props = mode[6]
                    if isinstance(mode_props, dict) and mode_props.get("is-current") is True:
                        best = (w, h)
                        break
                    if best is None and w > 0 and h > 0:
                        best = (w, h)
            if best:
                current_modes[key] = best
        except Exception:
            continue

    rects: list[tuple[int, int, int, int]] = []
    for lm in logical_monitors:
        try:
            # logical monitor: (x, y, scale, transform, primary, monitors, props)
            if not (isinstance(lm, tuple) and len(lm) >= 6):
                continue
            x = _clamp_int(lm[0])
            y = _clamp_int(lm[1])
            scale = float(lm[2]) if lm[2] is not None else 1.0
            transform = int(lm[3]) if lm[3] is not None else 0
            monitors_for_lm = lm[5]
            if not isinstance(monitors_for_lm, list) or not monitors_for_lm:
                continue

            # Pick the first physical monitor in this logical group.
            mon0 = monitors_for_lm[0]
            if not (isinstance(mon0, tuple) and len(mon0) == 4):
                continue
            key = tuple(str(v) for v in mon0)
            mode = current_modes.get(key)
            if not mode:
                continue
            w, h = mode

            # Apply transform (portrait swaps).
            if transform in {1, 3, 5, 7}:
                w, h = h, w

            if logical_layout and scale > 0.0:
                w = max(1, int(round(w / scale)))
                h = max(1, int(round(h / scale)))

            rects.append((x, y, w, h))
        except Exception:
            continue

    bbox = _bbox_rects(rects)
    if not bbox:
        return None
    w, h = bbox
    return ScreenSize(width=w, height=h, backend="gnome-displayconfig")


def _probe_gnome_displayconfig() -> ScreenSize | None:
    # Best-effort. We only attempt when gdbus exists.
    gdbus = _which("gdbus")
    if not gdbus:
        return None

    cmd = [
        gdbus,
        "call",
        "--session",
        "--dest",
        "org.gnome.Mutter.DisplayConfig",
        "--object-path",
        "/org/gnome/Mutter/DisplayConfig",
        "--method",
        "org.gnome.Mutter.DisplayConfig.GetCurrentState",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return parse_gnome_displayconfig_getcurrentstate(proc.stdout)


_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def parse_kscreen_doctor_outputs(text: str) -> ScreenSize | None:
    """Parse `kscreen-doctor --outputs` and derive a virtual size."""

    src = _ANSI_ESCAPE.sub("", text or "")
    rects: list[tuple[int, int, int, int]] = []
    # Example line seen in the wild: "Geometry: 0,0 2560x1440"
    geom = re.compile(r"\bGeometry:\s*(\d+)\s*,\s*(\d+)\s+(\d+)\s*x\s*(\d+)")
    for line in src.splitlines():
        m = geom.search(line)
        if not m:
            continue
        x, y, w, h = (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
        if w > 0 and h > 0:
            rects.append((x, y, w, h))
    bbox = _bbox_rects(rects)
    if not bbox:
        return None
    w, h = bbox
    return ScreenSize(width=w, height=h, backend="kscreen-doctor")


def _probe_kscreen_doctor() -> ScreenSize | None:
    exe = _which("kscreen-doctor")
    if not exe:
        return None
    try:
        proc = subprocess.run([exe, "--outputs"], capture_output=True, text=True, timeout=3)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return parse_kscreen_doctor_outputs(proc.stdout)

def _wlr_transform_swaps(transform: str | int | None) -> bool:
    if transform is None:
        return False
    if isinstance(transform, int):
        # wl_output transform enums: 1/3/5/7 swap portrait.
        return transform in {1, 3, 5, 7, 90, 270}
    t = str(transform).strip().lower()
    return any(k in t for k in ("90", "270"))


def _wlr_size_mode() -> str:
    """How to interpret wlr-randr-reported sizes.

    wlr-randr reports a current mode (in pixels) and a scale factor.

    By default, VHK interprets the virtual desktop size in *logical/layout*
    coordinates by dividing the mode dimensions by the scale factor (matching
    the approach used for GNOME DisplayConfig).

    Set `VHK_WLR_RANDR_SIZE_MODE=physical` to use raw mode pixel dimensions.
    """

    raw = os.environ.get("VHK_WLR_RANDR_SIZE_MODE", "logical").strip().lower()
    return "physical" if raw in {"physical", "raw", "px", "pixels"} else "logical"


def _parse_mode_string(s: str) -> tuple[int, int] | None:
    m = re.search(r"(\d+)\s*x\s*(\d+)", s)
    if not m:
        return None
    try:
        w = int(m.group(1))
        h = int(m.group(2))
    except Exception:
        return None
    if w <= 0 or h <= 0:
        return None
    return w, h


def parse_wlr_randr_json(text: str) -> ScreenSize | None:
    """Parse `wlr-randr --json` output and derive virtual size."""

    try:
        data = json.loads(text or "null")
    except Exception:
        return None

    if isinstance(data, dict) and "outputs" in data:
        data = data.get("outputs")

    if not isinstance(data, list):
        return None

    rects: list[tuple[int, int, int, int]] = []
    mode_pref = _wlr_size_mode()

    for out in data:
        if not isinstance(out, dict):
            continue

        enabled = out.get("enabled")
        if enabled is None:
            enabled = out.get("active")
        if enabled is False:
            continue

        # Position
        x = out.get("x")
        y = out.get("y")
        pos = out.get("position")
        if pos is not None and (x is None or y is None):
            if isinstance(pos, dict):
                x = pos.get("x")
                y = pos.get("y")
            elif isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x, y = pos[0], pos[1]
        x = _clamp_int(x or 0)
        y = _clamp_int(y or 0)

        # Mode dims
        wh: tuple[int, int] | None = None
        for key in ("current_mode", "currentMode", "mode", "current_mode_str", "current_mode_string"):
            v = out.get(key)
            if v is None:
                continue
            if isinstance(v, dict):
                wv = v.get("width") or v.get("w")
                hv = v.get("height") or v.get("h")
                try:
                    ww = int(wv)
                    hh = int(hv)
                except Exception:
                    ww = hh = 0
                if ww > 0 and hh > 0:
                    wh = (ww, hh)
                    break
            if isinstance(v, str):
                wh = _parse_mode_string(v)
                if wh:
                    break
        if wh is None and isinstance(out.get("modes"), list):
            modes = out.get("modes")
            chosen = None
            for m in modes or []:
                if not isinstance(m, dict):
                    continue
                props = {k.lower(): m.get(k) for k in m.keys()}
                if props.get("current") is True or props.get("is-current") is True or props.get("is_current") is True:
                    chosen = m
                    break
            if chosen is None:
                for m in modes or []:
                    if not isinstance(m, dict):
                        continue
                    props = {k.lower(): m.get(k) for k in m.keys()}
                    if props.get("preferred") is True or props.get("is-preferred") is True or props.get("is_preferred") is True:
                        chosen = m
                        break
            if chosen is None and modes:
                chosen = modes[0] if isinstance(modes[0], dict) else None
            if chosen:
                wv = chosen.get("width") or chosen.get("w")
                hv = chosen.get("height") or chosen.get("h")
                try:
                    ww = int(wv)
                    hh = int(hv)
                except Exception:
                    ww = hh = 0
                if ww > 0 and hh > 0:
                    wh = (ww, hh)

        if not wh:
            continue
        w, h = wh

        # Scale
        scale_raw = out.get("scale")
        if scale_raw is None:
            scale_raw = out.get("scale_factor")
        if scale_raw is None:
            scale_raw = out.get("scaleFactor")
        try:
            scale = float(scale_raw) if scale_raw is not None else 1.0
        except Exception:
            scale = 1.0
        if scale <= 0:
            scale = 1.0

        # Transform
        transform = out.get("transform")
        if _wlr_transform_swaps(transform if isinstance(transform, (str, int)) else None):
            w, h = h, w

        if mode_pref == "logical" and scale > 0.0:
            w = max(1, int(round(w / scale)))
            h = max(1, int(round(h / scale)))

        if w > 0 and h > 0:
            rects.append((x, y, w, h))

    bbox = _bbox_rects(rects)
    if not bbox:
        return None
    ww, hh = bbox
    return ScreenSize(width=ww, height=hh, backend="wlr-randr")


def parse_wlr_randr_outputs(text: str) -> ScreenSize | None:
    """Parse `wlr-randr` (plain text) output and derive virtual size."""

    lines = (text or "").splitlines()
    outputs: list[dict[str, object]] = []
    cur: dict[str, object] | None = None

    def flush() -> None:
        nonlocal cur
        if cur is not None:
            outputs.append(cur)
        cur = None

    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        if not line.startswith(" ") and not line.startswith("\t") and ":" not in line:
            # Output header line: "DP-1 \"...\""
            flush()
            name = line.split(None, 1)[0]
            cur = {"name": name}
            continue
        if cur is None:
            continue

        s = line.strip()
        if s.lower().startswith("enabled:"):
            v = s.split(":", 1)[1].strip().lower()
            cur["enabled"] = v in {"yes", "true", "on", "enabled"}
        elif s.lower().startswith("position:"):
            v = s.split(":", 1)[1].strip()
            m = re.match(r"(-?\d+)\s*,\s*(-?\d+)", v)
            if m:
                cur["x"] = int(m.group(1))
                cur["y"] = int(m.group(2))
        elif s.lower().startswith("scale:"):
            v = s.split(":", 1)[1].strip()
            try:
                cur["scale"] = float(v)
            except Exception:
                pass
        elif s.lower().startswith("transform:"):
            cur["transform"] = s.split(":", 1)[1].strip()
        else:
            # Mode lines show up under "Modes:" with indentation.
            # Prefer a line marked current.
            if "px" in s and "x" in s:
                wh = _parse_mode_string(s)
                if not wh:
                    continue
                if "mode" not in cur:
                    cur["mode"] = wh
                if "current" in s.lower():
                    cur["mode"] = wh

    flush()

    rects: list[tuple[int, int, int, int]] = []
    mode_pref = _wlr_size_mode()

    for o in outputs:
        if o.get("enabled") is False:
            continue
        w_h = o.get("mode")
        if not (isinstance(w_h, tuple) and len(w_h) == 2):
            continue
        w, h = int(w_h[0]), int(w_h[1])
        x = _clamp_int(o.get("x") or 0)
        y = _clamp_int(o.get("y") or 0)
        try:
            scale = float(o.get("scale") or 1.0)
        except Exception:
            scale = 1.0
        if scale <= 0:
            scale = 1.0
        transform = o.get("transform")
        if _wlr_transform_swaps(transform if isinstance(transform, (str, int)) else None):
            w, h = h, w
        if mode_pref == "logical" and scale > 0.0:
            w = max(1, int(round(w / scale)))
            h = max(1, int(round(h / scale)))
        if w > 0 and h > 0:
            rects.append((x, y, w, h))

    bbox = _bbox_rects(rects)
    if not bbox:
        return None
    ww, hh = bbox
    return ScreenSize(width=ww, height=hh, backend="wlr-randr")


def _probe_wlr_randr() -> ScreenSize | None:
    exe = _which("wlr-randr")
    if not exe:
        return None

    # Newer releases support `--json`.
    try:
        proc = subprocess.run([exe, "--json"], capture_output=True, text=True, timeout=3)
    except Exception:
        proc = None

    if proc is not None and proc.returncode == 0 and (proc.stdout or "").strip().startswith(("[", "{")):
        r = parse_wlr_randr_json(proc.stdout)
        if r:
            return r

    # Fallback: parse plain-text output (older releases).
    try:
        proc2 = subprocess.run([exe], capture_output=True, text=True, timeout=3)
    except Exception:
        return None
    if proc2.returncode != 0:
        return None
    return parse_wlr_randr_outputs(proc2.stdout)



def _probe_x11_xrandr() -> ScreenSize | None:
    xrandr = _which("xrandr")
    if not xrandr:
        return None
    proc = subprocess.run([xrandr, "--query"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    # Parse a line like: "Screen 0: minimum 8 x 8, current 1920 x 1080, maximum ..."
    for line in (proc.stdout or "").splitlines():
        if "current" in line and "Screen" in line:
            parts = line.split("current", 1)[1]
            parts = parts.split(",", 1)[0]
            nums = [p.strip() for p in parts.split("x")]
            if len(nums) == 2:
                try:
                    w = int(nums[0])
                    h = int(nums[1])
                    if w > 0 and h > 0:
                        return ScreenSize(width=w, height=h, backend="xrandr")
                except Exception:
                    continue
    return None


def get_virtual_screen_size(*, refresh: bool = False) -> ScreenSize:
    """Return best-effort virtual desktop size.

    The result is cached for the lifetime of the process unless refresh=True.
    """

    global _CACHED
    if _CACHED is not None and not refresh:
        return _CACHED

    if detect_backend() == "wayland":
        for probe in (_probe_hyprland, _probe_i3_sway_ipc, _probe_wlr_randr, _probe_gnome_displayconfig, _probe_kscreen_doctor):
            r = probe()
            if r:
                _CACHED = r
                return r

        # Wayland without a compositor probe: we intentionally do not attempt
        # an interactive screenshot fallback here. Callers should surface a
        # useful error message instead of hanging.
        raise RuntimeError(
            "Unable to determine screen size on Wayland. "
            "Install hyprctl (Hyprland) or ensure sway/i3 IPC is reachable; "
            "on GNOME install gdbus (glib2) to query Mutter DisplayConfig; "
            "on KDE install kscreen-doctor (libkscreen) to query output geometry."
        )

    r = _probe_x11_xrandr()
    if r:
        _CACHED = r
        return r
    raise RuntimeError("Unable to determine screen size (install xrandr on X11).")
