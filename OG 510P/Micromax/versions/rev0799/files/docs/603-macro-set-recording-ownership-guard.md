# Rev662 - macro set recording-ownership guard

## What changed

Micromax now refuses raw macro writes that an active recording session already
owns.

- `set_macro(NAME, steps)` now rejects writes to `last` while recording is open
- it also rejects writes to the active recording target slot
- portable `ed.macro-set` surfaces that same blocker as a Micromax error
- non-conflicting writes to other named slots still work during recording

## Why

Rev659 through rev661 made the macro surface much more truthful: blocked
record/play/stop/cancel paths stopped failing silently, missing names stopped
quietly drifting into `last`, and zero-step named slots stopped masquerading as
saved automation.

But one narrow raw-write seam still lingered underneath that honest surface:
while a recording session was open, `set_macro()` / `ed.macro-set` could still
write into `last` or the current recording target even though `stop` or
`cancel` were guaranteed to overwrite those exact slots moments later.

That meant headless scripts could be told a raw write had succeeded when the
active recording already owned the destination and was about to clobber it.

## Validation

Focused coverage now pins:

- direct `set_macro()` rejecting writes to `last` and the active target during
  recording
- portable `ed.macro-set` raising the same blocker for those owned slots
- allowed recording-time writes to other named slots still surviving the active
  recording session
