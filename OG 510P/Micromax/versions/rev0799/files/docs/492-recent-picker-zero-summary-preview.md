# Rev550 — recent picker query misses stay honest before Enter too

## What changed

`recentpick [QUERY]` and `recentdirpick [QUERY]` already reported
`0 recent file(s)` after Enter when a typed fuzzy name/path query matched no
remembered recent target.

This revision closes the small command-bar sibling seam. When you type one
unmatched recent-picker query like `recentpick zzz-no-such-recent-file` or
`recentdirpick zzz-no-such-recent-file`, completion now preserves that raw
token long enough to render the same zero-summary truth instead of falling back
to a generic `filter recent picker` hint.

## Why it matters

Micromax is trying to keep searchable command loops boring and trustworthy.
Once the editor can already tell that one recent-picker query resolves to zero
remembered files, the command bar should say `0 recent file(s)` before Enter
instead of making humans or future LLMs wait for the post-submit message. That
keeps the before/after contract aligned without widening the API.

## Verification

- completion row for `recentpick zzz-no-such-recent-file` now says
  `0 recent file(s)`
- completion row for `recentdirpick zzz-no-such-recent-file` now says
  `0 recent file(s)`
- after Enter, both pickers keep their existing zero-summary messages
