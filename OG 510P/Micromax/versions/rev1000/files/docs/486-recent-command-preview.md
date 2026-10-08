# Rev544: preview plain `recent` inventory in the command bar

## Why

Micromax already made the surrounding recent-file surfaces truthful before Enter:

- `showrecent PATH|N|#N` previews one exact visible recent slot
- `showrecentgroups [QUERY]` previews grouped recent-file bucket counts
- `showrecentdir DIR|N|#N` and `showrecentdirgroups [QUERY]` do the same for recent directories
- `recentpick [QUERY]` and `recentdirpick [QUERY]` preview the grouped picker inventory they are about to open

But the plain `recent` command itself still fell back to a generic no-arg command row even though it already knew the MRU register it would print after Enter.

That made the smallest direct recent-file surface slightly less trustworthy than its neighbors.

## What changed

Rev544 keeps the change tiny and headless-first:

- add `Editor._prompt_recent_command_summary_row(...)`
- reuse `recent_inventory_rows(limit=1)` plus the stable `recent_files` count
- wire exact command completion for plain `recent` to preview:
  - `N recent files · latest ...`
  - `0 recent files`
- rev552 later tightens the ordinary command doc to match reality too: `recent [N|#N|clear] - show/open recent files`
- pin both populated and empty command-row contracts in focused tests

## Result

The direct MRU surface now matches the rest of the recent-file family:
if Micromax already knows the recent register behind `recent`, the command bar says that truth before Enter instead of hiding behind a generic command hint.
