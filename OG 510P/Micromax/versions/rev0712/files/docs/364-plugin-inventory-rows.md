# Plugin inventory rows

Micromax already had the important tiny plugin loop before rev422: a legible plain `plugin list`, explicit `plugin reload` / `plugin info` / `plugin errors` detail paths, and grouped `pluginpick` rows that reused the same compact summary dialect for humans.

The remaining seam was not plugin loading; it was **host-boundary symmetry**.
Humans could inspect the richer plugin inventory directly, but scripts and future UIs still had to start from raw `plugin.list` names, raw `plugin.errors` tuples, or grouped picker rows and then reconstruct broad plugin state by hand.

Rev422 adds one deliberately small shared inventory surface instead of a bigger plugin manager API:

- `plugin_inventory_rows()` returns ordered rows inside the editor
- `ed.plugin-inventory-rows` exposes the same rows to Micromax scripts and future UIs
- plain `plugin list` now reuses that same row surface so command output and host data stay aligned

The rows stay intentionally tiny:

- `name` — plugin name
- `state` — one of `loaded`, `error`, or `available`
- `version` — declared plugin version when known
- `deps` — comma-joined declared dependency names when present
- `error_count` — current recorded load-error count for that plugin

This deliberately complements the richer grouped `ed.plugin-section-rows` picker surface and the raw `plugin.list` / `plugin.errors` hostcalls instead of replacing them.
The design goal is simple: if plain plugin inventory already helps humans trust plugin health, the same tiny surface should be available to scripts and future UIs too.
