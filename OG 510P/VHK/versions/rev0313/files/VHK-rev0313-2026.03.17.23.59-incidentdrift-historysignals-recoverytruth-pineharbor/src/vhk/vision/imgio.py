from __future__ import annotations

"""Small image IO helpers.

VHK's runtime often polls for a condition (e.g. WaitForImage / VisualAssert).
During polling, the *current* capture changes every attempt, but the *reference*
assets (needles, baselines) are constant.

Reading and decoding the same PNG repeatedly can dominate CPU time in tight
loops, so we provide a tiny cache keyed by (path, mtime_ns).

The cache is intentionally in-process only and is safe to ignore in callers:
- if a file changes, its mtime changes and the cache key invalidates
- if a file is missing, the underlying reader fails as usual

Callers must treat returned arrays as immutable.
"""

from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np


@lru_cache(maxsize=256)
def _imread_color_cached(path_str: str, mtime_ns: int) -> np.ndarray:
    img = cv2.imread(path_str, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {path_str}")
    return img


def imread_color(path: Path, *, cache: bool = False) -> np.ndarray:
    """Read a color image from disk.

    Parameters
    ----------
    path:
        Image path.
    cache:
        When True, cache decoded pixels by (path, mtime_ns). This is intended for
        relatively-static assets like needles/baselines.
    """

    if not cache:
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"Cannot read image: {path}")
        return img

    try:
        mtime_ns = int(path.stat().st_mtime_ns)
    except OSError:
        mtime_ns = 0

    return _imread_color_cached(str(path), mtime_ns)


def _clear_imgio_caches() -> None:
    """Test helper: clear internal caches."""

    _imread_color_cached.cache_clear()
