# Rev238 — docs-cues visible literal-source metadata

Rev312 follow-up: row/snapshot literal-kind slices now live in `docs/254-docs-cues-literal-kind-metadata.md` (`raw_html_literal_entries`, `escaped_markdown_entries`, matching row counts).

Rev238 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible inline raw-HTML
source tags and backslash-escaped markdown punctuation now show up as explicit
structured entries instead of living only inside generic dim spans.

This stays tiny and source-view-first. It does **not** add a richer HTML model
or a new escape parser. It simply reuses the same small helpers the reference
TUI already trusts for dimming and precedence.

## New per-row fields

Each visible docs/help row now also reports:

- `literal_entries`
- `literal_count`

Each `literal_entries` item includes:

- `kind` — `raw-html-tag` or `escaped-markdown`
- `start`, `end` — visible token span on the rendered row text
- `text` — visible literal token text
- `detail` — tiny structured detail:
  - raw HTML tags: lowercased tag name when available (`kbd`, `a`, ...)
  - escaped markdown pairs: escaped punctuation (`[`, `<`, `*`, ...)

## New top-level counts

Top-level docs-cues snapshots now also report:

- `literal_rows`
- `literal_entry_count`
- `raw_html_entry_count`
- `escaped_markdown_entry_count`

## Why this exists

Micromax already dimmed these visible source forms in docs/help buffers:

- inline raw HTML tags like `<kbd>` / `</kbd>` / `<a name=...>`
- escaped markdown pairs like `\[` / `\!` / `\<` / `\*`

That was enough for the curses TUI, but not quite enough for future
UIs/scripts/LLMs. They still had to reverse-engineer dim spans to answer:

- “why is this token dim?”
- “is this a literal HTML tag or just escaped markdown punctuation?”
- “which tag name is visible here?”

Rev238 closes that tiny gap while staying smaller than a richer HTML or
Markdown AST.

## Example shape

```python
{
  "text": "Use <kbd>, </kbd>, \\[tag], and \\<https://example.invalid/>.",
  "literal_entries": [
    {
      "kind": "raw-html-tag",
      "start": 4,
      "end": 9,
      "text": "<kbd>",
      "detail": "kbd",
    },
    {
      "kind": "raw-html-tag",
      "start": 11,
      "end": 17,
      "text": "</kbd>",
      "detail": "kbd",
    },
    {
      "kind": "escaped-markdown",
      "start": 19,
      "end": 21,
      "text": r"\\[",
      "detail": "[",
    },
    {
      "kind": "escaped-markdown",
      "start": 32,
      "end": 34,
      "text": r"\\<",
      "detail": "<",
    },
  ],
  "literal_count": 4,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible literal docs/help source more
honestly without scraping `dim_spans` or rerunning the tiny raw-HTML / escape
helpers by hand.
