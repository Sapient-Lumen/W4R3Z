# Rev315 — docs-cues link source-kind metadata

Rev307 made visible docs/help link *targets* easier to inspect, but future
UIs/scripts/LLMs still had to re-filter generic `link_entries` to answer
questions like:

- is this visible link inline markdown or reference-style markdown?
- is this row using a raw autolink rather than bracketed text?
- does this row contain a footnote reference token?

Rev315 keeps the model tiny while promoting those source-form slices directly.

## What changed

Each visible docs/help row now also carries:

- `inline_link_entries`
- `reference_link_entries`
- `autolink_entries`
- `footnote_ref_entries`
- matching row-local counts:
  - `inline_link_count`
  - `reference_link_count`
  - `autolink_count`
  - `footnote_ref_count`

Each `link_entries` item now also includes:

- `source_kind` — one of `inline`, `reference`, `autolink`, `footnote`

The top-level snapshot now also reports:

- `inline_link_rows`
- `reference_link_rows`
- `autolink_rows`
- `footnote_ref_rows`
- `inline_link_count`
- `reference_link_count`
- `autolink_count`
- `footnote_ref_count`

Existing `link_entries`, target-kind slices, row counts, and entry counts stay
intact.

## Classification policy

This remains intentionally tiny and source-view-first:

- `inline` covers bracketed links whose destination appears immediately after
  the label on the source line
- `reference` covers full / collapsed / shortcut reference-style links as one
  bucket
- `autolink` covers `<https://...>` / `<mailto:...>` style source forms
- `footnote` covers `[^id]` visible reference tokens

That keeps the shared snapshot honest without inventing a richer markdown AST.

## Why this helps

Before rev315, future UIs/scripts/LLMs could already inspect visible link
*targets*, but they still had to repeat source-form logic by hand to answer
questions like:

- "show me rows that still rely on reference definitions"
- "tell me whether the current row uses autolinks or bracketed links"
- "highlight visible footnote reference rows"

Rev315 makes those common questions directly inspectable while keeping the
parser and renderer contracts small.

## Focused coverage

The focused regression coverage lives in:

- `tests/test_editor_screen_layout.py`
- `tests/test_editor_main_cli.py`
- `tests/test_mxcontext.py`
