# Rev592: exact `plugin errors NAME` should keep available-state witness

## Why

Micromax already had a good trust-first dialect for exact plugin targets:

- `showplugin NAME` and `plugin info NAME` kept one concrete state fact even when richer plugin detail was blank.
- `plugin reload NAME` now says `available plugin · not loaded` for a known on-disk candidate instead of flattening that case to `plugin not loaded`.
- broken exact targets already preserved real recorded load-error detail.

But one narrow adjacent seam still remained. When a plugin existed on disk, was known to the plugin manager, and simply was not loaded, exact `plugin errors NAME` completion still rendered only:

- `0 load errors`

That sentence was technically true, but it quietly hid the more important exact-state fact right next door: this was a real available plugin candidate, not a loaded plugin and not an unknown name.

## What changed

Rev592 keeps the change deliberately tiny:

- exact `plugin errors NAME` rows now say `0 load errors · available plugin · not loaded` for known available candidates
- healthy loaded plugins still keep the compact `0 load errors` wording
- grouped plugin picker rows and broader plugin summaries stay unchanged

## Why this shape

Exact target inspection is where Micromax should be most concrete. When the editor already knows a plugin is present on disk and merely unloaded, the command-bar row should not force humans or future LLMs to infer that state from the bracketed menu alone.

The goal is simple: exact zero-error rows should stay as witnessable as exact reload rows when Micromax already knows the plugin is available but not loaded.
