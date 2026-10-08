from __future__ import annotations

import json
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


AreaType = Literal["match", "exclude", "ocr"]


@dataclass(frozen=True)
class NeedleClickPoint:
    """Relative click point inside a match area (openQA-style)."""

    xpos: int
    ypos: int
    id: str | None = None


@dataclass(frozen=True)
class NeedleArea:
    """openQA-inspired area.

    Coordinates are relative to the needle image.

    Notes
    -----
    openQA distinguishes:
      - match areas (what we actually match)
      - exclude areas (dynamic bits to ignore)
      - ocr areas (regions to OCR)

    VHK v0.3 currently *uses only match areas* for template matching. Exclude/OCR
    areas are still loaded/represented so we can build tooling around them.
    """

    type: AreaType
    xpos: int
    ypos: int
    width: int
    height: int
    id: str | None = None
    match: int | None = None
    click_point: NeedleClickPoint | None = None

    def threshold(self, default: float) -> float:
        """Return this area's similarity threshold.

        openQA stores per-area similarity as an integer percentage (0-100).
        If not present, we use the caller-provided default.
        """

        if self.match is None:
            return float(default)
        return float(self.match) / 100.0


@dataclass(frozen=True)
class Needle:
    """Visual asset: <name>.png + optional <name>.json metadata."""

    name: str
    image_path: Path
    areas: list[NeedleArea]
    tags: list[str]

    @property
    def match_areas(self) -> list[NeedleArea]:
        return [a for a in self.areas if a.type == "match"]

    @property
    def exclude_areas(self) -> list[NeedleArea]:
        return [a for a in self.areas if a.type == "exclude"]

    @property
    def ocr_areas(self) -> list[NeedleArea]:
        return [a for a in self.areas if a.type == "ocr"]


# Small cache for needle metadata to avoid re-reading JSON sidecars during
# polling waits (WaitForImage, VisualAssert, etc.).
#
# Keyed by the resolved .png path. Value is (json_mtime_ns, Needle|None).
_NEEDLE_META_CACHE: "OrderedDict[str, tuple[int, Needle | None]]" = OrderedDict()
_NEEDLE_META_CACHE_MAX = 256


def _parse_area(a: dict[str, Any]) -> NeedleArea:
    cp = a.get("click_point")
    click_point = None
    if isinstance(cp, dict) and "xpos" in cp and "ypos" in cp:
        click_point = NeedleClickPoint(
            xpos=int(cp["xpos"]),
            ypos=int(cp["ypos"]),
            id=str(cp.get("id")) if cp.get("id") is not None else None,
        )

    return NeedleArea(
        type=a.get("type", "match"),
        id=str(a.get("id")) if a.get("id") is not None else None,
        xpos=int(a["xpos"]),
        ypos=int(a["ypos"]),
        width=int(a["width"]),
        height=int(a["height"]),
        match=int(a["match"]) if a.get("match") is not None else None,
        click_point=click_point,
    )


