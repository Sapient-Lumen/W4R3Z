# Rev316 — docs-cues image source-kind metadata

Rev308 made visible docs/help image *targets* easier to inspect, but future
UIs/scripts/LLMs still had to re-filter generic `image_entries` to answer
questions like:

- is this visible image inline markdown or reference-style markdown?
- does this row still depend on reference definitions for its image targets?
- is this image using full/collapsed/shortcut reference syntax rather than an
  inline destination?

Rev316 keeps the model tiny while promoting those source-form slices directly.

## What changed

Each visible docs/help row now also carries:

- `inline_image_entries`
- `reference_image_entries`
- matching row-local counts:
  - `inline_image_count`
  - `reference_image_count`

Each `image_entries` item now also includes:

- `source_kind` — one of `inline`, `reference`

The top-level snapshot now also reports:

- `inline_image_rows`
- `reference_image_rows`
- `inline_image_count`
- `reference_image_count`

Existing `image_entries`, target-kind slices, row counts, and entry counts stay
intact.

## Classification policy

This remains intentionally tiny and source-view-first:

- `inline` covers `![alt](dest)` source forms, including the tiny wrapped inline
  destination support the docs/help parser already understands
- `reference` covers full / collapsed / shortcut reference-style images as one
  bucket

That keeps the shared snapshot honest without inventing a richer markdown AST.

## Why this helps

Before rev316, future UIs/scripts/LLMs could already inspect visible image
*targets*, but they still had to repeat source-form logic by hand to answer
questions like:

- "show me rows that still rely on reference-style images"
- "tell me whether the current row uses inline image destinations or reference
  definitions"
- "highlight visible rows that mix inline and reference image syntax"

Rev316 makes those common questions directly inspectable while keeping the
parser and renderer contracts small.

## Focused coverage

The focused regression coverage lives in:

- `tests/test_editor_screen_layout.py`
- `tests/test_editor_main_cli.py`
- `tests/test_mxcontext.py`
