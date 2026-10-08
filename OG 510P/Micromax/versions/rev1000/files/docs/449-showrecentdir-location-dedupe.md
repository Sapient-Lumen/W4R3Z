# showrecentdir location dedupe

Rev507 closes one more tiny taste/trust seam in Micromax's recent-directory
inspection loop.

Micromax already had the right exact recent-directory truth nearby:

- `recentdirpick` rows reused the same sample-row metadata as exact recent-file
  inspection
- `showrecentdir DIR` already surfaced that sample row for humans without
  reopening the picker
- `ed.recent-dir-detail-row` still kept the full literal directory plus
  `sample_info` fields for scripts and future UIs

But one tiny formatting seam still lingered on the human side:

- `showrecentdir DIR` already printed the bucket label at the start of the
  message
- the reused sample-row info could still begin with that exact same directory,
  producing lines like `recentdir /tmp/proj: ... | /tmp/proj | existing file`
- the second directory copy added no new location truth and pushed the real
  file/state cues one slot farther to the right

## What landed

Rev507 keeps the follow-up deliberately small.

- `Editor._trim_leading_location_echo(...)` now makes the dedupe rule explicit
  in one tiny shared helper
- plain `showrecentdir DIR` trims one echoed leading directory from reused
  sample-row info while leaving the stored `ed.recent-dir-detail-row` hostcall
  shape untouched
- focused tests pin both the ordinary nested-directory case and the top-level
  recent-file case

## Why this matters

This is a tiny taste/trust cleanup.

Exact inspectors are supposed to reduce guesswork, not add one more small thing
for humans or future LLMs to mentally cancel out. Once the command already names
one recent-directory bucket, the sample clause should spend its space on the
actual sample file and its state cues.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
