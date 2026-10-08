# Rev312 — shared docs/help literal-kind slices

Rev312 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible literal-source
entries now come with focused sibling slices for raw HTML tags versus
backslash-escaped markdown punctuation.

This stays tiny and source-view-first. It does **not** add a richer HTML model
or a second escape parser. It simply reuses the same literal-source entries the
shared model already emitted and publishes the two most common groupings future
UIs/scripts/LLMs immediately ask for.

## New per-row fields

Each visible docs/help row now also reports:

- `raw_html_literal_entries`
- `escaped_markdown_entries`
- `raw_html_literal_count`
- `escaped_markdown_count`

Each `raw_html_literal_entries` item is the same small entry shape already used
in `literal_entries`:

- `kind` — always `raw-html-tag`
- `start`, `end` — visible token span on the rendered row text
- `text` — visible literal token text
- `detail` — lowercased tag name when available (`kbd`, `a`, ...)

Each `escaped_markdown_entries` item also reuses the same entry shape:

- `kind` — always `escaped-markdown`
- `start`, `end` — visible token span on the rendered row text
- `text` — visible escape token text
- `detail` — escaped punctuation (`[`, `<`, `*`, ...)

## New top-level counts

Top-level docs-cues snapshots now also report:

- `raw_html_rows`
- `escaped_markdown_rows`

The older totals stay intact:

- `literal_rows`
- `literal_entry_count`
- `raw_html_entry_count`
- `escaped_markdown_entry_count`

## Why this exists

Before rev312, future UIs/scripts/LLMs could already see parsed literal-source
entries and aggregate raw-HTML / escaped-markdown totals, but they still had to
re-filter generic `literal_entries` row-by-row to answer small practical
questions like:

- “which visible rows contain raw HTML tags?”
- “does this row contain escaped markdown or actual raw HTML?”
- “which visible literal tokens on this row are tags versus backslash escapes?”

Rev312 keeps the parser and renderer contract small while making those common
questions direct.

## Example shape

```python
{
  "text": "Use <kbd>, </kbd>, \\[tag], and \\<https://example.invalid/>.",
  "literal_entries": [
    {"kind": "raw-html-tag", "text": "<kbd>", "detail": "kbd"},
    {"kind": "raw-html-tag", "text": "</kbd>", "detail": "kbd"},
    {"kind": "escaped-markdown", "text": r"\\[", "detail": "["},
    {"kind": "escaped-markdown", "text": r"\\<", "detail": "<"},
  ],
  "raw_html_literal_entries": [
    {"kind": "raw-html-tag", "text": "<kbd>", "detail": "kbd"},
    {"kind": "raw-html-tag", "text": "</kbd>", "detail": "kbd"},
  ],
  "escaped_markdown_entries": [
    {"kind": "escaped-markdown", "text": r"\\[", "detail": "["},
    {"kind": "escaped-markdown", "text": r"\\<", "detail": "<"},
  ],
  "raw_html_literal_count": 2,
  "escaped_markdown_count": 2,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help literal-source rows
more honestly without scraping `dim_spans` or re-filtering generic
`literal_entries` by hand just to separate tags from escapes.
