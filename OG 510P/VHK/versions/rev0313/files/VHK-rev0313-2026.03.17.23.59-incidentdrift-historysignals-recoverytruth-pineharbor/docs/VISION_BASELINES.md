# Visual baselines and region-change checks

VHK now supports a small "visual assert" toolkit for the cases where a classic
needle match is the wrong abstraction.

## When to use what

- `ClickNeedle` / `WaitForImage`: use when you want to locate a specific button,
  icon, or stable widget.
- `VisualAssert`: use when a whole panel / region should look the same as a
  baseline and mismatch should fail the macro.
- `VisualVerify`: same comparison, but continue running and record the result in
  variables.
- `WaitForRegionChange`: use when you do not know *what* the region will become,
  only that it should change (loading indicator completes, canvas updates, etc.).

## Baseline asset format

A baseline is just an image file, optionally with an openQA-style sidecar JSON:

- `foo.png`
- `foo.json`

If the JSON exists, VHK uses the same area semantics as needles:

- `match` areas limit what part of the baseline is compared
- `exclude` areas ignore dynamic subregions

This keeps the visual asset model unified across image search and visual asserts.

## Helpful CLI

```bash
vhk capture-baseline ./my_project login_panel --out-dir assets/baselines
```

The helper captures a region and writes a JSON stub that initially marks the
whole region as a `match` area. You can then edit the JSON to carve out exclude
areas for clocks, ads, animation, or timestamps.
