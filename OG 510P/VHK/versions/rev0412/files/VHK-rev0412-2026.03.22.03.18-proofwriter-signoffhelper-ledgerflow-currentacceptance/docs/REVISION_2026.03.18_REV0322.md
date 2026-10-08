# Revision 0322 — generic close/new polling and vanish parity

## Summary

Revision 0322 closes the next generic window-contract gap. VHK now has an honest X11/KWin fallback for `WaitForWindowVanish`, and the generic WM polling lane can emit best-effort `new` / `close` transitions by diffing window snapshots.

## Code changes

- `src/vhk/system/wm_events.py`
  - generic polling fallback now supports `new` / `close` by diffing `get_window_list_snapshot(...)` results
  - generic `new` / `close` events now carry row-shaped window payloads
- `src/vhk/core/runner.py`
  - `WaitForWindowVanish` now has a generic X11/KWin snapshot fallback instead of falling through to i3-only logic
- `src/vhk/system/doctor.py`
  - generic X11/KWin event-kind support now reflects focus/title plus best-effort new/close polling lanes

## Tests

- added generic polling tests for `new` and `close` WM events
- added a generic payload test for `WaitForWindowEvent(event=close)`
- added a generic X11 snapshot-fallback test for `WaitForWindowVanish`

## Docs

- updated `README.md`
- updated `docs/WINDOW_EVENT_WAITS.md`
- updated `docs/SPECS.md`
- updated `docs/ISSUES_2026Q1.md`
- added `docs/RESEARCH_2026.03.18_GENERIC_CLOSE_NEW_POLLING_AND_VANISH_TRUTH.md`
