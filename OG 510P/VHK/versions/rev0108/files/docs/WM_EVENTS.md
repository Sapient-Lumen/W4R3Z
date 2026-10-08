# WM events

VHK supports multiple desktop stacks and window managers.

`vhk wm-events` is a small debugging helper that lets you see what your
compositor is emitting.

## Examples

Stream focus and title events with window info attached:

```bash
vhk wm-events --kind focus --kind title --with-window
```

JSON lines (useful for piping into `jq`):

```bash
vhk wm-events --kind focus --kind urgent --kind new --kind close --with-window --json
```

Hyprland custom events (see `hyprctl dispatch event`):

```bash
vhk wm-events --kind custom --json
```

## Notes

- On i3/sway, VHK uses IPC subscribe events.
- On Hyprland, VHK reads socket2 events and reconnects if the socket drops.
  `closewindow` only includes a window address, so VHK keeps a small best-effort
  address→metadata cache from earlier events to attach `{class,title,workspace}`
  when possible.
- On unknown compositors, VHK can only provide `focus` events (other kinds require compositor IPC) by polling the
  active window.
