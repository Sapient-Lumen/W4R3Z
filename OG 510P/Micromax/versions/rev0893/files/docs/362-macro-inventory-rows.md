# Macro inventory rows

Micromax already had the important tiny macro loop before rev420: explicit `macro record` / `macro stop` / `macro cancel` / `macro play`, a legible plain `macro list` inventory, and portable raw step surfaces through `ed.macro-get` / `ed.macro-set`.

The remaining seam was not storage or playback; it was **host-boundary symmetry**.
Humans could inspect the richer saved-macro inventory directly, but scripts and future UIs still had to start from `ed.macro-names`, fetch each macro individually, count steps by hand, and then rediscover one small honesty rule too: an empty default `last` slot should stay absent instead of pretending a saved macro already exists.

Rev420 adds one deliberately small shared inventory surface instead of a bigger macro browser:

- `macro_inventory_rows()` returns ordered rows inside the editor
- `ed.macro-inventory-rows` exposes the same rows to Micromax scripts and future UIs
- plain `macro list` now reuses that same row surface so command output and host data stay aligned

The rows stay intentionally tiny:

- `name` — saved macro name
- `steps` — recorded step count

This deliberately complements the raw portable `ed.macro-get` / `ed.macro-set` step surfaces instead of replacing them.
The design goal is simple: if plain macro inventory already helps humans trust tiny automation, the same surface should be available to scripts and future UIs too.
