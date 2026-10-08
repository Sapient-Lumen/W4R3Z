Rev321 follow-up: resolved per-column alignment is now propagated onto all visible table entries, and `docs_cues_model(...)` / `ed.docs-cues` also expose focused row/snapshot alignment slices (`default_aligned_table_entries`, `left_aligned_table_entries`, `center_aligned_table_entries`, `right_aligned_table_entries`). See `docs/263-docs-cues-table-alignment-metadata.md`.

# Rev261 — docs-cues visible table metadata

Rev261 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible pipe-table rows
now expose parsed table cells instead of leaving future UIs/scripts/LLMs to
infer everything from `table_kind` plus generic `|` spans.

This stays tiny and source-view-first. It does **not** add a richer Markdown
block tree, rendered table widget, or column-width/layout policy. It simply
reuses the same small table helpers the reference TUI already trusts for
scanability cues.

## New per-row fields

Each visible docs/help row now also reports:

- `table_entries`
- `table_count`

Current entry kinds are:

- `header-cell`
  - `column` — zero-based visible column index
  - `start`, `end` — trimmed visible cell span
  - `text` — trimmed visible cell text
- `body-cell`
  - same fields as `header-cell`
- `delimiter-cell`
  - same visible span/text fields
  - `align` — `default`, `left`, `right`, or `center`
  - `marker_count` — number of `-` characters in the delimiter token

## New top-level counts

Top-level docs-cues snapshots now also report:

- `table_rows`
- `table_entry_count`
- `table_header_cell_count`
- `table_body_cell_count`
- `table_delimiter_cell_count`

## Why this exists

Micromax already recognized small GFM-style pipe tables and styled them in the
live docs/help source view:

- header rows
- delimiter rows
- body rows
- literal `|` separators

That was enough for the curses TUI, but not quite enough for future
UIs/scripts/LLMs. They still had to reverse-engineer plain pipe spans to answer:

- “what visible cells are on this row?”
- “which column is this cell in?”
- “does this delimiter row align left, center, or right?”

Rev261 closes that tiny gap while staying much smaller than a richer Markdown
AST or rendered-table subsystem.

## Example shape

```python
{
  "text": "| :--- | :---: | ---: |",
  "table_entries": [
    {
      "kind": "delimiter-cell",
      "column": 0,
      "start": 2,
      "end": 6,
      "text": ":---",
      "align": "left",
      "marker_count": 3,
    },
    {
      "kind": "delimiter-cell",
      "column": 1,
      "start": 9,
      "end": 14,
      "text": ":---:",
      "align": "center",
      "marker_count": 3,
    },
    {
      "kind": "delimiter-cell",
      "column": 2,
      "start": 17,
      "end": 21,
      "text": "---:",
      "align": "right",
      "marker_count": 3,
    },
  ],
  "table_count": 3,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help pipe tables more
honestly without scraping raw pipe spans or rerunning the tiny cell/alignment
helpers by hand.
