# Project-grouped recentpick menu truth

Rev503 closes one small trust/flow seam left behind by rev502.

Micromax already had the right adjacent recent-file surfaces:

- `recent_detail_row(PATH)` / `showrecent PATH` exposed MRU index, live state,
  cursor position, and tiny disk/action truth
- palette `Recent Files` rows and dedicated `recentdirpick` rows already reused
  that exact metadata visibly
- project-grouped `recentpick` rows already preserved project-relative path plus
  the same tiny `existing file` / `new file` and `current buffer` /
  `switch buffer` truth cues

But one small drift still lingered inside the project rewrite itself: the row
menu still collapsed back to bare `project-name`, which silently discarded the
MRU suffix the richer row already had.

That meant project-grouped `recentpick` rows could still hide exactly the cues
rev502 said they preserved:

- `#N` recency
- `[active]` / `[open]` / `[dirty]` / `[readonly]`
- `@ line:col`

## What landed

Rev503 keeps the fix tiny.

- `_recent_section_row(...)` now preserves the rich menu suffix when it rewrites
  a visible row to one project label
- project-grouped rows now render like `proj #1 [active] @ 2:1`
  instead of collapsing back to just `proj`
- info text still keeps the project-relative path plus the same trailing truth
  cues from rev502

Example:

```text
['/tmp/demo/proj/guide/intro.md', 'recent', 'proj #1 [active] @ 2:1', 'guide/intro.md | existing file | current buffer']
```

## Why this matters

This is a tiny but high-leverage honesty fix.

`recentpick` is the boring daily reopen/switch loop. If Micromax already knows
one visible project-grouped row is MRU #1, active, dirty, or currently at a
specific cursor target, those cues should stay visible before Enter instead of
getting erased by the project-label rewrite itself.

## Focused tests

- `tests/test_editor_buffer_lifecycle_recent.py`
- `tests/test_editor_statusline.py`
- `tests/test_tui_prompt_display_lines_sticky_header.py`
