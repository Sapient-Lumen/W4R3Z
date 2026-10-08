# Rev469 — showdocs completion now reuses tiny docs-family summary rows

## Why

Micromax already had the right broad docs-family summary surface:
`showdocs` / `doc_section_summary_rows(QUERY)` / `ed.doc-section-summary-rows`
exposed tiny `[[label count sample_name sample_detail] ...]` rows for the
numbered docs families. But one small flow seam still lingered in the
ordinary command-bar loop: `showdocs` itself took no optional filter query, so
people and future LLMs could only inspect every docs family at once, and the
prompt could not help aim at a known visible bucket.

## Tiny TODO

- let `showdocs [QUERY]` narrow docs-family summaries without leaving the
  ordinary command-bar flow
- make command-bar completion for `showdocs` reuse the same tiny docs-family
  summary rows
- keep the prompt rows honest: family label in `insert`, count/example in
  `menu`, sample detail in `info`
- pin the behavior with focused docs-summary and prompt-completion tests

## What changed

- `showdocs` now accepts an optional `QUERY` and filters via
  `doc_section_summary_rows(QUERY)` instead of rejecting arguments
- command-bar completion for `showdocs [QUERY]` now completes visible docs
  family labels
- prompt rows for `showdocs` now reuse the same tiny docs-family summary rows
  instead of falling back to opaque raw labels

## Result

The docs-family summary command now behaves like the newer grouped-summary
commands: if the editor already knows one tiny honest row for each visible docs
family, both the human command and the prompt loop reuse that same substrate.
