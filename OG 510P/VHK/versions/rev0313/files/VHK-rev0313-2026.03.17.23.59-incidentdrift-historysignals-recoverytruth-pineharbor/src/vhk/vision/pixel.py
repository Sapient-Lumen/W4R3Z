from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from vhk.core.models import Region


@dataclass
class PixelMatch:
    x: int
    y: int
    dist: float


@dataclass
class PixelHit:
    """A pixel hit (optionally representing a connected component)."""

    x: int
    y: int
    dist: float
    w: int = 1
    h: int = 1
    area: int = 1
    bbox_x: int | None = None
    bbox_y: int | None = None


@dataclass
class PixelColor:
    """A sampled pixel color."""

    r: int
    g: int
    b: int

    @property
    def hex(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    @property
    def ahk_hex(self) -> str:
        # AHK commonly displays colors as 0xRRGGBB.
        return f"0x{self.r:02X}{self.g:02X}{self.b:02X}"


class PixelSearchNoMatch(RuntimeError):
    """Raised when the best pixel is still outside the tolerance.

    Keeping the best distance/coords is useful for WaitForPixel-style loops,
    where users want progress telemetry ("how close am I?").
    """

    def __init__(self, message: str, *, dist: float, x: int, y: int):
        super().__init__(message)
        self.dist = float(dist)
        self.x = int(x)
        self.y = int(y)


def _parse_hex_rgb(s: str, *, order: str) -> tuple[int, int, int]:
    """Parse 6 hex digits into (r,g,b) with explicit channel order.

    order:
      - "rgb": input is RRGGBB
      - "bgr": input is BBGGRR (AHK default in some commands)
    """

    s = s.strip()
    if len(s) != 6:
        raise ValueError("hex color must be 6 digits")

    v = int(s, 16)
    a = (v >> 16) & 0xFF
    b = (v >> 8) & 0xFF
    c = v & 0xFF

    if order == "rgb":
        r, g, bl = a, b, c
    elif order == "bgr":
        bl, g, r = a, b, c
    else:
        raise ValueError(f"Unknown color order: {order!r}")

    return int(r), int(g), int(bl)


def parse_color(color: str | list[int]) -> tuple[int, int, int]:
    """Parse a color into BGR (OpenCV) order.

    Accepts:
      - "#RRGGBB"
      - "0xRRGGBB" (AHK-style literal)
      - "R,G,B"
      - [R, G, B]

    Prefixes for compatibility:
      - "rgb:" (default): interpret hex as RRGGBB
      - "bgr:": interpret hex as BBGGRR (AHK's legacy default for some APIs)

    Returns
    -------
    (b, g, r)

    Notes
    -----
    AutoHotkey historically defaults some pixel APIs to BGR order unless the
    "RGB" option is provided. VHK uses RGB as the default for hex literals, but
    supports the explicit "bgr:" prefix to make porting scripts less error-prone.
    """

    if isinstance(color, list):
        if len(color) != 3:
            raise ValueError("color list must have 3 integers [R,G,B]")
        r, g, b = (int(color[0]), int(color[1]), int(color[2]))
        return (b, g, r)

    s = (color or "").strip()
    if not s:
        raise ValueError("Empty color string")

    order = "rgb"
    if ":" in s:
        prefix, rest = s.split(":", 1)
        pref = prefix.strip().lower()
        if pref in {"rgb", "bgr"}:
            order = pref
            s = rest.strip()

    # Hex forms
    if s.startswith("#") and len(s) == 7:
        r, g, b = _parse_hex_rgb(s[1:], order=order)
        return (b, g, r)

    if s.lower().startswith("0x") and len(s) == 8:
        r, g, b = _parse_hex_rgb(s[2:], order=order)
        return (b, g, r)

    if len(s) == 6:
        # Accept bare hex digits for convenience.
        try:
            int(s, 16)
        except Exception:
            pass
        else:
            r, g, b = _parse_hex_rgb(s, order=order)
            return (b, g, r)

    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        if len(parts) != 3:
            raise ValueError("color string must be 'R,G,B'")
        r, g, b = (int(parts[0]), int(parts[1]), int(parts[2]))
        return (b, g, r)

    raise ValueError(
        "Unsupported color format. Use '#RRGGBB', '0xRRGGBB', 'R,G,B', or [R,G,B]. "
        "Optional prefixes: 'rgb:' or 'bgr:'."
    )


def _scan_order_flags(scan_order: str) -> tuple[bool, bool]:
    """Return (vflip, hflip) for a scan order.

    scan_order is a compact mnemonic for the direction the search traverses:

    - tlbr: top-left  -> bottom-right (default)
    - trbl: top-right -> bottom-left
    - bltr: bottom-left -> top-right
    - brtl: bottom-right -> top-left
    """

    s = (scan_order or "tlbr").strip().lower()
    mapping: dict[str, tuple[bool, bool]] = {
        "tlbr": (False, False),
        "trbl": (False, True),
        "bltr": (True, False),
        "brtl": (True, True),
    }
    if s not in mapping:
        raise ValueError(f"Unknown scan_order: {scan_order!r} (use tlbr|trbl|bltr|brtl)")
    return mapping[s]


def _view_coords_to_arr(
    yv: int, xv: int, *, h: int, w: int, vflip: bool, hflip: bool
) -> tuple[int, int]:
    """Map coordinates in a flipped view back to the original array."""

    ya = (h - 1 - yv) if vflip else yv
    xa = (w - 1 - xv) if hflip else xv
    return int(ya), int(xa)


def _scan_sort_key(scan_order: str) -> tuple[int, int]:
    """Return multipliers (sy, sx) for scan sorting."""

    vflip, hflip = _scan_order_flags(scan_order)
    sy = -1 if vflip else 1
    sx = -1 if hflip else 1
    return sy, sx


def pixel_search_all_file(
    image_path: Path,
    *,
    color: str | list[int],
    region: Region | None = None,
    tolerance: float = 0.0,
    tolerance_mode: str = "euclidean",
    step: int = 1,
    phase_x: int = 0,
    phase_y: int = 0,
    group: str = "none",
    pick: str = "center",
    min_area: int = 1,
    max_results: int = 200,
    sort: str = "scan",
    scan_order: str = "tlbr",
) -> list[PixelHit]:
    """Find **all** pixels close to a target color.

    This is the multi-match companion to :func:`pixel_search_file`, inspired by
    SikuliX-style ``findAll()`` workflows but applied to color matching.

    To keep this practical for automation:
    - Results are bounded by ``max_results``.
    - When ``group='connected'``, VHK collapses contiguous matching pixels into
      connected components (blobs) and returns one hit per blob.
    """

    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    x0, y0 = 0, 0
    if region is not None:
        x0, y0 = region.x, region.y
        img = img[region.y : region.y + region.h, region.x : region.x + region.w]

    if img.size == 0:
        return []

    target = np.array(parse_color(color), dtype=np.int32)  # BGR

    step = int(step)
    if step < 1:
        raise ValueError("step must be >= 1")
    phase_x = int(phase_x)
    phase_y = int(phase_y)
    if phase_x < 0 or phase_y < 0 or phase_x >= step or phase_y >= step:
        raise ValueError(
            f"phase_x/phase_y must be in [0, step-1]; got ({phase_x},{phase_y}) with step={step}"
        )

    tol = float(tolerance)
    if tol < 0:
        raise ValueError("tolerance must be >= 0")

    max_results = int(max_results)
    if max_results < 1:
        raise ValueError("max_results must be >= 1")

    group_mode = (group or "none").strip().lower()
    pick_mode = (pick or "center").strip().lower()
    sort_mode = (sort or "scan").strip().lower()
    if sort_mode not in {"scan", "dist"}:
        raise ValueError("sort must be 'scan' or 'dist'")

    vflip, hflip = _scan_order_flags(scan_order)
    sy, sx = _scan_sort_key(scan_order)

    sampled = img[phase_y::step, phase_x::step]
    diff = sampled.astype(np.int32) - target

    mode = (tolerance_mode or "").strip().lower()
    if mode in {"", "euclidean", "l2"}:
        dist2 = np.sum(diff * diff, axis=2, dtype=np.int32)
        tol2 = tol * tol
        mask = dist2 <= tol2
        dist_map: np.ndarray = dist2
        dist_is_squared = True
    elif mode in {"per_channel", "per-channel", "max", "variation"}:
        maxd = np.max(np.abs(diff), axis=2).astype(np.int16)
        mask = maxd <= tol
        dist_map = maxd
        dist_is_squared = False
    else:
        raise ValueError(f"Unknown tolerance_mode: {tolerance_mode!r}")

    if not np.any(mask):
        return []

    def _dist_at(ys: int, xs: int) -> float:
        d = float(dist_map[int(ys), int(xs)])
        return float(np.sqrt(d)) if dist_is_squared else float(d)

    def _to_abs_xy(ys: int, xs: int) -> tuple[int, int]:
        x = int(phase_x + xs * step + x0)
        y = int(phase_y + ys * step + y0)
        return x, y

    hits: list[PixelHit] = []

    if group_mode in {"none", "raw"}:
        if sort_mode == "scan":
            view_mask = mask
            if vflip:
                view_mask = view_mask[::-1, :]
            if hflip:
                view_mask = view_mask[:, ::-1]
            flat = np.flatnonzero(view_mask.ravel())
            if flat.size == 0:
                return []
            flat = flat[:max_results]
            ys_view, xs_view = np.unravel_index(flat, view_mask.shape)
            for yv, xv in zip(ys_view.tolist(), xs_view.tolist()):
                ys, xs = _view_coords_to_arr(
                    int(yv),
                    int(xv),
                    h=mask.shape[0],
                    w=mask.shape[1],
                    vflip=vflip,
                    hflip=hflip,
                )
                x, y = _to_abs_xy(ys, xs)
                hits.append(PixelHit(x=x, y=y, dist=_dist_at(ys, xs), bbox_x=x, bbox_y=y))
            return hits

        ys, xs = np.where(mask)
        if xs.size == 0:
            return []
        max_candidates = max(10_000, max_results * 500)
        if xs.size > max_candidates:
            dvals = dist_map[ys, xs]
            idx = np.argpartition(dvals, max_candidates - 1)[:max_candidates]
            ys = ys[idx]
            xs = xs[idx]
        dvals = dist_map[ys, xs].astype(np.float64)
        order = np.argsort(dvals)
        order = order[:max_results]
        for i in order.tolist():
            ysi = int(ys[int(i)])
            xsi = int(xs[int(i)])
            x, y = _to_abs_xy(ysi, xsi)
            hits.append(PixelHit(x=x, y=y, dist=_dist_at(ysi, xsi), bbox_x=x, bbox_y=y))
        return hits

    if group_mode not in {"connected", "components", "blobs"}:
        raise ValueError("group must be 'none' or 'connected'")

    min_area = int(min_area)
    if min_area < 1:
        raise ValueError("min_area must be >= 1")

    mask_u8 = mask.astype(np.uint8)
    num, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)

    for lab in range(1, int(num)):
        area = int(stats[lab, cv2.CC_STAT_AREA])
        if area < min_area:
            continue

        left = int(stats[lab, cv2.CC_STAT_LEFT])
        top = int(stats[lab, cv2.CC_STAT_TOP])
        width = int(stats[lab, cv2.CC_STAT_WIDTH])
        height = int(stats[lab, cv2.CC_STAT_HEIGHT])

        w_orig = int((max(1, width) - 1) * step + 1)
        h_orig = int((max(1, height) - 1) * step + 1)

        bbox_x, bbox_y = _to_abs_xy(top, left)

        if pick_mode in {"center", "centroid"}:
            cx, cy = centroids[lab]
            ys = int(round(float(cy)))
            xs = int(round(float(cx)))
            ys = int(np.clip(ys, top, top + height - 1))
            xs = int(np.clip(xs, left, left + width - 1))
            if labels[ys, xs] != lab:
                sub = labels[top : top + height, left : left + width]
                yy, xx = np.where(sub == lab)
                ys = int(top + int(yy[0]))
                xs = int(left + int(xx[0]))
        elif pick_mode in {"first", "scan"}:
            view_labels = labels
            if vflip:
                view_labels = view_labels[::-1, :]
            if hflip:
                view_labels = view_labels[:, ::-1]
            flat = np.flatnonzero((view_labels == lab).ravel())
            if flat.size == 0:
                continue
            idx_first = int(flat[0])
            yv, xv = np.unravel_index(idx_first, view_labels.shape)
            ys, xs = _view_coords_to_arr(
                int(yv),
                int(xv),
                h=labels.shape[0],
                w=labels.shape[1],
                vflip=vflip,
                hflip=hflip,
            )
        elif pick_mode in {"best", "min"}:
            sub_d = dist_map[top : top + height, left : left + width]
            sub_l = labels[top : top + height, left : left + width]
            d = sub_d.astype(np.float64)
            d[sub_l != lab] = np.inf
            idx_best = int(np.nanargmin(d))
            yy, xx = np.unravel_index(idx_best, d.shape)
            ys = int(top + int(yy))
            xs = int(left + int(xx))
        else:
            raise ValueError("pick must be 'center', 'first', or 'best'")

        x_abs, y_abs = _to_abs_xy(ys, xs)
        hits.append(
            PixelHit(
                x=x_abs,
                y=y_abs,
                dist=_dist_at(ys, xs),
                w=w_orig,
                h=h_orig,
                area=area,
                bbox_x=bbox_x,
                bbox_y=bbox_y,
            )
        )

    if not hits:
        return []

    if sort_mode == "dist":
        hits.sort(key=lambda m: (m.dist, sy * m.y, sx * m.x))
    else:
        hits.sort(key=lambda m: (sy * m.y, sx * m.x, m.dist))
    return hits[:max_results]


