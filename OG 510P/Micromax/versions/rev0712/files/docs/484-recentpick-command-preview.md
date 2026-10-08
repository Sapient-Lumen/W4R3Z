# Rev542 - recentpick command preview

## Goal
Make the `recentpick` entry point tell the truth before Enter.

## Why
`recentpick [QUERY]` already opens a grouped recent-file picker with honest MRU,
location, and action cues. Query-time completion already reuses exact
`showrecent PATH|N|#N` metadata when you start typing a specific path or slot.
But the picker's own no-arg command row still stayed generic, so the direct
"browse recent files" path hid how many remembered files existed and which row
would anchor the picker.

## Change
- add `Editor._prompt_recentpick_command_row(...)`
- reuse `_recent_prompt_rows('', limit=1)` for the first visible grouped picker row
- reuse `recent_files` count truth for the summary prefix
- keep the ordinary command doc while replacing the generic hint with either:
  - `N recent files · latest ...`
  - `0 recent files`

## Result
Typing plain `recentpick` in the command bar now previews the same grouped
recent-file truth the picker will immediately open with, instead of going blind
right before execution.
