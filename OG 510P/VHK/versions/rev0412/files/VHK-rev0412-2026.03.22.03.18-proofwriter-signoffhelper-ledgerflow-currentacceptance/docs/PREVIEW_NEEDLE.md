# Preview needle matches

VHK includes a small debugging helper inspired by the **"match preview"** workflow found in GUI automation tools like:

- **SikuliX** (match objects include a similarity score and can use a click point):
  - https://sikulix.github.io/docs/api/match
- **openQA** (needles can define match areas and optional click points):
  - https://open.qa/docs/#_click_points

The goal is to make it easy to answer:

- *Does this needle actually match my current screen?*
- *What is the best candidate match score?*
- *Where would the click land (including click points from metadata)?*

## Command

```bash
vhk preview-needle NEEDLE.png [--haystack SCREENSHOT.png]
```

### Typical usage

**Preview a needle against the current screen** (captures a screenshot automatically):

```bash
vhk preview-needle assets/needles/login_button.png --out-annotated /tmp/login_preview.png
```

**Preview against a saved screenshot** (best for reproducible debugging):

```bash
vhk preview-needle assets/needles/login_button.png \
  --haystack /tmp/screen.png \
  --threshold 0.85 \
  --out-annotated /tmp/preview.png \
  --json
```

**Limit the search region** for speed and fewer false positives:

```bash
vhk preview-needle assets/needles/login_button.png \
  --haystack /tmp/screen.png \
  --region 600x400+100+200
```

### DPI scaling / multi-scale matching

OpenCV's classic `matchTemplate` is **not scale invariant**; if your desktop is
running at 125% / 150% scaling (or you captured a needle at a different DPI),
plain template matching can fail.

VHK can try multiple scales and pick the best candidate:

```bash
vhk preview-needle assets/needles/login_button.png \
  --haystack /tmp/screen.png \
  --scales "0.9,1.0,1.1" \
  --threshold 0.85
```

Or use the shortcut sweep (0.85 → 1.15 step 0.05):

```bash
vhk preview-needle assets/needles/login_button.png --auto-scale
```

References:

- OpenCV docs: template matching is a sliding comparison and does not include scale invariance:
  https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
- A common workaround is multi-scale matching by iterating over scales:
  https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/

## Output

- Always reports the **best candidate** (even if it fails your threshold).
- Prints a suggested `ClickNeedle` YAML snippet you can paste into a macro.
- When `--out-annotated` is used, writes an image overlay that shows:
  - the match bounding box
  - match areas / exclude areas / OCR areas (if metadata exists)
  - the final computed click point

If your needle JSON includes `ocr` areas, preview overlays those too (useful with `OcrNeedleText` / `WaitForNeedleText`). See `docs/NEEDLE_OCR.md`.

## Notes on matching reliability

Template/pixel matching can be brittle across machines due to font rendering, DPI scaling, and anti-aliasing differences. A common recommendation in image-recognition macro tools is to constrain the search area and keep needles focused on stable UI shapes:

- https://www.macrorecorder.com/doc/reference/image-detection-method/

openQA-style match/exclude areas can help you carve out dynamic regions (e.g., timestamps), improving robustness:

- https://open.qa/docs/#_needles