def pixel_search_file(
    image_path: Path,
    *,
    color: str | list[int],
    region: Region | None = None,
    tolerance: float = 0.0,
    tolerance_mode: str = "euclidean",
    step: int = 1,
    phase_x: int = 0,
    phase_y: int = 0,
    match_strategy: str = "best",
    scan_order: str = "tlbr",
) -> PixelMatch:
    """Search an image for a pixel close to ``color``.

    By default, VHK returns the *best* (closest) pixel, which is useful for
    diagnostics and "closest match" workflows.

    Many automation ecosystems (AutoIt / AHK-style PixelSearch) instead return
    the **first** pixel that falls within the tolerance when scanning the region.
    VHK supports this with ``match_strategy="first"`` and a configurable
    ``scan_order``.

    Parameters
    ----------
    tolerance:
        If `tolerance_mode` is "euclidean", this is Euclidean distance in BGR
        space (0..~441). If `tolerance_mode` is "per_channel", this is the
        maximum per-channel absolute difference (0..255).

    tolerance_mode:
        - "euclidean": distance = sqrt(db^2 + dg^2 + dr^2)
        - "per_channel": distance = max(|db|, |dg|, |dr|)

    step:
        Instead of checking every pixel, check a strided grid for speed (like
        AutoIt PixelSearch's `step` parameter). A value of 2 checks every other
        pixel, etc. Default is 1.

    phase_x / phase_y:
        Offset into the strided grid (0..step-1). These are mainly useful for
        WaitForPixel-style loops that cycle phases across attempts so that
        `step>1` does not permanently miss pixels.

    match_strategy:
        - "best" (default): return the closest pixel (minimum distance).
        - "first": return the first pixel meeting the tolerance in scan order.

    scan_order:
        - "tlbr" (default): top-left -> bottom-right
        - "trbl": top-right -> bottom-left
        - "bltr": bottom-left -> top-right
        - "brtl": bottom-right -> top-left

        This affects tie-breaking for "best", and the traversal order for "first".
    """

    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    x0, y0 = 0, 0
    if region is not None:
        x0, y0 = region.x, region.y
        img = img[region.y : region.y + region.h, region.x : region.x + region.w]

    if img.size == 0:
        raise ValueError("Empty search region")

    target = np.array(parse_color(color), dtype=np.int32)  # BGR

    step = int(step)
    if step < 1:
        raise ValueError("step must be >= 1")
    phase_x = int(phase_x)
    phase_y = int(phase_y)
    if phase_x < 0 or phase_y < 0 or phase_x >= step or phase_y >= step:
        raise ValueError(
            f"phase_x/phase_y must be in [0, step-1]; got ({phase_x},{phase_y}) with step={step}"
        )

    tol = float(tolerance)
    if tol < 0:
        raise ValueError("tolerance must be >= 0")

    vflip, hflip = _scan_order_flags(scan_order)

    # Strided sampling grid (for speed); phase offsets let callers cycle phases
    # across attempts to avoid permanently missing pixels with step>1.
    sampled = img[phase_y::step, phase_x::step]
    diff = sampled.astype(np.int32) - target

    mode = (tolerance_mode or "").strip().lower()
    strategy = (match_strategy or "best").strip().lower()

    def _raise_nomatch(best_d: float, *, ys: int, xs: int) -> None:
        x = int(phase_x + xs * step)
        y = int(phase_y + ys * step)
        best_x = int(x + x0)
        best_y = int(y + y0)
        raise PixelSearchNoMatch(
            f"PixelSearch did not meet tolerance. best={best_d:.3f} tol={tol:.3f} "
            f"mode={mode} strategy={strategy} scan_order={scan_order}",
            dist=best_d,
            x=best_x,
            y=best_y,
        )

    def _match(xs: int, ys: int, d: float) -> PixelMatch:
        x = int(phase_x + xs * step)
        y = int(phase_y + ys * step)
        return PixelMatch(x=int(x + x0), y=int(y + y0), dist=float(d))

    if mode in {"", "euclidean", "l2"}:
        # Use squared distance for selection/masking to avoid a full sqrt.
        dist2 = np.sum(diff * diff, axis=2, dtype=np.int32)

        # Best pixel (for best-strategy, or for NoMatch telemetry)
        view = dist2
        if vflip:
            view = view[::-1, :]
        if hflip:
            view = view[:, ::-1]
        idx_best = int(view.argmin())
        yv_best, xv_best = np.unravel_index(idx_best, view.shape)
        ys_best, xs_best = _view_coords_to_arr(
            int(yv_best),
            int(xv_best),
            h=dist2.shape[0],
            w=dist2.shape[1],
            vflip=vflip,
            hflip=hflip,
        )
        min2 = int(dist2[ys_best, xs_best])
        best_dist = float(np.sqrt(min2))

        if strategy in {"best", "min"}:
            tol2 = tol * tol
            if float(min2) > tol2:
                _raise_nomatch(best_dist, ys=ys_best, xs=xs_best)
            return _match(xs_best, ys_best, best_dist)

        if strategy in {"first", "scan"}:
            tol2 = tol * tol
            mask = dist2 <= tol2
            view_mask = mask
            if vflip:
                view_mask = view_mask[::-1, :]
            if hflip:
                view_mask = view_mask[:, ::-1]
            flat = np.flatnonzero(view_mask.ravel())
            if flat.size == 0:
                _raise_nomatch(best_dist, ys=ys_best, xs=xs_best)
            idx_first = int(flat[0])
            yv, xv = np.unravel_index(idx_first, view_mask.shape)
            ys, xs = _view_coords_to_arr(
                int(yv),
                int(xv),
                h=mask.shape[0],
                w=mask.shape[1],
                vflip=vflip,
                hflip=hflip,
            )
            d = float(np.sqrt(int(dist2[ys, xs])))
            return _match(xs, ys, d)

        raise ValueError(f"Unknown match_strategy: {match_strategy!r} (use best|first)")

    if mode in {"per_channel", "per-channel", "max", "variation"}:
        # Use integer max abs diff; this mirrors AHK/AutoIt "variation" intuition.
        maxd = np.max(np.abs(diff), axis=2).astype(np.int16)  # 0..255

        view = maxd
        if vflip:
            view = view[::-1, :]
        if hflip:
            view = view[:, ::-1]
        idx_best = int(view.argmin())
        yv_best, xv_best = np.unravel_index(idx_best, view.shape)
        ys_best, xs_best = _view_coords_to_arr(
            int(yv_best),
            int(xv_best),
            h=maxd.shape[0],
            w=maxd.shape[1],
            vflip=vflip,
            hflip=hflip,
        )
        best_dist = float(int(maxd[ys_best, xs_best]))

        if strategy in {"best", "min"}:
            if best_dist > tol:
                _raise_nomatch(best_dist, ys=ys_best, xs=xs_best)
            return _match(xs_best, ys_best, best_dist)

        if strategy in {"first", "scan"}:
            mask = maxd <= tol
            view_mask = mask
            if vflip:
                view_mask = view_mask[::-1, :]
            if hflip:
                view_mask = view_mask[:, ::-1]
            flat = np.flatnonzero(view_mask.ravel())
            if flat.size == 0:
                _raise_nomatch(best_dist, ys=ys_best, xs=xs_best)
            idx_first = int(flat[0])
            yv, xv = np.unravel_index(idx_first, view_mask.shape)
            ys, xs = _view_coords_to_arr(
                int(yv),
                int(xv),
                h=mask.shape[0],
                w=mask.shape[1],
                vflip=vflip,
                hflip=hflip,
            )
            d = float(int(maxd[ys, xs]))
            return _match(xs, ys, d)

        raise ValueError(f"Unknown match_strategy: {match_strategy!r} (use best|first)")

    raise ValueError(f"Unknown tolerance_mode: {tolerance_mode!r}")


def pixel_get_color_file(
    image_path: Path,
    *,
    x: int,
    y: int,
    region: Region | None = None,
) -> PixelColor:
    """Sample the pixel color at (x,y) from an image file.

    Coordinates are absolute within the image. If a region is provided, the
    function will validate that (x,y) lies within it and will crop before
    indexing (useful for large images).

    Returns a :class:`PixelColor` in RGB order.
    """

    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    x = int(x)
    y = int(y)

    if region is not None:
        if x < region.x or y < region.y or x >= region.x + region.w or y >= region.y + region.h:
            raise ValueError(f"(x,y)=({x},{y}) lies outside region {region}")
        img = img[region.y : region.y + region.h, region.x : region.x + region.w]
        x -= region.x
        y -= region.y

    h, w = img.shape[:2]
    if x < 0 or y < 0 or x >= w or y >= h:
        raise ValueError(f"(x,y)=({x},{y}) is outside image bounds {w}x{h}")

    b, g, r = [int(v) for v in img[y, x]]
    return PixelColor(r=r, g=g, b=b)
