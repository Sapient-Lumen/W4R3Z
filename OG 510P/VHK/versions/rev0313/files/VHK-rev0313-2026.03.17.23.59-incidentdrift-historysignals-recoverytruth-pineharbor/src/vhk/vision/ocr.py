from __future__ import annotations

import re
from vhk.system.fuzzy import fuzzy_score, normalize_text
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytesseract
from PIL import Image, ImageFilter, ImageOps

from vhk.core.models import Region


def tesseract_available() -> bool:
    try:
        subprocess.run(["tesseract", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def _clamp_region_to_image(region: Region, *, img_w: int, img_h: int) -> Region | None:
    """Clamp a Region to the image bounds.

    PIL's crop() will happily accept out-of-bounds coordinates and pad with
    black pixels, which can hurt OCR. For automation we usually want the
    intersection with the captured image.

    Returns None when the intersection is empty.
    """

    x1 = max(0, int(region.x))
    y1 = max(0, int(region.y))
    x2 = min(int(img_w), int(region.x) + int(region.w))
    y2 = min(int(img_h), int(region.y) + int(region.h))
    if x2 <= x1 or y2 <= y1:
        return None
    return Region(x=x1, y=y1, w=int(x2 - x1), h=int(y2 - y1))




def _normalize_scale(scale: float | int | None) -> float:
    try:
        s = float(scale) if scale is not None else 1.0
    except Exception:
        return 1.0
    if s <= 0:
        return 1.0
    return s


def _build_tesseract_config(*, psm: int | None, oem: int | None, tess_config: str | None) -> str | None:
    """Build a pytesseract config string.

    pytesseract passes this string to the `tesseract` binary.
    """

    parts: list[str] = []
    if oem is not None:
        parts.extend(["--oem", str(int(oem))])
    if psm is not None:
        parts.extend(["--psm", str(int(psm))])
    if tess_config:
        parts.append(str(tess_config).strip())
    out = " ".join(p for p in parts if p)
    return out or None


def _parse_preprocess(preprocess: str | None) -> list[str]:
    if not preprocess:
        return []
    p = preprocess.strip().lower()
    if not p or p == "none":
        return []
    if p == "auto":
        # Good default for UI text: normalize to grayscale, boost contrast, binarize.
        return ["grayscale", "autocontrast", "binarize"]
    # Allow separators like: "grayscale+autocontrast+binarize".
    toks = re.split(r"[+,|\s]+", p)
    return [t for t in (tok.strip() for tok in toks) if t]


def _apply_preprocess(
    img: Image.Image,
    *,
    preprocess: str | None,
    scale: float | int | None,
) -> Image.Image:
    """Apply a minimal, dependency-free OCR preprocessing pipeline.

    References: Tesseract's "ImproveQuality" docs recommend rescaling and
    handling inverted text carefully.
    """

    s = _normalize_scale(scale)
    if s != 1.0:
        w, h = img.size
        nw = max(1, int(round(w * s)))
        nh = max(1, int(round(h * s)))
        try:
            resample = Image.Resampling.LANCZOS if s > 1.0 else Image.Resampling.BILINEAR
        except Exception:  # pragma: no cover
            resample = Image.LANCZOS if s > 1.0 else Image.BILINEAR
        img = img.resize((nw, nh), resample=resample)

    ops = _parse_preprocess(preprocess)
    if not ops:
        return img

    for op in ops:
        if op == "grayscale":
            img = img.convert("L")
            continue
        if op == "autocontrast":
            img = ImageOps.autocontrast(img)
            continue
        if op == "invert":
            # Invert works on L or RGB; prefer L for OCR.
            if img.mode not in {"L", "RGB"}:
                img = img.convert("RGB")
            if img.mode == "RGB":
                img = img.convert("L")
            img = ImageOps.invert(img)
            continue
        if op.startswith("binarize"):
            # Accept: binarize, binarize:170, binarize=170
            thresh = 128
            m = re.search(r"[:=](\d+)", op)
            if m:
                try:
                    thresh = max(0, min(255, int(m.group(1))))
                except Exception:
                    thresh = 128
            if img.mode != "L":
                img = img.convert("L")
            img = img.point(lambda p: 255 if p > thresh else 0)
            continue
        if op == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
            continue
        if op.startswith("median"):
            # Accept: median, median:3
            size = 3
            m = re.search(r"[:=](\d+)", op)
            if m:
                try:
                    size = max(1, int(m.group(1)))
                except Exception:
                    size = 3
            img = img.filter(ImageFilter.MedianFilter(size=size))
            continue
        raise ValueError(f"Unknown OCR preprocess op: {op}")

    return img
def ocr_read_text_file(
    image_path: Path,
    *,
    lang: str = "eng",
    region: Region | None = None,
    preprocess: str | None = None,
    scale: float | int | None = 1.0,
    psm: int | None = None,
    oem: int | None = None,
    tess_config: str | None = None,
) -> str:
    img = Image.open(image_path)

    if region is not None:
        r = _clamp_region_to_image(region, img_w=img.size[0], img_h=img.size[1])
        if r is None:
            return ""
        ox, oy = int(r.x), int(r.y)
        img = img.crop((ox, oy, ox + int(r.w), oy + int(r.h)))

    img = _apply_preprocess(img, preprocess=preprocess, scale=scale)
    cfg = _build_tesseract_config(psm=psm, oem=oem, tess_config=tess_config)
    text = pytesseract.image_to_string(img, lang=lang, config=cfg)
    return text.strip()


@dataclass
class OcrSpan:
    """A piece of OCR'd text with a bounding box."""

    text: str
    x: int
    y: int
    w: int
    h: int
    conf: float


def _scan_sort_key(scan_order: str) -> tuple[int, int]:
    """Return multipliers (sy, sx) for scan-order sorting."""

    s = (scan_order or "tlbr").strip().lower()
    mapping: dict[str, tuple[int, int]] = {
        "tlbr": (1, 1),
        "trbl": (1, -1),
        "bltr": (-1, 1),
        "brtl": (-1, -1),
    }
    if s not in mapping:
        raise ValueError("scan_order must be tlbr|trbl|bltr|brtl")
    return mapping[s]


def _match_text(
    s: str,
    pattern: str,
    *,
    match: str,
    case_sensitive: bool,
    fuzzy_threshold: float | None = None,
    fuzzy_mode: str = "partial",
) -> bool:
    s = normalize_text(s)
    pattern = normalize_text(pattern)
    if not case_sensitive:
        s = s.lower()
        pattern = pattern.lower()

    m = (match or "contains").strip().lower()
    if m == "contains":
        return pattern in s
    if m == "regex":
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.search(pattern, s, flags=flags) is not None
    if m == "fuzzy":
        thr = float(fuzzy_threshold) if fuzzy_threshold is not None else 0.8
        mode = (fuzzy_mode or "partial").strip().lower()
        score = fuzzy_score(pattern, s, mode=mode)
        return score >= thr
    raise ValueError("match must be contains|regex|fuzzy")


def ocr_read_spans_file(
    image_path: Path,
    *,
    lang: str = "eng",
    region: Region | None = None,
    level: str = "word",
    preprocess: str | None = None,
    scale: float | int | None = 1.0,
    psm: int | None = None,
    oem: int | None = None,
    tess_config: str | None = None,
) -> list[OcrSpan]:
    """Run OCR and return bounding boxes.

    Parameters
    ----------
    level:
        "word" (default) or "line".

    Notes
    -----
    Uses pytesseract's ``image_to_data`` (TSV-like) output, which includes
    ``left``, ``top``, ``width``, ``height``, and ``conf`` for each element.
    """

    img = Image.open(image_path)

    ox, oy = 0, 0
    if region is not None:
        r = _clamp_region_to_image(region, img_w=img.size[0], img_h=img.size[1])
        if r is None:
            return []
        ox, oy = int(r.x), int(r.y)
        img = img.crop((ox, oy, ox + int(r.w), oy + int(r.h)))

    img = _apply_preprocess(img, preprocess=preprocess, scale=scale)
    cfg = _build_tesseract_config(psm=psm, oem=oem, tess_config=tess_config)
    data = pytesseract.image_to_data(img, lang=lang, config=cfg, output_type=pytesseract.Output.DICT)
    n = len(data.get("level") or [])
    rows: list[dict[str, object]] = []
    keys = list(data.keys())
    for i in range(n):
        row = {k: (data.get(k) or [None] * n)[i] for k in keys}
        rows.append(row)

    lvl = (level or "word").strip().lower()
    spans: list[OcrSpan] = []

    def _conf(v) -> float:
        try:
            return float(v)
        except Exception:
            return 0.0

    if lvl == "word":
        for r in rows:
            txt = str(r.get("text") or "").strip()
            if not txt:
                continue
            c = _conf(r.get("conf"))
            if c < 0:
                continue
            left = int(r.get("left") or 0) + ox
            top = int(r.get("top") or 0) + oy
            w = int(r.get("width") or 0)
            h = int(r.get("height") or 0)
            spans.append(OcrSpan(text=txt, x=left, y=top, w=w, h=h, conf=float(c)))
        return spans

    if lvl == "line":
        groups: dict[tuple[int, int, int], list[dict[str, object]]] = {}
        for r in rows:
            txt = str(r.get("text") or "").strip()
            if not txt:
                continue
            c = _conf(r.get("conf"))
            if c < 0:
                continue
            key = (int(r.get("block_num") or 0), int(r.get("par_num") or 0), int(r.get("line_num") or 0))
            groups.setdefault(key, []).append(r)

        for items in groups.values():
            xs = [int(it.get("left") or 0) for it in items]
            ys = [int(it.get("top") or 0) for it in items]
            ws = [int(it.get("width") or 0) for it in items]
            hs = [int(it.get("height") or 0) for it in items]
            x1 = min(xs)
            y1 = min(ys)
            x2 = max(x + w for x, w in zip(xs, ws))
            y2 = max(y + h for y, h in zip(ys, hs))
            text = " ".join(str(it.get("text") or "").strip() for it in items if str(it.get("text") or "").strip())
            confs = [max(0.0, _conf(it.get("conf"))) for it in items]
            conf = sum(confs) / max(1, len(confs))
            spans.append(OcrSpan(text=text, x=int(x1 + ox), y=int(y1 + oy), w=int(x2 - x1), h=int(y2 - y1), conf=float(conf)))
        return spans

    raise ValueError("level must be word|line")


def ocr_find_text_file(
    image_path: Path,
    *,
    pattern: str,
    match: str = "contains",
    fuzzy_threshold: float | None = None,
    fuzzy_mode: str = "partial",
    case_sensitive: bool = False,
    lang: str = "eng",
    region: Region | None = None,
    level: str = "word",
    match_strategy: str = "first",
    scan_order: str = "tlbr",
    preprocess: str | None = None,
    scale: float | int | None = 1.0,
    psm: int | None = None,
    oem: int | None = None,
    tess_config: str | None = None,
) -> OcrSpan:
    """Find a text span (word/line) and return its bounding box."""

    spans = ocr_read_spans_file(
        image_path,
        lang=lang,
        region=region,
        level=level,
        preprocess=preprocess,
        scale=scale,
        psm=psm,
        oem=oem,
        tess_config=tess_config,
    )
    return ocr_find_text_in_spans(
        spans,
        pattern=pattern,
        match=match,
        case_sensitive=case_sensitive,
        match_strategy=match_strategy,
        scan_order=scan_order,
        fuzzy_threshold=fuzzy_threshold,
        fuzzy_mode=fuzzy_mode,
    )


def ocr_find_text_in_spans(
    spans: list[OcrSpan],
    *,
    pattern: str,
    match: str = "contains",
    fuzzy_threshold: float | None = None,
    fuzzy_mode: str = "partial",
    case_sensitive: bool = False,
    match_strategy: str = "first",
    scan_order: str = "tlbr",
) -> OcrSpan:
    """Find a matching span in a precomputed span list."""

    pat = pattern or ""
    candidates = [
        s
        for s in spans
        if _match_text(
            s.text,
            pat,
            match=match,
            case_sensitive=case_sensitive,
            fuzzy_threshold=fuzzy_threshold,
            fuzzy_mode=fuzzy_mode,
        )
    ]
    if not candidates:
        raise RuntimeError(f"OCR did not find pattern ({match}): {pattern!r}")

    strat = (match_strategy or "first").strip().lower()
    sy, sx = _scan_sort_key(scan_order)

    if strat == "first":
        candidates.sort(key=lambda s: (sy * int(s.y), sx * int(s.x)))
        return candidates[0]

    if strat == "best_conf":
        candidates.sort(key=lambda s: (-float(s.conf), sy * int(s.y), sx * int(s.x)))
        return candidates[0]

    raise ValueError("match_strategy must be first|best_conf")




def ocr_find_text_all_file(
    image_path: Path,
    *,
    pattern: str,
    match: str = "contains",
    fuzzy_threshold: float | None = None,
    fuzzy_mode: str = "partial",
    case_sensitive: bool = False,
    lang: str = "eng",
    region: Region | None = None,
    level: str = "word",
    sort: str = "scan",
    scan_order: str = "tlbr",
    max_results: int | None = None,
    min_conf: float | None = None,
    preprocess: str | None = None,
    scale: float | int | None = 1.0,
    psm: int | None = None,
    oem: int | None = None,
    tess_config: str | None = None,
) -> list[OcrSpan]:
    spans = ocr_read_spans_file(
        image_path,
        lang=lang,
        region=region,
        level=level,
        preprocess=preprocess,
        scale=scale,
        psm=psm,
        oem=oem,
        tess_config=tess_config,
    )
    return ocr_find_text_all_in_spans(
        spans,
        pattern=pattern,
        match=match,
        case_sensitive=case_sensitive,
        sort=sort,
        scan_order=scan_order,
        max_results=max_results,
        min_conf=min_conf,
        fuzzy_threshold=fuzzy_threshold,
        fuzzy_mode=fuzzy_mode,
    )


def ocr_find_text_all_in_spans(
    spans: list[OcrSpan],
    *,
    pattern: str,
    match: str = "contains",
    fuzzy_threshold: float | None = None,
    fuzzy_mode: str = "partial",
    case_sensitive: bool = False,
    sort: str = "scan",
    scan_order: str = "tlbr",
    max_results: int | None = None,
    min_conf: float | None = None,
) -> list[OcrSpan]:
    pat = pattern or ""
    candidates = [
        s
        for s in spans
        if _match_text(
            s.text,
            pat,
            match=match,
            case_sensitive=case_sensitive,
            fuzzy_threshold=fuzzy_threshold,
            fuzzy_mode=fuzzy_mode,
        )
    ]
    if min_conf is not None:
        candidates = [s for s in candidates if float(s.conf) >= float(min_conf)]

    sy, sx = _scan_sort_key(scan_order)
    mode = (sort or "scan").strip().lower()
    if mode in {"scan", "first"}:
        candidates.sort(key=lambda s: (sy * int(s.y), sx * int(s.x)))
    elif mode in {"best_conf", "conf"}:
        candidates.sort(key=lambda s: (-float(s.conf), sy * int(s.y), sx * int(s.x)))
    else:
        raise ValueError("sort must be scan|best_conf")

    if max_results is not None:
        try:
            m = int(max_results)
        except Exception:
            m = None
        if m is not None and m >= 0:
            candidates = candidates[:m]

    return candidates
def ocr_spans_to_text(spans: list[OcrSpan], *, level: str) -> str:
    """Convert spans to a human-readable text block (best-effort)."""

    if not spans:
        return ""

    lvl = (level or "word").strip().lower()
    if lvl == "line":
        ssp = sorted(spans, key=lambda s: (s.y, s.x))
        return "\n".join(s.text for s in ssp).strip()

    ssp = sorted(spans, key=lambda s: (s.y, s.x))
    lines: list[list[OcrSpan]] = []
    for sp in ssp:
        placed = False
        for line in lines:
            if abs(sp.y - line[0].y) <= max(3, int(0.5 * max(sp.h, line[0].h))):
                line.append(sp)
                placed = True
                break
        if not placed:
            lines.append([sp])
    out_lines: list[str] = []
    for line in lines:
        line.sort(key=lambda s: s.x)
        out_lines.append(" ".join(s.text for s in line).strip())
    return "\n".join(out_lines).strip()
