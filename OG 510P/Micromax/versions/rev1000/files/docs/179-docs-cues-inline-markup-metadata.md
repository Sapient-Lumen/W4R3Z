# Rev237 — shared docs/help inline-markup metadata

Rev237 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
tiny inspectability win: visible docs/help rows can now report explicit parsed
inline-markup entries for strong/emphasis/strike tokens.

## What is new

Each visible docs/help row now includes:

- `markup_entries`
- focused sibling slices: `strong_markup_entries`, `emphasis_markup_entries`, `strike_markup_entries`
- focused delimiter-family slices: `asterisk_markup_entries`, `underscore_markup_entries`, `tilde_markup_entries`
- `markup_count`
- `strong_markup_count`, `emphasis_markup_count`, `strike_markup_count`
- `asterisk_markup_count`, `underscore_markup_count`, `tilde_markup_count`

Each `markup_entries` item includes:

- `kind` — `strong`, `emphasis`, or `strike`
- `start`, `end` — full visible source span
- `body_start`, `body_end` — visible styled body span
- `delimiter` — the opener/closer token family (`**`, `__`, `*`, `_`, `~~`)
- `delimiter_kind` — `asterisk`, `underscore`, or `tilde`
- `delimiter_length` — 1 or 2 today
- `text` — visible body text

Top-level docs-cues snapshots now also report:

- `markup_rows`
- `markup_entry_count`
- `strong_markup_rows`, `emphasis_markup_rows`, `strike_markup_rows`
- `asterisk_markup_rows`, `underscore_markup_rows`, `tilde_markup_rows`
- `strong_entry_count`
- `emphasis_entry_count`
- `strike_entry_count`
- `asterisk_markup_count`, `underscore_markup_count`, `tilde_markup_count`

## Why this matters

Before rev237, future UIs/scripts/LLMs could see the style result (`bold_spans`,
`italic_spans`, `dim_spans`) but still had to infer whether a token came from
`**strong**`, `*emphasis*`, `_emphasis_`, or `~~strike~~`.

Now the shared snapshot says that directly while staying deliberately tiny:
no richer markdown tree, no widget model, and no new renderer contract.

## Example

```python
{
  "text": "Use **strong**, *soft*, _also_, and ~~gone~~.",
  "markup_entries": [
    {
      "kind": "strong",
      "start": 4,
      "end": 14,
      "body_start": 6,
      "body_end": 12,
      "delimiter": "**",
      "delimiter_kind": "asterisk",
      "delimiter_length": 2,
      "text": "strong",
    },
    {
      "kind": "emphasis",
      "start": 16,
      "end": 22,
      "body_start": 17,
      "body_end": 21,
      "delimiter": "*",
      "delimiter_length": 1,
      "text": "soft",
    },
  ],
}
```

## Contract shape

This metadata is built from the same tiny inline-markup helpers Micromax
already used for visible docs/help emphasis cues:

- code spans still take precedence
- emphasis still does not reparse inside strong or strike runs
- underscore-delimited emphasis still stays out of ordinary word-internal text

That keeps the shared model honest and aligned with the existing renderer.
