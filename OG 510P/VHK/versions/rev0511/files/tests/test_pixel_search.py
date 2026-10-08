from pathlib import Path

import cv2
import numpy as np

import pytest

from vhk.vision.pixel import PixelSearchNoMatch, pixel_search_file
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


def test_pixel_search_per_channel_variation_mode(tmp_path: Path):
    # AHK-style "variation" is usually interpreted per-channel.
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    # Set pixel to (R,G,B)=(250,5,5) => BGR=(5,5,250)
    img[2, 3] = (5, 5, 250)
    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    # Search for pure red with variation 10 should match.
    m = pixel_search_file(p, color="#FF0000", tolerance=10, tolerance_mode="per_channel")
    assert (m.x, m.y) == (3, 2)
    assert m.dist <= 10




def test_pixel_search_step_and_phase(tmp_path: Path):
    # Put the target pixel on an "odd" coordinate so it is missed by step=2 phase (0,0),
    # but found by phase (1,1).
    img = np.zeros((6, 6, 3), dtype=np.uint8)
    img[:, :] = (255, 255, 255)
    img[1, 1] = (0, 0, 255)  # red in BGR

    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    m = pixel_search_file(p, color="#FF0000", tolerance=0, step=2, phase_x=1, phase_y=1)
    assert (m.x, m.y) == (1, 1)
    assert m.dist == 0.0

def test_pixel_search_raises_with_best_distance(tmp_path: Path):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[4, 4] = (0, 0, 200)  # near red but not exact
    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    with pytest.raises(PixelSearchNoMatch) as ei:
        pixel_search_file(p, color="#FF0000", tolerance=0)
    # Error carries the best distance + coords for wait loops.
    assert hasattr(ei.value, "dist")
    assert hasattr(ei.value, "x")
    assert hasattr(ei.value, "y")

def test_pixel_search_match_strategy_first_and_scan_order(tmp_path: Path):
    # Two exact matches; first strategy should respect scan order.
    img = np.zeros((5, 5, 3), dtype=np.uint8)
    img[0, 0] = (0, 0, 255)  # red at top-left
    img[4, 4] = (0, 0, 255)  # red at bottom-right

    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    m1 = pixel_search_file(p, color="#FF0000", tolerance=0, match_strategy="first", scan_order="tlbr")
    assert (m1.x, m1.y) == (0, 0)

    m2 = pixel_search_file(p, color="#FF0000", tolerance=0, match_strategy="first", scan_order="brtl")
    assert (m2.x, m2.y) == (4, 4)

    # Best strategy uses scan_order only as a tie-breaker when distances are equal.
    m3 = pixel_search_file(p, color="#FF0000", tolerance=0, match_strategy="best", scan_order="brtl")
    assert (m3.x, m3.y) == (4, 4)
