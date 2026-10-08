from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from vhk.core.models import Region
from vhk.vision.assets import Needle, NeedleArea, scale_needle, try_load_needle
from vhk.vision.imgio import imread_color


@dataclass
class ImageMatch:
    x: int
    y: int
    score: float
    w: int
    h: int
    scale: float = 1.0


def _nms_iou(boxes: np.ndarray, scores: np.ndarray, *, iou_threshold: float, max_results: int) -> list[int]:
    """Non-maximum suppression (NMS) for axis-aligned boxes.

    Parameters
    ----------
    boxes:
        Nx4 array of [x, y, w, h].
    scores:
        N array of scores (higher is better).
    iou_threshold:
        Suppress boxes with IoU > threshold.
    max_results:
        Hard cap on kept indices.

    Notes
    -----
    Template matching produces a *cluster* of high scores around each true
    instance (sliding window shifts by 1px). NMS is the standard way to collapse
    those clusters into one detection per instance.
    """

    if boxes.size == 0:
        return []

    iou_threshold = float(iou_threshold)
    if iou_threshold < 0 or iou_threshold > 1:
        raise ValueError("iou_threshold must be in [0,1]")

    max_results = int(max_results)
    if max_results < 1:
        return []

    x1 = boxes[:, 0].astype(np.float32)
    y1 = boxes[:, 1].astype(np.float32)
    x2 = (boxes[:, 0] + boxes[:, 2]).astype(np.float32)
    y2 = (boxes[:, 1] + boxes[:, 3]).astype(np.float32)
    area = (boxes[:, 2].astype(np.float32) * boxes[:, 3].astype(np.float32)).clip(min=1.0)

    order = np.argsort(scores.astype(np.float32))[::-1]
    keep: list[int] = []

    while order.size > 0 and len(keep) < max_results:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = (xx2 - xx1).clip(min=0.0)
        h = (yy2 - yy1).clip(min=0.0)
        inter = w * h
        union = area[i] + area[order[1:]] - inter
        iou = inter / union.clip(min=1e-6)

        # Keep boxes with IoU <= threshold.
        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]

    return keep


def _scan_sort_key(scan_order: str) -> tuple[int, int]:
    """Return multipliers (sy, sx) for scan-order sorting."""

    s = (scan_order or "tlbr").strip().lower()
    mapping: dict[str, tuple[int, int]] = {
        "tlbr": (1, 1),
        "trbl": (1, -1),
        "bltr": (-1, 1),
        "brtl": (-1, -1),
    }
    if s not in mapping:
        raise ValueError("scan_order must be tlbr|trbl|bltr|brtl")
    return mapping[s]


def _normalize_scales(scales: list[float] | None) -> list[float]:
    if not scales:
        return [1.0]
    out: list[float] = []
    for s in scales:
        sf = float(s)
        if sf <= 0:
            raise ValueError(f"scale must be > 0 (got {s})")
        # Keep stable order, but de-dupe near-equal values.
        if any(abs(sf - prev) < 1e-6 for prev in out):
            continue
        out.append(sf)
    return out or [1.0]


def _resize_needle(img: np.ndarray, scale: float) -> np.ndarray:
    if abs(float(scale) - 1.0) < 1e-9:
        return img
    h, w = int(img.shape[0]), int(img.shape[1])
    nw = max(1, int(round(w * float(scale))))
    nh = max(1, int(round(h * float(scale))))
    interp = cv2.INTER_AREA if float(scale) < 1.0 else cv2.INTER_LINEAR
    return cv2.resize(img, (nw, nh), interpolation=interp)


