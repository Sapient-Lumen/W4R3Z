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

## Why this stays honest

This is still **not** a richer markdown AST or rendered-link widget system.
It is just one more inspectable snapshot of the visible docs/help links the
existing shared matcher already understands.

The help browser still owns follow/open behavior. `docs_cues_model(...)`
just makes that visible link-target truth easier to inspect offline.
