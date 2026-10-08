# Rev549 — grouped recent-summary query misses stay honest before Enter too

## What changed

`showrecentgroups [QUERY]` and `showrecentdirgroups [QUERY]` already reported
`0 section(s), 0 file(s)` after Enter when a typed query matched no recent-file
or recent-directory bucket.

This revision closes the small command-bar sibling seam. When you type one
unmatched grouped-recent query like `showrecentgroups zzz-no-such-recent-file`
or `showrecentdirgroups zzz-no-such-recent-file`, completion now preserves that
raw token long enough to render the same zero-summary truth instead of falling
back to a generic `filter ... buckets` hint.

## Why it matters

Micromax is trying to keep inspectable command loops boring and trustworthy.
Once the editor can already tell that a grouped recent-summary query resolves to
zero visible buckets, the command bar should say `0 section(s), 0 file(s)`
before Enter instead of making humans or future LLMs wait for the post-submit
message. That keeps the before/after contract aligned without widening the API.

## Verification

- completion row for `showrecentgroups zzz-no-such-recent-file` now says
  `0 section(s), 0 file(s)`
- completion row for `showrecentdirgroups zzz-no-such-recent-file` now says
  `0 section(s), 0 file(s)`
- after Enter, both commands keep their existing zero-summary messages
