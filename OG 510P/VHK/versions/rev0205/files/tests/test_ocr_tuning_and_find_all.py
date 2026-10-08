from __future__ import annotations

from pathlib import Path

from PIL import Image


def _write_blank(path: Path) -> Path:
    img = Image.new("RGB", (10, 8), color=(10, 20, 30))
    img.save(path)
    return path


def test_ocr_preprocess_and_config_are_passed(monkeypatch, tmp_path: Path):
    from vhk.vision import ocr as ocr_mod

    img_path = _write_blank(tmp_path / "x.png")

    seen = {}

    def fake_image_to_string(img, lang="eng", config=None):  # noqa: ARG001
        seen["mode"] = img.mode
        seen["size"] = img.size
        seen["config"] = config
        return "OK"

    monkeypatch.setattr(ocr_mod.pytesseract, "image_to_string", fake_image_to_string)

    txt = ocr_mod.ocr_read_text_file(
        img_path,
        preprocess="grayscale+autocontrast+invert+binarize:200",
        scale=2,
        psm=7,
        oem=1,
        tess_config="-c tessedit_char_whitelist=ABC",
    )

    assert txt == "OK"
    assert seen["mode"] == "L"  # grayscale pipeline
    assert seen["size"] == (20, 16)  # scaled
    cfg = seen["config"] or ""
    assert "--psm 7" in cfg
    assert "--oem 1" in cfg
    assert "tessedit_char_whitelist=ABC" in cfg


def test_ocr_find_text_all_sorting(monkeypatch, tmp_path: Path):
    from vhk.vision import ocr as ocr_mod

    img_path = _write_blank(tmp_path / "x.png")

    def fake_image_to_data(_img, lang="eng", config=None, output_type=None):  # noqa: ARG001
        return {
            "level": [5, 5, 5, 5],
            "block_num": [1, 1, 1, 1],
            "par_num": [1, 1, 1, 1],
            "line_num": [1, 1, 1, 1],
            "word_num": [1, 2, 3, 4],
            "left": [30, 10, 50, 5],
            "top": [5, 5, 5, 5],
            "width": [10, 10, 10, 10],
            "height": [10, 10, 10, 10],
            "conf": [50, 90, 70, 99],
            "text": ["OK", "OK", "NO", "OK"],
        }

    monkeypatch.setattr(ocr_mod.pytesseract, "image_to_data", fake_image_to_data)

    spans_scan = ocr_mod.ocr_find_text_all_file(img_path, pattern="OK", sort="scan", scan_order="tlbr")
    # scan-order tlbr should pick x=5 first
    assert [s.x for s in spans_scan][:2] == [5, 10]

    spans_conf = ocr_mod.ocr_find_text_all_file(img_path, pattern="OK", sort="best_conf")
    assert spans_conf[0].conf == 99
