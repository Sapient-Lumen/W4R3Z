# Rev313 — shared docs/help definition-kind slices

Rev313 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small inspectability follow-up: visible docs/help definition rows now expose
focused sibling slices for reference-definition starters, reference-definition
continuations, footnote-definition starters, and footnote-definition
continuations.

This stays tiny and source-view-first. It does **not** add a richer markdown
AST or a second definition parser. It simply reuses the same parsed
`definition_entries` the shared docs-cues model already emitted and publishes
the four row-local groupings future UIs/scripts/LLMs most naturally ask for.

## New per-row fields

Each visible docs/help row now also reports:

- `reference_definition_entries`
- `reference_definition_cont_entries`
- `footnote_definition_entries`
- `footnote_definition_cont_entries`
- `reference_definition_count`
- `reference_definition_cont_count`
- `footnote_definition_count`
- `footnote_definition_cont_count`

Each focused slice reuses the same small entry shape already used in
`definition_entries`.

## New top-level counts

Top-level docs-cues snapshots now also report:

- `reference_definition_rows`
- `reference_definition_cont_rows`
- `footnote_definition_rows`
- `footnote_definition_cont_rows`

The older totals stay intact:

- `definition_rows`
- `definition_entry_count`
- `reference_definition_entry_count`
- `reference_definition_cont_entry_count`
- `footnote_definition_entry_count`
- `footnote_definition_cont_entry_count`

## Why this exists

Before rev313, future UIs/scripts/LLMs could already inspect parsed visible
reference definitions, footnote definitions, and their continuation rows, but
still had to re-filter generic `definition_entries` row-by-row to answer small
practical questions like:

- “which visible rows define link references rather than footnotes?”
- “is this a starter row or just a continuation line?”
- “how many visible footnote-definition rows are on screen?”

Rev313 keeps the parser and renderer contract small while making those common
questions direct.

## Example shape

```python
{
  "text": "[^tiny]: first line",
  "definition_entries": [
    {
      "kind": "footnote-definition",
      "role": "starter",
      "id": "tiny",
      "text": "[^tiny]:",
      "target": "#^tiny",
      "target_kind": "footnote",
      "target_fragment": "^tiny",
    }
  ],
  "reference_definition_entries": [],
  "reference_definition_cont_entries": [],
  "footnote_definition_entries": [
    {
      "kind": "footnote-definition",
      "role": "starter",
      "id": "tiny",
      "text": "[^tiny]:",
      "target": "#^tiny",
      "target_kind": "footnote",
      "target_fragment": "^tiny",
    }
  ],
  "footnote_definition_cont_entries": [],
  "reference_definition_count": 0,
  "reference_definition_cont_count": 0,
  "footnote_definition_count": 1,
  "footnote_definition_cont_count": 0,
}
```

## Consequence

Future UIs/scripts/LLMs can now inspect visible docs/help definition rows more
honestly without scraping `definition_role` alone or re-filtering generic
`definition_entries` by hand just to separate reference definitions from
footnotes and starters from continuation rows.