def _scores_map(hay: np.ndarray, templ: np.ndarray, *, mask: np.ndarray | None = None) -> np.ndarray:
    """Return a score map where higher is better.

    Uses TM_CCOEFF_NORMED for most cases, but switches to TM_SQDIFF_NORMED when
    the template variance is near zero.

    When a ``mask`` is supplied, we must choose a matching method that supports
    masking. OpenCV documents mask support only for TM_SQDIFF(_NORMED) and
    TM_CCORR_NORMED, so we fall back to TM_CCORR_NORMED for the "normal"
    correlation path.

    Returns
    -------
    np.ndarray
        2D array of scores.
    """

    if float(np.std(templ)) < 1e-6:
        # SQDIFF is stable for near-constant templates (solid colors, etc.).
        res = cv2.matchTemplate(hay, templ, cv2.TM_SQDIFF_NORMED, mask=mask)
        return 1.0 - res

    if mask is not None:
        # Use a mask-capable method.
        return cv2.matchTemplate(hay, templ, cv2.TM_CCORR_NORMED, mask=mask)

    return cv2.matchTemplate(hay, templ, cv2.TM_CCOEFF_NORMED)


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
    scales: list[float] | None = None,
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

    hay = imread_color(haystack_path, cache=False)

    # Needle images are often reused across many polling attempts; cache decoding.
    needle_img = imread_color(needle_path, cache=True)

    x0, y0 = 0, 0
    if region is not None:
        x0, y0 = region.x, region.y
        hay = hay[region.y : region.y + region.h, region.x : region.x + region.w]

    # If we have needle metadata with match areas, use the multi-area matcher.
    needle_meta = try_load_needle(needle_path)

    scale_list = _normalize_scales(scales)
    best_any: ImageMatch | None = None
    best_ok: ImageMatch | None = None
    best_err: str | None = None

    for s in scale_list:
        templ = _resize_needle(needle_img, s)
        meta_s = scale_needle(needle_meta, s) if needle_meta is not None else None

        # Multi-area needles.
        if meta_s is not None and meta_s.match_areas:
            try:
                if float(threshold) < 0:
                    (mx, my), score, w, h = _multi_area_best_match(hay, templ, meta_s)
                else:
                    (mx, my), score = _multi_area_template_match(hay, templ, meta_s, threshold=threshold)
                    areas = meta_s.match_areas
                    min_x = min(a.xpos for a in areas)
                    min_y = min(a.ypos for a in areas)
                    max_x = max(a.xpos + a.width for a in areas)
                    max_y = max(a.ypos + a.height for a in areas)
                    w = int(max_x - min_x)
                    h = int(max_y - min_y)

                m = ImageMatch(x=int(mx + x0), y=int(my + y0), score=float(score), w=int(w), h=int(h), scale=float(s))
                if best_any is None or m.score > best_any.score:
                    best_any = m

                if float(threshold) < 0 or m.score >= float(threshold):
                    if best_ok is None or m.score > best_ok.score:
                        best_ok = m
                continue
            except Exception as exc:  # noqa: BLE001
                # Best-effort: still compute the best candidate score so the
                # caller can see *what* it matched.
                try:
                    (mx, my), score, w, h = _multi_area_best_match(hay, templ, meta_s)
                    m = ImageMatch(x=int(mx + x0), y=int(my + y0), score=float(score), w=int(w), h=int(h), scale=float(s))
                    if best_any is None or m.score > best_any.score:
                        best_any = m
                except Exception:
                    pass
                best_err = str(exc)
                continue

        # Full-template match.
        if hay.shape[0] < templ.shape[0] or hay.shape[1] < templ.shape[1]:
            # Skip this scale if it doesn't fit.
            continue

        mask = None
        if meta_s is not None and meta_s.exclude_areas and not meta_s.match_areas:
            # openQA-style exclude areas without explicit match areas: treat the
            # full needle as the match region, but mask out unstable pixels.
            mask = _mask_for_patch(
                int(templ.shape[1]),
                int(templ.shape[0]),
                patch_offset_x=0,
                patch_offset_y=0,
                exclude_areas=meta_s.exclude_areas,
            )

        scores = _scores_map(hay, templ, mask=mask)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(scores)
        score = float(max_val)
        m = ImageMatch(
            x=int(max_loc[0] + x0),
            y=int(max_loc[1] + y0),
            score=score,
            w=int(templ.shape[1]),
            h=int(templ.shape[0]),
            scale=float(s),
        )
        if best_any is None or m.score > best_any.score:
            best_any = m
        if float(threshold) < 0 or score >= float(threshold):
            if best_ok is None or m.score > best_ok.score:
                best_ok = m

    if best_any is None:
        raise ValueError("Needle is larger than search region")

    if float(threshold) < 0:
        return best_any

    if best_ok is None:
        msg = f"ImageSearch did not meet threshold. best={best_any.score:.3f} threshold={float(threshold):.3f}"
        if best_err:
            msg += f" ({best_err})"
        raise RuntimeError(msg)

    return best_ok


