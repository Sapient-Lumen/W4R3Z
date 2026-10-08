# Rev263 — docs-cues visible definition metadata

Rev263 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability layer for docs/help source view: visible reference
definition rows and footnote definition rows now carry explicit definition
metadata instead of leaving future UIs/scripts/LLMs to infer everything from
`definition_role` or a second parse.

This stays tiny and source-view-first. It does **not** add a richer Markdown
AST, reference-resolution engine, or footnote subsystem. It simply reuses the
same small shared definition scans Micromax already trusts for docs navigation
and live TUI styling.

## New per-row fields

Each visible docs/help row now also reports:

- `definition_entries`
- `definition_count`

Current entry shapes are:

- `reference-definition` — starter row for `[id]: target`
- `reference-definition-cont` — wrapped destination/title continuation row
- `footnote-definition` — starter row for `[^id]: body`
- `footnote-definition-cont` — indented continuation row under a footnote body

Shared fields include:

- `kind` — starter/continuation kind
- `role` — `starter` or `continuation`
- `id` — normalized definition id
- `start`, `end`, `text` — visible row-local marker/body span/text

Starter rows also carry tiny target metadata:

- reference-definition starters: `target`, `target_kind`, `target_doc`, `target_fragment`
- footnote-definition starters: `target=#^id`, `target_kind=footnote`, `target_fragment=^id`

Continuation rows also carry:

- `parent_kind` — owning starter kind
- `continuation_index` — 1-based continuation row ordinal
- the same id/target fields as the owning starter row

## New top-level counts

Top-level docs-cues snapshots now also report:

- `definition_rows`
- `definition_entry_count`
- `reference_definition_entry_count`
- `reference_definition_cont_entry_count`
- `footnote_definition_entry_count`
- `footnote_definition_cont_entry_count`

## Why this exists

Micromax already had one tiny shared answer for docs/help definition handling:

- reference-definition parsing
- footnote-definition parsing
- wrapped reference-destination continuation rules
- footnote continuation-line render roles
- TUI dim/bold marker styling

That was enough for the live TUI and navigation commands, but not quite enough
for future UIs/scripts/LLMs receiving an offline archive. They still had to
rerun definition parsing to answer:

- “what definition id is visible on this row?”
- “is this a starter row or a continuation row?”
- “what target does this visible reference definition resolve to?”
- “which footnote body does this continuation row belong to?”

Rev263 closes that tiny gap while staying much smaller than a richer Markdown
block tree.

## Example shape

```python
{
  "text": "[^tiny]: first line",
  "line_role": "definition",
  "definition_role": "footnote",
  "definition_entries": [
    {
      "kind": "footnote-definition",
      "role": "starter",
      "id": "tiny",
      "start": 0,
      "end": 8,
      "text": "[^tiny]:",
      "target": "#^tiny",
      "target_kind": "footnote",
      "target_doc": "",
      "target_fragment": "^tiny",
    },
  ],
  "definition_count": 1,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help definition rows more
honestly — including what a visible reference definition points to and which
footnote body a continuation row belongs to — without scraping raw source or
rerunning the tiny definition scans by hand.
