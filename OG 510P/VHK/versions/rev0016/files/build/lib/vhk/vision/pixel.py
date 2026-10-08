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


def parse_color(color: str | list[int]) -> tuple[int, int, int]:
    """Parse a color into BGR (OpenCV) order.

    Accepts:
      - "#RRGGBB"
      - "R,G,B"
      - [R, G, B]

    Returns
    -------
    (b, g, r)
    """

    if isinstance(color, list):
        if len(color) != 3:
            raise ValueError("color list must have 3 integers [R,G,B]")
        r, g, b = (int(color[0]), int(color[1]), int(color[2]))
        return (b, g, r)

    s = color.strip()
    if s.startswith("#") and len(s) == 7:
        r = int(s[1:3], 16)
        g = int(s[3:5], 16)
        b = int(s[5:7], 16)
        return (b, g, r)

    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        if len(parts) != 3:
            raise ValueError("color string must be 'R,G,B'")
        r, g, b = (int(parts[0]), int(parts[1]), int(parts[2]))
        return (b, g, r)

    raise ValueError("Unsupported color format. Use '#RRGGBB', 'R,G,B', or [R,G,B].")


def pixel_search_file(
    image_path: Path,
    *,
    color: str | list[int],
    region: Region | None = None,
    tolerance: float = 0.0,
) -> PixelMatch:
    """Find the closest pixel to `color` within an image.

    tolerance is interpreted as Euclidean distance in BGR space.
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
    diff = img.astype(np.int32) - target
    dist2 = np.sum(diff * diff, axis=2, dtype=np.int32)
    dist = np.sqrt(dist2.astype(np.float32))

    idx = int(dist.argmin())
    min_val = float(dist.flat[idx])
    if min_val > float(tolerance):
        raise RuntimeError(f"PixelSearch did not meet tolerance. best={min_val:.3f} tol={tolerance:.3f}")

    y, x = np.unravel_index(idx, dist.shape)
    return PixelMatch(x=int(x + x0), y=int(y + y0), dist=min_val)
