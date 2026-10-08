# Rev585 — plain `plugin` previews broad plugin inventory truth

## Why

Micromax already had the right tiny plugin state nearby:

- exact `plugin list` / `plugin reload` / `plugin info` / `plugin errors` command rows already reused truthful live inventory before Enter
- rev581 had already taught adjacent broad plugin previews to distinguish `plugin manager not available` from a real empty configured manager
- rev584 had just taught plain `pluginpick` to preview grouped plugin inventory truth too

But the exact no-arg `plugin` command row still fell back to generic command/provenance metadata. That made the umbrella plugin dispatcher less honest than the subcommands and picker it immediately led into.

## What changed

Rev585 keeps the fix deliberately small:

- add `_prompt_plugin_root_command_row(...)`
- reuse the existing `plugin list` preview summary so plain `plugin` keeps the same populated/empty/unavailable plugin inventory truth
- wire exact command completion for raw `plugin` through that helper
- pin populated, empty-manager, and unavailable-manager root command rows with focused prompt-completion tests

## Example rows

- live inventory: `3 plugins (1 error, 2 loaded) · e.g. beta [error, deps:missingdep]`
- empty configured manager: `0 plugins`
- unavailable subsystem: `plugin manager not available`

## Why this shape

`plugin` is still a usage-style dispatcher, so the syntax stays in the row menu. But the info slot should spend itself on the live subsystem state humans will immediately care about, not on generic command provenance. Reusing the same tiny plugin inventory summary already trusted by `plugin list` keeps the top-level plugin entry point calmer, more coherent, and easier to inspect in headless tests.
