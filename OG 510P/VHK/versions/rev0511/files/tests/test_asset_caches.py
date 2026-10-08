import json
import time
from pathlib import Path

import cv2
import numpy as np

from vhk.vision import assets
from vhk.vision import imgio
from vhk.vision import match


def test_try_load_needle_caches_by_json_mtime(monkeypatch, tmp_path: Path):
    assets._NEEDLE_META_CACHE.clear()  # type: ignore[attr-defined]

    png = tmp_path / "foo.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")

    meta = tmp_path / "foo.json"
    meta.write_text(
        json.dumps(
            {
                "area": [
                    {
                        "type": "match",
                        "xpos": 0,
                        "ypos": 0,
                        "width": 10,
                        "height": 10,
                        "match": 90,
                    }
                ],
                "tags": ["test"],
            }
        )
    )

    calls = {"n": 0}
    real_load = assets.load_needle

    def wrapped(p: Path):
        calls["n"] += 1
        return real_load(p)

    monkeypatch.setattr(assets, "load_needle", wrapped)

    n1 = assets.try_load_needle(png)
    n2 = assets.try_load_needle(png)

    assert n1 is not None
    assert n2 is not None
    assert calls["n"] == 1

    # Ensure mtime changes across filesystems with coarse resolution.
    time.sleep(0.01)
    meta.write_text(meta.read_text() + "\n")

    n3 = assets.try_load_needle(png)
    assert n3 is not None
    assert calls["n"] == 2


def test_imread_color_cache_reuses_static_assets(monkeypatch, tmp_path: Path):
    imgio._clear_imgio_caches()

    hay = np.zeros((40, 40, 3), dtype=np.uint8)
    hay[10:20, 10:20] = 255

    needle = np.zeros((10, 10, 3), dtype=np.uint8)
    needle[:, :] = 255

    hay_path = tmp_path / "hay.png"
    needle_path = tmp_path / "needle.png"
    cv2.imwrite(str(hay_path), hay)
    cv2.imwrite(str(needle_path), needle)

    calls = {"n": 0}
    orig = imgio.cv2.imread

    def wrapped(*args, **kwargs):
        calls["n"] += 1
        return orig(*args, **kwargs)

    monkeypatch.setattr(imgio.cv2, "imread", wrapped)

    # First call reads hay + needle.
    m1 = match.image_search_file(hay_path, needle_path, threshold=0.9)
    # Second call reads hay again but should reuse cached needle pixels.
    m2 = match.image_search_file(hay_path, needle_path, threshold=0.9)

    assert m1.score >= 0.9
    assert m2.score >= 0.9
    assert calls["n"] == 3
