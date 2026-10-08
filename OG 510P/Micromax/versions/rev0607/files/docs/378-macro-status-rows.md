# Rev436: macro status rows

Micromax already had the important tiny macro pieces before rev436: explicit `macro record` / `macro stop` / `macro cancel` / `macro play` / `macro list`, filtered saved-macro inventory through `macro_inventory_rows()` / `ed.macro-inventory-rows`, and thinner runtime probes through `ed.macro-recording?` / `ed.macro-playing?` plus status-model fields.

The remaining seam was **runtime snapshot symmetry**.
Humans could ask the command bar to list saved macros, and scripts could separately ask whether recording or playback was active, but neither side had one tiny first-stop register for the combined question future UIs/LLMs actually care about: *what is macro automation doing right now, and what saved macros already exist next to it?*

Rev436 keeps the fix deliberately small:

- `macro_status_rows()` returns one combined runtime-status-plus-saved-inventory register inside the editor
- `ed.macro-status-rows` exposes the same rows to Micromax scripts and future UIs
- plain `macro status` reuses that same row surface instead of restitching flags and inventory ad hoc
- playback now also keeps the active macro name/step count explicit while it is running, so hooks and script-side inspection can see the live target instead of only a bare boolean

Wire shape:

```text
[[section ...] ...]
```

Rows:

- `['status', state, name, steps, saved_count]`
  - `state` is `idle`, `recording`, or `playing`
  - `name` is the current recording/playback target name, or `""` when idle
  - `steps` is the buffered step count while recording, the played macro size while replaying, or `0` when idle
  - `saved_count` is the number of visible saved macros in the following rows
- `['saved', name, steps]`
  - the same filtered saved-macro inventory already exposed by `macro_inventory_rows()` / `ed.macro-inventory-rows`

Examples:

```text
[['status', 'idle', '', 0, 0]]
[['status', 'recording', 'demo', 2, 0]]
[['status', 'playing', 'demo', 3, 2], ['saved', 'demo', 3], ['saved', 'last', 3]]
```

Why keep this even though the separate flags and inventory rows already existed? Because those older surfaces answer narrower questions:

- `ed.macro-recording?` / `ed.macro-playing?` = live booleans only
- `ed.macro-inventory-rows` = saved macros only
- `ed.macro-status-rows` = the tiny combined runtime snapshot behind `macro status`

That split matches the editor's broader inspectability cleanup: keep the raw lower-level probes when they are useful, but also expose the exact tiny human-facing register once humans and future automation already need it.
