# Rev659 - direct macro control blockers tell the truth too

## Why

Micromax had already made the visible macro command surface calm and truthful:
plain `macro record`, `macro stop`, and `macro cancel` previewed and reported
live blockers such as `stop or cancel first`, `wait for playback`, and
`not recording` instead of failing silently.

But one narrow headless seam remained underneath that honest surface.
Direct editor methods and their portable hostcalls still returned `False`
quietly on blocked paths:

- `Editor.start_macro(...)`
- `Editor.stop_macro()`
- `Editor.cancel_macro()`
- `ed.macro-record`
- `ed.macro-stop`
- `ed.macro-cancel`

That meant scripts, tests, and future plugin code could miss the same runtime
truth a user would already get from the command path.

## What changed

Blocked direct macro control now reuses the same shared runtime witness as the
command surface.

- `start_macro()` now reports the `record` blocker when recording or playback is
  already active.
- `stop_macro()` now reports the `stop` blocker when playback is active or no
  recording session exists.
- `cancel_macro()` now reports the `cancel` blocker under the same states.
- Portable hostcalls inherit that behavior automatically because they already
  call the editor methods directly.

Examples:

- `macro record: recording · demo (1 step) · stop or cancel first`
- `macro record: playing · demo (1 step) · wait for playback`
- `macro stop: idle · not recording`
- `macro cancel: playing · demo (1 step) · wait for playback`

## Tests

Focused coverage lives in `tests/test_editor_macros_named.py`:

- direct `start_macro()` and `ed.macro-record` reject recording and playback
  blockers with the shared witness
- direct `stop_macro()` / `cancel_macro()` and `ed.macro-stop` /
  `ed.macro-cancel` reject idle and playback blockers with the shared witness

## Result

Tiny direct macro control boundaries now fail just as truthfully as the command
surface. That keeps headless automation, hostcalls, future plugins, and human
expectations on one shared runtime dialect instead of letting one path go quiet
while another explains what happened.
