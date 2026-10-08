# Rev609 — keep root `showhook` truthful before and after Enter

## Why

Micromax already had the right tiny hook state nearby:

- `hook_summary_rows()` / `ed.hook-summary-rows` already exposed the live hook namespace as one small counted register
- plain `showhooks` already previewed that same summary before Enter
- exact `showhook NAME` rows already kept missing-hook truth in prompt completion after rev510
- raw root `showplugin` had just learned not to jump straight from Enter to a generic usage line

But one small trust seam still lingered in the exact hook-inspection loop:

- typing plain `showhook` still showed generic command metadata before Enter
- running raw `showhook` still went straight to `usage: showhook NAME` after Enter

That made the root exact hook inspector slightly less truthful than the nearby broad `showhooks` surface and less consistent than the adjacent root `showplugin` cleanup.

## What changed

- added shared `_hook_inventory_preview_summary()` so root hook summary text lives on one tiny substrate
- plain `showhook` command-bar completion now reuses that summary instead of generic provenance text
- raw runtime `showhook` now prints `showhook: ...` before its existing usage hint
- focused prompt/runtime tests pin both populated and empty root-hook states

## Example states

- populated root preview/runtime summary: `7 hooks · 1 with handlers · ed.test.alpha: 1 handler (e.g. h1#cfg)`
- fresh editor root preview/runtime summary: `5 hooks · 0 with handlers · ed.on-action: 0 handlers`

## Why this shape

This keeps the change deliberately small. `showhook` is still an exact inspector that expects one name, and `showhooks` still owns the broader browse surface. But the root entry point no longer has to pretend it knows nothing about the namespace it is asking the user to inspect.

Future humans and LLMs can now see whether the hook system is populated, empty-but-real, or merely built-in-only without pressing through a generic usage wall first.

## Checks

Focused coverage now pins:

- plain `showhook` command rows with populated root-hook inventory truth
- plain `showhook` command rows with built-in-only root-hook truth
- raw `showhook` runtime feedback with populated root-hook summary then usage
- raw `showhook` runtime feedback with built-in-only root-hook summary then usage
