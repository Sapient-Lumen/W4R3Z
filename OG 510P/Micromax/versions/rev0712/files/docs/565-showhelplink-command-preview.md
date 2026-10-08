# Rev624 — `showhelplink` command preview tells the truth

## Why

`showhelplink` already had one exact runtime answer after Enter through the same
current-link detail row that powers scripts and future UIs. But plain
`showhelplink` still looked generic inside command-bar completion right before
execution, even though the editor already knew whether the cursor was outside a
help buffer, over plain prose, or inside one exact docs link.

That gap is small, but it hurts trust at exactly the moment people are checking
what will happen next.

## What changed

- added `_current_help_link_preview_summary()` as one tiny shared current-link
  witness
- plain `showhelplink` command-bar completion now reuses that summary instead of
  generic command metadata
- the preview stays typed across all three real states:
  - resolved current link
  - `no link under cursor`
  - `not in a docs buffer`

## Why this shape

The change stays deliberately small:

- no new docs parser path
- no new row schema
- no behavior change after Enter
- one helper reused by the exact command row only

That keeps the editor headless-first and easy to reason about while making the
command bar more honest.

## Focused checks

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showhelplink_command_previews_current_link`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showhelplink_command_previews_typed_blocker`
- `tests/test_editor_helplinkpick.py::test_help_link_detail_row_and_showhelplink_are_explicit`
