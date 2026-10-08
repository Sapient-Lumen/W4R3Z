# Rev264 — docs-cues visible block metadata

Rev264 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible fenced-code,
raw-HTML-block, and indented-code rows now carry explicit block metadata
instead of leaving future UIs/scripts/LLMs to infer everything from coarse
`line_role` values.

This stays tiny and source-view-first. It does **not** add a richer Markdown
AST, syntax highlighter, or block-rendering subsystem. It simply reuses the
same small shared fence / HTML-block / indented-code scans Micromax already
trusts for docs/help precedence and live TUI styling.

## New per-row fields

Each visible docs/help row now also reports:

- `block_entries`
- `block_count`

Current entry shapes are:

- `fenced-code` — visible opener/body/closer row from a fenced code block
- `html-block` — visible row from a raw HTML block
- `indented-code` — visible row from a blank-separated indented code run

Shared fields include:

- `kind` — block-ish row kind
- `role` — `opener` / `body` / `closer` for fenced code, `line` otherwise
- `block_index` — stable 1-based block ordinal within the source buffer
- `start`, `end`, `text` — visible row-local span/text

Fenced opener/closer rows also carry tiny fence metadata:

- `marker` — `` ` `` or `~`
- `marker_count` — visible fence length
- `indent` — opening/closing fence indent

Fenced opener rows also carry:

- `info_string` — trimmed post-fence text
- `language` — first word of the info string, or `""`

Indented-code rows also carry:

- `indent_text` — the visible leading whitespace prefix
- `indent_width` — its raw character length

## New top-level counts

Top-level docs-cues snapshots now also report:

- `block_rows`
- `block_entry_count`
- `fenced_code_entry_count`
- `fenced_code_opener_entry_count`
- `fenced_code_body_entry_count`
- `fenced_code_closer_entry_count`
- `html_block_entry_count`
- `indented_code_entry_count`

## Why this exists

Micromax already had one tiny shared answer for docs/help block-ish precedence:

- fenced-code line detection
- raw HTML block detection
- blank-separated indented-code detection
- inert-row styling and docs-action masking

That was enough for the live TUI and navigation commands, but not quite enough
for future UIs/scripts/LLMs receiving an offline archive. They still had to
rerun block scans to answer:

- “is this visible fence row an opener or a closer?”
- “what info string/language hint does this visible opener carry?”
- “which raw HTML rows belong to the same block?”
- “which visible indented-code rows are part of the same run?”

Rev264 closes that tiny gap while staying much smaller than a richer Markdown
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
  "block_count": 1,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help fenced/html/indented
rows more honestly — including fence info strings and simple block grouping —
without scraping raw source or rerunning the tiny shared scans by hand.
