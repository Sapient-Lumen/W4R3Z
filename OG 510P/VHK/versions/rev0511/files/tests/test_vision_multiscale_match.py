from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from vhk.vision.match import best_image_match_file, image_search_file


def _write_scaled_pattern(tmp_path: Path) -> tuple[Path, Path]:
    """Create a needle and a haystack containing a scaled copy of that needle."""

    needle = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.rectangle(needle, (2, 2), (17, 17), (255, 255, 255), -1)
    cv2.circle(needle, (10, 10), 3, (0, 0, 0), -1)

    # Use the same interpolation as VHK's internal multi-scale matcher (linear
    # for upscales) so scores are deterministic.
    scaled = cv2.resize(needle, (24, 24), interpolation=cv2.INTER_LINEAR)

    hay = np.zeros((120, 160, 3), dtype=np.uint8)
    hay[30:54, 40:64] = scaled

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)
    return hay_path, needle_path


def test_image_search_file_multiscale_picks_best_scale(tmp_path: Path) -> None:
    hay_path, needle_path = _write_scaled_pattern(tmp_path)
    m = image_search_file(hay_path, needle_path, threshold=0.95, scales=[1.0, 1.2])
    assert (m.x, m.y) == (40, 30)
    assert abs(m.scale - 1.2) < 1e-6
    assert m.score >= 0.95


def test_best_image_match_file_multiscale_returns_best_candidate(tmp_path: Path) -> None:
    hay_path, needle_path = _write_scaled_pattern(tmp_path)
    m = best_image_match_file(hay_path, needle_path, scales=[1.0, 1.2])
    assert (m.x, m.y) == (40, 30)
    assert abs(m.scale - 1.2) < 1e-6
