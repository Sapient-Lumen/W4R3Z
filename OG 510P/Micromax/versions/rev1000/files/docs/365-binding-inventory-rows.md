# Binding inventory rows

Micromax already had the important tiny current-binding loop before rev423: `showbindings active` exposed the precedence-resolved reachable keymap, `whichkey` preferred human descriptions when available, one-shot winners kept the `!` cue, and lower-level hostcalls like `ed.available-bindings`, `ed.available-binding-info`, and `ed.keymode-rows` already exposed the raw pieces.

The remaining seam was not discovery logic; it was **host-boundary symmetry**.
Humans could inspect the richer current-binding inventory directly, but scripts and future UIs still had to join resolved binding rows with active keymode rows to reconstruct the final label and current one-shot state by hand.

Rev423 adds one deliberately small shared inventory surface instead of a bigger keymap API:

- `available_binding_inventory_rows()` returns ordered rows inside the editor
- `ed.available-binding-inventory-rows` exposes the same rows to Micromax scripts and future UIs
- plain `showbindings active` and `whichkey` now both reuse that same row surface so command output and host data stay aligned

The rows stay intentionally tiny:

- `mode` — winning mode name (`global`, `nav`, `goto`, ...)
- `key` — resolved key text
- `action` — winning action-spec
- `label` — the human-facing `whichkey` label (resolved description when present, otherwise the action-spec)
- `once` — `1` when that winning mode is currently one-shot / transient

This deliberately complements the lower-level `ed.available-bindings` / `ed.available-binding-info` rows instead of replacing them.
The design goal is simple: if current binding discovery already helps humans trust prefix and keymode state, the same tiny surface should be available to scripts and future UIs too.
