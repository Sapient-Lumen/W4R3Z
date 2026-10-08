# Revision REV0321 — 2026-03-18

## Summary

Extended the runtime window-contract lane so recorder-authored X11/KWin guards are backed by a real generic wait/focus path instead of depending on i3-only assumptions.

## Code

- added backend-aware `focus_window_matching(...)` helper in `vhk.system.active_window`
- `FocusWindow` now works through that shared helper instead of only an i3 focus command
- `WaitForWindow` now has a generic snapshot-polling fallback for non-i3/non-Hyprland backends
- `WaitForWindow(..., focus: true)` now uses the same shared activation helper on that generic path
- X11 activation prefers `xdotool windowactivate --sync` and can fall back to `wmctrl -ia`; KWin activation uses `kdotool windowactivate`; Hyprland and i3/sway keep their compositor-native paths

## Tests

- added focused unit tests for X11 and KWin window activation helpers
- added a runner test proving generic X11 `WaitForWindow` fallback + post-wait focus
- reran adjacent wait/window tests and compile checks

## Docs

- updated `README.md`
- updated `docs/PROJECT_FORMAT.md`
- updated `docs/RECORDER_X11.md`
- updated `docs/SPECS.md`
- updated `docs/ISSUES_2026Q1.md`
- added `docs/RESEARCH_2026.03.18_GENERIC_WINDOW_WAITS_AND_ACTIVATION_LANES.md`
