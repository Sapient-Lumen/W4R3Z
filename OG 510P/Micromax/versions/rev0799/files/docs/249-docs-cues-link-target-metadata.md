# Rev307 — docs-cues link-target metadata

Rev307 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small sibling view over the link metadata it already exposed: visible docs/help
rows now carry explicit link-target slices for local-doc jumps, fragment jumps,
external links, and footnote references.

That means future UIs/scripts/LLMs no longer need to re-filter the broader
`link_entries` list just to answer questions like:

- "which visible links on this row stay inside the local docs set?"
- "does this row contain a footnote reference?"
- "which visible links here are external?"

## What changed

Each visible docs/help row now also carries:

- `local_doc_link_entries`
- `fragment_link_entries`
- `external_link_entries`
- `footnote_link_entries`
- row-local counts with the same names as the existing snapshot counters:
  - `local_doc_link_count`
  - `fragment_link_count`
  - `external_link_count`
  - `footnote_link_count`

The top-level snapshot now also reports:

- `local_doc_link_rows`
- `fragment_link_rows`
- `external_link_rows`
- `footnote_link_rows`

Existing `link_entries`, `link_count`, `link_rows`, and the existing top-level
entry counts stay intact.

## Classification rules

The focused sibling slices intentionally reuse the same target-kind split the
existing aggregate counters already trusted:

- local-doc: `doc`, `doc-fragment`, `file`, `file-fragment`
- fragment-like: `fragment`, `footnote`, `doc-fragment`, `file-fragment`
- external: `external`, `mailto`
- footnote: `footnote`

This keeps the model tiny and source-view-oriented instead of inventing a richer
link taxonomy.

## Why this helps

Before rev307, future UIs/scripts/LLMs could already inspect full `link_entries`
and snapshot-wide counts, but row-local questions still required repeating the
classification logic by hand.

Rev307 keeps the parser/renderer contract small while making the common questions
directly inspectable:

- "show me rows with visible footnote refs"
- "tell me whether the current row links outside the docs set"
- "highlight rows whose visible links all stay local"

## Focused coverage

The focused regression coverage lives in:

- `tests/test_editor_screen_layout.py`
- `tests/test_editor_main_cli.py`
- `tests/test_mxcontext.py`
