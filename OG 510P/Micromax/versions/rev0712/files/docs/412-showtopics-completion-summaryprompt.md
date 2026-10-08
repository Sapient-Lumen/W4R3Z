# Rev470 — `showtopics` completion reuses generic topic-family summary rows

## Why

Micromax already had the right broad generic help-topic summary surface: `showtopics` / `help_topic_section_summary_rows()` / `ed.topic-section-summary-rows` exposed tiny count-aware `[[label count sample_name sample_detail] ...]` rows for `Commands`, `Actions`, `Words`, and `Docs`. But the ordinary command-bar loop still treated that query slot as opaque text, and the human command itself had no optional filter path. That made broad generic-help exploration slightly driftier than the newer grouped-summary commands even though the summary rows already existed.

## What changed

- `showtopics [QUERY]` now accepts an optional filter query instead of being all-or-nothing
- command-bar completion for `showtopics` now completes visible topic-family labels
- prompt rows for `showtopics` now reuse the same tiny `ed.topic-section-summary-rows` metadata instead of a bare label
- exact visible labels like `Commands` or `Docs` round-trip cleanly back to one summary row

## Why it fits

This keeps Micromax on the same small, inspectable path as the recent grouped-summary cleanup:

- one tiny shared summary substrate
- one human command that reuses it directly
- one command-bar completion path that shows the same metadata while choosing a target
- focused tests that pin the contract

The result is a slightly calmer generic-help loop: if a broad topic family already exists as one honest summary row, both the human command and the prompt should reuse it too.
