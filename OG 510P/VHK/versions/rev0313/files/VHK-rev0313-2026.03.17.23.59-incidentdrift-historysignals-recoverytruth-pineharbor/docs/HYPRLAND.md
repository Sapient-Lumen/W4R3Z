# Hyprland integration

VHK can generate Hyprland `bind` lines from your project’s `bindings:`.

Hyprland keybinds are **comma-separated** and accidental trailing commas can turn into part of the argument.
If a bind doesn’t work, double-check the commas. The Hyprland wiki calls this out explicitly.

## Generate Hyprland binds

```bash
vhk gen-hyprland-config /path/to/project > ~/.config/hypr/vhk.conf
# then source it from your hyprland.conf, e.g.
# source = ~/.config/hypr/vhk.conf
```

Or use the generic command:

```bash
vhk gen-wm-config /path/to/project --wm hyprland --out ~/.config/hypr/vhk.conf
```

## Release trigger (`bindr`)

VHK generates `bindr` lines (trigger on **release**) to avoid triggering commands while the key is being held.
This mirrors the intent of i3’s recommended `bindsym --release` pattern.

## Context-sensitive binds (`when:`)

Hyprland doesn’t have i3-style `criteria` in bind lines.

When a binding specifies `when:`, VHK adds a portable guard:

- the bind remains global
- the invoked command gets `--require-window <selector-json>`
- VHK checks the active window before running the macro

This is useful for WMs that cannot scope binds per focused window.

## Pointer movement without ydotool

Hyprland exposes a built-in cursor mover:

```bash
hyprctl dispatch movecursor <x> <y>
```

VHK will use this for **absolute** mouse movement (e.g. `MouseMove(x=..., y=...)`,
`MouseClickAt`, `MouseDrag` endpoints) when `HYPRLAND_INSTANCE_SIGNATURE` and
`hyprctl` are available. This avoids the most common Wayland automation footgun
(`ydotoold` + `/dev/uinput` permissions) for the *move* part of pointer actions.

Clicking still requires a separate backend (`ydotool`), because Hyprland does not
expose a click dispatcher.

## Socket2 events and close-window metadata

Hyprland’s `socket2` IPC is a great foundation for **window watchers**.
However, some events are intentionally minimal:

- `openwindow` carries `address, workspace, class, title`
- `closewindow` (and `kill`) carries **only** the `address`

This means an “on close” automation can’t reliably know the window’s class/title
by the time the close event arrives.

VHK keeps a small best-effort **address → metadata** cache built from earlier
events (open/title/move/focus). When a `closewindow` event arrives and
`hyprctl clients` no longer lists the window, VHK falls back to this cache so
window watchers can still see `{class, title, workspace}` in `vars.window`.

This cache is intentionally conservative (time-based expiry) and should be
treated as **best effort** evidence, not a security boundary.

## Custom events (user-defined triggers)

Hyprland can emit a custom socket2 event via the `event` dispatcher.
This shows up on socket2 as:

```
custom>>yourdata
```

VHK exposes this as a window watcher event kind:

```yaml
window_watchers:
  - name: on_custom
    event: custom
    macro: my_macro
```

This is a handy escape hatch for wiring compositor config → VHK without writing
additional IPC glue scripts.

## Key syntax

Your project’s `bindings[].keys` is still written in the i3-like form:

- `Mod4+Shift+P`
- `Control+Alt+K`

VHK converts common modifiers to Hyprland’s `MODS` field (`SUPER`, `SHIFT`, `CTRL`, `ALT`).
If you use unusual keysyms, Hyprland recommends using tools like `wev` to discover the exact keysym name.

## Trigger VHK via Hyprland `event` dispatcher (custom>>...)

Hyprland can emit a `custom>>...` line on socket2 using the `event` dispatcher.
This is a convenient way to make Hyprland config trigger automations.

VHK includes a small bridge that forwards these socket2 custom events into the
VHK bus:

```bash
vhk bridge-hypr-custom /path/to/project --bus-event hotkey
```

Then configure a `bus_watcher` (recommended: `dispatch: true`) and send JSON
payloads from Hyprland binds, e.g. a custom payload of:

```json
{"macro":"screenshot","vars":{"mode":"region"}}
```

The bridge will parse JSON and emit it as the bus data directly, so dispatch
watchers can use it without wrapping.

Notes:
- Socket2 event format is `EVENT>>DATA` (one line per event).
- `hyprctl` info calls are synchronous and should not be spammed; prefer socket2
  for event-driven automation.