def image_search_all_file(
    haystack_path: Path,
    needle_path: Path,
    *,
    region: Region | None = None,
    threshold: float = 0.8,
    scales: list[float] | None = None,
    max_results: int = 50,
    overlap_threshold: float = 0.3,
    sort: str = "score",
    scan_order: str = "tlbr",
) -> list[ImageMatch]:
    """Find **all** matches of ``needle`` in ``haystack``.

    This is VHK's pragmatic "FindAll" primitive inspired by SikuliX/AutoIt
    workflows: return multiple detections so macros can "click all checkboxes"
    style UIs.

    Implementation notes
    --------------------
    - Template matching yields many overlapping detections around each instance.
      We filter by `threshold`, then apply non-maximum suppression (NMS) to
      collapse overlaps into one match per visual instance.
    - When multi-scale search is enabled, we collect candidates across scales
      and run NMS globally.
    """

    hay = imread_color(haystack_path, cache=False)

    # Needle images are often reused across many polling attempts; cache decoding.
    needle_img = imread_color(needle_path, cache=True)

    x0, y0 = 0, 0
    if region is not None:
        x0, y0 = region.x, region.y
        hay = hay[region.y : region.y + region.h, region.x : region.x + region.w]

    if hay.size == 0:
        return []

    sort_mode = (sort or "score").strip().lower()
    if sort_mode not in {"score", "scan"}:
        raise ValueError("sort must be 'score' or 'scan'")
    sy, sx = _scan_sort_key(scan_order)

    scale_list = _normalize_scales(scales)
    needle_meta = try_load_needle(needle_path)

    # Collect candidates across scales.
    boxes: list[list[int]] = []
    scores_all: list[float] = []
    metas: list[tuple[int, int, float]] = []  # (w, h, scale)

    def _add_candidates_from_score_map(
        score_map: np.ndarray,
        *,
        w: int,
        h: int,
        scale: float,
        per_area_maps: list[np.ndarray] | None = None,
        per_area_thresholds: list[float] | None = None,
    ) -> None:
        if score_map.size == 0:
            return

        # Candidates above the minimum threshold. For multi-area needles,
        # per-area checks are applied below.
        thr_min = float(threshold)
        if per_area_thresholds:
            thr_min = min(float(t) for t in per_area_thresholds)

        ys, xs = np.where(score_map >= thr_min)
        if xs.size == 0:
            return

        # Guardrail: in pathological cases (too-low threshold), the candidate
        # set can explode. Bound it by selecting top-K scores.
        max_candidates = max(10_000, int(max_results) * 500)
        if xs.size > max_candidates:
            flat_scores = score_map[ys, xs]
            idx = np.argpartition(flat_scores, -max_candidates)[-max_candidates:]
            ys = ys[idx]
            xs = xs[idx]

        for x, y in zip(xs.tolist(), ys.tolist()):
            s = float(score_map[int(y), int(x)])
            if s < float(threshold):
                continue
            if per_area_maps is not None and per_area_thresholds is not None:
                ok = True
                for amap, thr in zip(per_area_maps, per_area_thresholds):
                    if float(amap[int(y), int(x)]) < float(thr):
                        ok = False
                        break
                if not ok:
                    continue
            boxes.append([int(x), int(y), int(w), int(h)])
            scores_all.append(float(s))
            metas.append((int(w), int(h), float(scale)))

    for s in scale_list:
        templ = _resize_needle(needle_img, s)
        meta_s = scale_needle(needle_meta, s) if needle_meta is not None else None

        # Multi-area needles: compute the combined score map (min across areas)
        # and enforce per-area thresholds per candidate.
        if meta_s is not None and meta_s.match_areas:
            areas = meta_s.match_areas
            min_x = min(a.xpos for a in areas)
            min_y = min(a.ypos for a in areas)
            max_x = max(a.xpos + a.width for a in areas)
            max_y = max(a.ypos + a.height for a in areas)
            w = int(max_x - min_x)
            h = int(max_y - min_y)

            # Reuse the multi-area derivation logic: build aligned area score
            # maps and combine by min.
            needle_crop = templ[min_y:max_y, min_x:max_x]
            if hay.shape[0] < needle_crop.shape[0] or hay.shape[1] < needle_crop.shape[1]:
                continue

            full_h = hay.shape[0] - needle_crop.shape[0] + 1
            full_w = hay.shape[1] - needle_crop.shape[1] + 1

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
                    exclude_areas=meta_s.exclude_areas,
                )
                patch_scores = _scores_map(hay, patch, mask=mask)
                patch_aligned = patch_scores[ay : ay + full_h, ax : ax + full_w].astype(np.float32)
                aligned_maps.append(patch_aligned)
                area_thresholds.append(a.threshold(threshold))

            if not aligned_maps:
                continue
            stacked = np.stack(aligned_maps, axis=0)
            combined = np.min(stacked, axis=0)
            _add_candidates_from_score_map(
                combined,
                w=w,
                h=h,
                scale=float(s),
                per_area_maps=aligned_maps,
                per_area_thresholds=area_thresholds,
            )
            continue

        # Full-template match candidates.
        if hay.shape[0] < templ.shape[0] or hay.shape[1] < templ.shape[1]:
            continue

        mask = None
        if meta_s is not None and meta_s.exclude_areas and not meta_s.match_areas:
            mask = _mask_for_patch(
                int(templ.shape[1]),
                int(templ.shape[0]),
                patch_offset_x=0,
                patch_offset_y=0,
                exclude_areas=meta_s.exclude_areas,
            )

        score_map = _scores_map(hay, templ, mask=mask)
        _add_candidates_from_score_map(score_map, w=int(templ.shape[1]), h=int(templ.shape[0]), scale=float(s))

    if not boxes:
        return []

    b = np.asarray(boxes, dtype=np.int32)
    sc = np.asarray(scores_all, dtype=np.float32)
    keep = _nms_iou(b, sc, iou_threshold=float(overlap_threshold), max_results=int(max_results))

    out: list[ImageMatch] = []
    for idx in keep:
        x, y, w, h = [int(v) for v in b[idx].tolist()]
        score = float(sc[idx])
        _w, _h, scale = metas[idx]
        out.append(
            ImageMatch(
                x=int(x + x0),
                y=int(y + y0),
                w=int(w),
                h=int(h),
                score=float(score),
                scale=float(scale),
            )
        )

    if sort_mode == "score":
        out.sort(key=lambda m: (m.score, -m.h, -m.w), reverse=True)
    else:
        out.sort(key=lambda m: (sy * m.y, sx * m.x))

    # Hard cap again after sorting (NMS already caps, but this is cheap safety).
    return out[: int(max_results)]


