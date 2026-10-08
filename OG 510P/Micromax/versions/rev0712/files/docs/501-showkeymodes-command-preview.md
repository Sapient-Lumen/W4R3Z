Rev579 follow-up: the same `showkeymodes` command row now also keeps one visible empty mode witness in the default-global startup case, so the preview can say `active global · known=1 · global bindings=0` instead of collapsing back to counts-only; `docs/521-showkeymodes-empty-sample-preview.md` records the adjacent trust/taste reason.

# Rev559 — `showkeymodes` command-bar preview reuses live mode inventory

## Why

Micromax already had the right tiny state underneath plain `showkeymodes`:

- the command itself already printed active and known key modes after Enter
- `keymode_inventory_rows()` / `ed.keymode-inventory-rows` already exposed that
  same inventory headlessly
- `keymode_detail_row(NAME)` / `ed.keymode-detail-row` already exposed one exact
  mode with binding-count and sample-binding truth

But the exact no-arg command row still fell back to generic command metadata.
That meant the broadest keymode inspection entry point stayed less honest than
adjacent exact-mode completion rows.

## What changed

- added `_prompt_showkeymodes_command_row(...)`
- exact command completion for plain `showkeymodes` now reuses
  `keymode_inventory_rows()` plus one leading `keymode_detail_row(NAME)` sample
- the row stays intentionally small:
  - `active global · known=1`
  - `active goto!, nav · known=3 · goto g->command:showstatus`

## Why this shape

This keeps the command bar aligned with Micromax's existing headless-first
substrate instead of inventing one more bespoke summary path. Future humans and
LLMs can see the same live mode inventory before Enter that the command and
hostcall already trust after Enter.

## Checks

Focused prompt-completion coverage now pins:

- populated `showkeymodes` command-row preview with active/known/sample truth
- default-global `showkeymodes` command-row preview when no extra modes exist
