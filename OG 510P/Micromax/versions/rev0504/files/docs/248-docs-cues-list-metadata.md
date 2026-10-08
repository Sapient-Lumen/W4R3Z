# Rev306 — docs-cues explicit list-marker metadata

Rev260 already taught `docs_cues_model(lines, cols)` / `ed.docs-cues` how to
surface visible docs/help structure through `structure_entries`, and rev304/rev305
promoted task/blockquote/thematic slices into focused sibling metadata.

That still left one tiny docs/help inspection gap for future UIs/scripts/LLMs:

- plain bullet and ordered list markers were still only present inside generic
  `structure_entries`
- answering questions like "which visible rows are bullets?" or "how many
  ordered-list rows are on screen?" still required client-side filtering
- top-level docs-cues summaries had `list_entry_count`, but not a direct row
  split between bullet and ordered rows

Rev306 keeps the docs/help model tiny and source-view-first, but closes that
last small list-marker gap too.

## New per-row fields

Each visible docs/help row now also reports focused sibling fields:

- `list_entries`
- `list_count`
- `bullet_list_count`
- `ordered_list_count`

`list_entries` is a focused sibling view over the already existing
`structure_entries` list-marker data. Each entry currently carries:

- `kind` — always `list-marker`
- `start`, `end` — visible marker span
- `text` — visible source marker (`-`, `*`, `+`, `1.`, `2)`, ...)
- `list_kind` — `bullet` or `ordered`
- `marker` — the visible source marker token again, for direct copy/display

This deliberately does **not** replace `structure_entries`.
It simply avoids making clients re-filter broader structure metadata when they
only care about visible list markers.

## New top-level row counts

Top-level docs-cues snapshots now also report:

- `list_rows`
- `bullet_list_rows`
- `ordered_list_rows`
- `bullet_list_entry_count`
- `ordered_list_entry_count`

That means future UIs/scripts/LLMs can distinguish:

- "how many visible rows are list rows?"
- "how many visible rows are bullet-list rows?"
- "how many visible rows are ordered-list rows?"

without scraping row text or replaying the tiny markdown list-marker helpers by
hand.

## Example shape

```python
{
  "text": "2) beta",
  "list_entries": [
    {
      "kind": "list-marker",
      "start": 0,
      "end": 2,
      "text": "2)",
      "list_kind": "ordered",
      "marker": "2)",
    },
  ],
  "list_count": 1,
  "bullet_list_count": 0,
  "ordered_list_count": 1,
}
```

## Consequence

Micromax still does **not** grow a richer markdown AST or interactive list
widget model here.

It just makes one more common repo-local authoring form — plain bullet and
ordered list rows — a little more honest and inspectable for offline humans,
scripts, and future LLMs.
