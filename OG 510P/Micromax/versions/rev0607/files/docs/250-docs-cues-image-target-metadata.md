# Rev308 — docs-cues focused image-target metadata

Rev235 already made visible docs/help image tokens inspectable through
`image_entries`, and the snapshot already counted local-doc, fragment-like, and
external image targets globally. But row-local consumers still had to re-filter
`image_entries` by hand when they wanted to ask small archive-first questions
like:

- which visible image tokens on this row stay inside the docs set?
- does this visible row point at a footnote target?
- are the visible image targets here fragment-only, cross-doc, or external?

Rev308 keeps the contract tiny and source-view-first while making those
questions direct.

## New per-row fields

Each visible docs/help row now also reports focused image-target slices:

- `local_doc_image_entries`
- `fragment_image_entries`
- `external_image_entries`
- `footnote_image_entries`

These are filtered siblings of the existing `image_entries` list, preserving the
same entry shape (`kind`, source spans, `alt_text`, `target`, `target_kind`,
`target_doc`, `target_fragment`).

Rows now also report matching row-local counts:

- `local_doc_image_count`
- `fragment_image_count`
- `external_image_count`
- `footnote_image_count`

The grouping rules intentionally mirror the existing link-target slices:

- local-doc includes `doc`, `doc-fragment`, `file`, `file-fragment`
- fragment-like includes `fragment`, `footnote`, `doc-fragment`, `file-fragment`
- external includes `external`, `mailto`
- footnote includes `footnote` only

## New top-level summary fields

The whole snapshot now also reports:

- `local_doc_image_rows`
- `fragment_image_rows`
- `external_image_rows`
- `footnote_image_rows`
- `footnote_image_count`

Existing `image_rows`, `image_entry_count`, `local_doc_image_count`,
`fragment_image_count`, and `external_image_count` remain intact.

## Why this stays honest

This is still **not** a rendered-image model, gallery, preview system, or fuller
markdown AST. It is just one more inspectable view of the visible markdown
image tokens the shared docs/help parser already understands well enough to
keep inert and dim in source view.

The help browser still owns navigation and source-view policy.
`docs_cues_model(...)` just makes visible image-target truth easier to inspect
offline, especially inside release archives handed to future humans or LLMs.
