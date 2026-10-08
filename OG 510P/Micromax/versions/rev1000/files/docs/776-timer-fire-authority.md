# Rev817 — Timer fire authority and script pump containment

## Why this was risky

Timer cancellation already had runtime-registration provenance, and timer callbacks already re-entered their captured script/plugin context when they fired. The missing boundary was the explicit pump surface: `ed.pump-timers` could be called from script context and ask the editor to execute all due timer callbacks.

That made timers different from keybindings, hooks, macros, commands, marks, and prompts. A lower-authority script could not cancel a trusted timer, but it could still force a trusted due timer to run. The same call also reached editor maintenance work after the timer pass, including autosave checks, so the surface was too close to a “script tick the editor loop” primitive.

## What changed

New policy seam:

`src/micromax_editor/timer_policy.py`

New capability:

`cap.timer-fire` / `ed.timer-fire`

`Editor.pump_timers()` now filters due timers when called inside `script_context()`. Script-origin callers may pump timers they created themselves, but trusted/user or other-origin script/plugin timers remain pending unless `cap.timer-fire` is explicitly enabled.

The timer queue now supports an authority-aware due-pop path. Due-but-denied timers are preserved in the queue instead of being consumed or blocking same-origin due timers behind them.

Script-origin `ed.pump-timers` also no longer runs autosave maintenance. The normal UI/event-loop path still calls `pump_timers()` outside script context and keeps editor-owned autosave behavior.

## Semantics

- Trusted/interactive timer pumping remains unchanged.
- Script-origin timer pumping can run same-origin timers.
- Trusted/user timers remain pending when a script without `cap.timer-fire` pumps due timers.
- `cap.timer-fire` lets a script explicitly trigger protected timer callbacks, but the callback still executes with captured script/plugin authority where applicable; the capability does not make the script trusted.
- Script-origin timer pumping does not trigger autosave maintenance.

## Tests

New/updated focused coverage:

`tests/test_editor_timer_authority.py`

It covers protected timer refusal, same-origin timer pumping, explicit `cap.timer-fire`, capability registry advertisement, and the autosave-maintenance guard.

## Remaining risk

Timer inventory/read rows are still intentionally absent rather than authority-filtered. If a future UI exposes timer detail rows, it should use the same protected-register rule: same-origin rows are visible, trusted/user or other-origin rows require an explicit read capability or a deliberate public-design decision.
