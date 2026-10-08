# Rev323: docs-cues heading-level metadata

## Why

`docs_cues_model(lines, cols)` / `ed.docs-cues` already exposed visible heading
rows, title-vs-underline roles, and ATX-vs-setext source kinds. Each heading
entry also already carried its numeric `level`.

That was enough for consumers willing to re-filter generic `heading_entries`
row-by-row, but it still made simple source-view questions noisier than they
needed to be:

- which visible rows are H1 vs H2 vs H3?
- how many visible heading rows on screen are level 2?
- does this tiny help excerpt contain any H4+ rows at all?

Rev323 keeps the parser/policy small while promoting heading level into the same
focused sibling surface used for other docs-cues slices.

## What changed

Every visible row in `docs_cues_model(...)` now also exposes:

- `h1_heading_entries`
- `h2_heading_entries`
- `h3_heading_entries`
- `h4_heading_entries`
- `h5_heading_entries`
- `h6_heading_entries`

with matching row-local counts:

- `h1_heading_count`
- `h2_heading_count`
- `h3_heading_count`
- `h4_heading_count`
- `h5_heading_count`
- `h6_heading_count`

The top-level snapshot now also reports:

- `h1_heading_rows`
- `h2_heading_rows`
- `h3_heading_rows`
- `h4_heading_rows`
- `h5_heading_rows`
- `h6_heading_rows`
- `h1_heading_entry_count`
- `h2_heading_entry_count`
- `h3_heading_entry_count`
- `h4_heading_entry_count`
- `h5_heading_entry_count`
- `h6_heading_entry_count`

Existing heading metadata stays intact:

- `heading_entries`
- `heading_title_entries`
- `heading_underline_entries`
- `atx_heading_entries`
- `setext_heading_entries`
- per-entry `level`, `title`, `fragment`, `fragment_source`, and optional
  setext underline marker fields

## Notes

This is intentionally still a source-view helper, not a full markdown AST.
The goal is simply to make one common visible classification — heading level —
cheap and explicit for future UIs, scripts, tests, and LLM handoffs.
