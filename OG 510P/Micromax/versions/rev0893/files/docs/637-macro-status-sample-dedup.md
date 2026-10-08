# Rev696 - macro status sample dedup

Date: 2026-03-28

## Why

After rev695, the playback-root `macro` / `showmacro` summaries had already stopped repeating the current live macro as their own `e.g.` sample. But `macro status` still had the same small readability problem:

- `macro status: playing demo (1 step), 2 macro(s), demo (1 step), last (1 step) [default]`
- prompt row: `playing · demo (1 step) · 2 macros · e.g. demo (1 step)`

## What changed

Playback status summaries now skip saved entries whose name matches the current live macro and prefer another saved clue when one exists, for example:

- `macro status: playing demo (1 step), 2 macro(s), last (1 step) [default]`
- prompt row: `playing · demo (1 step) · 2 macros · e.g. last (1 step) [default]`

## Result

The status lane now matches the root-summary lane: the tail/sample spends its last words on new information instead of repeating the same live macro a second time.
