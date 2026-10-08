# Rev527 — `jumppick` command-bar completion reuses exact jump rows too

## What changed

`jumppick N|#N` was already a valid direct way to target one visible jumplist slot,
and rev526 had already aligned the live picker itself with the visible `#N`
dialect. But the command bar still had one tiny blind spot before execution:
`showjump` completion could already preview one exact jump slot with
lane/depth/buffer/position/preview metadata, while `jumppick` completion offered
no direct slot candidates or exact row preview at all.

Rev527 keeps that follow-up deliberately small:

- add one shared `_prompt_exact_jump_row(...)` helper for exact jump-slot
  completion rows
- reuse that helper for existing `showjump INDEX|#N` command-bar completion
- teach `jumppick INDEX|#N` command-bar completion to offer the same visible slot
  candidates and exact row metadata
- keep the visible dialect aligned: bare `N` candidates appear for bare numeric
  prefixes, and `#N` candidates appear when the typed prefix itself starts with
  `#`

## Why it matters

This is a tiny flow/trust fix.

If Micromax already accepts `jumppick #3`, the command bar should not force
humans or future LLMs to either remember what `#3` means from another surface or
press Enter blind. One small exact row is enough:

- lane (`current` / `back` / `forward`)
- depth inside that lane
- buffer name
- cursor position
- preview text

That keeps the direct command-bar path aligned with the already-trusted exact
inspection path behind `showjump`.

## Tests

Focused prompt-completion tests now pin both direct slot forms:

- `jumppick 1` completion rows reuse exact jump metadata
- `jumppick #1` completion rows reuse the same metadata while keeping the
  visible hash-prefixed dialect

## Follow-up shape

The jumplist surface is now more coherent across five tiny adjacent scales:

- `jumps` — flat register
- `showjump INDEX|#N` — one exact side-effect-free row
- `showjumpgroups [QUERY]` — broad grouped summary rows
- `jumppick [QUERY]` live prompt — grouped browse/submit path with visible `#N`
- `jumppick INDEX|#N` command-bar completion — exact direct-slot preview before
  submit

That is enough structure for humans, future UIs, and future LLMs without making
jumplist state larger or less inspectable.
