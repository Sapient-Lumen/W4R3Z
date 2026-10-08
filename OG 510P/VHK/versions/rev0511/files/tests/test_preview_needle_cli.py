from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from typer.testing import CliRunner

from vhk.cli import app
from vhk.vision.match import best_image_match_file, preview_image_search_file


runner = CliRunner()


def _write_square_images(tmp_path: Path) -> tuple[Path, Path]:
    hay = np.zeros((120, 160, 3), dtype=np.uint8)
    # Use a slightly dimmer target than the needle so we can reliably
    # exercise the "best candidate but below threshold" preview path.
    # (Constant-color templates use SQDIFF, which would otherwise yield a
    # perfect 1.0 score and make threshold-based failure tests flaky.)
    hay[30:50, 40:60] = 250

    needle = np.zeros((20, 20, 3), dtype=np.uint8)
    needle[:, :] = 255

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)
    return hay_path, needle_path


def test_best_image_match_file_returns_best_candidate(tmp_path: Path) -> None:
    hay_path, needle_path = _write_square_images(tmp_path)
    m = best_image_match_file(hay_path, needle_path)
    assert (m.x, m.y) == (40, 30)
    assert m.score > 0.9


def test_preview_image_search_file_reports_failure_but_returns_best(tmp_path: Path) -> None:
    hay_path, needle_path = _write_square_images(tmp_path)
    m, ok, err = preview_image_search_file(hay_path, needle_path, threshold=0.9999)
    assert ok is False
    assert err
    assert (m.x, m.y) == (40, 30)


def test_preview_needle_cli_json_and_annotated(tmp_path: Path) -> None:
    hay_path, needle_path = _write_square_images(tmp_path)
    out_img = tmp_path / "annotated.png"

    res = runner.invoke(
        app,
        [
            "preview-needle",
            str(needle_path),
            "--haystack",
            str(hay_path),
            "--threshold",
            "0.9",
            "--out-annotated",
            str(out_img),
            "--json",
        ],
    )
    assert res.exit_code == 0
    payload = json.loads(res.output)
    assert payload["ok"] is True
    assert payload["match"]["x"] == 40
    assert payload["match"]["y"] == 30
    assert Path(payload["annotated"]).exists()


def test_preview_needle_cli_check_exit_code(tmp_path: Path) -> None:
    hay_path, needle_path = _write_square_images(tmp_path)
    res = runner.invoke(app, ["preview-needle", str(needle_path), "--haystack", str(hay_path), "--threshold", "0.9999", "--json"])
    assert res.exit_code == 1
