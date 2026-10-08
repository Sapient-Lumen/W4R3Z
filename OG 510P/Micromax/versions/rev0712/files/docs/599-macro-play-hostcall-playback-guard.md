# Rev658 - direct macro replay keeps playback blocker truth too

## What changed

- `Editor.play_macro(...)` now reports the active-playback blocker instead of silently returning `False`
- the portable `ed.macro-play` hostcall inherits that same message because it already routes through `play_macro(...)`
- new editor-owned `_macro_runtime_subcommand_summary(...)` centralizes the tiny blocker wording shared by direct replay and command-line macro failures
- `command_dispatcher._macro_subcommand_runtime_summary(...)` now delegates to that editor-owned helper instead of rebuilding its own copy

## Why it matters

- command-line `macro play` / `run` already said `wait for playback` during active playback
- exact prompt rows, slot rows, count rows, and blocked menus already exposed that same blocker before Enter
- but direct headless replay through `play_macro(...)` / `ed.macro-play` could still fail silently while the visible command surface was already telling the truth

## Guardrail

- active-playback direct replay now reports `macro play: playing · NAME (N step[s]) · wait for playback`
- the same shared helper also continues to cover the earlier recording-blocked direct replay path
- focused tests pin both direct method and portable hostcall behavior so future command/host-boundary cleanup cannot drift
