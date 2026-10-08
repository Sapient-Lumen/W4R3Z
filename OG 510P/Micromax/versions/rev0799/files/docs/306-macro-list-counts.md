# Rev364: macro inventory should stay count-aware even when empty

Recent trust-first work already made macro playback explicit and made `macro list` show saved step counts. That was a good baseline, but one tiny structural mismatch still lingered: the empty inventory path fell back to `macros: (none)` while non-empty inventory already had visible per-macro rows.

## Change

`macro list` now keeps one tiny count-aware inventory dialect in both cases:

- old empty path: `macros: (none)`
- new empty path: `macros: 0 macro(s)`
- non-empty path now starts with the same prefix, for example `macros: 2 macro(s), a (1 step), last (1 step)`

## Why this matters

This is a deliberately small trust/flow change.

Micromax is aiming for inspectable automation, not spooky automation. A future user or future LLM glancing at `macro list` should not have to mentally switch between a special-case empty message and a different non-empty inventory shape. Keeping the same small count-aware prefix in both cases makes it easier to answer simple questions quickly:

- are there any saved macros right now?
- how many visible macro entries exist?
- did recording/canceling leave the inventory empty again?

## Scope discipline

This does **not** add macro persistence, editing, deduplication, or richer inspection views.

It only tightens the existing one-line inventory path so the zero case keeps the same tiny structural dialect as the non-zero case.
