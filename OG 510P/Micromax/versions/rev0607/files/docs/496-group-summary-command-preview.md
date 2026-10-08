# Rev554: grouped summary commands preview their own inventory before Enter

## Why this existed

Micromax already had a solid grouped-summary substrate:

- plain grouped summary commands such as `showbuffergroups [QUERY]`,
  `showplugins [QUERY]`, and `showhelpnav [QUERY]` already printed tiny
  count-aware section summaries after Enter
- query-time completion for those same commands already reused the matching
  shared `[[label count sample_name sample_detail] ...]` rows while filtering
  one visible bucket label
- newer exact command-row previews for jumps, recents, and saves had already
  established the local product rule that the command bar should surface the
  truth Micromax already knows before Enter

But one broad sibling seam still lingered across the remaining grouped-summary
entry points: typing plain `showbuffergroups`, `showplugins`, `showoptiongroups`,
`showhelpnav`, `showdocs`, `showpalettegroups`, `showmarkgroups`,
`showbindingmodes`, or `showtopics` still showed only a generic command/help
row even though Micromax already knew the current section counts and first
visible sample bucket behind each command.

That was small, but it weakened trust and flow in exactly the same way the
older recent/jump/save command rows did: the product had the truth already, but
hid it right before execution.

## What changed

Rev554 adds one small shared helper:

- `_prompt_section_summary_command_row(...)`

It reuses the existing shared grouped-summary substrate:

- `_prompt_section_summary_rows_for_command(...)`

Exact command completion for the remaining grouped-summary commands now keeps
the normal command doc while replacing the generic info hint with one tiny live
preview such as:

- `3 section(s), 3 buffers · latest Help: 1 | e.g. help:guide — 1 lines`
- `2 section(s), 3 plugins · latest Errors: 1 | e.g. beta — missing dependency: missingdep`
- `0 section(s), 0 plugins`

The implementation stays deliberately small:

- no new grouped-summary data model
- no change to command execution behavior
- no new hostcall surface
- only the exact no-arg command row learns to reuse the summary rows the rest
  of the repo already trusts

## Why this matters

This keeps one more family of command-bar entry points aligned with the
project's trust-first rule:

- if Micromax already knows what a no-arg inspection command will summarize,
  say that before Enter
- keep docs/help rows intact
- make the command bar a truthful preview surface rather than a generic prompt
  wrapper

For future LLMs and humans, the rule is now simpler and easier to continue:
exact command rows should reuse nearby inspectable truth whenever the repo
already has a small stable summary substrate.
