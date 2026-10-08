# Rev561 — `plugin list` command-bar preview reuses live plugin inventory

## Why

Micromax already had the right tiny state underneath plain `plugin list`:

- the command itself already emitted a count-aware live plugin inventory after Enter
- `plugin_inventory_rows()` already exposed that same inventory register headlessly
- exact plugin completion for `plugin reload NAME` / `plugin info NAME` / `plugin errors NAME` and `showplugin NAME` already reused one-plugin state/version/dependency truth

But the exact `plugin list` subcommand row still fell back to a generic `plugin action` placeholder. That meant the broadest plugin-health entry point stayed less honest than the adjacent exact plugin rows around it.

## What changed

- added `_prompt_plugin_list_command_row(...)`
- exact command completion for `plugin list` now reuses `plugin_inventory_rows()` plus the shared plugin inventory-entry formatter
- the row stays intentionally small:
  - `3 plugins (1 error, 2 loaded) · e.g. beta [error, deps:missingdep]`
  - `0 plugins`

## Why this shape

This keeps the command bar aligned with Micromax's existing headless-first plugin inventory register instead of inventing one more bespoke summary path. The preview surfaces the overall health shape first, then samples one broken plugin when one exists so the highest-risk state is visible before Enter.

Future humans and LLMs can now see the same broad plugin inventory truth before Enter that `plugin list` already trusts after Enter.

## Checks

Focused prompt-completion coverage now pins:

- populated `plugin list` subcommand preview with count/state/sample truth
- empty `plugin list` subcommand preview when no plugin inventory exists
