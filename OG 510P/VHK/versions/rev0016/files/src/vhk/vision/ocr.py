from __future__ import annotations

import subprocess
from pathlib import Path

import pytesseract
from PIL import Image


def tesseract_available() -> bool:
    try:
        subprocess.run(["tesseract", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def ocr_read_text_file(image_path: Path, *, lang: str = "eng") -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=lang)
    return text.strip()
