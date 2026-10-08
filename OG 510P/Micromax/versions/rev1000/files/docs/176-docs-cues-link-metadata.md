# Rev234 — docs-cues visible link metadata

Rev227 made the visible docs/help cue surface inspectable, but it still only
reported `link_spans`.

That was enough for renderers, but not for future humans/LLMs who want to ask
simple questions like:

- what does this visible row link to?
- is that target a same-page fragment, another help topic, a relative file, or
  an external URL?
- how many visible docs/help links are on screen right now?

Rev234 keeps the contract tiny and source-view-first while answering those
questions directly.

Rev315 follow-up: each `link_entries` item now also carries tiny `source_kind` metadata (`inline`, `reference`, `autolink`, `footnote`), and rows now expose focused `inline_link_entries` / `reference_link_entries` / `autolink_entries` / `footnote_ref_entries` slices plus matching row-local counts so consumers can inspect visible link source kinds without repeating that source-shape logic by hand.

Rev317 follow-up: each `link_entries` item now also carries tiny `reference_form` metadata (`full`, `collapsed`, `shortcut`, or empty for non-reference links), and rows now expose focused `full_reference_link_entries` / `collapsed_reference_link_entries` / `shortcut_reference_link_entries` slices plus matching row-local counts so consumers can inspect exact visible reference-link spellings without reparsing bracket shapes by hand.

## New per-row field

Each visible docs/help row now also reports `link_entries`.

Each entry includes:

- `kind` — shared matcher kind (`link`, `autolink`, `footnote`)
- source spans: `start`, `end`, `label_start`, `label_end`
- `display` — visible label/url text
- `target` — raw resolved target string used by the docs browser
- `target_kind` — tiny target classification:
  - `doc`
  - `doc-fragment`
  - `file`
  - `file-fragment`
  - `fragment`
  - `footnote`
  - `external`
  - `mailto`
- `target_doc` — decoded topic/path part when present
- `target_fragment` — decoded fragment id when present

## New top-level summary fields

The whole snapshot now also reports:

- `link_rows`
- `link_entry_count`
- `local_doc_link_count`
- `fragment_link_count`
- `external_link_count`
- `footnote_link_count`
- `inline_link_rows`, `reference_link_rows`, `full_reference_link_rows`, `collapsed_reference_link_rows`, `shortcut_reference_link_rows`, `autolink_rows`, `footnote_ref_rows`
- `inline_link_count`, `reference_link_count`, `full_reference_link_count`, `collapsed_reference_link_count`, `shortcut_reference_link_count`, `autolink_count`, `footnote_ref_count`

## Why this stays honest

This is still **not** a richer markdown AST or rendered-link widget system.
It is just one more inspectable snapshot of the visible docs/help links the
existing shared matcher already understands.

The help browser still owns follow/open behavior. `docs_cues_model(...)`
just makes that visible link-target truth easier to inspect offline.
