# Rev529 — `jumppick` submit feedback keeps selected slot truth

Micromax already did most of the hard nearby jumplist work:

- `jumps` exposed visible `#N` entry ids
- `showjump INDEX|#N` / `ed.jump-detail-row` exposed exact lane/depth/buffer/position/preview truth
- rev526 made live `jumppick` rows use the same visible `#N` slot dialect
- rev527 taught command-bar completion for `jumppick N|#N` to preview that same exact row before submit
- rev528 kept exact-slot misses honest with `jumppick: no such jump: TOKEN`

But one small trust seam still lingered on the success path. After choosing or typing one exact visible slot, successful `jumppick` still reported only:

- `jump: buffer @ line:col`

That hid which picker row had actually run.

## What changed

- add `Editor.format_jump_picker_feedback(label, target, detail_row=...)`
- capture the exact jump detail row **before** mutating jumplist state
- successful `jumppick` submits now report `jumppick #N [lane depth] -> buffer @ line:col`
- built-in command docs now advertise `jumppick [QUERY|N|#N]`

## Why this tiny change matters

This is mostly a trust fix.

Once Micromax already lets humans, scripts, and future LLMs inspect one visible jump slot, preview that same slot in completion, and type that same slot directly into the picker, the final success message should preserve the same identity instead of flattening back to a generic navigation verb.

Using the **pre-submit** exact row matters too. Jumping naturally reshapes the current/back/forward lanes, so recomputing after the move could turn the chosen row into a different truth than the one the user actually selected.

## Resulting behavior

- selected prompt row: `jumppick #2 [back 1] -> a @ 2:1`
- typed exact slot: `jumppick #1 [back 2] -> a @ 1:0`
- exact miss still stays typed: `jumppick: no such jump: #9`
- fuzzy zero-match still stays counted: `jumppick QUERY: 0 jump(s)`

## Nearby surfaces

- flat register: `jumps`
- grouped browse/submit path: `jumppick [QUERY|N|#N]` / `ed.jump-section-rows`
- broad grouped summaries: `showjumpgroups [QUERY]` / `ed.jump-section-summary-rows`
- one exact entry: `showjump INDEX|#N` / `jump_detail_row(INDEX|#N)` / `ed.jump-detail-row`
