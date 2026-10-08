# `pluginpick` keeps compact grouped menus again (rev583)

Rev583 closes one tiny trust/taste seam in the plugin inspection loop: grouped `pluginpick` rows, section hostcalls, and previews now keep the compact bracketed plugin-state menu dialect again.

## The seam

Micromax already had two adjacent plugin dialects on purpose:

- grouped picker rows like `pluginpick` should stay compact and section-friendly
- exact `showplugin NAME` completion can afford a slightly richer one-plugin hint

Before rev583, `_prompt_plugin_row(...)` had started appending `errors=N` into the menu text for both cases. That made grouped picker rows drift from:

- `[error, deps:missingdep]`

into:

- `[error, deps:missingdep] errors=1`

The row detail already carried the concrete failure witness (`missing dependency: missingdep`), so the extra count in grouped picker menus was mostly noise.

## What changed

Rev583 keeps the underlying helper shared, but makes the richer suffix opt-in:

- grouped `pluginpick` rows/sections/previews keep compact bracketed menus
- exact `showplugin NAME` completion still asks for the richer `errors=N` hint

That means Micromax now keeps both truths aligned with their jobs:

- grouped browsing stays compact
- exact one-plugin inspection stays slightly richer

## Why it matters

This is a tiny change, but it sharpens two editor qualities that matter a lot in headless-first workflows:

1. **Trust** — grouped picker rows now match the compact dialect the rest of the plugin browse loop already promised
2. **Taste** — sectioned picker menus avoid redundant count noise when the row detail already says what is broken
3. **Flow** — future humans and LLMs can treat grouped picker rows as stable browse labels and exact `showplugin` rows as the richer inspection surface

## Pinned behavior

- grouped section row: `['b', 'plugin', '[error, deps:missingdep]', 'missing dependency: missingdep']`
- exact `showplugin b` completion row: `['b ', 'plugin', '[error, deps:missingdep] errors=1', 'missing dependency: missingdep']`
