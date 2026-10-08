# Rev528 — `jumppick` exact-slot misses stay exact too

## What changed

Micromax already treated `jumppick N|#N` as a direct visible-slot request:

- rev526 made the live jumplist prompt speak visible `#N` slots
- rev527 taught command-bar completion for `jumppick N|#N` to preview the same exact jump metadata as `showjump`
- `showjump N|#N` already failed plainly as `showjump: no such jump: TOKEN`

But one tiny trust seam still lingered at submit time. If a user typed a direct
slot that did not exist, `jumppick` still fell back to the generic fuzzy-search
message `jumppick QUERY: 0 jump(s)`.

Rev528 keeps the fix deliberately small:

- direct numeric or visible `#N` `jumppick` misses now report `jumppick: no such jump: TOKEN`
- ordinary fuzzy queries still keep the existing counted zero-summary path
- successful direct slot picks are unchanged

## Why this matters

This is mostly a trust fix. Once Micromax already accepts `jumppick #3` as an
exact visible-slot request, the miss path should keep telling the truth about
what kind of request it was.

That matters for humans and future LLMs alike:

- command-bar completion already frames `jumppick N|#N` as exact slot lookup
- `showjump N|#N` already uses a typed exact-miss dialect
- the picker still needs counted zero summaries for ordinary fuzzy search

So the clean split is:

- exact slot request: `jumppick: no such jump: TOKEN`
- fuzzy search request: `jumppick QUERY: 0 jump(s)`

## Surfaces kept aligned

- `jumps` — flat visible jumplist register
- `showjump INDEX|#N` — exact side-effect-free row with typed misses
- `showjumpgroups [QUERY]` — grouped bucket summary rows
- `jumppick [QUERY]` — grouped browse/submit path
- `jumppick N|#N` — direct visible-slot pick with exact success and exact miss
