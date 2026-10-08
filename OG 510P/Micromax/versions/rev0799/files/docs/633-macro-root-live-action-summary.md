# Rev692 - macro root live action summary

Date: 2026-03-28

## Why

Micromax's macro subcommands had already become very explicit about what Enter would do next:

- `macro play` / `run` could say `default slot empty` or `play default slot`
- `macro record` / `rec` / `start` could say `record default slot` or `overwrite default slot on save`
- blocked subcommands already said `stop or cancel first` or `wait for playback`

But the umbrella `macro` root still flattened recording/playback back to a broader state summary.

## What changed

`_macro_root_preview_summary()` now keeps one tiny live action witness in those non-idle states too:

- recording: `recording · demo (1 step) · stop to save, cancel to discard · 0 macros`
- playback: `playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]`
- idle still centers the default slot: `idle · default=last (1 step) · 2 macros · e.g. demo (1 step)`

## Result

The plain `macro` root now matches the same trust-first pattern as the rest of the macro surface:

- idle tells you what the default slot is
- recording tells you how to finish or discard it
- playback tells you to wait instead of hinting at another immediate action
