# Rev573 — truthful plain `whichkey` prompt row

## Why

Micromax already had the right nearby keymap-discovery truth:

- `whichkey` already reused the same live reachable-binding inventory as `showbindings active` after Enter
- plain `showbindings` already previewed that default active inventory in command-bar completion after rev572
- exact `showbindings MODE|active` rows already previewed truthful active and mode-local keymap state before Enter

But one small seam still lingered at the no-arg `whichkey` entry point in the command bar:

- typing plain `whichkey` still fell back to generic exact-command metadata
- the prompt hid the active binding count and sample reachable winner even though Micromax already knew both before Enter

## What changed

- added shared `_prompt_whichkey_command_row(...)`
- exact command completion for plain `whichkey` now reuses `_prompt_showbindings_mode_row("active ")`
- the command row now previews the live active binding inventory before Enter

## Examples

- `whichkey` can now preview `active bindings=1 · g@goto!->command:showstatus (show portable statusline summary)`
- empty active inventory now previews `active bindings=0 · global bindings=0`

## Why this shape

This keeps the no-arg command row aligned with the command's real runtime semantics instead of inventing a second explanation dialect. The change stays deliberately narrow: key resolution and execution do not change, only the pre-Enter row stops hiding the same active reachable-key inventory Micromax already trusts after Enter.

Future humans and LLMs can now see that plain `whichkey` means “show what I can press right now” without needing to remember that it reuses the current active keymap or press Enter first.

## Checks

Focused coverage now pins:

- plain `whichkey` command rows previewing populated active inventory
- plain `whichkey` command rows previewing empty active inventory
- existing `showbindings` active/default command rows staying intact
