# Window process context

VHK's window-introspection lane now aims to support the same *kind* of
process-aware workflows that many AutoHotkey users rely on, while keeping the
Linux backend differences explicit.

## What is exposed

### `GetActiveWindow`

`GetActiveWindow` can now emit:

- `window` — full snapshot dict
- `window_pid` — best-effort owning process id
- `window_process` — best-effort process/executable name
- existing convenience vars like `window_title`, `window_class`, `workspace`

### `GetWindowAtCursor`

`GetWindowAtCursor` can now emit the same process-aware convenience vars for the
top-level window currently under the pointer.

### `GetWindowList`

`GetWindowList` row objects may now contain:

- `pid`
- `process_name`

when the current backend can supply them honestly.

## Selector support

`I3WindowSelector` now accepts:

```yaml
selector:
  class: Firefox
  pid: 4242
```

VHK uses that field in runtime-side matching and in sway-oriented criteria
generation. Generated i3 criteria stay more conservative.

## Backend stance

- **X11**: best-effort via `_NET_WM_PID` / helper tools; not every window will
  expose a usable pid.
- **sway/i3**: runtime tree metadata can expose pid-bearing nodes; sway config
  criteria explicitly document numeric `pid`.
- **Hyprland**: client metadata can expose pid/process context, but higher-rate
  polling should still avoid spamming `hyprctl`.
- **KDE Wayland**: process-aware context is possible through `kdotool`-backed
  window inspection, but remains a KWin-specific bridge.

## Why this matters

This makes several Linux-native automation patterns more direct:

- run-or-raise / focus-if-running flows
- app-scoped macros that need stronger identity than a volatile title
- support/debug capture that wants class + title + process context together
- safer multi-window targeting when one app opens many titles at once
