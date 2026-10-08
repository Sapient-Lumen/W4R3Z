# Recent-group summary row truth

Rev508 closes one small trust/taste seam in Micromax's broad recent-bucket
inspection loop.

Micromax already had the right nearby recent surfaces:

- grouped `recentpick` / `recentdirpick` rows reused exact MRU metadata and
  live-buffer truth
- exact `showrecent PATH` / `showrecentdir DIR` inspection already kept the
  same tiny file/state dialect without reopening anything
- broad `showrecentgroups [QUERY]` / `showrecentdirgroups [QUERY]` summaries
  were already count-aware and reused by command-bar completion

But one small broad-summary seam still lingered:

- those broad summary rows still showed their example in an older flattened
  dialect like `full/path — parent`
- that repeated location the section label already named, hid the sample row's
  MRU/live-buffer cues, and made the broad summary path less truthful than the
  grouped picker rows beside it

## What landed

Rev508 keeps the follow-up deliberately small.

- `_recent_section_summary_rows(...)` now builds recent-group summaries from the
  first visible grouped recent row instead of flattening back to raw path data
- `sample_name` now keeps the same visible file-facing menu dialect as the
  adjacent picker row (`name #N [flags] @ line:col`)
- `sample_detail` now keeps the grouped landing/action truth, and the
  directory-grouped sibling trims one echoed leading directory when the bucket
  label already names it
- plain `showrecentgroups` / `showrecentdirgroups` and command-bar completion
  inherit that same richer summary row automatically

## Why this matters

This is a tiny honesty/legibility cleanup.

Broad inspectors are supposed to answer “what kind of recent bucket is this?”
without forcing one more hop back into the picker. Once Micromax already knows
which visible row best represents one recent bucket, the summary path should
reuse that same row instead of flattening back to noisier `path — parent`
echoes.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
