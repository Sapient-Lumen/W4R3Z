# Rev691 - macro main doc sync

Date: 2026-03-28

## Why

Recent macro work made the live editor much more explicit about the default `last` slot:

- bare `macro play` / `run` rows now name the default-slot playback outcome
- bare `macro record` / `rec` / `start` rows now name the default-slot recording outcome
- exact `last` rows wear `[default]`
- empty default-slot playback stays inspectable as `0 steps [default] · default slot empty`
- exact `macro play|run NAME COUNT` rows now validate the count token before later slot-state fallback

The narrower rev docs already reflected that, but the main repo guidance still had a few older examples like `idle · default=last · 0 macros` or `last (default slot)` in summary sections.

## What changed

- refreshed the rev564/rev565 historical note blocks to use the current default-slot dialect
- updated the main macro summary bullets in:
  - `docs/64-editor-prompt-completion.md`
  - `docs/66-editor-micromax-commands.md`
- refreshed copied overview notes in:
  - `README.md`
  - `TODO.md`
  - `docs/01-llm-start-here.md`
  - `docs/02-repo-map.md`
  - `docs/43-worklist.md`

## Result

Future humans and LLMs now see the same macro language in the repo's main guidance that the editor itself already uses:

- `idle · default=last (0 steps) · default slot empty · 0 macros`
- `idle · default=last (0 steps) · record default slot · 0 macros`
- `last [default] · record default slot`
- `last (1 step) [default] · play default slot`
- count rows fail first on `count must be an int` / `count must be > 0` before later slot-state fallbacks
