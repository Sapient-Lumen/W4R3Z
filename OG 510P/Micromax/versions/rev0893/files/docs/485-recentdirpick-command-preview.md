# Rev543 - recentdirpick command preview

## Goal
Make the `recentdirpick` entry point tell the truth before Enter.

## Why
`recentdirpick [QUERY]` already opens a grouped recent-directory picker with honest MRU, location, and action cues. Query-time completion already reuses exact recent-file metadata when you start typing a specific file path. But the picker's own no-arg command row still stayed generic, so the direct "browse recent files by directory" path hid how many remembered files and visible directory buckets existed and which row would anchor the picker.

## Change
- add `Editor._prompt_recentdirpick_command_row(...)`
- reuse `_recent_dir_prompt_rows('', limit=1)` for the first visible grouped recent-directory row
- reuse live recent-file and grouped-directory counts for the summary prefix
- keep the ordinary command doc while replacing the generic hint with either:
  - `N recent files in M directories · latest ...`
  - `0 recent files`

## Result
Typing plain `recentdirpick` in the command bar now previews the same grouped recent-directory truth the picker will immediately open with, instead of going blind right before execution.
