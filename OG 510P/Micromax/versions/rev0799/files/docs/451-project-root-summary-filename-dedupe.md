# Project-root recent summary filename dedupe

Rev509 closes one more tiny taste/trust seam in Micromax's broad recent-group
inspection loop.

Micromax already had the right nearby summary behavior:

- broad `showrecentgroups [QUERY]` summaries now reuse the same visible sample
  row dialect as adjacent grouped picker rows
- directory-grouped summaries already trimmed one leading directory echo when
  the bucket label itself named that directory
- project-grouped summaries already kept the sample row's MRU/live-buffer cues
  instead of flattening back to `full/path — parent`

But one tiny repetition seam still lingered in the project-grouped sibling:

- when a recent file lived directly under the project root, the grouped sample
  detail could still begin with that same basename
- broad summaries could then read like
  `e.g. root.md #1 [active] @ 1:0 — root.md | current buffer`
- the second `root.md` added no new location truth because the sample menu had
  already named that file

## What landed

Rev509 keeps the follow-up deliberately small.

- `Editor._trim_leading_location_echo(...)` now accepts the small set of cues a
  row already shows (directory, section, or sample basename) instead of only a
  single literal location string
- `_recent_section_summary_rows(...)` now passes both the visible bucket label
  and the sample basename through that helper, so root-level project samples can
  drop one repeated leading filename while nested relative paths stay intact
- focused tests pin both the direct `showrecentgroups root.md` surface and the
  adjacent command-bar completion row

## Why this matters

This is another tiny taste/trust cleanup.

Broad recent summaries are supposed to answer “what lives in this bucket?” in
one quick glance. Once the sample menu already names the file, repeating that
same basename in the detail slot is just noise that pushes the real action cue
farther right.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
