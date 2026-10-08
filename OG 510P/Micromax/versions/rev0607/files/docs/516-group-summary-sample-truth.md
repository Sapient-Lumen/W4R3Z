# Rev574 — grouped help/docs/topic summaries keep sample-row truth

## Why

Micromax already had the right nearby discovery surfaces:

- broad `showtopics`, `showdocs`, and `showhelpnav` summary commands already
  exposed tiny count-aware `[[label count sample_name sample_detail] ...]` rows
- the same summary rows already powered grouped command-bar completion before
  Enter
- nearby exact surfaces such as `showtopic`, `showdoc`, current-doc heading
  detail, and current-link detail already reused richer per-target truth

But one small seam still lingered inside the broad grouped summaries. The
underlying prompt rows already carried both a `menu` field and an `info`
field, yet `_section_summary_rows(...)` only kept one of them.

That meant grouped help/docs/topic inspection quietly discarded useful truth
Micromax already knew:

- docs buckets kept the slug and summary, but dropped the visible doc title
- help-nav link buckets kept the location, but dropped the target itself
- help-nav heading buckets kept the position, but dropped the heading kind
- word/topic buckets could drop the small kind/effect metadata already visible
  in the first sample row

## What changed

Rev574 keeps the fix deliberately small:

- added `_section_summary_prompt_row_detail(...)`
- broad help/docs/topic summaries now reuse non-duplicated `menu · info`
  detail from their first visible sample row
- applied that helper to:
  - `help_topic_section_summary_rows()`
  - `apropos_section_summary_rows()`
  - `doc_section_summary_rows()`
  - `help_nav_section_summary_rows()`

The shared summary shape stays the same:

- `[label count sample_name sample_detail]`

Only the sample detail becomes more faithful to the visible row Micromax was
already showing elsewhere.

## Examples

Grouped summaries can now say things like:

- `Words: ... (e.g. ! — primitive wl=forth ( x cell -- ) · store)`
- `00–09 Project: ... (e.g. llm-start-here — LLM start here rev263 · Rev220 note: ...)`
- `Files: ... (e.g. Vision — 00-vision.md · 48:4 — Links)`
- `Top: ... (e.g. Help browser — h1 · 1:3)`

## Why this shape

This keeps grouped summaries aligned with the exact/detail surfaces already
trusted nearby without widening the host boundary or inventing a second summary
format just for help/docs discovery.

For future humans and LLMs, the rule is simpler now:

- if one visible sample row already contains two truthful bits of context,
  the grouped summary should preserve both unless they are duplicates

## Checks

Focused coverage now pins:

- richer topic section summary detail
- richer docs section summary detail
- richer help-nav section summary detail
- command-bar completion for `showtopics`, `showdocs`, and `showhelpnav`
  reusing the same enriched summary rows
