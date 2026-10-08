# Rev478 — `commandpick` prompt rows now keep exact command/action detail

## Why

Micromax already had the right tiny exact command and action inspection
surfaces: `showcmd NAME` / `command_detail_row(NAME)` exposed one command's
doc/group/provenance, and `showaction NAME` / `action_detail_row(NAME)` exposed
one action's doc plus best-effort source provenance. But one small drift still
lingered in the broad command-palette loop: when command-bar completion for
`commandpick NAME` had already resolved a visible row to one exact command or
one exact action, it still flattened the info slot back to plain `command
palette`.

That made the palette-selection loop slightly less trustworthy exactly where
future humans/LLMs were deciding whether a visible entry was built in,
plugin-owned, or locally registered.

## What changed

- add a tiny shared `_prompt_contextual_row(...)` helper for broad loops that
  still want to keep exact row metadata visible
- `commandpick NAME` completion now reuses exact command metadata from
  `_prompt_command_row(...)` and exact action metadata from `_prompt_action_row(...)`
- the prompt keeps the existing `command palette` cue while also appending exact
  group/provenance metadata when Micromax already knows it
- focused prompt-completion tests pin the command/action row contract

## Result

Broad palette selection stays broad, but it stops hiding metadata Micromax
already knows. If one visible palette target has already resolved to one exact
command or action row, the prompt can keep that tiny honest metadata visible
without pretending the loop became something else.
