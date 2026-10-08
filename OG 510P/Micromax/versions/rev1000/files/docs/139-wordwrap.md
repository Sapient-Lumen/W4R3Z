# Wordwrap (rev198)

Micromax already had a shared **softwrap** model (`docs/94-softwrap.md`): headless row rendering,
cursor-to-screen mapping, visual-row movement, and `top_subline` scrolling all agreed on one wrap
policy.

This revision adds a tiny companion option:

- `wordwrap` (bool, default `false`)

## Contract

When `softwrap=true` and `wordwrap=true`:

- wrapped rows prefer breaking at the final whitespace character that fits on the current row
- the chosen boundary is shared by `view_rows`, `cursor_view_pos`, visual-row Up/Down, and visual-row Home/End
- long unbroken tokens still fall back to hard wrapping by width
- continuation indent (`softwrap.contindent`) still applies exactly as before

When `softwrap=false`, `wordwrap` does nothing.

## Deliberate first-pass policy

This stays intentionally conservative:

- it is still a **visual** policy, not a formatter
- it keeps source characters visible instead of deleting break whitespace from the model
- it does not yet implement paragraph/list-aware hanging indents or Unicode display-width logic

## Why this shape

The editor already had one shared wrap model, so the smallest honest change was to improve the row
start calculation rather than grow a second renderer-only word-splitting path. That keeps future UIs,
future ports, and future LLMs all reading the same wrapped-row contract from the headless core.
