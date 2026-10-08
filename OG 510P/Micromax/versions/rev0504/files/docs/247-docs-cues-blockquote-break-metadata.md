Rev322 follow-up: visible GitHub-style alert rows now also expose focused per-kind slices (`note_blockquote_alert_entries`, `tip_blockquote_alert_entries`, `important_blockquote_alert_entries`, `warning_blockquote_alert_entries`, `caution_blockquote_alert_entries`) plus matching row/count summaries. See `docs/264-docs-cues-blockquote-alert-kind-metadata.md`.

# Rev305 — docs-cues explicit blockquote and thematic-break metadata

Rev304 already taught `docs_cues_model(lines, cols)` / `ed.docs-cues` how to
surface visible task rows as their own focused sibling metadata instead of
forcing clients to re-filter `structure_entries`.

That still left one tiny docs/help inspection gap for future UIs/scripts/LLMs:

- blockquote prefixes and GitHub-style alert markers were still only present in
  generic `structure_entries`
- thematic-break separators were also only present there
- answering questions like "which visible rows are alerts?" or "how many quote
  separators are on screen?" still required client-side filtering

Rev305 keeps the docs/help model tiny and source-view-first, but closes that
gap too.

## New per-row fields

Each visible docs/help row now also reports focused sibling fields:

- `blockquote_entries`
- `blockquote_alert_entries`
- `thematic_break_entries`
- `blockquote_count`
- `blockquote_alert_count`
- `thematic_break_count`

`blockquote_entries` currently carries the already visible source prefix plus
small structural context:

- `kind` — always `blockquote-prefix`
- `start`, `end` — visible prefix span
- `text` — visible source token such as `>` or `> > `
- `depth` — tiny nesting depth inferred from the visible prefix
- optional `body_start`, `body_end` — visible body span on the row

`blockquote_alert_entries` currently carries:

- `kind` — always `blockquote-alert`
- `start`, `end` — visible alert marker span
- `text` — visible marker such as `[!TIP]`
- `alert_kind` — normalized kind such as `note`, `tip`, or `warning`

`thematic_break_entries` currently carries:

- `kind` — always `thematic-break`
- `start`, `end` — visible break span
- `text` — visible source token such as `---` or `* * *`
- `marker` — normalized marker character (`-`, `*`, `_`)
- `marker_count` — visible marker count on the row

This deliberately does **not** replace `structure_entries`.
It simply avoids making clients re-filter broader structure metadata when they
only care about quote/alert/separator rows.

## New top-level row counts

Top-level docs-cues snapshots now also report:

- `blockquote_rows`
- `blockquote_alert_rows`
- `thematic_break_rows`

That means future UIs/scripts/LLMs can distinguish:

- "how many visible rows are blockquotes?"
- "how many visible rows carry GitHub-style alert markers?"
- "how many visible rows are thematic separators?"

without scraping row text or replaying the tiny markdown helpers by hand.

## Example shape

```python
{
  "text": "> [!WARNING] careful now",
  "blockquote_entries": [
    {
      "kind": "blockquote-prefix",
      "start": 0,
      "end": 2,
      "text": "> ",
      "depth": 1,
      "body_start": 2,
      "body_end": 24,
    },
  ],
  "blockquote_alert_entries": [
    {
      "kind": "blockquote-alert",
      "start": 2,
      "end": 12,
      "text": "[!WARNING]",
      "alert_kind": "warning",
    },
  ],
  "blockquote_count": 1,
  "blockquote_alert_count": 1,
}
```

## Consequence

Micromax still does **not** grow a richer markdown AST or renderer-owned alert
widget model here.

It just makes a few common docs/help source cues — quotes, GitHub-style alerts,
and thematic separators — easier for offline humans, scripts, and future LLMs
to inspect honestly.
