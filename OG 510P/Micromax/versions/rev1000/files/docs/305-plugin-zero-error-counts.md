# Plugin zero-error detail counts (rev363)

## Why

Recent plugin-loop work made broad `plugin errors` inventory count-aware, made `plugin info NAME` show current error lines directly, and made command-bar plus hostcall reload reuse one honest feedback dialect. But one tiny filtered-detail mismatch still lingered: healthy `plugin info NAME` and filtered `plugin errors NAME` still fell back to `errors: (none)` while broken plugins used `errors: N`.

That was truthful, but it quietly changed the structure of the detail surface exactly when the current error count dropped to zero.

## What changed

Filtered plugin detail now keeps the same tiny count-aware shape in both the empty and non-empty cases:

- old healthy detail: `errors: (none)`
- new healthy detail: `errors: 0`
- broken detail stays `errors: N`

This applies to:

- `plugin info NAME`
- filtered `plugin errors NAME`

## Why it matters

This is a small trust/flow follow-up, not a new subsystem. A detail command should not switch dialects just because the count became zero. Keeping the empty path as `errors: 0` makes the healthy and broken states easier to scan, easier to compare, and easier for future UIs/scripts/LLMs to consume without special-casing another `(none)` branch.
