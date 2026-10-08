# Matchbrace style (`matchbracestyle`)

Rev204 adds a tiny follow-up to the existing visible brace cue.

## What it does

- `matchbracestyle=underline` keeps the earlier bold+underline rendering for visible matching braces
- `matchbracestyle=highlight` uses a tiny bold+reverse highlight instead
- the same helper is reused for ordinary buffers and docs/help buffers

## What it does **not** do

- no new brace spans in headless editor state
- no syntax-aware brace matching
- no theme/color contract yet beyond ordinary curses attributes

## Why this size

Micromax already had the meaningful part of visible brace matching: one tiny shared visible-position calculation in the curses TUI. The remaining low-risk win was just a renderer choice, so `matchbracestyle` stays an option-shaped toggle instead of expanding into a broader highlight/theme subsystem.
