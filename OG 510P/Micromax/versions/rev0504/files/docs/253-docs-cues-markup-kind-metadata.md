# Rev311 — shared docs/help inline-markup kind slices

Rev311 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability follow-up: visible docs/help rows can now expose focused
row-local strong/emphasis/strike slices instead of making callers re-filter the
broader `markup_entries` list.

## What is new

Each visible docs/help row still includes:

- `markup_entries`
- `markup_count`

Rows now also include focused sibling slices and counts:

- `strong_markup_entries`
- `emphasis_markup_entries`
- `strike_markup_entries`
- `strong_markup_count`
- `emphasis_markup_count`
- `strike_markup_count`

Top-level docs-cues snapshots now also report:

- `strong_markup_rows`
- `emphasis_markup_rows`
- `strike_markup_rows`

Existing aggregate entry totals stay intact:

- `strong_entry_count`
- `emphasis_entry_count`
- `strike_entry_count`

## Why this matters

Before rev311, future UIs/scripts/LLMs could already see parsed inline-markup
entries and total counts, but they still had to scan each row's generic
`markup_entries` to answer tiny questions like:

- does this visible row contain strong text?
- which visible runs here are emphasis rather than strike?
- how many visible rows on screen contain strike markup at all?

Rev311 keeps the parser and renderer contract small while making those common
questions direct.

## Example

```python
{
  "text": "Use **strong**, *soft*, _also_, and ~~gone~~.",
  "markup_entries": [
    {"kind": "strong", "text": "strong"},
    {"kind": "emphasis", "text": "soft"},
    {"kind": "emphasis", "text": "also"},
    {"kind": "strike", "text": "gone"},
  ],
  "strong_markup_entries": [
    {"kind": "strong", "text": "strong"},
  ],
  "emphasis_markup_entries": [
    {"kind": "emphasis", "text": "soft"},
    {"kind": "emphasis", "text": "also"},
  ],
  "strike_markup_entries": [
    {"kind": "strike", "text": "gone"},
  ],
  "strong_markup_count": 1,
  "emphasis_markup_count": 2,
  "strike_markup_count": 1,
}
```

## Contract shape

This remains a tiny view over the same shared inline-markup matcher Micromax
already used for visible docs/help styling:

- code spans still take precedence
- emphasis still does not reparse inside strong or strike runs
- underscore emphasis still avoids ordinary word-internal cases

So the new slices are only a friendlier projection of the same existing parsed
source truth rather than a second markup parser.
