# Rev610 — keep root `showkeymode` truthful before and after Enter

## Why

Micromax already had the right tiny keymode state nearby:

- `keymode_inventory_rows()` / `ed.keymode-inventory-rows` already exposed the live active/known keymode register
- plain `showkeymodes` already previewed that same summary before Enter
- exact `showkeymode NAME` rows already kept missing-keymode truth in prompt completion
- raw root `showhook` had just learned not to jump straight from Enter to a generic usage line

But one small trust/flow seam still lingered in the exact keymode-inspection loop:

- typing plain `showkeymode` still showed generic command metadata before Enter
- running raw `showkeymode` still went straight to `usage: showkeymode MODE` after Enter

That made the root exact keymode inspector slightly less truthful than the nearby broad `showkeymodes` surface and less consistent than the adjacent root-inspector cleanup pattern.

## What changed

- added shared `_keymode_inventory_preview_summary()` so root keymode summary text lives on one tiny substrate
- plain `showkeymodes` and plain `showkeymode` command-bar rows now reuse that summary instead of generic provenance text
- raw runtime `showkeymode` now prints `showkeymode: ...` before its existing usage hint
- focused prompt/runtime tests pin a populated root-keymode state with exact sample-binding truth

## Example state

- populated root preview/runtime summary: `active goto!, nav · known=3 · goto g->command:showstatus`

## Why this shape

This keeps the change deliberately small. `showkeymode` is still an exact inspector that expects one mode name, and `showkeymodes` still owns the broader browse surface. But the root entry point no longer has to pretend it knows nothing about the live keymode stack it is asking the user to inspect.

Future humans and LLMs can now see whether Micromax is in `global`, sitting inside one transient mode, or stacked in multiple durable modes without pressing through a generic usage wall first.

## Checks

Focused coverage now pins:

- plain `showkeymode` command rows with populated root-keymode inventory truth
- raw `showkeymode` runtime feedback with populated root-keymode summary then usage