def compute_click_offset(needle: Needle, click_point_id: str | None = None) -> tuple[int, int]:
    """Return (dx, dy) click offset within the *matched needle bbox*.

    The returned offset is relative to the top-left of the effective match bbox
    (the union of match areas when present; otherwise the full needle image).

    Semantics are inspired by openQA:
      - click points are *relative to the match area* they belong to
      - if no explicit click point exists, fall back to the center of the last
        match area (or full image when no areas are present)

    Parameters
    ----------
    needle:
        Loaded needle metadata.
    click_point_id:
        Optional id to select among multiple click points.

    Returns
    -------
    (dx, dy) in pixels.
    """

    match_areas = needle.match_areas
    if match_areas:
        min_x = min(a.xpos for a in match_areas)
        min_y = min(a.ypos for a in match_areas)

        chosen: NeedleArea | None = None
        if click_point_id is not None:
            for a in match_areas:
                if a.click_point and a.click_point.id == click_point_id:
                    chosen = a
                    break
            if chosen is None:
                raise ValueError(f"No click_point with id={click_point_id!r} in needle {needle.name}")
        else:
            for a in match_areas:
                if a.click_point is not None:
                    chosen = a
                    break

        if chosen and chosen.click_point is not None:
            dx = int(chosen.xpos - min_x + chosen.click_point.xpos)
            dy = int(chosen.ypos - min_y + chosen.click_point.ypos)
            return dx, dy

        # No click point: center of the last match area.
        last = match_areas[-1]
        dx = int(last.xpos - min_x + last.width // 2)
        dy = int(last.ypos - min_y + last.height // 2)
        return dx, dy

    # No match areas: fall back to the center of the full needle image.
    # (This path is rare; most needles will have at least one match area.)
    try:
        from PIL import Image

        with Image.open(needle.image_path) as im:
            w, h = im.size
    except Exception:
        w, h = 0, 0
    return int(w // 2), int(h // 2)


def load_needle(png_path: Path) -> Needle:
    """Load an openQA-style needle metadata file next to a .png.

    Raises if the metadata json does not exist.
    """

    meta_path = png_path.with_suffix(".json")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing needle metadata: {meta_path}")

    raw: dict[str, Any] = json.loads(meta_path.read_text())
    areas = [_parse_area(a) for a in raw.get("area", [])]

    return Needle(
        name=png_path.stem,
        image_path=png_path,
        areas=areas,
        tags=list(raw.get("tags", [])),
    )


def scale_needle(needle: Needle, scale: float) -> Needle:
    """Return a copy of ``needle`` with areas/click points scaled.

    This is used by multi-scale template matching and preview tooling.

    Notes
    -----
    - Coordinates in openQA-style needles are integer pixels, so we round to
      the nearest pixel after scaling.
    - ``image_path`` continues to point at the original .png. The caller is
      responsible for scaling the actual image content when matching.
    """

    s = float(scale)
    if abs(s - 1.0) < 1e-9:
        return needle
    if s <= 0:
        raise ValueError(f"scale must be > 0 (got {scale})")

    def _sv_dim(v: int) -> int:
        """Scale a dimension (width/height), clamped to >= 1."""
        return max(1, int(round(float(v) * s)))

    def _sv_pos(v: int) -> int:
        """Scale a position/offset. 0 is valid, so no clamping."""
        return int(round(float(v) * s))

    new_areas: list[NeedleArea] = []
    for a in needle.areas:
        cp = a.click_point
        new_cp = None
        if cp is not None:
            new_cp = NeedleClickPoint(xpos=_sv_pos(cp.xpos), ypos=_sv_pos(cp.ypos), id=cp.id)

        # xpos/ypos can legitimately become 0 after scaling; keep that.
        new_areas.append(
            NeedleArea(
                type=a.type,
                xpos=_sv_pos(a.xpos),
                ypos=_sv_pos(a.ypos),
                width=_sv_dim(a.width),
                height=_sv_dim(a.height),
                match=a.match,
                click_point=new_cp,
            )
        )

    return Needle(name=needle.name, image_path=needle.image_path, areas=new_areas, tags=list(needle.tags))


def try_load_needle(png_path: Path) -> Needle | None:
    """Load needle metadata if it exists; otherwise return None.

    This function is called frequently during polling waits (e.g.
    WaitForImage/VisualAssert). We keep a small in-process cache keyed by the
    needle path and the JSON sidecar's mtime so we don't re-parse the same file
    thousands of times in a single run.

    If the JSON is invalid (mid-edit), we cache ``None`` until the file's mtime
    changes.
    """

    meta_path = png_path.with_suffix(".json")
    key = str(png_path.resolve())

    if not meta_path.exists():
        _NEEDLE_META_CACHE.pop(key, None)
        return None

    try:
        mtime_ns = int(meta_path.stat().st_mtime_ns)
    except OSError:
        mtime_ns = 0

    cached = _NEEDLE_META_CACHE.get(key)
    if cached is not None and int(cached[0]) == mtime_ns:
        # Move-to-end for LRU-ish behavior.
        _NEEDLE_META_CACHE.move_to_end(key)
        return cached[1]

    try:
        needle = load_needle(png_path)
    except Exception:
        # Tooling should still work even if a user is mid-editing the json.
        needle = None

    _NEEDLE_META_CACHE[key] = (mtime_ns, needle)
    _NEEDLE_META_CACHE.move_to_end(key)

    # Bound cache growth.
    while len(_NEEDLE_META_CACHE) > int(_NEEDLE_META_CACHE_MAX):
        _NEEDLE_META_CACHE.popitem(last=False)

    return needle
