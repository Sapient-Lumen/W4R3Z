import json
from pathlib import Path

import cv2
import numpy as np

from vhk.vision.match import image_search_file


def test_image_search_with_needle_json_match_area(tmp_path: Path):
    # Haystack: black with a needle pasted in.
    hay = np.zeros((90, 120, 3), dtype=np.uint8)

    needle = np.zeros((30, 30, 3), dtype=np.uint8)

    # Create a distinctive sub-region (10x12) inside the needle.
    # We'll define it as the match area.
    ax, ay, aw, ah = 5, 7, 10, 12
    needle[ay : ay + ah, ax : ax + aw] = (255, 255, 255)

    # Paste full needle at (nx, ny)
    nx, ny = 40, 20
    hay[ny : ny + needle.shape[0], nx : nx + needle.shape[1]] = needle

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)

    # openQA-style metadata next to needle.png
    meta = {
        "tags": ["demo"],
        "area": [
            {
                "type": "match",
                "xpos": ax,
                "ypos": ay,
                "width": aw,
                "height": ah,
                "click_point": {"xpos": aw // 2, "ypos": ah // 2},
            }
        ],
    }
    needle_path.with_suffix(".json").write_text(json.dumps(meta))

    m = image_search_file(hay_path, needle_path, threshold=0.9)

    # Because VHK matches using the union bbox of match areas,
    # the returned location is the bbox top-left, not the full needle top-left.
    assert m.x == nx + ax
    assert m.y == ny + ay
    assert m.w == aw
    assert m.h == ah
    assert m.score >= 0.9
