# Rev625 - `helpfollow` command preview

## Why

`showhelplink` already made the current docs-link target inspectable before Enter,
but the action people usually take from that same state was still quieter.
Typing plain `helpfollow` in the command bar still showed a generic command row
right before execution even though Micromax already knew the exact current link
or the typed blockers (`not in a docs buffer`, `no link under cursor`).

## What changed

- plain `helpfollow` command-bar completion now reuses the shared
  `_current_help_link_preview_summary()` helper
- the no-arg action row can now preview the exact current link target before
  Enter instead of hiding that state behind generic command metadata
- the same tiny typed blockers stay visible when no docs buffer or no current
  link exists

## Why it matters

This is a small flow/trust cleanup. The command bar should help you decide
whether `helpfollow` will do the thing you expect before you press Enter,
especially in the same docs buffer loop where `showhelplink` already tells that
truth.
