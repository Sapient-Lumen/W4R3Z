# Window at cursor / MouseGetPos-style introspection

`GetWindowAtCursor` answers a question that AHK users lean on constantly:

> what window is the mouse currently over?

VHK now exposes that directly inside macros and through the CLI sibling
`vhk window-at-cursor`.

## Runtime step

```yaml
- type: GetWindowAtCursor
  include_geometry: true
  require_window: false
```

This step returns:

- `window`: best-effort top-level window snapshot or `null`
- `window_found`: whether VHK identified a window under the pointer
- `wm`: detected backend/compositor family
- `cursor_x`, `cursor_y`: global pointer position
- `cursorpos_backend`: helper used for the pointer probe

Convenience vars can also be emitted:

- `window_title`
- `window_class`
- `workspace`
- `window_focused`

The returned `window` object also reuses the best-effort state vocabulary from
the focused/list lanes (`visible`, `fullscreen`, `floating`, `sticky`,
`minimized`, `mapped`, `hidden`) when those fields are available.

## Why this is Linux-native instead of pretending to be universal

There is no single cross-desktop Linux API for “give me the exact top-level
window under the pointer.” VHK therefore uses the most honest lane available in
each environment:

- **X11**: prefers `xdotool getmouselocation --shell` and the reported `WINDOW` id
- **KDE Wayland**: prefers `kdotool getmouselocation getwindowid`
- **i3 / sway / Hyprland**: uses cursor position plus compositor window geometry

That means `GetWindowAtCursor` is strongest as an introspection and routing
primitive, not as a promise of perfect child-widget hit testing.

## Use cases

- build hover-sensitive macros without forcing focus first
- inspect palette overlays and chooser windows
- branch on the window under the pointer before injecting input
- reproduce the “window under mouse” side of AHK Window Spy / MouseGetPos flows
