from __future__ import annotations

from pathlib import Path

import cv2

from vhk.vision.assets import Needle, scale_needle
from vhk.vision.match import ImageMatch


def annotate_match(
    haystack_path: Path,
    out_path: Path,
    match: ImageMatch,
    *,
    needle_meta: Needle | None = None,
    click_xy: tuple[int, int] | None = None,
    threshold: float | None = None,
    ok: bool | None = None,
) -> Path:
    """Write an annotated copy of `haystack_path` highlighting the match.

    Notes
    -----
    This is intended for debugging and review tooling. Colors are chosen for
    visibility, not theme compatibility.
    """

    img = cv2.imread(str(haystack_path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read haystack image: {haystack_path}")

    x1, y1 = int(match.x), int(match.y)
    x2, y2 = int(match.x + match.w), int(match.y + match.h)

    # Main match bbox.
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Draw match/exclude areas if present.
    meta_draw = needle_meta
    if meta_draw is not None and abs(float(getattr(match, "scale", 1.0)) - 1.0) > 1e-9:
        # Match bboxes and click points are computed against the scaled needle.
        # Scale areas for overlay so the drawn rectangles line up.
        meta_draw = scale_needle(meta_draw, float(match.scale))

    if meta_draw is not None:
        # Match coordinates are relative to:
        # - the union bbox of match areas when present, or
        # - the full needle image when no match areas exist.
        if meta_draw.match_areas:
            min_x = min(a.xpos for a in meta_draw.match_areas)
            min_y = min(a.ypos for a in meta_draw.match_areas)
        else:
            min_x, min_y = 0, 0

        for a in meta_draw.match_areas:
            ax1 = x1 + int(a.xpos - min_x)
            ay1 = y1 + int(a.ypos - min_y)
            ax2 = ax1 + int(a.width)
            ay2 = ay1 + int(a.height)
            cv2.rectangle(img, (ax1, ay1), (ax2, ay2), (255, 0, 0), 1)

        for a in meta_draw.exclude_areas:
            ax1 = x1 + int(a.xpos - min_x)
            ay1 = y1 + int(a.ypos - min_y)
            ax2 = ax1 + int(a.width)
            ay2 = ay1 + int(a.height)
            cv2.rectangle(img, (ax1, ay1), (ax2, ay2), (128, 128, 128), 1)

        for a in meta_draw.ocr_areas:
            ax1 = x1 + int(a.xpos - min_x)
            ay1 = y1 + int(a.ypos - min_y)
            ax2 = ax1 + int(a.width)
            ay2 = ay1 + int(a.height)
            # Orange-ish (BGR) to match openQA's "OCR area" mental model.
            cv2.rectangle(img, (ax1, ay1), (ax2, ay2), (0, 165, 255), 1)

    if click_xy is not None:

        cx, cy = int(click_xy[0]), int(click_xy[1])
        cv2.drawMarker(img, (cx, cy), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=18, thickness=2)

    # Overlay text.
    label = f"score={match.score:.3f}"
    if threshold is not None:
        label += f" thr={float(threshold):.3f}"
    if ok is not None:
        label += " OK" if ok else " FAIL"

    # Put label near top-left but inside image bounds.
    lx, ly = max(0, x1), max(20, y1 - 8)
    cv2.putText(img, label, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, label, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    out_path = out_path.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(out_path), img):
        raise RuntimeError(f"Failed to write annotated image: {out_path}")
    return out_path
