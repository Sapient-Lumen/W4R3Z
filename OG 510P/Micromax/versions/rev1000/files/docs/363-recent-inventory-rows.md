# Recent inventory rows

Micromax already had the important tiny recent-files loop before rev421: explicit `open ...` feedback, searchable `recentpick` / `recentdirpick` rows, grouped recent sections for future UIs, and a legible plain `recent` inventory line that showed active/open state, visible flags, and current cursor targets for still-open entries.

The remaining seam was not MRU storage; it was **host-boundary symmetry**.
Humans could inspect the richer recent inventory directly, but scripts and future UIs still had to start from raw `ed.recent` paths or repurpose grouped picker rows that were designed for search/browsing rather than for one tiny count-aware register.

Rev421 adds one deliberately small shared inventory surface instead of a bigger recent-file manager:

- `recent_inventory_rows()` returns ordered rows inside the editor
- `ed.recent-inventory-rows` exposes the same rows to Micromax scripts and future UIs
- plain `recent` now reuses that same row surface so command output and host data stay aligned

The rows stay intentionally tiny:

- `index` — 1-based MRU slot number, matching plain `recent N`
- `path` — stored recent-file path text
- `position` — small 1-based `line:col` label for the current primary cursor when that file is still open
- `active` — `1` when the row names the active open buffer
- `open` — `1` when the file is open in some buffer
- `dirty` — `1` when that open buffer has unsaved edits
- `readonly` — `1` when that open buffer is currently protected from editing
- `disk_truth` — best-effort `existing file` / `new file` when Micromax is allowed to inspect the stored path
- `action_truth` — tiny `current buffer` / `switch buffer` / `empty buffer @ 1:0` cue when Micromax already knows what `recent N` would actually revisit or reopen

The editor also now matches open buffers against recent rows with the same best-effort path normalization already used by the MRU itself, so `./notes.txt`, `~/proj/notes.txt`, and an absolute spelling of the same file do not silently drift into different truth surfaces.

This deliberately complements the thinner raw `ed.recent` path list and the richer grouped recent-section hostcalls instead of replacing them.
The design goal is simple: if plain recent inventory already helps humans trust file return loops, the same tiny surface should be available to scripts and future UIs too.


Follow-up: rev511 keeps this flat inventory aligned with the stronger exact recent-file surfaces too, so both plain `recent` and `ed.recent-inventory-rows` can carry the same tiny disk/action truth instead of reserving that honesty only for `showrecent PATH`, palette recent rows, or picker prompts.
