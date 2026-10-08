from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from vhk.vision.assets import NeedleArea, try_load_needle


@dataclass
class VisualDiff:
    changed_pixels: int
    total_pixels: int
    change_ratio: float
    max_channel_delta: int


def _build_compare_mask(shape: tuple[int, int], *, match_areas: list[NeedleArea], exclude_areas: list[NeedleArea]) -> np.ndarray:
    h, w = int(shape[0]), int(shape[1])
    if match_areas:
        mask = np.zeros((h, w), dtype=bool)
        for a in match_areas:
            x1 = max(0, int(a.xpos))
            y1 = max(0, int(a.ypos))
            x2 = min(w, int(a.xpos + a.width))
            y2 = min(h, int(a.ypos + a.height))
            if x2 > x1 and y2 > y1:
                mask[y1:y2, x1:x2] = True
    else:
        mask = np.ones((h, w), dtype=bool)

    for a in exclude_areas:
        x1 = max(0, int(a.xpos))
        y1 = max(0, int(a.ypos))
        x2 = min(w, int(a.xpos + a.width))
        y2 = min(h, int(a.ypos + a.height))
        if x2 > x1 and y2 > y1:
            mask[y1:y2, x1:x2] = False
    return mask


def _load_compare_inputs(current_path: Path, baseline_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    cur = cv2.imread(str(current_path), cv2.IMREAD_COLOR)
    if cur is None:
        raise FileNotFoundError(f"Cannot read current image: {current_path}")

    base = cv2.imread(str(baseline_path), cv2.IMREAD_COLOR)
    if base is None:
        raise FileNotFoundError(f"Cannot read baseline image: {baseline_path}")

    if cur.shape != base.shape:
        raise ValueError(
            f"Visual compare requires same-size images. current={cur.shape[:2]} baseline={base.shape[:2]}"
        )

    meta = try_load_needle(baseline_path)
    match_areas = meta.match_areas if meta else []
    exclude_areas = meta.exclude_areas if meta else []
    mask = _build_compare_mask(cur.shape[:2], match_areas=match_areas, exclude_areas=exclude_areas)

    diff = np.abs(cur.astype(np.int16) - base.astype(np.int16))
    max_delta = np.max(diff, axis=2)
    return cur, base, mask, max_delta


def _summarize(mask: np.ndarray, max_delta: np.ndarray, *, color_tolerance: int) -> tuple[VisualDiff, np.ndarray]:
    changed = (max_delta > int(color_tolerance)) & mask
    changed_pixels = int(np.count_nonzero(changed))
    total_pixels = int(np.count_nonzero(mask))
    ratio = (changed_pixels / total_pixels) if total_pixels else 0.0
    max_channel_delta = int(max_delta[mask].max()) if total_pixels else 0
    return (
        VisualDiff(
            changed_pixels=changed_pixels,
            total_pixels=total_pixels,
            change_ratio=float(ratio),
            max_channel_delta=max_channel_delta,
        ),
        changed,
    )


def visual_compare_file(
    current_path: Path,
    baseline_path: Path,
    *,
    color_tolerance: int = 0,
) -> VisualDiff:
    """Compare two same-size images and quantify changed pixels.

    If the baseline image has an openQA-style sidecar JSON, compare semantics are:
      - if any `match` areas exist, only those areas are compared
      - any `exclude` areas are ignored
    Otherwise the full image is compared.
    """

    _, _, mask, max_delta = _load_compare_inputs(current_path, baseline_path)
    diff, _ = _summarize(mask, max_delta, color_tolerance=color_tolerance)
    return diff


def write_visual_diff_image(
    current_path: Path,
    baseline_path: Path,
    out_path: Path,
    *,
    color_tolerance: int = 0,
) -> VisualDiff:
    """Write a simple debug image highlighting changed pixels.

    The output is a mostly-baseline image with changed pixels painted red and masked
    out areas dimmed. This makes timeouts and visual mismatches much easier to audit.
    """

    cur, base, mask, max_delta = _load_compare_inputs(current_path, baseline_path)
    diff, changed = _summarize(mask, max_delta, color_tolerance=color_tolerance)

    vis = base.copy()
    vis[~mask] = (vis[~mask] * 0.35).astype(np.uint8)
    vis[changed] = np.array([0, 0, 255], dtype=np.uint8)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), vis)
    return diff
