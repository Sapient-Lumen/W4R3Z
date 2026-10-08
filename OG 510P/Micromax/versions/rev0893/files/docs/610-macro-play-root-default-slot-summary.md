# Rev669 - keep idle macro playback roots centered on `last`

## What changed

Micromax now uses one shared idle default-slot summary for both exact macro inspection and root playback entry points.

- plain `showmacro` still reports `idle · default=last (N steps) · ...`
- idle `macro play` / `macro run` root rows now report that same `default=last (N steps)` witness instead of collapsing to broad inventory text like `0 macros`
## Why it matters

Rev668 fixed the slot menus, but the first idle playback witness still drifted from the story those menus taught. A user could see `last` led in completion, then hit bare `macro play` and get a root summary that forgot `last` entirely. That is tiny, but it chips away at trust and legibility.

This rev keeps the semantics boring and obvious:

- `last` is the default replay slot
- idle inspection should say so
- idle playback should say so too
- prompt previews and runtime failures should share the same tiny wording

## Verification

Focused tests pin both the prompt rows and the shared helper output.
