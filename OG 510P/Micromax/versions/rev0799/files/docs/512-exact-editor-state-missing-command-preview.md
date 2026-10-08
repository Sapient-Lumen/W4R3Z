# Rev570 — truthful missing-target rows for exact editor-state inspectors

## Why

Micromax already had the important nearby exact-inspection behavior after Enter:

- `showoption NAME` already failed as `showoption: no such option: NAME`
- `showbuffer NAME` already failed as `showbuffer: no such buffer: NAME`
- `showmark NAME` already failed as `showmark: no such mark: NAME`
- `showjump INDEX|#N` already failed as `showjump: no such jump: QUERY`
- `showkeymode MODE` already failed as `showkeymode: no such keymode: MODE`
- `showkey KEY` already failed as `showkey: no such binding: KEY`

And for known targets, prompt completion already reused the same tiny exact metadata rows humans trust after Enter.

But one small trust seam still lingered across this adjacent family: completion only surfaced known names or visible slots. When a user typed an unmatched exact target, the command bar dropped that token instead of saying what Micromax already knew would fail.

## What changed

- `_prompt_exact_option_row(...)` now gives exact `showoption NAME` rows one shared place to say `missing option · no such option`
- `_prompt_exact_buffer_row(...)` now has strict missing-target mode and can say `missing buffer · no such buffer`
- `_prompt_exact_mark_row(...)` now has strict missing-target mode and can say `missing mark · no such mark`
- `_prompt_exact_jump_row(...)` now has strict missing-target mode and can say `missing jump · no such jump`
- `_prompt_keymode_row(...)` now has strict missing-target mode and can say `missing keymode · no such keymode`
- `_prompt_binding_row(...)` now has strict missing-target mode and can say `missing binding · no such binding`
- exact token completion for `showoption`, `showbuffer`, `showmark`, `showjump`, `showkeymode`, and `showkey` now preserves one unmatched typed token long enough to render that truthful row

## Why this shape

This keeps pre-Enter inspection aligned with the same plain miss feedback Micromax already trusted after Enter. The change stays deliberately narrow: known exact rows are unchanged, command semantics are unchanged, and only unmatched exact targets stop disappearing from the prompt.

Future humans and LLMs can now type a precise option/buffer/mark/jump/keymode/binding guess and see whether Micromax thinks that target exists before submitting the command.

## Checks

Focused prompt-completion coverage now pins:

- preserved exact typed-token completion for `showoption`, `showbuffer`, `showmark`, `showjump`, `showkeymode`, and `showkey`
- missing-target rows for all six commands
- existing exact metadata rows for known options/buffers/marks/jumps/keymodes/bindings remain unchanged
