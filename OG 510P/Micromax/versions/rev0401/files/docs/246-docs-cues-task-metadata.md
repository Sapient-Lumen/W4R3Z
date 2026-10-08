# Rev304 — docs-cues explicit task metadata

Rev260 already taught `docs_cues_model(lines, cols)` / `ed.docs-cues` how to
surface visible docs/help structure through `structure_entries`.

That was enough for the reference TUI, but it still left one tiny usability gap
for TODO-heavy docs and future UIs/scripts/LLMs:

- task rows were present only as filtered `structure_entries`
- answering "which visible tasks are checked right now?" still required
  extra client-side filtering
- top-level counts could say how many task-checkbox entries existed, but not how
  many task rows were visible or how many were checked vs unchecked

Rev304 keeps the docs/help model tiny and source-view-first, but closes that gap.

## New per-row fields

Each visible docs/help row now also reports:

- `task_entries`
- `task_count`
- `checked_task_count`
- `unchecked_task_count`

`task_entries` is a focused sibling view over the already existing
`structure_entries` task-checkbox data. Each entry currently carries:

- `kind` — always `task-checkbox`
- `start`, `end` — visible checkbox span
- `text` — visible source token (`[ ]`, `[x]`, `[X]`)
- `checked` — `1` or `0`
- `list_kind` — `bullet` or `ordered` when the task is attached to a visible list marker
- `list_marker` — the visible list token (`-`, `*`, `1.`, `2)`, ...) that owns the task row
- optional `body_start`, `body_end` — visible task body span on the row

This deliberately does **not** replace `structure_entries`.
It simply avoids making clients re-filter broader structure metadata when they
only care about tasks.

## New top-level counts

Top-level docs-cues snapshots now also report:

- `task_rows`
- `checked_task_entry_count`
- `unchecked_task_entry_count`
- `bullet_task_rows`
- `ordered_task_rows`
- `bullet_task_entry_count`
- `ordered_task_entry_count`

That means future UIs/scripts/LLMs can distinguish:

- "how many visible rows are task rows?"
- "how many visible task checkboxes are checked?"
- "how many visible task checkboxes are unchecked?"

without scraping row text or replaying the tiny markdown helpers by hand.

## Example shape

```python
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
      "body_end": 15,
    },
  ],
  "task_count": 1,
  "checked_task_count": 1,
  "unchecked_task_count": 0,
  "bullet_task_count": 1,
  "ordered_task_count": 0,
}
```

## Consequence

Micromax still does **not** grow a richer markdown AST or interactive checkbox
widget model here.

It just makes one common repo-local authoring form — visible TODO/task rows — a
little more honest and inspectable for offline humans, scripts, and future LLMs.


Rev325 follow-up: visible task rows now also expose focused `bullet_task_entries` and `ordered_task_entries` sibling slices plus matching row/snapshot counts, so TODO-heavy docs/help views can distinguish bullet-task rows from ordered-task rows without correlating `list_entries` and `task_entries` by hand. See `docs/267-docs-cues-task-list-kind-metadata.md`.

Rev326 follow-up: visible task rows now also expose focused `checked_task_entries` and `unchecked_task_entries` sibling slices plus matching row/snapshot counts, so TODO-heavy docs/help views can inspect done-vs-open task rows without re-filtering generic `task_entries`. See `docs/268-docs-cues-task-state-metadata.md`.
