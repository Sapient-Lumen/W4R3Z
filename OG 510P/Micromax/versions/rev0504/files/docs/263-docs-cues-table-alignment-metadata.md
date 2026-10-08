# Rev321 — docs-cues table-alignment metadata

Rev321 keeps the shared docs/help cue model small, but removes one more piece of
manual correlation work for future humans, scripts, and LLMs.

Before this landing, `docs_cues_model(lines, cols)` / `ed.docs-cues` already
surfaced:

- parsed visible `table_entries`
- focused `table_header_entries`, `table_body_entries`, and
  `table_delimiter_entries`
- delimiter-cell `align` labels on the delimiter row itself

That was enough to reconstruct alignment, but only by finding the delimiter row
for a table block and rejoining it with nearby header/body rows.

## What changes

Every visible table entry now carries a resolved `align` field:

- `default`
- `left`
- `center`
- `right`

That alignment is propagated from the delimiter row onto the visible header,
body, and delimiter rows in the same table block.

The shared row model now also exposes focused sibling slices:

- `default_aligned_table_entries`
- `left_aligned_table_entries`
- `center_aligned_table_entries`
- `right_aligned_table_entries`

with matching row-local counts:

- `default_aligned_table_count`
- `left_aligned_table_count`
- `center_aligned_table_count`
- `right_aligned_table_count`

and matching snapshot summaries:

- `default_aligned_table_rows`
- `left_aligned_table_rows`
- `center_aligned_table_rows`
- `right_aligned_table_rows`
- `default_aligned_table_entry_count`
- `left_aligned_table_entry_count`
- `center_aligned_table_entry_count`
- `right_aligned_table_entry_count`

## Why this is useful

This keeps the model small, but makes common questions direct:

- which visible body cells are right-aligned numeric columns?
- does this visible header row belong to a centered or default-aligned column?
- which visible rows in the viewport participate in any centered columns?

Future UIs and future LLMs no longer have to special-case delimiter rows or
reconstruct per-column alignment by hand.

## Testing

Focused coverage lives in:

- `tests/test_editor_screen_layout.py`
- `tests/test_editor_main_cli.py`
- `tests/test_mxcontext.py`
