# Rev661 - macro empty-slot inventory truth

## What changed

Micromax no longer advertises zero-step named macros as if they were real saved
automation.

- `macro list` / `macro status` no longer count or display empty-step named slots
- `macro_inventory_rows()` / `ed.macro-inventory-rows` omit them too
- raw `macro_names()` / `ed.macro-names` now match that same filtered saved
  inventory instead of exposing names that `macro play NAME` would only reject
- `set_macro(NAME, [])` now prunes the named slot directly
- stopping a zero-step named recording keeps `last` explicit but reports
  `macro: saved 0 steps (NAME omitted)`

## Why

Rev660 already made raw fetches honest: missing named slots now come back as
`[]` instead of quietly drifting into `last`. But one narrow trust seam remained
right next to that fix: zero-step named slots could still be created and then
show up in saved-inventory/name surfaces even though replay already treated them
as effectively missing.

That taught the wrong next step to both humans and future scripts/LLMs:
Micromax would say a macro was saved, then reject `macro play NAME` as `no such
macro` anyway.

## Validation

Focused coverage now pins:

- zero-step named `macro record NAME` + `macro stop` omission from list/status
  and raw names
- `set_macro(NAME, [])` / portable `ed.macro-set` pruning named slots
- command-bar play-slot completion omitting zero-step named slots and showing an
  exact typed miss instead
