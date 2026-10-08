# Rev384 — macro play miss feedback

## What changed

`macro play NAME` now fails as `macro play: no such macro: NAME` instead of the older `macro play: no macro: NAME`.

## Why this tiny change matters

Macros are one of the first serious automation loops in Micromax. The editor already made command lookup, help lookup, hook inspection, keybinding inspection, and unknown `macro` subcommands fail in a plain, typed dialect. Playback misses were still understandable, but they lagged that newer shape.

The new wording keeps three things visible at a glance:

- the surface (`macro play`)
- the noun (`macro`)
- the missing target (`NAME`)

That makes failures easier to scan in the command bar, easier to assert in headless tests, and easier for future LLMs to reason about without guessing which layer produced the message.

## Scope

Deliberately tiny:

- no playback semantics changed
- no macro storage changed
- successful `macro play` feedback stays the same
- only the missing-target wording changed
