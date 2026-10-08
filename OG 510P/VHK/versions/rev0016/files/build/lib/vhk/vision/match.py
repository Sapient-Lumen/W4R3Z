from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from vhk.core.models import Region
from vhk.vision.assets import Needle, NeedleArea, try_load_needle


@dataclass
class ImageMatch:
    x: int
    y: int
    score: float
    w: int
    h: int


def _scores_map(hay: np.ndarray, templ: np.ndarray, *, mask: np.ndarray | None = None) -> np.ndarray:
    """Return a score map where higher is better.

    Uses TM_CCOEFF_NORMED for most cases, but switches to TM_SQDIFF_NORMED when
    the template variance is near zero.

    Returns
    -------
    np.ndarray
        2D array of scores.
    """

    if float(np.std(templ)) < 1e-6:
        res = cv2.matchTemplate(hay, templ, cv2.TM_SQDIFF_NORMED, mask=mask)
        return 1.0 - res

    return cv2.matchTemplate(hay, templ, cv2.TM_CCOEFF_NORMED, mask=mask)


def _mask_for_patch(
    patch_w: int,
    patch_h: int,
    *,
    patch_offset_x: int,
    patch_offset_y: int,
    exclude_areas: list[NeedleArea],
) -> np.ndarray | None:
    """Create an OpenCV mask for a template patch using exclude areas.

    Notes
    -----
    The mask is a single-channel 8-bit image where non-zero pixels are *used*.
    """

    if not exclude_areas:
        return None

    m = np.full((patch_h, patch_w), 255, dtype=np.uint8)

    for e in exclude_areas:
        # Intersect exclude area with patch rectangle.
        ex1, ey1 = int(e.xpos), int(e.ypos)
        ex2, ey2 = int(e.xpos + e.width), int(e.ypos + e.height)
        px1, py1 = int(patch_offset_x), int(patch_offset_y)
        px2, py2 = int(patch_offset_x + patch_w), int(patch_offset_y + patch_h)

        ix1, iy1 = max(ex1, px1), max(ey1, py1)
        ix2, iy2 = min(ex2, px2), min(ey2, py2)
        if ix2 <= ix1 or iy2 <= iy1:
            continue

        # Convert to patch-local coordinates.
        lx1, ly1 = ix1 - px1, iy1 - py1
        lx2, ly2 = ix2 - px1, iy2 - py1
        m[ly1:ly2, lx1:lx2] = 0

    # If mask is all 255, skip allocating it.
    if int(m.min()) == 255:
        return None
    return m


def _multi_area_template_match(
    hay: np.ndarray,
    needle_img: np.ndarray,
    needle_meta: Needle,
    *,
    threshold: float,
) -> tuple[tuple[int, int], float]:
    """Template match using multiple 'match areas' (openQA-ish).

    We compute a score map for each match area patch and then combine them into
    a full-placement score map by slicing (see derivation in docs).

    This avoids needing OpenCV's optional matchTemplate mask support and tends
    to behave nicely when users carve out only stable sub-regions.
    """

    areas = needle_meta.match_areas
    exclude = needle_meta.exclude_areas

    # Effective needle bbox is the union of match areas.
    min_x = min(a.xpos for a in areas)
    min_y = min(a.ypos for a in areas)
    max_x = max(a.xpos + a.width for a in areas)
    max_y = max(a.ypos + a.height for a in areas)

    needle_crop = needle_img[min_y:max_y, min_x:max_x]
    crop_h, crop_w = int(needle_crop.shape[0]), int(needle_crop.shape[1])

    if hay.shape[0] < crop_h or hay.shape[1] < crop_w:
        raise ValueError("Needle is larger than search region")

    full_h = hay.shape[0] - crop_h + 1
    full_w = hay.shape[1] - crop_w + 1

    aligned_maps: list[np.ndarray] = []
    area_thresholds: list[float] = []

    for a in areas:
        ax = int(a.xpos - min_x)
        ay = int(a.ypos - min_y)
        aw = int(a.width)
        ah = int(a.height)

        patch = needle_crop[ay : ay + ah, ax : ax + aw]
        if patch.size == 0:
            continue

        mask = _mask_for_patch(
            aw,
            ah,
            patch_offset_x=min_x + ax,
            patch_offset_y=min_y + ay,
            exclude_areas=exclude,
        )
        patch_scores = _scores_map(hay, patch, mask=mask)

        # Convert patch placement scores to full needle placement scores.
        # For a full placement (x,y), patch is placed at (x+ax, y+ay).
        patch_aligned = patch_scores[ay : ay + full_h, ax : ax + full_w].astype(np.float32)
        aligned_maps.append(patch_aligned)
        area_thresholds.append(a.threshold(threshold))

    if not aligned_maps:
        raise ValueError("Needle has match areas but none produced valid patches")

    # openQA semantics: each match area must meet its own threshold.
    # We rank placements by the worst (minimum) area score to bias toward
    # "all areas are decent" rather than "one great area, one terrible one".
    stacked = np.stack(aligned_maps, axis=0)
    scores = np.min(stacked, axis=0)

    # We'll try a few top candidates; if none satisfy per-area thresholds,
    # we fail.
    threshold_min = min(area_thresholds) if area_thresholds else float(threshold)
    attempts = 0
    while attempts < 50:
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(scores)
        best = float(max_val)
        if best < threshold_min:
            break

        x, y = int(max_loc[0]), int(max_loc[1])
        per_ok = True
        for amap, thr in zip(aligned_maps, area_thresholds):
            if float(amap[y, x]) < float(thr):
                per_ok = False
                break
        if per_ok:
            return (x, y), best

        # Mask out this candidate and keep searching.
        scores[y, x] = -1.0
        attempts += 1

    # Failed.
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(scores)
    score = float(max_val)
    raise RuntimeError(
        f"ImageSearch did not meet per-area thresholds. best={score:.3f} min_threshold={threshold_min:.3f} (areas)"
    )


