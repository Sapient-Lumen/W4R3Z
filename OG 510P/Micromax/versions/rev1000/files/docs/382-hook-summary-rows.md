# Rev440 — live hooks get one tiny broad summary row

## What changed

Micromax already had a good exact hook-inspection path:

- `showhook NAME` exposed one hook's installed handlers
- `hook_inventory_rows(NAME)` / `ed.hook-inventory-rows` exposed the same ordered handler rows to scripts and future UIs
- command-bar completion already knew visible hook names

But one small inspectability seam still remained: there was still no tiny first-stop register for the broader question future humans/LLMs usually ask before drilling into one hook:

> what hooks exist right now, how many handlers are attached, and which ones are active vs empty?

Rev440 keeps the follow-up deliberately small:

- add `hook_summary_rows(QUERY)` in the editor core
- expose it as `ed.hook-summary-rows`
- add plain `showhooks [QUERY]` for humans

## Row shape

`hook_summary_rows(QUERY)` / `ed.hook-summary-rows` return:

```
[name handler_count sample_handler|0 [file line col]|0]
```

Where:

- `name` is the hook name
- `handler_count` is the current installed handler count for that hook
- `sample_handler|0` reuses the first visible handler label (`handler` or `handler#group`) when one exists
- `[file line col]|0` points at the hook definition span itself

Examples:

- `['ed.pre-action', 0, 0, ['<editor>', 1, 1]]`
- `['ed.test.alpha', 1, 'h1#cfg', ['<hook-summary>', 1, 1]]`

The shape intentionally stays tiny. Exact handler chains still belong to `showhook NAME` / `ed.hook-inventory-rows`.

## Why this matters

This is a small trust/flow improvement for the live scripting surface.

Hooks are part of Micromax's eventual commands/keybindings/hooks/reload/debugging loop, but broad hook state was still oddly indirect: humans could inspect one hook at a time, and scripts could inspect one hook at a time, yet neither side had one named machine-facing register for the broad live hook surface.

The new summary rows and plain `showhooks [QUERY]` keep that first-stop answer inspectable without scraping completion output, probing hooks one by one, or rebuilding the live hook namespace from VM internals.

## Focused tests

- `tests/test_editor_showhook.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some other exact-only inspection surfaces still have no matching broad summary sibling
- hook search is now inspectable at both exact and broad-summary levels, but future work may still want grouped lifecycle-specific hook families once that remains worth the surface area
