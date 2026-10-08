# Rev368: `apropos` should tell the truth about discovery inventory

This is a tiny **trust/flow** follow-up to the recent count-aware inventory cleanup.

`apropos QUERY` was already a good headless discovery surface: it searched command, action, and visible-word topics with the same deterministic ranking used elsewhere, and it showed a small preview of the best matches. But one small structural mismatch still lingered in that search-first loop:

- the empty path still collapsed to `apropos QUERY: (none)`
- the non-empty path jumped straight into preview rows without saying how many topics matched

That meant the same command quietly changed dialect when the result set dropped to zero, and even successful searches hid one piece of useful state: whether you were looking at a singleton hit or a broader slice.

## What rev368 changes

`apropos QUERY` now keeps one tiny count-aware dialect:

- empty results say `apropos QUERY: 0 topic(s)`
- non-empty results start with `apropos QUERY: N topic(s), ...`
- the existing preview rows and `... (+N more)` suffix stay intact

The implementation stays deliberately small: the command now counts the full ranked result set before rendering the same short preview rows, and the shared tiny summary helper can accept an explicit total when a command shows only a preview slice.

## Why this matters

This is another small "inventory tells the truth" move.

`apropos` is one of the first places a user or future LLM goes when they do not yet know the exact command, action, or word they want. That discovery surface should stay structurally glanceable whether the answer is zero, one, or many.
