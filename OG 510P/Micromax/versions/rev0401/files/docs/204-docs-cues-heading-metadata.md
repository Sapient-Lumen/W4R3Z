# Rev262 — docs-cues visible heading metadata

Rev262 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible heading rows now
carry explicit heading metadata instead of leaving future UIs/scripts/LLMs to
infer titles and fragments from `line_role`, `heading_level`, or a second
heading scan.

This stays tiny and source-view-first. It does **not** add a richer Markdown
AST, rendered heading widget, or outline subsystem. It simply reuses the same
small shared heading scan Micromax already trusts for docs titles, outline
rows, heading breadcrumbs, and fragment jumps.

## New per-row fields

Each visible docs/help row now also reports:

- `heading_entries`
- `heading_count`

Current entry shape is:

- `kind` — currently always `heading`
- `role` — `title` or `underline`
- `source_kind` — `atx` or `setext`
- `level` — resolved heading level
- `title` — cleaned human heading title
- `fragment` — resolved fragment/slug used for jumps
- `explicit_fragment` — explicit `{#id}` fragment when present, else `""`
- `fragment_source` — `explicit` or `auto`
- `start`, `end`, `text` — the visible row-local fragment span/text
- underline rows also carry `marker` and `marker_count`

## New top-level counts

Top-level docs-cues snapshots now also report:

- `heading_rows`
- `heading_entry_count`
- `heading_title_entry_count`
- `heading_underline_entry_count`

## Why this exists

Micromax already had one tiny shared answer for docs/help heading discovery:

- titles
- outline rows
- heading breadcrumbs
- fragment jumps
- title/underline render roles

That was enough for the live TUI and navigation commands, but not quite enough
for future UIs/scripts/LLMs receiving an offline archive. They still had to
rerun heading discovery to answer:

- “what human heading title is visible on this row?”
- “what fragment would this row navigate to?”
- “is this underline row part of a setext heading?”

Rev262 closes that tiny gap while staying much smaller than a richer Markdown
block tree.

## Example shape

```python
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
      "explicit_fragment": "",
      "fragment_source": "auto",
      "start": 0,
      "end": 5,
      "text": "-----",
      "marker": "-",
      "marker_count": 5,
    },
  ],
  "heading_count": 1,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help heading rows more
honestly — including the resolved fragment a title row or underline row points
to — without scraping raw source or rerunning the tiny heading scan by hand.
