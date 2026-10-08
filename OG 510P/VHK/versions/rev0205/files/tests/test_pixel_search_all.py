from pathlib import Path

import cv2
import numpy as np

from vhk.core.models import Region
from vhk.vision.pixel import pixel_search_all_file


def test_pixel_search_all_raw_scan_order(tmp_path: Path):
    img = np.zeros((5, 5, 3), dtype=np.uint8)
    img[0, 0] = (0, 0, 255)
    img[4, 4] = (0, 0, 255)

    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    hits = pixel_search_all_file(p, color="#FF0000", tolerance=0, max_results=10, group="none", sort="scan", scan_order="tlbr")
    assert [(h.x, h.y) for h in hits] == [(0, 0), (4, 4)]

    hits2 = pixel_search_all_file(p, color="#FF0000", tolerance=0, max_results=10, group="none", sort="scan", scan_order="brtl")
    assert [(h.x, h.y) for h in hits2] == [(4, 4), (0, 0)]


def test_pixel_search_all_connected_components_bbox(tmp_path: Path):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    # Two green blobs
    img[1:3, 1:4] = (0, 255, 0)
    img[7:9, 6:9] = (0, 255, 0)

    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    hits = pixel_search_all_file(
        p,
        color="#00FF00",
        tolerance=0,
        tolerance_mode="per_channel",
        group="connected",
        pick="center",
        min_area=1,
        max_results=10,
        sort="scan",
        scan_order="tlbr",
    )
    assert len(hits) == 2

    # First blob bbox
    h0 = hits[0]
    assert h0.bbox_x == 1
    assert h0.bbox_y == 1
    assert h0.w == 3
    assert h0.h == 2
    assert h0.area == 6

    # Second blob bbox
    h1 = hits[1]
    assert h1.bbox_x == 6
    assert h1.bbox_y == 7
    assert h1.w == 3
    assert h1.h == 2
    assert h1.area == 6


def test_pixel_search_all_connected_step_span(tmp_path: Path):
    # Two pixels that are adjacent in the sampled grid when step=2
    img = np.zeros((6, 6, 3), dtype=np.uint8)
    img[0, 0] = (0, 0, 255)
    img[0, 2] = (0, 0, 255)

    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    hits = pixel_search_all_file(
        p,
        color="#FF0000",
        tolerance=0,
        group="connected",
        pick="first",
        step=2,
        phase_x=0,
        phase_y=0,
        max_results=10,
    )

    assert len(hits) == 1
    h = hits[0]
    # Sampled bbox spans two sampled pixels horizontally => original span 3 pixels (0..2).
    assert h.bbox_x == 0
    assert h.bbox_y == 0
    assert h.w == 3
    assert h.h == 1


def test_pixel_search_all_respects_region_offset(tmp_path: Path):
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    img[10, 10] = (0, 0, 255)
    p = tmp_path / "img.png"
    cv2.imwrite(str(p), img)

    r = Region(x=5, y=5, w=10, h=10)
    hits = pixel_search_all_file(p, color="#FF0000", tolerance=0, region=r, max_results=10)
    assert len(hits) == 1
    assert (hits[0].x, hits[0].y) == (10, 10)
