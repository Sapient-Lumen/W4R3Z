# Cursor position (GetCursorPos / vhk cursorpos)

Global cursor position is easy on X11 and intentionally difficult on Wayland.
VHK therefore treats cursor coordinates as **best-effort** and relies on
compositor/tool-specific helpers when present.

## CLI

```bash
vhk cursorpos --json
vhk cursorpos --no-json   # prints: "x y"
vhk cursorpos --copy      # copies "x,y" to the clipboard
```

## Macro step

```yaml
- type: GetCursorPos
  out_x: cursor_x
  out_y: cursor_y
  out_backend: cursorpos_backend
```

Defaults:
- `cursor_x`, `cursor_y`, `cursorpos_backend`

## Backends

### X11

Uses `xdotool getmouselocation --shell`.

### Wayland (Hyprland)

Uses `hyprctl cursorpos` which returns the cursor coordinates in the global
layout coordinate space.

### Wayland (wlroots compositors)

Uses [`wl-find-cursor`](https://github.com/cjacker/wl-find-cursor) in `-p` mode.
This tool uses the layer-shell + virtual-pointer protocols, so it **does not**
work on compositors that intentionally avoid those protocols (notably GNOME).

If your compositor lacks virtual pointer support but supports layer-shell,
`wl-find-cursor` supports an emulation workaround via `-e`.
VHK exposes this via the `VHK_WL_FIND_CURSOR_EMULATE` environment variable:

```bash
export VHK_WL_FIND_CURSOR_EMULATE='ydotool mousemove 0 1'
vhk cursorpos
```

### Wayland (KDE Plasma / KWin)

When running on KDE Wayland, VHK will use `kdotool getmouselocation --shell`
when `kdotool` is installed.

`kdotool` is an xdotool-like helper that queries KWin via scripting + DBus.
It is best-effort (and slower than X11 polling), but it avoids the common
"Wayland has no global cursor position" dead-end.