def image_search_file(
    haystack_path: Path,
    needle_path: Path,
    *,
    region: Region | None = None,
    threshold: float = 0.8,
) -> ImageMatch:
    """Find `needle` in `haystack` using template matching.

    Behavior
    --------
    - If a sibling JSON exists next to `needle_path` (e.g. foo.png + foo.json),
      we load openQA-style areas and, if any `match` areas exist, we match using
      *only* those sub-regions. We also honor:
        - per-area `match` percentages (0-100)
        - `exclude` areas (mask out unstable pixels)
    - Otherwise, we match the full template.

    Notes
    -----
    - For near-constant templates (solid colors), correlation metrics can be
      degenerate; we fall back to SQDIFF in that case.
    """

    hay = cv2.imread(str(haystack_path), cv2.IMREAD_COLOR)
    if hay is None:
        raise FileNotFoundError(f"Cannot read haystack image: {haystack_path}")

    needle_img = cv2.imread(str(needle_path), cv2.IMREAD_COLOR)
    if needle_img is None:
        raise FileNotFoundError(f"Cannot read needle image: {needle_path}")

    x0, y0 = 0, 0
    if region is not None:
        x0, y0 = region.x, region.y
        hay = hay[region.y : region.y + region.h, region.x : region.x + region.w]

    # If we have needle metadata with match areas, use the multi-area matcher.
    needle_meta = try_load_needle(needle_path)

    if needle_meta and needle_meta.match_areas:
        (mx, my), score = _multi_area_template_match(hay, needle_img, needle_meta, threshold=threshold)

        # Effective bbox size is union of match areas.
        areas = needle_meta.match_areas
        min_x = min(a.xpos for a in areas)
        min_y = min(a.ypos for a in areas)
        max_x = max(a.xpos + a.width for a in areas)
        max_y = max(a.ypos + a.height for a in areas)
        w = int(max_x - min_x)
        h = int(max_y - min_y)

        return ImageMatch(x=int(mx + x0), y=int(my + y0), score=score, w=w, h=h)

    # Full template match.
    if hay.shape[0] < needle_img.shape[0] or hay.shape[1] < needle_img.shape[1]:
        raise ValueError("Needle is larger than search region")

    scores = _scores_map(hay, needle_img)
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(scores)
    score = float(max_val)

    if score < threshold:
        raise RuntimeError(f"ImageSearch did not meet threshold. best={score:.3f} threshold={threshold:.3f}")

    return ImageMatch(
        x=int(max_loc[0] + x0),
        y=int(max_loc[1] + y0),
        score=score,
        w=int(needle_img.shape[1]),
        h=int(needle_img.shape[0]),
    )
