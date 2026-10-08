# Rev318 — shared docs/help inline-markup delimiter metadata

Rev318 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small source-view inspectability win: visible docs/help rows can now report
which delimiter family each inline-markup token used.

## What is new

Each visible docs/help row now also includes:

- `asterisk_markup_entries`
- `underscore_markup_entries`
- `tilde_markup_entries`
- `asterisk_markup_count`
- `underscore_markup_count`
- `tilde_markup_count`

Each `markup_entries` item now also includes:

- `delimiter_kind` — `asterisk`, `underscore`, or `tilde`

Top-level docs-cues snapshots now also report:

- `asterisk_markup_rows`
- `underscore_markup_rows`
- `tilde_markup_rows`
- `asterisk_markup_count`
- `underscore_markup_count`
- `tilde_markup_count`

## Why this matters

Rev311 already made strong/emphasis/strike runs inspectable, but future
UIs/scripts/LLMs still had to re-filter raw `delimiter` strings to answer
source-view questions like:

- is this emphasis row star-based or underscore-based?
- which visible rows use tilde-delimited strike syntax?
- how many visible inline-markup entries still use asterisks?

Rev318 keeps the model tiny and inspectable:

- no richer markdown tree
- no renderer-only hidden state
- same shared inline-markup matches the docs/help renderer already trusts

## Example

```python
{
  "markup_rows": 1,
  "asterisk_markup_rows": 1,
  "underscore_markup_rows": 1,
  "tilde_markup_rows": 1,
  "asterisk_markup_count": 2,
  "underscore_markup_count": 1,
  "tilde_markup_count": 1,
  "rows": [
    {
      "text": "Use **strong**, *soft*, _also_, and ~~gone~~.",
      "markup_count": 4,
      "asterisk_markup_count": 2,
      "underscore_markup_count": 1,
      "tilde_markup_count": 1,
      "markup_entries": [
        {
          "kind": "strong",
          "delimiter": "**",
          "delimiter_kind": "asterisk",
          "text": "strong",
        },
        {
          "kind": "emphasis",
          "delimiter": "*",
          "delimiter_kind": "asterisk",
          "text": "soft",
        },
        {
          "kind": "emphasis",
          "delimiter": "_",
          "delimiter_kind": "underscore",
          "text": "also",
        },
        {
          "kind": "strike",
          "delimiter": "~~",
          "delimiter_kind": "tilde",
          "text": "gone",
        },
      ],
      "asterisk_markup_entries": [
        {"text": "strong"},
        {"text": "soft"},
      ],
      "underscore_markup_entries": [
        {"text": "also"},
      ],
      "tilde_markup_entries": [
        {"text": "gone"},
      ],
    },
  ],
}
```

## Contract shape

This metadata is built from the same tiny inline-markup helpers Micromax
already used for visible docs/help emphasis cues and rev311's row-local markup
entries. Rev318 simply promotes the delimiter family into a first-class shared
surface instead of making future consumers scrape raw delimiter strings.
