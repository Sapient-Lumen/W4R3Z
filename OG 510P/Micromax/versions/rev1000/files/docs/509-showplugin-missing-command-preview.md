# Rev567 — truthful missing/unavailable `showplugin NAME` rows

## Why

Micromax already had the right nearby plugin truth:

- `showplugin NAME` already reused one exact plugin-state/detail row for known plugins
- the executed `showplugin NAME` path already knew how to say `showplugin: no such plugin: NAME`
- the same command already knew how to fail as `showplugin: no plugin manager` when plugin support was unavailable

But command-bar completion for `showplugin NAME` still only surfaced known plugin names. If you typed an unmatched exact target, the token disappeared from the suggestion surface before Enter, so the command bar could not say `missing plugin · no such plugin` or `plugin manager · not available` even though execution already knew both truths.

## What changed

- `_prompt_plugin_row(...)` now accepts `strict_missing=True`
- exact `showplugin` suggestion rows now reuse that helper instead of hand-building known-plugin-only rows
- `showplugin` token completion now preserves unmatched typed names long enough to render a truthful exact row
- known plugins keep the same exact state/detail preview as before

## Examples

- `showplugin a` keeps the usual exact row, such as `[loaded, v1.0.0] | demo plugin`
- `showplugin ghost` can now stay visible as `missing plugin | no such plugin`
- without a plugin manager, `showplugin ghost` can now stay visible as `plugin manager | not available`

## Why this shape

This keeps single-plugin inspection aligned with the same tiny state Micromax already trusts after Enter. The fix stays deliberately narrow: command semantics do not change, only the pre-Enter exact inspection row stops pretending that unmatched targets do not exist.

Future humans and LLMs can now see whether one typed plugin target is real, missing, or blocked by missing plugin support before they commit the command.

## Checks

Focused coverage now pins:

- known `showplugin NAME` rows keeping the existing exact state/detail metadata
- unmatched `showplugin NAME` completion preserving the typed token
- missing exact rows reporting `missing plugin` / `no such plugin`
- no-manager exact rows reporting `plugin manager` / `not available`
