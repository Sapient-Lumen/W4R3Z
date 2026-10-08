# Wayland support (sway, etc.)

VHK started as an **i3 + X11** automation tool, but the ecosystem around
Wayland has converged on a small set of reliable CLI building blocks. VHK uses
those when `settings.desktop_backend: wayland` (or when auto-detection sees a
Wayland session).

## Detection and overrides

Resolution order:

1. `settings.desktop_backend` in `project.yaml` (`auto|x11|wayland`)
2. `VHK_BACKEND` environment variable (`auto|x11|wayland`)
3. Heuristics: `XDG_SESSION_TYPE=wayland`, or `WAYLAND_DISPLAY` without `DISPLAY`

## Tooling by feature

### Screenshots

- X11: `maim` (preferred) or ImageMagick `import`
- Wayland: `grim` with optional `-g "<x>,<y> <w>x<h>"` region capture

`grim` is the standard Wayland-native screenshot tool. Its region format matches
`slurp` output, making them easy to combine. See the grim(1) man page for the
`-g` geometry format.

### Region selection

- X11: `slop` (select rectangle)
- Wayland: `slurp` (select rectangle)

`slurp`'s default output format is `%x,%y %wx%h` (e.g. `10,20 300x400`).

### Clipboard

- X11: `xclip` or `xsel`
- Wayland: `wl-copy` / `wl-paste` from `wl-clipboard`

### Input

- X11: `xdotool`
- Wayland keyboard: `wtype` (virtual keyboard)
- Wayland mouse/pointer: `ydotool` (uinput) **requires** `ydotoold` daemon

Notes:

- `wtype` supports key presses and typing but does **not** drive the pointer.
- `ydotool` is powerful (works on X11 and Wayland) but is more "system-level":
  it needs the daemon and permissions.

## i3 IPC on Wayland

If you're on sway, the IPC protocol is i3-compatible and the socket path is
exported in `SWAYSOCK` (and often `I3SOCK` for compatibility). VHK's socket
discovery checks both.
