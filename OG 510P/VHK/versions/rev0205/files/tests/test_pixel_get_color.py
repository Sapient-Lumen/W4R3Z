from pathlib import Path

import cv2
import numpy as np

import pytest

from vhk.core.models import Region
from vhk.vision.pixel import parse_color, pixel_get_color_file


def test_parse_color_supports_0x_rgb_and_bgr_prefix():
    # 0xRRGGBB -> BGR tuple (OpenCV)
    assert parse_color("0xFF0000") == (0, 0, 255)  # red
    # bgr:0xBBGGRR
    assert parse_color("bgr:0xFF0000") == (255, 0, 0)  # blue


def test_pixel_get_color_file_basic(tmp_path: Path):
    img = np.zeros((5, 6, 3), dtype=np.uint8)
    # Set pixel at (x=4,y=1) to RGB=(255,128,0) => BGR=(0,128,255)
    img[1, 4] = (0, 128, 255)
    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    c = pixel_get_color_file(p, x=4, y=1)
    assert (c.r, c.g, c.b) == (255, 128, 0)
    assert c.hex == "#FF8000"
    assert c.ahk_hex == "0xFF8000"


def test_pixel_get_color_file_with_region_validation(tmp_path: Path):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[6, 7] = (10, 20, 30)  # BGR
    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    region = Region(x=5, y=5, w=4, h=4)
    c = pixel_get_color_file(p, x=7, y=6, region=region)
    assert (c.r, c.g, c.b) == (30, 20, 10)

    with pytest.raises(ValueError):
        pixel_get_color_file(p, x=1, y=1, region=region)
