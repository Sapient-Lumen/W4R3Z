# Rev530 — keep visible slot/lane truth in plain jumpback/jumpforward feedback

## Why

Micromax already made the jumplist increasingly honest at every nearby scale:

- `jumps` shows visible `#N` entry ids
- `showjump INDEX|#N` inspects one exact entry without mutating history
- `showjumpgroups [QUERY]` summarizes grouped `Current` / `Back` / `Forward` buckets
- `jumppick [QUERY|N|#N]` now speaks `#N`, previews exact rows before submit, keeps exact-slot misses typed, and preserves the chosen visible slot/lane on success

But the simplest history loop still had one tiny trust seam: plain `jumpback` / `jumpforward` flattened successful traversal back to a generic landed-target message. That confirmed *where* the editor landed, but not *which visible jumplist slot* or *which lane/depth* produced that move.

That missing bit matters in the headless-first/archive-first world Micromax wants: humans and future LLMs should be able to line up the direct navigation message with the visible `jumps` / `showjump` / `jumppick` row they just inspected.

## What changed

Rev530 keeps the fix deliberately small:

- new internal helper `Editor._peek_jump_navigation_detail_row(direction)` captures the pre-move exact jumplist row for the next `back` or `forward` traversal
- `JumpBack` / `JumpForward` actions now reuse that pre-move row in their final success feedback
- command-bar `jumpback` / `jumpforward` do the same
- no-op traversal stays explicit and unchanged:
  - `jumpback: no earlier jump`
  - `jumpforward: no later jump`

## Result

Successful one-step history traversal now preserves the same visible jumplist dialect as the adjacent inspection surfaces:

- `jumpback #1 [back 1] -> *t* @ 1:0`
- `jumpforward #2 [forward 1] -> *t* @ 3:0`

The goal is small but important: if Micromax already exposes visible jumplist slots elsewhere, the simplest back/forward loop should keep that same truth instead of discarding it at the final message.
