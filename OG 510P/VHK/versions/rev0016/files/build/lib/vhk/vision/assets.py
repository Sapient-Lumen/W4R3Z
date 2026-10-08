from __future__ import annotations

import json
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


def try_load_needle(png_path: Path) -> Needle | None:
    """Load needle metadata if it exists; otherwise return None."""

    meta_path = png_path.with_suffix(".json")
    if not meta_path.exists():
        return None
    try:
        return load_needle(png_path)
    except Exception:
        # Tooling should still work even if a user is mid-editing the json.
        return None
