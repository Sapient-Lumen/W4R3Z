# Rev601: runtime `showplugin NAME` keeps the loaded-state witness too

## What changed

The one-line runtime `showplugin NAME` inspector already kept concrete detail for
broken plugins and the explicit `available plugin · not loaded` witness for
known on-disk unloaded candidates. But a healthy loaded plugin with no
additional description still flattened back to bare `errors=0` after Enter.

Rev601 keeps that path just as small and concrete as the matching exact
command-bar row: runtime `showplugin NAME` now says `errors=0 — loaded plugin`
for a healthy loaded plugin when no richer detail is available.

## Why it matters

This is a tiny trust/taste cleanup:

- exact `showplugin NAME` completion already used `loaded plugin`
- the narrowest post-Enter exact inspector should not be weaker than its own
  pre-Enter row when Micromax already knows the plugin is loaded
- the fix stays local to one helper and does not widen the host boundary
