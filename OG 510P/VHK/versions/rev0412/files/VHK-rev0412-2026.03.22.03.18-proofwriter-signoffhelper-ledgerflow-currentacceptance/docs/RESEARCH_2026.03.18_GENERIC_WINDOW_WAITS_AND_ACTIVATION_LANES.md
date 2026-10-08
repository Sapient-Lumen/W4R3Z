# Research note — generic window waits and activation lanes

## What we learned from adjacent tools

AutoHotkey keeps both `WinWait*` and `WinActivate` in the main window toolbox for
a reason: real desktop flows need both *state proof* and *foreground-taking*
operations.

The X11 toolchain says the same thing in Linux-native language. `xdotool`
separates `search --sync`/query-style flows from `windowactivate --sync`, and it
explicitly notes that `windowactivate` can switch desktops and wait until the
window is actually active.

KDE's `kdotool` tells a similar story for Plasma/KWin: it aims to be an
`xdotool`-like window-control tool, works on both KDE 5 and 6, and supports
`windowactivate` even though many other xdotool-style commands remain missing or
backend-limited.

## Implication for VHK

VHK already had richer recorder output for X11 than many Linux tools: stable or
exact selectors, window-context sidecars, segmented waits, and event-shaped
transitions. But that authoring work was at risk of outrunning runtime truth if
`WaitForWindow` or `FocusWindow` only behaved strongly on i3/sway or Hyprland.

That is exactly the kind of gap that makes a pseudoclone feel impressive in docs
and flaky in practice. If the recorder emits window-scoped guards for generic
X11, the runtime needs a real generic wait/focus lane too.

## Product decision

Revision 0321 therefore does three things:

- `WaitForWindow` now has a generic snapshot-polling fallback for X11/KWin-style
  backends instead of assuming i3 IPC semantics everywhere
- `FocusWindow` now routes through a backend-aware helper that can activate via
  i3/sway, Hyprland, `xdotool`/`wmctrl`, or `kdotool` depending on the host
- generic wait success plus `focus: true` now uses that same helper so window
  contracts stop diverging between explicit `FocusWindow` steps and implicit
  post-wait activation

## Why this stays honest

This does **not** claim universal Linux parity. The remaining truth is still
important:

- X11 has a strong helper-based activation lane
- KWin has a useful but partial `kdotool` lane
- Wayland remains compositor-specific rather than one uniform window-control API

That is precisely why VHK should make each lane explicit in code and docs rather
than hiding it behind one fake “Linux windows just work” abstraction.
