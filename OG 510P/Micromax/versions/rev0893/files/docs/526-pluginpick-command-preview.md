# Rev584 — plain `pluginpick` previews grouped plugin inventory truth

## Why

Micromax already had the right tiny plugin-picker state nearby:

- grouped `pluginpick [QUERY]` rows already exposed searchable `Errors` / `Loaded` / `Available` sections after Enter
- rev581 had already taught adjacent broad plugin previews to distinguish `plugin manager not available` from a real empty configured manager
- rev583 had just restored the compact grouped picker row dialect itself

But the exact no-arg `pluginpick` command row still fell back to a generic command/provenance hint. That made the picker entry point less honest than the grouped browse state it immediately opened.

## What changed

Rev584 keeps the fix deliberately small:

- add `_prompt_pluginpick_command_row(...)`
- reuse `_plugin_inventory_preview_state()` so no-manager startup still says `plugin manager not available`
- reuse grouped `plugin_section_rows("")` so a live picker preview keeps visible section-count and sample-row truth
- pin populated, empty-manager, and unavailable-manager exact command rows with focused prompt-completion tests

## Example rows

- live inventory: `2 section(s), 3 plugins · Errors (1): e.g. beta — missing dependency: missingdep`
- empty configured manager: `0 section(s), 0 plugins`
- unavailable subsystem: `plugin manager not available`

## Why this shape

`pluginpick` is a grouped browse entry point, so its no-arg preview should spend the row on the grouped inventory it will actually open, not on generic command metadata. Reusing the same availability and section state that nearby plugin surfaces already trust keeps the plugin loop more coherent for humans, tests, and future LLMs.
