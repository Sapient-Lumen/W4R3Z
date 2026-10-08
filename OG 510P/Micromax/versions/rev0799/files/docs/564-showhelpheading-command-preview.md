# Rev623 - `showhelpheading` command preview

## Goal

Keep the exact current-heading inspector truthful one step earlier.

## What changed

- plain `showhelpheading` in command-bar completion now reuses one shared
  `_current_help_heading_preview_summary()` helper
- the preview is intentionally typed and tiny:
  - `TITLE @topic [hN] [section ...] [#fragment] @ line:col` when the cursor is
    inside a resolved docs heading
  - `no heading under cursor` when the current docs buffer has no heading above
    the primary cursor yet
  - `not in a docs buffer` when the current buffer is not a docs/help page

## Why it matters

Micromax already knew the exact current docs heading after Enter through
`showhelpheading` and headlessly through
`current_help_heading_detail_row()` / `ed.help-current-heading-detail-row`.
Leaving the no-arg command-bar row generic made the command feel less reliable
at the exact moment a human or future LLM was deciding whether it was the right
inspection tool.

## Verification

Focused tests cover:

- live-heading prompt preview
- typed blocker preview outside docs
- context/archive manifest checks for the new handoff note
