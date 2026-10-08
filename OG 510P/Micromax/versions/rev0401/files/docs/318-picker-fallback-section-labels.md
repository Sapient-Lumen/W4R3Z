# Picker fallback section labels

Rev376 is a tiny taste/trust follow-up on the grouped-picker work.

Micromax already had the right grouped browse model for buffers and recent files:
project roots and parent directories became visible section labels, empty-query
browse windows budgeted rows across sections, and prompt/status/TUI surfaces all
reused the same small section helpers.

But one small fallback seam still lingered in that loop:

- relative or path-light file rows like `notes.txt` could still surface a raw
  filesystem placeholder like `.` as the section label
- the shared helpers still carried old `(unknown)` fallback strings even though
  the surrounding picker surfaces had already moved toward plain human-facing
  labels

That was not a correctness bug, but it was a small coherence bug. When
Micromax cannot infer a richer project root or parent directory, the picker
header/status should still read like an editor category, not like a raw path
artifact.

## Change

The shared section-label helpers now fall back to visible category labels:

- buffer rows fall back to `Buffers`
- recent-file rows fall back to `Recent Files`

This applies to the grouped hostcall rows, the live picker section headers, and
status/preview surfaces that reuse `prompt_current_section`.

## Why it matters

This keeps grouped picker output a little more legible in the exact degenerate
cases that future humans/LLMs will often hit inside an archive:

- relative-path buffers opened from the repo root
- seeded/replayed recent-file rows that do not carry a richer parent directory
- prompt/status inspection where `.` is technically accurate as a `Path.parent`
  value but not actually a useful UI label

The point is small but consistent with the current direction:
**visible picker sections should read like editor concepts, not raw path
placeholders.**
