# Rev522 — visible recent-slot hash dialect

## Why

Micromax already made numbered recent-file state easy to inspect and reopen:

- `recent` shows visible MRU slots
- picker feedback now keeps the selected slot as `#N`
- `showrecent N` and `recent-slot-detail` already inspect one numbered recent entry without reopening it

But one tiny dialect seam still lingered. The human-facing rows tended to show the slot as `#N`, while the command and host surfaces still only accepted bare integers. That meant a human or future LLM could copy the visible token literally and hit an avoidable mismatch.

## What changed

Rev522 keeps the fix deliberately small:

- one shared recent-slot parser now accepts `N` or `#N`
- `showrecent #N` works the same as `showrecent N`
- `recent #N` works the same as `recent N`
- `"#N" recent-slot-detail` works the same as `N recent-slot-detail`
- command-bar completion for `showrecent` / `recent` now offers `#N` candidates when the typed prefix starts with `#`

## Why it matters

This is a trust/flow/headless-first cleanup, not a new feature family. If Micromax already shows one recent entry as `#N`, the exact inspect and reopen surfaces should understand that same token instead of forcing callers to strip one small prefix first.
