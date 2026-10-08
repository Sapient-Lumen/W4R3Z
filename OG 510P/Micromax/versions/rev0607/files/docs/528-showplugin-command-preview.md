# Rev586 — plain `showplugin` previews exact-plugin inventory truth

## Why

Micromax already had the right tiny plugin state nearby:

- exact `showplugin NAME` completion already reused precise per-plugin state and typed missing-manager feedback
- plain `showplugins`, `plugin`, and `pluginpick` command rows already previewed live plugin availability before Enter
- exact `plugin info` subcommand rows already reused the broad plugin inventory summary when browsing one plugin family entry point

But the exact no-arg `showplugin` command row still fell back to generic command metadata. That made the narrow exact-plugin inspector less honest than the adjacent plugin entry points it sat beside.

## What changed

Rev586 keeps the fix deliberately small:

- add `_prompt_showplugin_command_row(...)`
- reuse the existing `plugin info` preview summary so plain `showplugin` keeps the same populated/empty/unavailable plugin inventory truth
- wire exact command completion for raw `showplugin` through that helper
- pin populated, empty-manager, and unavailable-manager root command rows with focused prompt-completion tests

## Example rows

- live inventory: `3 plugins · e.g. beta [error, deps:missingdep]`
- empty configured manager: `0 plugins`
- unavailable subsystem: `plugin manager not available`

## Why this shape

`showplugin` is still an exact-target inspector, so the syntax stays in the row menu. But the info slot should spend itself on whether there is any plugin inventory to inspect right now, not on generic provenance. Reusing the same tiny plugin summary already trusted by `plugin info` keeps the exact-plugin entry point calmer, more coherent, and easier to validate in headless tests.
