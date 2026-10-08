# Rev314 — docs-cues heading-kind metadata

Rev314 extends the shared `docs_cues_model(lines, cols)` / `ed.docs-cues`
snapshot with focused heading-kind slices.

## What is new

Per visible docs/help row, the model now also exposes:

- `heading_title_entries`
- `heading_underline_entries`
- `atx_heading_entries`
- `setext_heading_entries`

with matching row-local counts:

- `heading_title_count`
- `heading_underline_count`
- `atx_heading_count`
- `setext_heading_count`

Top-level docs-cues snapshots now also report:

- `heading_title_rows`
- `heading_underline_rows`
- `atx_heading_rows`
- `setext_heading_rows`
- `atx_heading_entry_count`
- `setext_heading_entry_count`

Existing `heading_entries`, `heading_rows`, `heading_entry_count`,
`heading_title_entry_count`, and `heading_underline_entry_count` stay intact.

## Why this exists

Micromax already had one tiny shared answer for visible heading rows:

- `heading_entries` told you the resolved title, fragment, level, source kind,
  and whether a row was the title line or the underline line.
- the top-level snapshot already counted heading entries and title-vs-underline
  totals.

That was enough for rendering and navigation, but future UIs/scripts/LLMs still
had to re-filter generic `heading_entries` row-by-row to answer small practical
questions like:

- is this visible heading row ATX or setext source?
- is this visible row the title line or the underline line of a setext heading?
- how many visible ATX rows are on screen right now?

Rev314 keeps the parser/policy tiny while promoting those common slices into
first-class siblings.

## Example shape

```python
{
  "heading_rows": 3,
  "heading_title_rows": 2,
  "heading_underline_rows": 1,
  "atx_heading_rows": 1,
  "setext_heading_rows": 2,
  "rows": [
    {
      "text": "# Alpha Beta {#start-here}",
      "heading_entries": [
        {
          "kind": "heading",
          "role": "title",
          "source_kind": "atx",
          "level": 1,
          "title": "Alpha Beta",
          "fragment": "start-here",
        },
      ],
      "heading_title_entries": [
        {
          "kind": "heading",
          "role": "title",
          "source_kind": "atx",
          "level": 1,
          "title": "Alpha Beta",
          "fragment": "start-here",
        },
      ],
      "heading_underline_entries": [],
      "atx_heading_entries": [
        {
          "kind": "heading",
          "role": "title",
          "source_kind": "atx",
          "level": 1,
          "title": "Alpha Beta",
          "fragment": "start-here",
        },
      ],
      "setext_heading_entries": [],
      "heading_title_count": 1,
      "heading_underline_count": 0,
      "atx_heading_count": 1,
      "setext_heading_count": 0,
    },
    {
      "text": "-----",
      "line_role": "heading-underline",
      "heading_entries": [
        {
          "kind": "heading",
          "role": "underline",
          "source_kind": "setext",
          "level": 2,
          "title": "Setext topic",
          "fragment": "setext-topic",
          "marker": "-",
          "marker_count": 5,
        },
      ],
      "heading_title_entries": [],
      "heading_underline_entries": [
        {
          "kind": "heading",
          "role": "underline",
          "source_kind": "setext",
          "level": 2,
          "title": "Setext topic",
          "fragment": "setext-topic",
          "marker": "-",
          "marker_count": 5,
        },
      ],
      "atx_heading_entries": [],
      "setext_heading_entries": [
        {
          "kind": "heading",
          "role": "underline",
          "source_kind": "setext",
          "level": 2,
          "title": "Setext topic",
          "fragment": "setext-topic",
          "marker": "-",
          "marker_count": 5,
        },
      ],
      "heading_title_count": 0,
      "heading_underline_count": 1,
      "atx_heading_count": 0,
      "setext_heading_count": 1,
    },
  ],
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help heading rows more
directly — especially ATX-vs-setext and title-vs-underline questions — without
scraping raw source or re-filtering generic `heading_entries` by hand.
