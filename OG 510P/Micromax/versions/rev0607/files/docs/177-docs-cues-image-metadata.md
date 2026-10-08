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

Rev308 follow-up: rows now also expose focused target slices `local_doc_image_entries`, `fragment_image_entries`, `external_image_entries`, and `footnote_image_entries` plus matching row-local counts, so consumers do not need to re-filter `image_entries` by hand.

Rev316 follow-up: each `image_entries` item now also carries tiny `source_kind` metadata (`inline` or `reference`), and rows now expose focused `inline_image_entries` / `reference_image_entries` slices plus matching row-local counts so consumers can inspect visible inline-vs-reference image source forms without repeating that source-shape logic by hand.

Rev317 follow-up: each `image_entries` item now also carries tiny `reference_form` metadata (`full`, `collapsed`, `shortcut`, or empty for inline images), and rows now expose focused `full_reference_image_entries` / `collapsed_reference_image_entries` / `shortcut_reference_image_entries` slices plus matching row-local counts so consumers can inspect exact visible reference-image spellings without reparsing bracket shapes by hand.

## New top-level summary fields

The whole snapshot now also reports:

- `image_rows`
- `image_entry_count`
- `local_doc_image_rows`
- `fragment_image_rows`
- `external_image_rows`
- `footnote_image_rows`
- `local_doc_image_count`
- `fragment_image_count`
- `external_image_count`
- `footnote_image_count`
- `inline_image_rows`, `reference_image_rows`, `full_reference_image_rows`, `collapsed_reference_image_rows`, `shortcut_reference_image_rows`
- `inline_image_count`, `reference_image_count`, `full_reference_image_count`, `collapsed_reference_image_count`, `shortcut_reference_image_count`

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

