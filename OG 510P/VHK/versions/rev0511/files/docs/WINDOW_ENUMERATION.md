# Window enumeration lane

`GetActiveWindow` answers “what is focused right now?”
`GetWindowList` answers “what windows currently exist?”

That second question matters for:
- AHK-style `WinGet` / `WinGetList` workflows
- ad-hoc switchers and pickers
- diagnostics and support capture
- macros that need to filter or count windows before acting

## Runtime step

```yaml
- type: GetWindowList
  include_geometry: true

- type: If
  condition: "window_count >= 2 and any(w.class == 'Firefox' for w in windows)"
  then_steps:
    - type: Log
      message: "Firefox is open, alongside ${window_count} total windows"
```

## Output shape

`GetWindowList` returns:
- `windows`: list of watcher-style window dicts
- `window_count`: count of returned rows
- `wm`: backend label

Each row aims to reuse the same vocabulary as `GetActiveWindow` where possible:
- `id`
- `pid`
- `process_name`
- `class` / `app_id`
- `title`
- `workspace`
- `focused`
- best-effort state fields such as `visible`, `fullscreen`, `floating`,
  `sticky`, `minimized`, `mapped`, or `hidden`
- optional `geometry`

## Backend stance

VHK keeps this lane intentionally honest:
- i3/sway: IPC tree enumeration
- Hyprland: `hyprctl clients`
- X11: `wmctrl` / `xdotool` / EWMH helpers
- KDE Wayland: `kdotool search`

There is still no generic cross-desktop portal for open-window enumeration, so
VHK exposes one stable macro-facing shape while still routing through the real
backend-specific metadata sources underneath.


## Process-aware enumeration

`GetWindowList` is now intentionally useful for run-or-raise, app cycling, and
support capture workflows that care about *which process* owns a window, not
just what title it currently has.

That means row objects now try to expose:
- `pid`
- `process_name`

when the current backend can answer them cleanly. Selector matching also accepts
`pid`, which is especially useful on sway and in runtime-side matching for i3.
