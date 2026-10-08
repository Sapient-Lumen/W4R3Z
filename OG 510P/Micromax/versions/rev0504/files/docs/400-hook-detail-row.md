# Rev458 — live hooks get one tiny exact detail row

## What changed

Micromax already had the right broad hook surfaces:

- plain `showhook NAME` exposed one hook's installed handler chain for humans
- `hook_inventory_rows(NAME)` / `ed.hook-inventory-rows` exposed that same ordered handler register to scripts and future UIs
- rev440 added `showhooks [QUERY]` / `hook_summary_rows(QUERY)` / `ed.hook-summary-rows` for the lighter broad live-namespace question

But one small inspectability seam still remained: there was still no official
side-effect-free exact first-stop answer to the adjacent question future
humans/LLMs often ask next:

> what is true about this one known hook right now?

Rev458 keeps the fix deliberately small:

- add `hook_detail_row(NAME)` in the editor core
- expose it as `ed.hook-detail-row`
- add a small convenience word, `hook-state`
- make `showhook` completion reuse that same exact metadata

## Row shape

`hook_detail_row(NAME)` / `ed.hook-detail-row` return:

```
[query name handler_count sample_handler|0 sample_detail|0 [file line col]|0] | 0
```

Where:

- `query` preserves the exact spelling the caller asked for
- `name` is the resolved hook name
- `handler_count` is the current installed handler count
- `sample_handler|0` reuses the first visible handler label (`handler` or `handler#group`) when one exists
- `sample_detail|0` reuses the first visible human-facing handler entry (for example `handler#group@file:line:col`) when one exists
- `[file line col]|0` points at the hook definition span itself

Examples:

- `['ed.pre-action', 'ed.pre-action', 0, 0, 0, ['<editor>', 1, 1]]`
- `['ed.test.alpha', 'ed.test.alpha', 1, 'h1#cfg', 'h1#cfg@<hook-test>:3:6', ['<hook-test>', 1, 1]]`

## Why this helps

This intentionally does **not** replace the fuller ordered handler inventory.
`hook_inventory_rows(NAME)` and core-language `hook-detail NAME` still remain
the right surfaces when a caller wants every installed handler.

The new exact row just answers the smaller first-stop question directly. That
keeps live hook inspection aligned with the newer exact rows Micromax already
added for buffers, marks, jumps, recent items, keymodes, options, and plugins:
one known live thing should have one tiny honest exact row before callers have
to reopen the broader inventory behind it.
