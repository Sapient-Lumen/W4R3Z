# Rev235 — docs-cues visible image metadata

Rev159 already made visible markdown image tokens read like deliberately inert
source in the live docs/help TUI, but the shared `docs_cues_model(...)`
snapshot still could not answer simple handoff questions like:

- what does this visible image token point to?
- is that target local, fragment-only, or external?
- what visible alt text did the author write on this row?

Rev235 keeps the contract tiny and source-view-first while answering those
questions directly.

## New per-row field

Each visible docs/help row now also reports `image_entries`.

Each entry includes:

- `kind` — currently `image`
- source spans: `start`, `end`
- alt-text spans: `alt_start`, `alt_end`
- `alt_text` — the visible image description inside `![ ... ]`
- `target` — raw resolved target string used by the tiny image matcher
- `target_kind` — tiny target classification reused from docs/help links:
  - `doc`
  - `doc-fragment`
  - `file`
  - `file-fragment`
  - `fragment`
  - `external`
  - `mailto`
  - `footnote`

- `target_doc` — decoded topic/path part when present
- `target_fragment` — decoded fragment id when present

Rows now also report `image_count` alongside the existing `link_count`.

## New top-level summary fields

The whole snapshot now also reports:

- `image_rows`
- `image_entry_count`
- `local_doc_image_count`
- `fragment_image_count`
- `external_image_count`

## Why this stays honest

This is still **not** a rendered-image system, gallery model, or richer
markdown AST. It is just one more inspectable snapshot of the visible
markdown image tokens the shared docs/help parser already understands well
enough to keep inert and dim in source view.

The help browser still owns navigation and source-view policy. `docs_cues_model(...)`
just makes that visible image-target truth easier to inspect offline.
## Hidden image metadata anchor {#image-metadata-anchor}

This tiny explicit heading exists mostly as stable help-browser target data, so
link queries can prove they understand target-heading titles as hidden search
metadata instead of only raw labels or raw `#fragment` ids.

