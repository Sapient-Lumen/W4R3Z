# Revision REV0320 — 2026-03-18

## Summary

Added an event-shaped recorder guard lane for `vhk record-x11`, corrected the polling semantics behind generic `WaitForWindowEvent`, and documented the remaining geometry-refresh boundary honestly.

## Code

- added `--window-guard-mode state|event` to `vhk record-x11`
- segmented recordings can now keep the first segment as `WaitForWindow` and emit `WaitForWindowEvent(event=focus|title)` for later recorded transitions
- event guard mode now requires `--window-guard-scope active`
- generic polling-backed `WaitForWindowEvent` no longer invents an initial pseudo-event
- generic polling-backed `WaitForWindowEvent(event=title)` now supports active-window title changes
- geometry-only segment refreshes intentionally fall back to state guards

## Tests

- added recorder CLI tests for focus-event guards, title-event guards, and scope validation
- added polling event tests for true future focus waits and active-window title changes
- ran the focused recorder/window-event suite plus adjacent coord/window tests

## Docs

- updated `README.md`
- updated `docs/RECORDER_X11.md`
- updated `docs/WINDOW_EVENT_WAITS.md`
- updated `docs/SPECS.md`
- updated `docs/ISSUES_2026Q1.md`
- added `docs/RESEARCH_2026.03.18_EVENT_GUARDS_AND_POLLING_TRUTH.md`
