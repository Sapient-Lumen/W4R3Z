import json
from pathlib import Path

import cv2
import numpy as np

from vhk.vision.match import image_search_file


def test_image_search_respects_exclude_area(tmp_path: Path):
    """Exclude areas should mask out dynamic pixels in the reference."""

    # Needle: 40x30 with a stable white border and a dynamic center.
    needle = np.zeros((30, 40, 3), dtype=np.uint8)
    needle[:, :] = (0, 0, 0)
    needle[2:28, 2:38] = (255, 255, 255)
    needle[10:20, 15:25] = (0, 255, 0)  # dynamic region (green)

    # Haystack: paste needle, but flip the dynamic center to a different color.
    hay = np.zeros((80, 100, 3), dtype=np.uint8)
    nx, ny = 33, 21
    hay[ny : ny + needle.shape[0], nx : nx + needle.shape[1]] = needle
    hay[ny + 10 : ny + 20, nx + 15 : nx + 25] = (0, 0, 255)  # dynamic differs (red)

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)

    meta = {
        "tags": ["demo"],
        "area": [
            {"type": "match", "xpos": 0, "ypos": 0, "width": 40, "height": 30, "match": 90},
            {"type": "exclude", "xpos": 15, "ypos": 10, "width": 10, "height": 10},
        ],
    }
    needle_path.with_suffix(".json").write_text(json.dumps(meta))

    m = image_search_file(hay_path, needle_path, threshold=0.9)
    assert (m.x, m.y) == (nx, ny)


def test_image_search_uses_per_area_thresholds(tmp_path: Path):
    """Per-area match thresholds (openQA 'match' %) should be honored."""

    needle = np.zeros((30, 30, 3), dtype=np.uint8)
    # Area A: very distinctive
    needle[2:12, 2:12] = (255, 255, 255)
    # Area B: low-contrast gray (will score worse)
    needle[18:28, 18:28] = (40, 40, 40)

    hay = np.zeros((80, 90, 3), dtype=np.uint8)
    nx, ny = 20, 25
    hay[ny : ny + 30, nx : nx + 30] = needle

    # Slightly perturb area B in hay to reduce similarity.
    hay[ny + 18 : ny + 28, nx + 18 : nx + 28] = (45, 45, 45)

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)

    meta = {
        "tags": ["demo"],
        "area": [
            {"type": "match", "xpos": 2, "ypos": 2, "width": 10, "height": 10, "match": 90},
            # Allow the low-contrast area to be looser.
            {"type": "match", "xpos": 18, "ypos": 18, "width": 10, "height": 10, "match": 50},
        ],
    }
    needle_path.with_suffix(".json").write_text(json.dumps(meta))

    m = image_search_file(hay_path, needle_path, threshold=0.9)
    # Returned bbox is union of match areas: (2,2) -> (28,28)
    assert (m.x, m.y) == (nx + 2, ny + 2)