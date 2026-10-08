# Rev663 - exact macro inspection for one slot

## What changed

Micromax now has one exact macro inspector instead of only broad inventory/runtime views.

- `showmacro NAME` reports one exact macro slot without replaying it
- `Editor.macro_detail_row(NAME)` exposes the same shared detail row in Python
- portable `ed.macro-detail-row` exposes that exact row to Micromax scripts and future UIs/LLMs
- command-bar completion for `showmacro` now previews exact saved, recording, playing, default, and missing-slot states before Enter

The shared detail row is:

- `[query canonical state steps default shadow_steps]`

where:

- `state` is `saved`, `recording`, or `playing`
- `default` is `1` only for `last`
- `shadow_steps` preserves the saved slot size hidden underneath an active recording-owned slot

## Why

Rev659 through rev662 made the macro surface much more truthful: blocked control paths stopped failing silently, missing names stopped drifting into `last`, empty-step named slots stopped masquerading as saved automation, and raw writes stopped pretending to stick when recording already owned the destination.

But one exact-inspection gap still lingered beside those fixes. There was still no `showmacro NAME` sibling to `showmark`, `showjump`, `showbuffer`, or `showplugin`. That meant anyone asking “what does macro slot `NAME` mean right now?” had to reconstruct the answer from several nearby surfaces:

- broad `macro list` inventory
- broad `macro status` runtime state
- raw `ed.macro-get` step fetches

That was especially awkward while recording, because `last` and the active target were already live-owned even before `stop` committed them.

## Result

One exact macro slot is now inspectable in one place.

Examples:

- saved slot: `showmacro demo: 3 steps`
- default slot: `showmacro last [default]: 3 steps · default replay slot`
- live recording target: `showmacro demo [recording]: 2 live steps · stop to save, cancel to discard`
- missing slot: `showmacro: no such macro: ghost`

This is deliberately small, but it helps both **trust** and **flow**:

- trust, because Micromax now tells the truth about one exact automation slot
- flow, because users/scripts/LLMs no longer need to stitch together multiple nearby surfaces just to inspect one name
