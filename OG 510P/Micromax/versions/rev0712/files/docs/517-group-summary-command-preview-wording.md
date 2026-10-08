# Rev575 — grouped-summary command previews drop false temporal wording

## Why

Micromax already had the right command-bar behavior nearby:

- plain grouped-summary commands such as `showtopics`, `showdocs`,
  `showbuffergroups`, `showplugins`, and `showhelpnav` already previewed live
  section counts plus one visible sample bucket before Enter
- those exact command rows already reused the same shared
  `[label count sample_name sample_detail]` substrate that the commands and
  query-time completion used after/around Enter
- rev574 had just made several grouped help/docs/topic summaries more faithful
  to the visible sample rows they were summarizing

But one tiny wording seam still lingered in the exact command-row helper:

- `_prompt_section_summary_command_row(...)` called the first visible bucket
  `latest ...`
- that wording made sense for MRU-style surfaces, but not for static grouped
  families like `Help`, `Commands`, `Top`, `Errors`, or numbered docs buckets
- the result was a small trust/taste mismatch where the pre-Enter hint sounded
  more temporal than the grouped surface it was mirroring

## What changed

Rev575 keeps the fix deliberately small:

- grouped-summary exact command rows now say `LABEL: N | e.g. ...`
- they no longer inject `latest` into static section previews
- the shared preview shape stays otherwise unchanged:
  - `N section(s), M items · LABEL: N | e.g. sample — detail`

## Examples

Command-bar rows now read like:

- `4 section(s), 975 topics · Commands: 115 | e.g. apropos — ...`
- `3 section(s), 3 buffers · Help: 1 | e.g. help:guide — 1 lines`
- `5 section(s), 86 targets · Top: 1 | e.g. Help browser — h1 · 1:3`
- `2 section(s), 3 plugins · Errors: 1 | e.g. beta — missing dependency: ...`

instead of pretending those sections are the `latest` section.

## Why this shape

This keeps the command-bar preview aligned with what the grouped command is
actually showing: one visible leading section, not a temporal event.

For future humans and LLMs, the rule is smaller and clearer now:

- grouped exact-command previews should say what section is visible
- they should not invent time-oriented wording unless the underlying surface is
  actually temporal or MRU-ordered

## Checks

Focused coverage now pins:

- neutral exact-command preview wording for grouped topic/docs/helpnav commands
- existing grouped buffer/plugin exact-command previews updated to the same
  neutral wording
