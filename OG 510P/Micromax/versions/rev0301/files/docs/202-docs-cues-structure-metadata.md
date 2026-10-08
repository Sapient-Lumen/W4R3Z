# Rev260 — docs-cues visible structure metadata

Rev260 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible list/task/blockquote
/thematic structure now shows up as explicit structured entries instead of living
only inside generic bold/dim spans and line roles.

This stays tiny and source-view-first. It does **not** add a richer Markdown
block tree or a new renderer policy. It simply reuses the same small helpers the
reference TUI already trusts for scanability cues.

## New per-row fields

Each visible docs/help row now also reports:

- `structure_entries`
- `structure_count`

Each `structure_entries` item includes a `kind` plus the visible source span
and token `text`. Current kinds are:

- `list-marker`
  - `list_kind` — `bullet` or `ordered`
  - `marker` — the visible marker token (`-`, `*`, `1.`, `2)`, ...)
- `task-checkbox`
  - `checked` — `1` or `0`
  - optional `body_start`, `body_end` for the visible task body
- `blockquote-prefix`
  - `depth` — visible quote nesting depth
  - optional `body_start`, `body_end` for the visible quoted body
- `blockquote-alert`
  - `alert_kind` — `note`, `tip`, `important`, `warning`, or `caution`
- `thematic-break`
  - `marker` — `-`, `*`, or `_`
  - `marker_count` — visible marker count on the row

## New top-level counts

Top-level docs-cues snapshots now also report:

- `structure_rows`
- `structure_entry_count`
- `list_entry_count`
- `task_entry_count`
- `blockquote_entry_count`
- `blockquote_alert_entry_count`
- `thematic_break_entry_count`

## Why this exists

Micromax already styled these visible docs/help source forms:

- list bullets / ordered markers
- task-list checkboxes
- blockquote prefixes and GitHub-style alert openers
- thematic break marker runs

That was enough for the curses TUI, but not quite enough for future
UIs/scripts/LLMs. They still had to reverse-engineer bold/dim spans to answer:

- “why does this row read like a task item or quote?”
- “is this blockquote line also an alert opener?”
- “what visible structure marker is on this row?”

Rev260 closes that tiny gap while staying much smaller than a richer Markdown
AST or renderer-level block model.

## Example shape

```python
{
  "text": "> [!WARNING] careful now",
  "structure_entries": [
    {
      "kind": "blockquote-prefix",
      "start": 0,
      "end": 2,
      "text": "> ",
      "depth": 1,
      "body_start": 2,
      "body_end": 24,
    },
    {
      "kind": "blockquote-alert",
      "start": 2,
      "end": 12,
      "text": "[!WARNING]",
      "alert_kind": "warning",
    },
  ],
  "structure_count": 2,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help structure markers
more honestly without scraping generic spans or rerunning the tiny list/task
/blockquote/thematic helpers by hand.
