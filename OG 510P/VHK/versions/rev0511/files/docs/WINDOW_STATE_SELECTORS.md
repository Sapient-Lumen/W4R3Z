# Window-state selectors

VHK now lets `I3WindowSelector` match best-effort window state, not only
title/class/workspace metadata. This is the runtime follow-through for the
window-state shape documented elsewhere in the repo.

## Supported selector fields

When the active backend exposes them honestly, selectors may use:

- `visible`
- `fullscreen`
- `fullscreen_mode`
- `floating`
- `sticky`
- `minimized`
- `hidden`
- `mapped`
- `pinned`

## Where they work

These selectors are used by:

- `WaitForWindow`
- `WaitForWindowVanish`
- `GetWindowList(selector=...)`
- runtime-side selector checks such as watcher `require_window` gates

## Example

```yaml
- type: WaitForWindow
  selector:
    class: mpv
    visible: true
    floating: true
    fullscreen: false
  timeout_ms: 5000
```

```yaml
- type: GetWindowList
  selector:
    pinned: true
    visible: true
  out_var: pinned_windows
```

## Portability stance

This is a **runtime** selector surface, not a promise that generated WM config
can express the same thing.

- sway/i3 runtime matching can use tree-native state like `visible`,
  `floating`, `sticky`, and `fullscreen_mode`
- Hyprland runtime matching can use client state like `mapped`, `hidden`,
  `floating`, `pinned`, and fullscreen-related fields
- X11 runtime matching can use EWMH-derived `fullscreen`, `sticky`, and
  minimized semantics
- exported WM config snippets remain conservative and only claim criteria the
  target WM really supports

That split is intentional: VHK should be richer at runtime than it is willing to
pretend in static config exporters.
