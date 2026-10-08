# Window introspection lane

VHK now treats window introspection as a **runtime primitive**, not only
as a CLI/debugging surface. The focused-window lane lives in `GetActiveWindow`;
the open-window lane lives in `GetWindowList` and the companion
`docs/WINDOW_ENUMERATION.md`.

## Why this matters

AHK users rely heavily on Window Spy / WinGet / active-window checks to scope
macros safely. Linux has similar building blocks, but they are not one uniform
API:

- X11: `xdotool`, `xprop`, `wmutils`
- sway/i3: tree / IPC data, often keyed by `app_id` for native Wayland windows
- Hyprland: `hyprctl activewindow`
- KDE Wayland: `kdotool` via KWin scripting

That means VHK should expose a stable authoring shape while remaining honest
about backend differences.

## Runtime step

```yaml
- type: GetActiveWindow
  include_geometry: true

- type: If
  condition: "window_class == 'Alacritty' and window.geometry is not None"
  then_steps:
    - type: Log
      message: "Terminal active at ${window.geometry.rect.x},${window.geometry.rect.y}"
```

Default outputs intentionally match `window_watchers`:

- `window`: active-window info dict
- `wm`: compositor/backend label
- `window_title`
- `window_class` (`class` or fallback `app_id`)
- `workspace`
- `urgent`
- best-effort state fields such as `visible`, `fullscreen`, `floating`,
  `sticky`, or `minimized` when the backend exposes them

## Geometry stance

Geometry is attached under `window.geometry` on a best-effort basis. That is an
honest Linux-native compromise:

- some desktops expose enough data cheaply
- some only expose metadata but not robust client/outer geometry
- some Wayland flows still need compositor-specific helpers

Use `require_geometry: true` only when the macro truly depends on exact window
rectangles.


## Process-aware selectors

VHK now keeps AHK-style process scoping close to the window lane instead of
forcing authors to shell out for it.

- active-window snapshots may include `pid` and `process_name`
- `GetActiveWindow` can emit `window_pid` and `window_process`
- `I3WindowSelector(pid=...)` works for runtime matching
- generated sway criteria may include `pid`, but generated i3 criteria stay more
  conservative because i3 config criteria are not documented the same way

That lets macros ask questions like “is the focused Firefox window actually the
`firefox` process I care about?” without pretending every compositor exports the
same window/process contract.
