# Runtime `showplugin NAME` keeps the available not-loaded witness

Rev596 is a tiny trust/legibility follow-up to the recent exact available-plugin cleanup. Micromax already kept the fuller `available plugin · not loaded` witness in exact `showplugin NAME` / `plugin info NAME` completion, exact/runtime `plugin errors NAME`, and exact/runtime `plugin reload NAME`. But one narrow runtime seam still lingered beside those fixes: the one-line post-Enter `showplugin NAME` inspector still stopped at bare `errors=0` when the plugin was a real on-disk candidate that was not currently loaded.

The fix stays intentionally small: runtime `showplugin NAME` now reuses one tiny `_plugin_showplugin_detail(...)` helper so available-but-unloaded plugins render `errors=0 — available plugin · not loaded` when richer detail would otherwise be blank, while broken plugins and described plugins keep their existing exact detail.

Why it matters:
- `showplugin NAME` is the smallest post-Enter exact plugin inspector
- bare `errors=0` was true but still hid whether the plugin was loaded or only available on disk
- the new suffix keeps runtime and command-bar exact inspection aligned without widening the host boundary
