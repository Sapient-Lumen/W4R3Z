# Research note: geometry event guards and rect truth

## Why this revision happened

VHK had already become much more honest about window appearance, focus, title, and close/new transitions. But one recorder/runtime seam still showed up in practice: relative-coordinate authoring depends on window geometry, yet geometry refreshes were still forced back into plain state waits.

That was increasingly hard to justify after looking at the surrounding ecosystem:

- AutoHotkey keeps window waiting as a first-class surface and pairs it with Window Spy so geometry/title/class evidence can shape the script instead of hiding inside sleeps.
- i3 IPC documents more than just `new` / `close` / `focus` / `title`; window events also include `move`, `floating`, and `fullscreen_mode`, which are all meaningful geometry-adjacent transitions.
- `xdotool behave` only exposes a small X11 event set (`focus`, `blur`, mouse enter/leave/click), which is a useful reminder that generic X11 does **not** hand VHK a universal window-rect event stream.
- KWin’s scripting API does expose window geometry change signals such as `frameGeometryChanged`, but that is a compositor-specific scripting surface, not something VHK can claim generically through `kdotool` alone.

That combination suggests the right product rule:

- add an explicit `geometry` event kind
- map it to direct WM events when a backend actually exposes them
- otherwise expose it as best-effort active-window geometry polling instead of pretending Linux has one universal rect-event API

## What VHK now does

Revision 0323 follows exactly that rule.

- i3/sway can now map `WaitForWindowEvent(event=geometry)` onto window IPC changes that are geometry-adjacent (`move`, `floating`, `fullscreen_mode`)
- generic X11/KWin/other desktop lanes can emit best-effort geometry events by polling the active window snapshot and comparing rectangles between polls
- the polling payload now preserves:
  - the current window snapshot
  - the previous rectangle as `old_geometry`
  - a simple `geometry_reason` classification (`move`, `resize`, or generic `geometry`)
- segmented `record-x11 --window-guard-mode event` output can now preserve geometry-refresh segments with `WaitForWindowEvent(event=geometry, ...)`

## Remaining honesty boundary

This still does **not** mean VHK has solved universal compositor geometry events on Linux.

- generic geometry waits remain active-window and polling-backed
- KWin still lacks a first-class dedicated rect-event bridge in VHK itself
- Hyprland still has richer socket2 state than generic desktops, but VHK’s strongest portable geometry story there remains the active-window polling lane unless/until a dedicated rect-event bridge is added

That is acceptable because it preserves the important truth: geometry is now a first-class contract, but its strength still depends on the backend.
