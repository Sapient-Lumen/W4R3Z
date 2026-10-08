# Rev545: keep exact recent-picker slot misses honest

## Why

Micromax already made the surrounding recent-file loops more truthful:

- `showrecent PATH|N|#N` reports exact recent-file misses honestly after Enter
- `recent`, `showrecent`, `recentpick`, and `recentdirpick` now preview live recent state before Enter
- exact recent completion rows already reuse the same `#N` recent-slot dialect humans see in MRU output

But one small trust seam still lingered at submit time for the searchable recent pickers.
Typing a visible slot like `recentpick #9` or `recentdirpick #9` could fall through to the generic fuzzy `0 recent file(s)` path even though Micromax already knew that `#9` was being used as an exact recent-slot request.

## What changed

Rev545 keeps the change tiny and local:

- teach `_prompt_exact_recent_row(...)` to say `no such recent file` for missing visible-slot tokens
- teach `_prompt_recent_command_row(...)` to keep the same exact-slot miss truth for `recent #N` previews
- keep `recentpick` / `recentdirpick` submit feedback split by intent:
  - exact `N|#N` slot misses now report `no such recent file`
  - ordinary fuzzy name/path queries still report `0 recent file(s)`
- pin the completion-row and picker-submit contracts in focused tests

## Result

Recent-file picking now matches the jumplist’s exact-vs-fuzzy trust split:
if Micromax can tell that a query is one exact visible recent slot request, it says `no such recent file` instead of pretending it was only a fuzzy zero-match search.
