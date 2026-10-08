# Rev309 — docs-cues focused table-kind metadata

Rev261 already made visible docs/help pipe-table cells inspectable through
`table_entries`, and the snapshot already counted header/body/delimiter cells
globally. But row-local consumers still had to re-filter `table_entries` by hand
when they wanted to ask small archive-first questions like:

- which visible cells on this row are header cells?
- is this visible row a delimiter row or a body row?
- which visible table rows on screen carry data cells versus separators?

Rev309 keeps the contract tiny and source-view-first while making those
questions direct.

## New per-row fields

Each visible docs/help row now also reports focused table-kind slices:

- `table_header_entries`
- `table_body_entries`
- `table_delimiter_entries`

These are filtered siblings of the existing `table_entries` list, preserving the
same entry shape (`kind`, visible cell spans/text, `column`, and delimiter-row
alignment metadata).

Rows now also report matching row-local counts:

- `table_header_count`
- `table_body_count`
- `table_delimiter_count`

## New top-level summary fields

The whole snapshot now also reports:

- `table_header_rows`
- `table_body_rows`
- `table_delimiter_rows`

Existing `table_rows`, `table_entry_count`, `table_header_cell_count`,
`table_body_cell_count`, and `table_delimiter_cell_count` remain intact.

## Why this stays honest

This is still **not** a rendered-table model, layout engine, rich markdown AST,
or spreadsheet-like widget. It is just one more inspectable view of the visible
pipe-table source rows the shared docs/help parser already understands well
enough to style and classify in source view.

The help browser still owns rendering and navigation policy.
`docs_cues_model(...)` just makes visible table-kind truth easier to inspect
offline, especially inside release archives handed to future humans or LLMs.
