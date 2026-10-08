# Rev580 — empty active-binding previews keep one visible keymode witness

## Why

Micromax already had the right tiny state underneath plain `showbindings` and
plain `whichkey`:

- `available_binding_inventory_rows()` / `ed.available-binding-inventory-rows`
  already exposed the reachable binding register when bindings existed
- `keymode_inventory_rows()` / `ed.keymode-inventory-rows` already exposed the
  ordered visible active/known keymode stack
- `keymode_detail_row(NAME)` / `ed.keymode-detail-row` already exposed one exact
  keymode with binding-count truth
- rev572 and rev573 had already taught the no-arg `showbindings` / `whichkey`
  command rows to reuse the shared active-binding preview path

But one tiny seam still lingered in the safest startup case. When the active
keymode inventory was visible yet the reachable binding inventory was empty, the
shared preview path ended with generic `show bindings` and threw away the first
visible active-mode witness Micromax already knew.

## What changed

- added `_active_keymode_binding_witness()`
- the helper reuses `keymode_inventory_rows()` plus `keymode_detail_row(NAME)`
  to keep one tiny `MODE bindings=N` witness for the current active keymode
  stack
- `_prompt_showbindings_mode_row(...)` now falls back to that witness whenever
  the reachable active-binding inventory is empty
- the no-arg command rows for both commands stay intentionally small:
  - `default=active bindings=1 · g@goto!->command:showstatus (...)`
  - `default=active bindings=0 · global bindings=0`
  - `active bindings=0 · global bindings=0`

## Why this shape

The broad active-binding entry points should stay calm and concrete even in a
fresh editor with no custom bindings installed yet. Showing the visible active
mode in that all-empty case keeps the preview aligned with the same exact
keymode row Micromax already trusts elsewhere, without widening the host
boundary or inventing a second active-keymap snapshot path.

Future humans and LLMs can see that the active binding inventory is not just
“empty somehow” but exactly which visible mode currently anchors that empty
state.

## Checks

Focused prompt-completion coverage now pins:

- populated `showbindings` and `whichkey` command-row previews with live active
  binding truth
- empty active-inventory previews for both commands with the first visible
  active keymode witness preserved
