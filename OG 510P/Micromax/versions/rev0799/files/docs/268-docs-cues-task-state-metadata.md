# Rev326 — docs cues task-state metadata

Rev304 already made visible task rows first-class in the shared
`docs_cues_model(lines, cols)` / `ed.docs-cues` surface, and rev325 added tiny
list-ownership metadata for bullet-vs-ordered task rows.

That was enough to answer questions like:

- which visible rows contain task checkboxes?
- which visible tasks belong to bullet lists versus ordered lists?

But future UIs/scripts/LLMs still had to re-filter generic `task_entries` just to
answer an even more common TODO-ish question:

- which visible tasks are already done?
- which visible tasks are still open?

Rev326 keeps the parser/policy tiny while promoting those state slices into the
shared row/snapshot surface directly.

## Row-local fields

Each visible docs/help row now also carries:

- `checked_task_entries`
- `unchecked_task_entries`
- `checked_task_count`
- `unchecked_task_count`

These are focused sibling views over `task_entries`.

Each entry keeps the same tiny shape as the existing task metadata, including:

- `kind`
- `start` / `end`
- `text`
- `checked`
- `list_kind`
- `list_marker`
- optional `body_start` / `body_end`

## Snapshot-level fields

Top-level docs-cues snapshots now also carry:

- `checked_task_rows`
- `unchecked_task_rows`
- `checked_task_entry_count`
- `unchecked_task_entry_count`

That means consumers can answer both row-local and whole-viewport questions
without re-filtering generic task rows by hand.

## Example

```json
{
  "text": "- [x] done item",
  "task_entries": [
    {
      "kind": "task-checkbox",
      "start": 2,
      "end": 5,
      "text": "[x]",
      "checked": 1,
      "list_kind": "bullet",
      "list_marker": "-",
      "body_start": 6,
      "body_end": 15
    }
  ],
  "checked_task_entries": [
    {
      "kind": "task-checkbox",
      "start": 2,
      "end": 5,
      "text": "[x]",
      "checked": 1,
      "list_kind": "bullet",
      "list_marker": "-",
      "body_start": 6,
      "body_end": 15
    }
  ],
  "unchecked_task_entries": [],
  "checked_task_count": 1,
  "unchecked_task_count": 0
}
```

## Why this stays small

This does **not** add an interactive checkbox system.
It does **not** turn Micromax into a richer Markdown AST project.
It just makes one common repo-local authoring form — visible TODO/task rows — a
little easier to inspect honestly in headless snapshots and packaged archives.
