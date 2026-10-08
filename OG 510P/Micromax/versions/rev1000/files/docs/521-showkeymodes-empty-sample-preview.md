# Rev579 — `showkeymodes` empty previews keep one visible mode sample

## Why

Micromax already had the right tiny state underneath plain `showkeymodes`:

- `keymode_inventory_rows()` / `ed.keymode-inventory-rows` already exposed the
  ordered visible active/known keymode register
- `keymode_detail_row(NAME)` / `ed.keymode-detail-row` already exposed one exact
  mode with binding-count and sample-binding truth
- populated `showkeymodes` previews already reused that exact detail row when
  the leading visible mode had at least one binding

But one tiny seam still lingered in the safest startup case. When the visible
`global` mode existed but had `0` bindings, the no-arg command row collapsed
back to bare counts and threw away the first visible mode witness Micromax
already knew.

## What changed

- `_prompt_showkeymodes_command_row(...)` now keeps the first visible exact
  keymode row even when its binding count is `0`
- when no visible mode currently has any bindings, the no-arg command row now
  keeps that first mode witness instead of dropping back to counts-only
- the row stays intentionally small:
  - `active goto!, nav · known=3 · goto g->command:showstatus`
  - `active global · known=1 · global bindings=0`

## Why this shape

The broad keymode entry point should stay calm and concrete even in a fresh
editor with no custom bindings installed yet. Showing one visible mode name in
that all-empty case keeps the preview aligned with the same exact keymode row
Micromax already trusts elsewhere, without widening the host boundary or
inventing a second keymode snapshot path.

Future humans and LLMs can see that the live keymode inventory is not just
“global exists somehow” but exactly which visible mode currently anchors the
register and how empty it really is.

## Checks

Focused prompt-completion coverage now pins:

- populated `showkeymodes` command-row preview with active/known/sample-binding
  truth
- default-global `showkeymodes` command-row preview with the first visible empty
  mode sample preserved