def _multi_area_best_match(
    hay: np.ndarray,
    needle_img: np.ndarray,
    needle_meta: Needle,
) -> tuple[tuple[int, int], float, int, int]:
    """Return the best match location for a multi-area needle without enforcing thresholds.

    Returns
    -------
    (x, y), score, w, h
        (x, y) is the top-left of the effective match bbox (union of match areas)
        in the haystack coordinate space.

    Notes
    -----
    This is intended for debugging / preview tooling ("what is the best candidate?"),
    not for pass/fail assertions.
    """

    areas = needle_meta.match_areas
    exclude = needle_meta.exclude_areas

    min_x = min(a.xpos for a in areas)
    min_y = min(a.ypos for a in areas)
    max_x = max(a.xpos + a.width for a in areas)
    max_y = max(a.ypos + a.height for a in areas)

    needle_crop = needle_img[min_y:max_y, min_x:max_x]
    crop_h, crop_w = int(needle_crop.shape[0]), int(needle_crop.shape[1])

    if hay.shape[0] < crop_h or hay.shape[1] < crop_w:
        raise ValueError('Needle is larger than search region')

    full_h = hay.shape[0] - crop_h + 1
    full_w = hay.shape[1] - crop_w + 1

    aligned_maps: list[np.ndarray] = []
    for a in areas:
        ax = int(a.xpos - min_x)
        ay = int(a.ypos - min_y)
        aw = int(a.width)
        ah = int(a.height)
        patch = needle_crop[ay:ay+ah, ax:ax+aw]
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
        patch_aligned = patch_scores[ay:ay+full_h, ax:ax+full_w].astype(np.float32)
        aligned_maps.append(patch_aligned)

    if not aligned_maps:
        raise ValueError('Needle has match areas but none produced valid patches')

    stacked = np.stack(aligned_maps, axis=0)
    scores = np.min(stacked, axis=0)

    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(scores)
    score = float(max_val)
    x, y = int(max_loc[0]), int(max_loc[1])
    w = int(max_x - min_x)
    h = int(max_y - min_y)
    return (x, y), score, w, h


