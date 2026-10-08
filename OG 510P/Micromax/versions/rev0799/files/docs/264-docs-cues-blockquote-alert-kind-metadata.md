# Rev322 — docs-cues blockquote alert-kind metadata

Rev305 already taught `docs_cues_model(lines, cols)` / `ed.docs-cues` how to
surface visible blockquote alert markers as their own focused sibling metadata
instead of leaving them only inside broader `structure_entries`.

That still left one tiny docs/help inspection gap for future UIs/scripts/LLMs:

- visible alert rows already carried a normalized `alert_kind`
- but clients still had to re-filter generic `blockquote_alert_entries` to tell
  `note` rows from `warning` rows or count `tip` rows on screen
- answering questions like "which visible alert rows are warnings rather than
  tips?" still required client-side filtering

Rev322 keeps the docs/help model tiny and source-view-first, but closes that gap
without inventing a richer markdown AST or renderer-owned alert widget model.

## New per-row fields

Each visible docs/help row now also reports focused sibling fields:

- `note_blockquote_alert_entries`
- `tip_blockquote_alert_entries`
- `important_blockquote_alert_entries`
- `warning_blockquote_alert_entries`
- `caution_blockquote_alert_entries`
- `note_blockquote_alert_count`
- `tip_blockquote_alert_count`
- `important_blockquote_alert_count`
- `warning_blockquote_alert_count`
- `caution_blockquote_alert_count`

Each entry still carries the same tiny source metadata already exposed by
`blockquote_alert_entries`:

- `kind` — always `blockquote-alert`
- `start`, `end` — visible alert marker span
- `text` — visible marker such as `[!TIP]`
- `alert_kind` — normalized kind such as `note`, `tip`, `important`,
  `warning`, or `caution`

This deliberately does **not** replace `blockquote_alert_entries`.
It simply avoids making clients re-filter a broader alert bucket when they only
care about one visible alert kind.

## New top-level row and entry counts

Top-level docs-cues snapshots now also report:

- `note_blockquote_alert_rows`, `note_blockquote_alert_entry_count`
- `tip_blockquote_alert_rows`, `tip_blockquote_alert_entry_count`
- `important_blockquote_alert_rows`, `important_blockquote_alert_entry_count`
- `warning_blockquote_alert_rows`, `warning_blockquote_alert_entry_count`
- `caution_blockquote_alert_rows`, `caution_blockquote_alert_entry_count`

That means future UIs/scripts/LLMs can distinguish:

- "how many visible alert rows are warnings?"
- "does the current viewport show any cautions?"
- "is this visible quote row a tip or an important alert?"

without scraping row text or replaying the tiny alert helper by hand.

## Example shape

```python
{
  "text": "> [!WARNING] careful now",
  "blockquote_alert_entries": [
    {
      "kind": "blockquote-alert",
      "start": 2,
      "end": 12,
      "text": "[!WARNING]",
      "alert_kind": "warning",
    },
  ],
  "warning_blockquote_alert_entries": [
    {
      "kind": "blockquote-alert",
      "start": 2,
      "end": 12,
      "text": "[!WARNING]",
      "alert_kind": "warning",
    },
  ],
  "blockquote_alert_count": 1,
  "warning_blockquote_alert_count": 1,
  "tip_blockquote_alert_count": 0,
}
```

## Consequence

Micromax still does **not** grow a richer markdown AST or renderer-owned alert
widget model here.

It just makes one more common docs/help source cue — GitHub-style alert kinds —
easier for offline humans, scripts, and future LLMs to inspect honestly.
