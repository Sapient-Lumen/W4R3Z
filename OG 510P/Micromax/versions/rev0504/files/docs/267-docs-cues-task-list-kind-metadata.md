# Rev325 — docs-cues task-list source-kind metadata

Rev304 already taught `docs_cues_model(lines, cols)` / `ed.docs-cues` how to
surface visible task rows as explicit `task_entries`.

That was enough for the reference TUI, but it still left one tiny usability gap
for TODO-heavy docs and future UIs/scripts/LLMs:

- visible task rows still had to be correlated with separate `list_entries`
  just to answer whether a task belonged to a bullet list or an ordered list
- row-local task counts could say checked vs unchecked, but not bullet-vs-
  ordered task rows
- top-level snapshots could count visible tasks, but not how many visible task
  rows were bullet tasks vs ordered tasks

Rev325 keeps the docs/help model tiny and source-view-first, but closes that
gap.

## New per-entry fields

Each visible task entry now also carries:

- `list_kind` — `bullet` or `ordered`
- `list_marker` — the visible source token that owns the task row (`-`, `*`,
  `1.`, `2)`, ...)

That means `task_entries` can now answer a small but common question directly:

- “is this visible task row written as a bullet task or an ordered task?”

without joining task and list metadata by hand.

## New per-row fields

Each visible docs/help row now also reports:

- `bullet_task_entries`
- `ordered_task_entries`
- `bullet_task_count`
- `ordered_task_count`

These are focused sibling views over `task_entries`.

## New top-level counts

Top-level docs-cues snapshots now also report:

- `bullet_task_rows`
- `ordered_task_rows`
- `bullet_task_entry_count`
- `ordered_task_entry_count`

That means future UIs/scripts/LLMs can distinguish:

- “how many visible task rows are bullet tasks?”
- “how many visible task rows are ordered tasks?”

without scraping row text or replaying the tiny markdown helpers by hand.

## Example shape

```python
{
  "text": "1. [ ] todo item",
  "task_entries": [
    {
      "kind": "task-checkbox",
      "start": 3,
      "end": 6,
      "text": "[ ]",
      "checked": 0,
      "list_kind": "ordered",
      "list_marker": "1.",
      "body_start": 7,
      "body_end": 16,
    },
  ],
  "bullet_task_entries": [],
  "ordered_task_entries": [
    {
      "kind": "task-checkbox",
      "start": 3,
      "end": 6,
      "text": "[ ]",
      "checked": 0,
      "list_kind": "ordered",
      "list_marker": "1.",
      "body_start": 7,
      "body_end": 16,
    },
  ],
  "bullet_task_count": 0,
  "ordered_task_count": 1,
}
```

## Consequence

Micromax still does **not** grow a richer markdown AST or interactive checkbox
widget model here.

It just makes one common repo-local authoring form — visible TODO/task rows — a
little more honest and inspectable for offline humans, scripts, and future LLMs.
