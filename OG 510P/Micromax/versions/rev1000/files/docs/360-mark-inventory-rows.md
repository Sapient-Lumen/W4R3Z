# Mark inventory rows

Micromax already had the important tiny marks loop before rev418: explicit `mark NAME` placement, explicit `markjump NAME` / `markpick` navigation, and a legible `marks` inventory line that marked the active buffer and the exact current-cursor anchor.

The remaining seam was not user-facing wording; it was **host-boundary symmetry**.
Humans could inspect the richer mark inventory directly, but scripts and future UIs still had to start from the thinner raw `ed.marks` rows and then reconstruct owner state, `[here]` state, and source preview by hand.

Rev418 adds one deliberately small shared inventory surface instead of a bigger bookmark system:

- `mark_inventory_rows()` returns ordered rows inside the editor
- `ed.mark-inventory-rows` exposes the same rows to Micromax scripts and future UIs
- plain `marks` now reuses that same row surface so command output and host data stay aligned

The rows stay intentionally tiny:

- `name` — mark name
- `buffer` — owning buffer name
- `position` — small 1-based `line:col` label
- `preview` — trimmed source-line preview when available
- `active` — `1` when the mark belongs to the current buffer
- `here` — `1` when the mark matches the current primary cursor exactly

This deliberately complements the thinner raw `ed.marks` tuples instead of replacing them.
The design goal is simple: if plain mark inventory already helps humans trust their anchors, the same tiny surface should be available to scripts and future UIs too.
