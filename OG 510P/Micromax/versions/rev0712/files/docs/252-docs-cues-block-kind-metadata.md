# Rev310 — docs-cues visible block-kind metadata

Rev310 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible fenced-code,
raw-HTML-block, and indented-code rows now also carry focused block-kind slices
instead of leaving future UIs/scripts/LLMs to re-filter generic `block_entries`
row by row.

This stays tiny and source-view-first. It does **not** add a richer Markdown
AST, syntax highlighter, or block-rendering subsystem. It simply reuses the
same small shared block scans Micromax already trusts for docs/help
precedence, navigation masking, and live TUI styling.

## New per-row fields

Each visible docs/help row now also reports:

- `fenced_code_entries`
- `fenced_code_opener_entries`
- `fenced_code_body_entries`
- `fenced_code_closer_entries`
- `html_block_entries`
- `indented_code_entries`
- matching row-local `*_count` fields

These are focused sibling slices over the existing `block_entries` data.

## New top-level counts

Top-level docs-cues snapshots now also report:

- `fenced_code_rows`
- `fenced_code_opener_rows`
- `fenced_code_body_rows`
- `fenced_code_closer_rows`
- `html_block_rows`
- `indented_code_rows`

Existing `block_rows`, `block_entry_count`, and the older block entry totals all
stay intact.

## Why this exists

Micromax already had one tiny shared answer for docs/help block-ish
inspectability:

- `block_entries` exposed parsed visible fenced/html/indented rows
- top-level counts already tracked fenced/html/indented entry totals
- `line_role` already distinguished fenced/body/html/indented render roles

That was enough for the live TUI and narrow tests, but future UIs/scripts/LLMs
receiving an offline archive still had to re-filter generic `block_entries` to
answer questions like:

- “is this visible fenced-code row an opener, body, or closer?”
- “which visible rows are raw HTML block lines?”
- “which visible rows belong to indented code?”

Rev310 closes that tiny gap while staying much smaller than a richer Markdown
block tree.

## Example shape

```python
{
  "text": "```python",
  "line_role": "fenced-fence",
  "block_entries": [
    {
      "kind": "fenced-code",
      "role": "opener",
      "block_index": 1,
      "start": 0,
      "end": 3,
      "text": "```python",
      "marker": "`",
      "marker_count": 3,
      "indent": 0,
      "info_string": "python",
      "language": "python",
    },
  ],
  "fenced_code_entries": [
    {
      "kind": "fenced-code",
      "role": "opener",
      "block_index": 1,
      "start": 0,
      "end": 3,
      "text": "```python",
      "marker": "`",
      "marker_count": 3,
      "indent": 0,
      "info_string": "python",
      "language": "python",
    },
  ],
  "fenced_code_opener_entries": [
    {
      "kind": "fenced-code",
      "role": "opener",
      "block_index": 1,
      "start": 0,
      "end": 3,
      "text": "```python",
      "marker": "`",
      "marker_count": 3,
      "indent": 0,
      "info_string": "python",
      "language": "python",
    },
  ],
  "fenced_code_body_entries": [],
  "fenced_code_closer_entries": [],
  "html_block_entries": [],
  "indented_code_entries": [],
  "block_count": 1,
  "fenced_code_count": 1,
  "fenced_code_opener_count": 1,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help fenced/html/indented
rows more honestly without scraping raw source or re-filtering generic
`block_entries` by hand.
