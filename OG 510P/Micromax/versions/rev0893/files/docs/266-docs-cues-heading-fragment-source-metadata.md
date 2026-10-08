# Rev324: docs-cues heading fragment-source metadata

## Why

`docs_cues_model(lines, cols)` / `ed.docs-cues` already exposed visible heading
rows, resolved fragments, explicit fragment text, ATX-vs-setext source kinds,
and heading levels.

That was enough for consumers willing to re-filter generic `heading_entries`
row-by-row, but it still made simple source-view deep-link questions noisier
than they needed to be:

- which visible heading rows use explicit `{#id}` fragments?
- which visible heading rows still depend on auto-generated slugs?
- how many visible heading rows would keep the same deep-link if the title text
  changed?

Rev324 keeps the parser/policy small while promoting fragment-source into the
same focused sibling surface used for other docs-cues slices.

## What changed

Every visible row in `docs_cues_model(...)` now also exposes:

- `explicit_fragment_heading_entries`
- `auto_fragment_heading_entries`

with matching row-local counts:

- `explicit_fragment_heading_count`
- `auto_fragment_heading_count`

The top-level snapshot now also reports:

- `explicit_fragment_heading_rows`
- `auto_fragment_heading_rows`
- `explicit_fragment_heading_entry_count`
- `auto_fragment_heading_entry_count`

Existing heading metadata stays intact:

- `heading_entries`
- `heading_title_entries`
- `heading_underline_entries`
- `atx_heading_entries` / `setext_heading_entries`
- `h1_heading_entries` .. `h6_heading_entries`
- per-entry `fragment`, `explicit_fragment`, and `fragment_source`

## Example shape

```python
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
      "explicit_fragment": "start-here",
      "fragment_source": "explicit",
      "start": 0,
      "end": 27,
      "text": "# Alpha Beta {#start-here}",
    }
  ],
  "explicit_fragment_heading_entries": [ ...same entry... ],
  "auto_fragment_heading_entries": [],
  "explicit_fragment_heading_count": 1,
  "auto_fragment_heading_count": 0,
}
```

Setext title rows, underline rows, and ordinary ATX headings without a trailing
`{#id}` keep surfacing under `auto_fragment_heading_entries`.

## Why this helps future UIs / LLMs

This keeps the archive more honest for offline consumers. A future UI or future
LLM no longer has to re-filter every visible heading entry just to answer:

- “is this link target stable even if the heading text changes?”
- “which rows here are intentionally pinned to explicit fragment ids?”
- “how many visible heading rows still rely on the auto slugger?”

That is useful for docs navigation, link-audit tools, migration helpers, and
plain archive comprehension, while still staying much smaller than a richer
Markdown AST.
