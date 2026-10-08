# showjump hash dialect

Rev524 tightens one small trust/flow/headless-first seam in the jumplist loop: exact jump inspection no longer forces callers to strip the visible `#` prefix from a jump entry before asking for exact truth.

## Why

By rev455, Micromax already had a coherent exact jumplist inspection surface:

- plain `jumps` exposed the current/back/forward trail for humans
- those rows already printed entry ids as visible `#N` tokens
- `showjump INDEX` let humans inspect one exact jumplist entry without moving through history
- `jump-detail` / `ed.jump-detail-row` exposed that same exact row headlessly
- command-bar completion for `showjump` already reused the exact row metadata for bare integers

But one tiny dialect seam still lingered exactly where humans and future LLMs were likely to follow the visible register text literally:

- the broad jumplist surfaces already said `#N`
- the adjacent exact inspection surfaces still only accepted bare integers
- completion for `showjump` went blind again if you actually typed the visible `#`

That mismatch was small, but it made one honest visible token less reusable exactly where the archive already encouraged people to inspect one known jump entry directly.

## What changed

Rev524 keeps the fix deliberately small and aligned with the recent-slot cleanup pattern:

- `showjump INDEX|#N` now accepts the same visible hash-prefixed token the `jumps` register already prints
- `ed.jump-detail-row ( n|"#n" -- row|0 )` now accepts the same token headlessly
- `jump-detail ( n|"#n" -- row|0 )` mirrors that hostcall inside Micromax scripts
- command-bar completion for `showjump` now offers `#N` candidates when the typed prefix starts with `#`, while reusing the same exact row metadata as the bare-integer path

The row shape itself stays unchanged:

- `[query index lane depth buffer position preview]`

Only the addressing surface grows: callers can now reach the same exact jumplist row by the visible token they already have in front of them.

## Trust and flow effect

This is intentionally a tiny follow-up, but it removes one needless translation step:

- `jumps` already prints one entry as `#N`
- exact jumplist inspection already exists beside it
- exact jumplist inspection now understands the same visible token too

So the archive keeps one consistent story: if Micromax already shows a jump entry as `#N`, the adjacent exact inspection surface should understand that same visible handle instead of forcing callers to strip the hash first.
