# Rev572 — truthful plain `showbindings` prompt row

## Why

Micromax already had the right nearby keymap-discovery truth:

- plain `showbindings` already defaulted to `active` after Enter
- `showbindings active` already reused the same reachable-binding inventory behind `whichkey`
- exact `showbindings MODE|active` rows were already truthful in prompt completion after rev571

But one small seam still lingered at the no-arg command entry point in the command bar:

- typing plain `showbindings` still fell back to generic exact-command metadata
- the prompt hid the default active binding count and sample winner even though Micromax already knew both before Enter

## What changed

- added shared `_prompt_showbindings_command_row(...)`
- exact command completion for plain `showbindings` now reuses `_prompt_showbindings_mode_row('')`
- the command row now previews the default active binding inventory before Enter

## Examples

- `showbindings` can now preview `default=active bindings=1 · g@goto!->command:showstatus (show portable statusline summary)`
- empty active inventory now previews `default=active bindings=0 · global bindings=0`

## Why this shape

This keeps the no-arg command row aligned with the command’s real default semantics instead of inventing a second explanation dialect. The change stays deliberately narrow: binding resolution and execution do not change, only the pre-Enter row stops hiding the same active inventory Micromax already trusts after Enter.

Future humans and LLMs can now see that plain `showbindings` means “inspect the current reachable keymap right now” without needing to remember the implicit `active` default or press Enter first.

## Checks

Focused coverage now pins:

- plain `showbindings` command rows previewing populated active inventory
- plain `showbindings` command rows previewing empty active inventory
- existing exact `showbindings active` / `showbindings MODE` prompt rows staying intact
