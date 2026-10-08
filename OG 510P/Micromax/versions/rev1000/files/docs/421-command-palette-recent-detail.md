# Rev479 — command-palette recent-file rows now keep exact MRU detail

## Why

Micromax already treated recent files as a first-class part of the command
palette: empty-query `commandpick` opened with a `Recent Files` bucket first,
palette file selections reported the landed target explicitly, and one exact
MRU entry already had an inspectable side-effect-free sibling through
`recent_detail_row(PATH)` / `showrecent PATH`.

But one small trust/flow seam still lingered inside the palette rows
themselves. Visible recent-file rows still flattened back to basename +
parent, which made it harder to tell whether a target was merely recent or was
also the active dirty buffer, an already-open readonly file, or a file with a
useful remembered cursor.

## What changed

- add one tiny `_command_palette_recent_file_row(...)` helper that formats
  palette `recentfile` rows from the existing exact MRU substrate
- `command_palette_recent_file_rows()` now reuses `recent_detail_row(PATH)` when
  one visible palette row already maps to one exact recent entry
- palette recent-file rows now keep recency order, active/open/dirty/readonly
  flags, cursor position when open, and the same section/detail metadata used by
  `showrecent PATH`
- focused hostcall coverage pins the `ed.command-palette-rows QUERY` contract
  for a recent-file match

## Result

The palette stays search-first and lightweight, but it stops hiding exact MRU
metadata Micromax already knows. If one visible `commandpick` file row is
already one exact recent entry, the editor can keep that tiny honest state
visible before selection instead of making humans or future LLMs reopen the
file just to rediscover it.
