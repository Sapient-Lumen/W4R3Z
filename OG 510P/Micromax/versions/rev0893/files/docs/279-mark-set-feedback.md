# Rev337: mark placement should report the anchor target

This is a tiny follow-up to the recent orientation work.

Micromax already made mark *jumps* explicit in rev333: `markjump NAME` and picker-driven `markpick` jumps now report the real landed buffer/cursor target. But one small gap remained inside the same navigation loop: placing a mark was still verbally vague.

Before rev337, `mark NAME` only said `mark set: NAME`. That confirmed that *something* happened, but not *where* the anchor actually lives. In a headless-first editor, that matters more than it might in a heavier UI, because marks are meant to be lightweight navigation primitives that stay inspectable and easy to trust.

Rev337 keeps the fix intentionally small. Successful `mark NAME` commands now report the actual anchor target in the same orientation dialect as the rest of the navigation surface:

- `mark set: NAME -> target @ line:col`

Example:

- `mark set: here -> alpha @ 2:0`

Why this matters:

- **trust:** the editor now tells the truth about where the mark was recorded
- **flow:** dropping a navigation anchor no longer forces the user to re-check the screen or run `marks` to confirm the exact spot
- **coherence:** the full marks loop now matches itself — place a mark, jump to a mark, and picker-drive a mark jump all speak the same explicit orientation style

This is deliberately not a larger marks subsystem. It does not add persistent marks, local/global mark classes, or richer mark previews. It just makes ordinary mark placement a little more honest.