def best_image_match_file(
    haystack_path: Path,
    needle_path: Path,
    *,
    region: Region | None = None,
    scales: list[float] | None = None,
) -> ImageMatch:
    """Return the best match for a needle in a haystack image (no threshold enforcement).

    This is useful for debugging tools like `vhk preview-needle`, where you want
    to see the best candidate even if it's below the pass threshold.
    """

    hay = cv2.imread(str(haystack_path), cv2.IMREAD_COLOR)
    if hay is None:
        raise FileNotFoundError(f'Cannot read haystack image: {haystack_path}')

    needle_img = cv2.imread(str(needle_path), cv2.IMREAD_COLOR)
    if needle_img is None:
        raise FileNotFoundError(f'Cannot read needle image: {needle_path}')

    x0, y0 = 0, 0
    if region is not None:
        x0, y0 = region.x, region.y
        hay = hay[region.y:region.y+region.h, region.x:region.x+region.w]

    needle_meta = try_load_needle(needle_path)

    scale_list = _normalize_scales(scales)
    best: ImageMatch | None = None

    for s in scale_list:
        templ = _resize_needle(needle_img, s)
        meta_s = scale_needle(needle_meta, s) if needle_meta is not None else None

        if meta_s is not None and meta_s.match_areas:
            try:
                (mx, my), score, w, h = _multi_area_best_match(hay, templ, meta_s)
            except Exception:
                continue
            m = ImageMatch(x=int(mx + x0), y=int(my + y0), score=float(score), w=int(w), h=int(h), scale=float(s))
            if best is None or m.score > best.score:
                best = m
            continue

        if hay.shape[0] < templ.shape[0] or hay.shape[1] < templ.shape[1]:
            continue

        mask = None
        if meta_s is not None and meta_s.exclude_areas and not meta_s.match_areas:
            mask = _mask_for_patch(
                int(templ.shape[1]),
                int(templ.shape[0]),
                patch_offset_x=0,
                patch_offset_y=0,
                exclude_areas=meta_s.exclude_areas,
            )

        scores = _scores_map(hay, templ, mask=mask)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(scores)
        score = float(max_val)
        m = ImageMatch(
            x=int(max_loc[0] + x0),
            y=int(max_loc[1] + y0),
            score=score,
            w=int(templ.shape[1]),
            h=int(templ.shape[0]),
            scale=float(s),
        )
        if best is None or m.score > best.score:
            best = m

    if best is None:
        raise ValueError('Needle is larger than search region')
    return best


def preview_image_search_file(
    haystack_path: Path,
    needle_path: Path,
    *,
    region: Region | None = None,
    threshold: float = 0.8,
    scales: list[float] | None = None,
) -> tuple[ImageMatch, bool, str | None]:
    """Attempt an image search; always return the best match.

    Returns
    -------
    (match, ok, error)
        ok is True if the strict `image_search_file` check passed.
        If it failed, match is the best candidate (no threshold enforcement).
    """

    try:
        m = image_search_file(haystack_path, needle_path, region=region, threshold=threshold, scales=scales)
        return m, True, None
    except Exception as exc:  # noqa: BLE001
        best = best_image_match_file(haystack_path, needle_path, region=region, scales=scales)
        return best, False, str(exc)
