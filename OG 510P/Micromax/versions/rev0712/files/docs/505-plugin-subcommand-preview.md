# Rev563 - truthful exact `plugin reload` / `plugin info` / `plugin errors` rows

## What changed

Micromax already had one good broad plugin row: exact `plugin list` completion previewed the live inventory before Enter. But sibling broad subcommands `plugin reload`, `plugin info`, and `plugin errors` still fell back to a generic `plugin action` placeholder even though they all depend on that same tiny live plugin register.

Rev563 keeps the fix deliberately small:

- add shared `_prompt_plugin_command_row(insert, subcommand=...)`
- keep `plugin list` on that shared path
- teach exact `plugin reload` to preview loaded-plugin availability
- teach exact `plugin info` to preview total plugin inventory
- teach exact `plugin errors` to preview current broken-plugin inventory
- pin populated and empty states with focused prompt-completion tests

## Why it matters

This is a trust-first command-bar cleanup. If Micromax already knows the live plugin inventory behind a broad no-arg plugin subcommand, the exact row should spend that slot on real state instead of generic prose. That makes the plugin surface easier to trust, easier to drive headlessly, and easier for future LLMs to continue without re-reading command output after every tentative thought.

## Examples

- `plugin reload` -> `2 loaded plugins · e.g. alpha [loaded]`
- `plugin info` -> `3 plugins · e.g. beta [error, deps:missingdep]`
- `plugin errors` -> `1 plugin with errors · e.g. beta [error, deps:missingdep]`
- empty inventory keeps the same rows explicit as `0 loaded plugins`, `0 plugins`, and `0 plugins with errors`
