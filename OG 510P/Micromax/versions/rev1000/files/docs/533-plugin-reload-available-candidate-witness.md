# Rev591 — exact `plugin reload NAME` keeps available-candidate state witness

## Why

Micromax already had most of the right tiny plugin truth nearby:

- exact `showplugin NAME` / `plugin info NAME` rows now keep state-aware fallback info when richer detail is blank
- exact broken `plugin reload NAME` rows already keep recorded load-failure detail as `... · not loaded`
- runtime `plugin reload NAME` feedback already starts with the shared inventory entry like `name [available, vX.Y.Z]`

But one small trust seam still lingered in the known-available reload path. When a
plugin candidate existed on disk but was not currently loaded, both the exact
command-bar row and the after-Enter reload feedback still flattened that state
back to generic `plugin not loaded`.

## What changed

Rev591 keeps the fix deliberately small:

- exact `plugin reload NAME` completion now reuses the existing
  `_plugin_exact_state_info_fallback(...)` helper when a known plugin is
  available-but-unloaded and has no load errors
- that row now says `available plugin · not loaded` instead of the vaguer
  `plugin not loaded`
- `plugin_reload_with_feedback(...)` now keeps the same wording in the
  after-Enter runtime message for that same available-candidate state

## Why this shape

This keeps the reload path aligned with nearby exact plugin inspection rows
without widening the host boundary or inventing new plugin state machinery. The
command bar and the runtime feedback now both preserve the same concrete fact:
Micromax knows this plugin is real and available, it just is not loaded yet.

That is a tiny trust improvement, but it matters in calm headless workflows and
future LLM-driven inspection loops because it reduces one more place where a
known state could be mistaken for an unknown one.

## Checks

Focused coverage now pins:

- exact `plugin reload NAME` completion for an available candidate
- runtime `plugin reload NAME` feedback for an available candidate
- adjacent broken-target and missing-target reload behavior remains unchanged
