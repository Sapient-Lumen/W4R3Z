# Revision 0323 — geometry event guards and active-window rect truth

## Summary

Revision 0323 closes the next recorder/runtime seam. `WaitForWindowEvent` now has a first-class `geometry` kind, generic backends can surface best-effort active-window geometry changes, and segmented `record-x11 --window-guard-mode event` output can now preserve geometry-refresh boundaries as `WaitForWindowEvent(event=geometry, ...)` instead of flattening them back into state waits.

## Code changes

- `src/vhk/core/models.py`
  - added `geometry` to `WaitForWindowEvent.event`
- `src/vhk/system/wm_events.py`
  - generic polling fallback now supports active-window `geometry` events
  - geometry polling emits `geometry_reason` plus `old_geometry` context
  - i3/sway window events now map geometry-affecting changes (`move`, `floating`, `fullscreen_mode`) into `geometry`
  - event window snapshots now preserve geometry for i3/sway and Hyprland payloads when that data is available
- `src/vhk/cli.py`
  - recorder event-guard mode can now emit `WaitForWindowEvent(event=geometry, ...)` for geometry-refresh segments
- `src/vhk/system/doctor.py`
  - window-contract support now advertises `geometry` event-kind support on X11, i3/sway, Hyprland, and KWin lanes

## Tests

- added a polling test for active-window geometry events
- added a runner payload test for `WaitForWindowEvent(event=geometry)`
- added a recorder test proving geometry-refresh segments can emit geometry event guards
- updated window-contract capability expectations for the new event kind

## Docs

- updated `README.md`
- updated `docs/RECORDER_X11.md`
- updated `docs/WINDOW_EVENT_WAITS.md`
- updated `docs/SPECS.md`
- updated `docs/ISSUES_2026Q1.md`
- added `docs/RESEARCH_2026.03.18_GEOMETRY_EVENT_GUARDS_AND_RECT_TRUTH.md`
