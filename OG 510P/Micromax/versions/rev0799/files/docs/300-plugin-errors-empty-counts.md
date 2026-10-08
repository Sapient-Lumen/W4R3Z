# Plugin errors empty-state counts (rev300)

## Why

Recent plugin-loop work made broad `plugin errors` inspection count-aware and grouped when failures exist, but the empty state still fell back to a special-case `plugin errors: (none)` message. That was truthful, but it quietly dropped the same tiny inventory structure that the non-empty path already used.

## What changed

Plain `plugin errors` now stays count-aware even when nothing is broken:

- old: `plugin errors: (none)`
- new: `plugin errors: 0 plugin(s), 0 error(s)`

## Why it matters

This is a tiny trust/flow polish pass. The command now answers the same question in the same shape whether the result set is empty or not. That keeps broad broken-plugin inspection feeling like inventory rather than a special log-ish path with its own exceptions.
