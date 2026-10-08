# Jump history register

Micromax already had the important jumplist mechanics before rev417: exact per-buffer back/forward traversal, explicit picker rows through `jumppick`, and grouped headless section rows for future UIs.

The remaining seam was not storage or traversal; it was **plain visibility**.
A human in the editor could traverse the jumplist or open the picker, but there was no tiny register-shaped surface for quickly inspecting the current/back/forward trail directly, and scripts had to choose between the compressed `[index size]` pair from `ed.jump-info` and reverse-engineering picker/group rows.

Rev417 adds one deliberately small register surface instead of a bigger browser subsystem:

- plain `jumps` now prints a count-aware inventory of the current jumplist head plus visible back/forward rows
- `jump_history_rows()` returns the same ordered register rows inside the editor
- `ed.jump-history-rows` exposes that row surface to Micromax scripts and future UIs

The rows stay intentionally tiny:

- `current` — the active jumplist entry
- `back` — immediate back target first, then older entries
- `forward` — immediate forward target first, then newer entries

Each row carries only `lane`, `depth`, `index`, `buffer`, `position`, and `preview`.
That is enough to witness the local navigation trail without pretending that Micromax now owns a global location history browser, persisted replay log, or richer navigation stack model.

The design goal is simple: if navigation history matters, it should be visible as a tiny register, not only as a hidden stack or transient picker.
