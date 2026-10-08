from pathlib import Path

import cv2
import numpy as np

from vhk.vision.pixel import pixel_search_file
from vhk.core.models import Region


def test_pixel_search_exact(tmp_path: Path):
    img = np.zeros((40, 50, 3), dtype=np.uint8)
    # Set a single pixel to red (RGB), which is BGR (0,0,255)
    img[12, 34] = (0, 0, 255)

    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    m = pixel_search_file(p, color="#FF0000", tolerance=0)
    assert (m.x, m.y) == (34, 12)
    assert m.dist == 0.0


def test_pixel_search_region(tmp_path: Path):
    img = np.zeros((40, 50, 3), dtype=np.uint8)
    img[20, 10] = (0, 255, 0)  # green
    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    r = Region(x=0, y=15, w=30, h=20)
    m = pixel_search_file(p, color=[0, 255, 0], region=r, tolerance=0)
    assert (m.x, m.y) == (10, 20)
