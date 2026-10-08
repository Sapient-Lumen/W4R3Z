# REV0314 — explicit multi-click pointer semantics

This revision tightens one practical recorder/runtime gap: repeated click intent
(now explicit double-click/triple-click semantics) should not stay buried in raw
lexical click streams.

## What changed

- `MouseClickAt` now accepts:
  - `clicks`
  - `delay_between_clicks_ms`
- the runner now executes repeated clicks from one `MouseClickAt` step after a
  single move to the target coordinates
- the optimizer now collapses repeated `MouseClickAt` runs into one multi-click
  step when coordinates/button/modifier-clearing intent match within a bounded
  inter-click gap
- CLI optimization surfaces now expose:
  - `--max-multiclick-gap-ms`
  - `--optimize-max-multiclick-gap-ms`
- docs now make the new step contract and optimizer behavior explicit

## Why this matters

Linux recorder cleanup still needs to feel closer to AHK/Pulover authoring:
users should see “double-click here” instead of reverse-engineering it from a
stack of low-level click fragments. This keeps recorded macros smaller, clearer,
more editable, and closer to native user intent.

## Tests run

- `python -m compileall -q src/vhk tests`
- `pytest -q tests/test_record_x11.py tests/test_coord_mode.py tests/test_optimize_cli.py`

All of those targeted suites passed in this revision.
