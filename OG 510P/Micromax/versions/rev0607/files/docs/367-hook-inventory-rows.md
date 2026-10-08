# Hook inventory rows (rev425)

Rev425 adds one tiny editor-side inspection surface for live hook wiring:
`hook_inventory_rows(NAME)` in the shared editor core, mirrored to Micromax as
`ed.hook-inventory-rows`.

## Why

Micromax already had two useful hook inspection paths:

- core-language `hook-detail NAME` returned portable handler rows
- editor `showhook NAME` gave humans a count-aware handler summary with group and provenance detail

But the editor-side host boundary still had a small asymmetry: the human-facing
`showhook` surface was assembled ad hoc from live `HookWord.handlers`, while
scripts and future UIs had no matching hostcall register for that same ordered
handler chain.

That made a common trust/debugging question slightly more awkward than it needed
to be: “what is currently attached to `ed.pre-action`, in what order, and where
did each handler registration come from?”

## Surface

```forth
"ed.pre-action" "ed.hook-inventory-rows" hostcall

\ => [["handler-name" group|0 [file line col]|0] ...]
```

The row shape is intentionally tiny and matches the detail already shown by
`showhook NAME`:

- `handler-name` — best-effort xt name (`<quote>` if unnamed)
- `group|0` — grouped registration tag when present
- `[file line col]|0` — best-effort registration provenance

If the looked-up name is not a hook, the hostcall returns `0` instead of `[]`,
so empty real hooks stay distinguishable from wrong-kind lookups.

## Command-bar reuse

`showhook NAME` now reuses that same row register for its handler chain instead
of re-walking `HookWord.handlers` inline. The command still keeps its existing
plain failure path (`showhook: not a hook: NAME`) and its existing trailing
`(defined at file:line:col)` cue for the hook definition span itself.

## Why this is enough for now

This intentionally does **not** add a bigger hook browser, a second hook-detail
dialect, or a richer editor-only map structure. Core Micromax `hook-detail` is
still the language-level portable primitive; rev425 only closes the editor-side
host-boundary gap so humans, scripts, and future UIs can all rely on one tiny
honest handler register.

## Tests

Focused coverage lives in:

- `tests/test_editor_showhook.py`
- `tests/test_editor_capabilities_registry.py`
