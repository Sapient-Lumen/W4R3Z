# Buffer inventory rows

Micromax already had the important tiny buffer loop before rev419: explicit `buffer NAME` / `prevbuf` traversal, searchable `bufferpick` rows, and a legible plain `buffers` inventory line that showed the active buffer, dirty state, readonly state, and current cursor target.

The remaining seam was not user-facing wording; it was **host-boundary symmetry**.
Humans could inspect the richer buffer inventory directly, but scripts and future UIs still had to start from thinner raw `ed.buffers` names or repurpose picker/group rows that were designed for search, not for plain open-state inspection.

Rev419 adds one deliberately small shared inventory surface instead of a bigger buffer browser:

- `buffer_inventory_rows()` returns ordered rows inside the editor
- `ed.buffer-inventory-rows` exposes the same rows to Micromax scripts and future UIs
- plain `buffers` now reuses that same row surface so command output and host data stay aligned

The rows stay intentionally tiny:

- `name` — buffer name
- `position` — small 1-based `line:col` label for the current primary cursor in that buffer
- `active` — `1` when the row names the active buffer
- `dirty` — `1` when the buffer has unsaved edits
- `readonly` — `1` when the buffer is currently protected from editing

This deliberately complements the thinner raw `ed.buffers` name list instead of replacing it.
The design goal is simple: if plain buffer inventory already helps humans trust open-state navigation, the same tiny surface should be available to scripts and future UIs too.
