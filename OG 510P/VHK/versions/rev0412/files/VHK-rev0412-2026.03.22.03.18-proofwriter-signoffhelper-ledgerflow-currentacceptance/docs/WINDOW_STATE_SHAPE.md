# Window state shape

VHK's window lanes now try to carry a small **state vocabulary** in addition to
title/class/workspace metadata. This is intentionally best-effort and
backend-shaped, not a promise that every Linux desktop exposes the same window
state contract.

## Common fields

When available, `GetActiveWindow`, `GetWindowAtCursor`, and `GetWindowList` may
include:

- `visible`
- `fullscreen`
- `fullscreen_mode`
- `floating`
- `sticky`
- `minimized`
- `mapped`
- `hidden`
- `pinned`

## Current backend stance

- **sway / i3-like trees**: strong support for `visible`, `floating`,
  `fullscreen_mode`, and `sticky`
- **X11 / EWMH**: strong support for `fullscreen`, `sticky`, and
  `_NET_WM_STATE_HIDDEN`-style minimization semantics; `visible` is derived
  conservatively from current desktop + sticky + hidden state
- **Hyprland**: carries through `mapped`, `hidden`, `floating`, `pinned`, and
  fullscreen-related fields when `hyprctl` exposes them
- **KDE Wayland / KWin**: currently more limited; VHK keeps the state shape
  stable but does not pretend kdotool exposes every state equally cheaply

## Why this exists

AHK-style automation often needs more than “what window is this?” Real macros
also ask “is it actually visible?”, “is it fullscreen right now?”, or “is this
a floating popup instead of the main tiled window?”

Linux can answer those questions, but through different seams on different
backends. VHK therefore keeps the *shape* stable while remaining honest about
which fields are derived from which compositor/tool path.


See also `docs/WINDOW_STATE_SELECTORS.md` for how these fields participate in runtime selector matching.
