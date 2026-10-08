# Rev571 — truthful `showbindings MODE|active` prompt rows

## Why

Micromax already had the right nearby keymap-discovery truth:

- `showbindings active` already reused the same reachable-binding inventory behind `whichkey`
- known `showbindings MODE` rows already reused exact keymode metadata in prompt completion
- the real `showbindings ghost` command path already answered unknown mode names as `0 binding(s)` instead of a hard error

But one small seam still lingered at exact mode entry in the command bar:

- the special `active` row still fell back to a generic placeholder instead of previewing the live reachable-binding inventory
- unmatched typed mode names disappeared from completion entirely, so the command bar could not preview the same `0 binding(s)` truth Micromax already knew after Enter

## What changed

- added shared `_prompt_showbindings_mode_row(...)`
- exact `showbindings active` rows now preview the live reachable-binding count plus one sample winner
- known exact `showbindings MODE` rows keep the same exact keymode metadata as before
- unmatched typed mode names now stay visible long enough to preview `0 bindings`

## Examples

- `showbindings active` can now preview `active bindings=1 · g@goto!->command:showstatus (show portable statusline summary)`
- `showbindings goto` keeps the existing exact keymode detail, such as `known bindings=1 · g->command:showstatus (show portable statusline summary)`
- `showbindings ghost` can now stay visible as `0 bindings · show bindings`

## Why this shape

This keeps prompt completion aligned with the exact `showbindings` semantics Micromax already trusts after Enter. The change stays deliberately narrow: binding resolution and command behavior do not change, only the pre-Enter row stops being generic or silently dropping unmatched typed mode names.

Future humans and LLMs can now see whether `showbindings` will inspect the current reachable map, one exact named mode, or simply return an empty binding set before they commit the command.

## Checks

Focused coverage now pins:

- exact `showbindings active` rows previewing reachable-binding inventory
- exact known `showbindings MODE` rows keeping their existing keymode metadata
- unmatched exact `showbindings MODE` completion preserving the typed token
- unmatched exact rows previewing `0 bindings`
