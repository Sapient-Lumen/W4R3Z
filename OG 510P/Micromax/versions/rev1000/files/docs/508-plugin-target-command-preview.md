# Rev566 — truthful exact `plugin reload NAME` / `plugin info NAME` / `plugin errors NAME` rows

## Why

Micromax already had the important nearby plugin state:

- broad `plugin reload` / `plugin info` / `plugin errors` rows already previewed live inventory truth before Enter
- `showplugin NAME` already exposed exact one-plugin state/version/dependency detail
- the real command paths already knew whether a typed plugin target was loaded, known-but-not-loaded, clean, erroring, or missing

But the exact plugin-target layer still had two small trust leaks:

- `plugin reload NAME` / `plugin info NAME` / `plugin errors NAME` reused one generic plugin row that could not say `not loaded` or `0 load errors`
- unmatched names disappeared from completion entirely, so the command bar could not say `no such plugin` before Enter

## What changed

- added shared `_prompt_plugin_target_row(insert, subcommand=...)`
- exact plugin-name rows for `plugin reload NAME`, `plugin info NAME`, and `plugin errors NAME` now stay subcommand-aware
- token completion now preserves unmatched or unloaded names long enough to render a truthful exact row

## Examples

- `plugin reload alpha` -> `[loaded] | reload loaded plugin`
- `plugin reload beta` -> `[error, deps:missingdep] | 1 load error · not loaded`
- `plugin errors alpha` -> `[loaded] | 0 load errors`
- `plugin info ghost` -> `missing plugin | no such plugin`

## Why this shape

This keeps exact plugin-target discovery aligned with the state Micromax already trusts after Enter. The fix stays deliberately narrow: no plugin semantics changed, only the pre-Enter row became more specific and unmatched names stopped disappearing.

Future humans and LLMs can now tell whether one exact plugin target can reload, has load errors, has none, or does not exist before they submit the command.

## Checks

Focused prompt-completion coverage now pins:

- preserved exact-name candidates for unloaded and missing plugin targets
- exact `plugin reload NAME` rows showing `reload loaded plugin` vs `1 load error · not loaded`
- exact `plugin errors NAME` rows showing `0 load errors`
- exact missing `plugin info NAME` rows showing `missing plugin · no such plugin`
