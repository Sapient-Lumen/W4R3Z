# Exact available plugin info rows keep the not-loaded witness

Rev595 is a tiny trust/legibility follow-up to the recent exact available-plugin cleanup. Micromax already kept the fuller `available plugin · not loaded` witness in exact `plugin reload NAME`, exact `plugin errors NAME`, and the filtered runtime `plugin info NAME` / `plugin errors NAME` paths. But one narrow exact-inspection seam still lingered beside those fixes: exact `showplugin NAME` and exact `plugin info NAME` completion rows still stopped at `available plugin`, even though Micromax already knew the plugin was a real on-disk candidate that was not currently loaded.

The fix stays intentionally small: exact `showplugin NAME` and exact `plugin info NAME` now append the same `· not loaded` witness when their richer detail column would otherwise fall back to the available-candidate state, grouped plugin picker rows stay unchanged, and focused completion tests pin both exact paths.

Why it matters:
- exact plugin inspection is the narrowest, most trust-sensitive browse path
- `available plugin` was true but still slightly incomplete beside neighboring exact/runtime plugin rows
- `available plugin · not loaded` makes the unloaded state explicit without adding new host boundary surface area
