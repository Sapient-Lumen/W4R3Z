from pathlib import Path

import cv2
import numpy as np

from vhk.vision.match import image_search_file


def test_image_search_file(tmp_path: Path):
    hay = np.zeros((120, 160, 3), dtype=np.uint8)
    # draw a white square at (40, 30) size 20x20
    hay[30:50, 40:60] = 255

    needle = np.zeros((20, 20, 3), dtype=np.uint8)
    needle[:, :] = 255

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)

    m = image_search_file(hay_path, needle_path, threshold=0.9)
    assert m.x == 40
    assert m.y == 30
    assert m.score >= 0.9
