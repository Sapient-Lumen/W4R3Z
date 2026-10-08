# Rev697 - macro preview sample helper

## What changed

- added `Editor._macro_inventory_preview_sample(...)`
- reused it in macro root, idle-default, status, and showmacro preview summaries
- kept visible prompt/runtime wording stable while removing copy-pasted sample-picking loops

## Why

Recent macro cleanup made several tiny summaries smarter:

- playback roots stop echoing the currently live macro as their own `e.g.` sample
- status rows prefer another saved clue like `last (N step[s]) [default]`
- idle default-slot summaries prefer a non-`last` sample when one exists

Those choices were all good, but the code that picked the sample had started to spread across several nearby helpers. That made the archive harder to trust because another small wording tweak could easily land in one path and miss two others.

`_macro_inventory_preview_sample(...)` makes the policy explicit:

- start from macro inventory rows
- skip any requested names
- return the first prompt-facing inventory entry
- preserve the existing `[default]` badge policy through `_macro_inventory_preview_entry_from_row(...)`

## Directly pinned

With saved `demo` and `last`, the helper now guarantees:

- skipping `demo` returns `last (1 step) [default]`
- skipping `last` returns `demo (1 step)`
- skipping both returns an empty sample

## Trust/taste/flow impact

This is mostly a trust and archive-maintenance win. The editor surface does not grow, but future changes to macro sample wording now have one small place to update instead of several half-neighboring loops.
