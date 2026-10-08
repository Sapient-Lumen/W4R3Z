# Needle OCR (openQA-style)

A recurring automation problem:

- You want to verify *text* ("READY", "Error", "Connecting…")
- but the UI element that contains that text can move around
- and running OCR over a giant region (or the whole screen) is slow/noisy.

openQA’s “needle” format supports **OCR areas** inside the `foo.json` next to a needle image (`foo.png`). In openQA, an `area` can be one of `match | ocr | exclude`.

Reference: openQA needle format docs:
- https://open.qa/docs/  (Needles → Areas)

VHK already understands openQA-ish `match` + `exclude` areas for template matching.
This document describes VHK’s additional **needle-relative OCR** helpers.

## New steps

### `OcrNeedleText`

Find a needle, then OCR a region relative to it.

```yaml
- type: OcrNeedleText
  needle_path: assets/status.png
  threshold: 0.85
  # Optional: limit search to a region
  region: "@toolbar"

  # OCR tuning
  lang: eng
  preprocess: auto
  scale: 2
  psm: 7

  out_text: status
  out_match_x: match_x
  out_match_y: match_y
  out_ocr_x: ocr_x
  out_ocr_y: ocr_y
```

Selection behavior:

- If the needle has one or more `ocr` areas → OCR those (defaults to the *first* OCR area).
- If no `ocr` areas exist → optionally OCR the **match bounding box** (`fallback_to_match_bbox: true`).

### `WaitForNeedleText`

Wait until the needle is present **and** OCR text matches.

```yaml
- type: WaitForNeedleText
  needle_path: assets/status.png
  threshold: 0.85

  pattern: READY
  match: contains   # contains|regex|fuzzy
  timeout_ms: 15000

  # Optional: require the *text match* to be stable
  stable_attempts: 2
  stable_ms: 200

  out_found: ready
  out_text: status
```

## Choosing which OCR area to use

If your needle has multiple OCR areas, you can choose:

- `ocr_strategy: first` (default)
- `ocr_strategy: concat` + `ocr_join: "\n"` to OCR all areas and join

You can also select a specific area:

- `ocr_area_index: 0` (0-based, in the JSON order)
- `ocr_area_id: "label"` (VHK extension: optional `id` field on an area)

Example needle JSON snippet (VHK extension shown):

```json
{
  "area": [
    {"type": "match", "xpos": 10, "ypos": 10, "width": 80, "height": 30},
    {"type": "ocr", "id": "label", "xpos": 15, "ypos": 15, "width": 200, "height": 40}
  ]
}
```

## Debugging tips

- `vhk preview-needle --out-annotated out.png ...` now draws **match** (blue), **exclude** (gray), and **ocr** (orange) rectangles.
- Prefer defining a `match` area that is stable (icons/background), and an `ocr` area that tightly bounds text.

