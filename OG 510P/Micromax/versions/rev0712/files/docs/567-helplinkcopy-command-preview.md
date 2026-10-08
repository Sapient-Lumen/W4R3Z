# Rev626 — keep plain `helplinkcopy` truthful before Enter

## What changed

Plain `helplinkcopy` command-bar completion now reuses the same tiny current-link
preview as `showhelplink` and `helpfollow`.

That means the no-arg exact command row can now show one of three truthful states
_before_ execution:

- `LABEL @topic [kind] -> TARGET @ line:col`
- `no link under cursor`
- `not in a docs buffer`

instead of falling back to generic command metadata.

## Why this matters

This is a trust/flow cleanup, not a feature expansion.

Micromax already knew the exact current docs-link target through
`help_link_detail_row()` and already used that truth after Enter through
`showhelplink`, `helpfollow`, and `helplinkcopy` itself. Leaving plain
`helplinkcopy` generic right before execution created one unnecessary blind spot in
an otherwise coherent current-link loop.

Making copy/follow/show share the same tiny preview keeps the docs browser more
legible and easier to trust:

- copy does not feel like a second-class path
- the command bar tells the same truth as the action it is about to run
- future UIs/LLMs get one calmer substrate for exact current-link state

## Tests

Focused prompt coverage pins both live-link and blocker previews:

- `test_prompt_complete_helplinkcopy_command_previews_current_link`
- `test_prompt_complete_helplinkcopy_command_previews_typed_blocker`
