# Rev468 — showbindingmodes completion now reuses tiny section-summary rows

Micromax already had the right broad reachable-binding bucket surface before rev468:

- `showbindingmodes [QUERY]` / `binding_section_summary_rows(QUERY)` / `ed.binding-section-summary-rows`
- tiny shared `[[label count sample_name sample_detail] ...]` rows for visible winning-mode buckets such as `goto`, `nav`, and `Global`

That meant humans, scripts, and future UIs could already inspect which broad binding buckets existed without opening `bindingpick` or walking every grouped binding row.

But one small prompt-loop drift still lingered next to that model: command-bar completion for `showbindingmodes [QUERY]` still treated the query as opaque text. Users could *see* buckets like `goto` or `Global` after running the command, but the command bar itself could not help them choose those same visible labels with the matching count/sample metadata.

Rev468 keeps the fix deliberately small:

- `showbindingmodes [QUERY]` now completes visible winning-mode labels
- prompt rows for those suggestions now reuse the same tiny `binding_section_summary_rows(QUERY)` metadata
- focused tests pin the completion + metadata contract next to the existing summary-surface tests

The goal is simple: if a broad grouped-summary command already has one tiny honest row for each visible binding bucket, command completion should reuse that same row instead of hiding the bucket behind raw text.
