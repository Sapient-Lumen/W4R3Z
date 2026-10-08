# Rev581 — broad plugin previews distinguish unavailable manager from empty inventory

## Why

Micromax already had most of the right plugin truth nearby:

- exact typed plugin targets already said `plugin manager not available` when the subsystem itself was absent
- `plugin_inventory_rows()` already powered plain `plugin list`, `plugin info`, `plugin reload`, `plugin errors`, and grouped `showplugins` whenever a manager existed
- earlier command-bar cleanup had been steadily teaching broad no-arg entry points not to flatten known visible state back into generic prose

But one small trust seam still lingered in the calm startup / headless-no-manager case: the broad plugin inventory entry points still previewed `0 plugins` or `0 loaded plugins`, which looked exactly like a real empty plugin manager.

## What changed

Rev581 keeps the fix deliberately small:

- add shared `_plugin_inventory_preview_state()` so broad plugin previews can distinguish manager availability from inventory counts
- route plain `showplugins` through `_prompt_showplugins_command_row(...)`
- keep the existing count-aware section/sample preview when a manager exists
- make exact `plugin list` / `plugin reload` / `plugin info` / `plugin errors` subcommand rows say `plugin manager not available` when no manager is configured
- pin both real-empty-manager and unavailable-manager states with focused prompt-completion tests

## Why it matters

This is a tiny trust-first cleanup. A missing plugin subsystem is a different editor state than an empty plugin tree, especially in headless tests, stripped-down harnesses, or early startup. The command bar should preserve that distinction before Enter so humans and future LLMs do not have to infer whether plugins are merely absent from disk or unavailable as a subsystem.

## Examples

- no manager: `showplugins` -> `plugin manager not available`
- no manager: `plugin list` -> `plugin manager not available`
- empty manager: `showplugins` -> `0 section(s), 0 plugins`
- empty manager: `plugin list` -> `0 plugins`
