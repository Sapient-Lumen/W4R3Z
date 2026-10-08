# Global shortcuts portal

Wayland compositors typically prevent arbitrary applications from listening to
all keypresses (anti-keylogging design). The **XDG Desktop Portal Global
Shortcuts** API provides a *permissioned* way for applications to request global
keyboard shortcuts.

VHK implements an **experimental** integration by calling the portal via `gdbus`
(and listening for signals via `dbus-monitor`).

## What this unlocks

- Wayland-friendly **global hotkeys** without building a compositor-specific
  keygrab daemon.
- A single trigger surface that works across multiple DEs (where supported),
  similar to how the screenshot/screencast portals work.

## Reality check

- `BindShortcuts` is usually **interactive** (portal dialog).
- A `parent_window` identifier may be required.
- Backend support varies by DE and version.
- Many wlroots setups use `xdg-desktop-portal-wlr`, which (as of late 2025) implements Screenshot/ScreenCast only, so GlobalShortcuts may be missing unless another backend provides it.
- Some GNOME setups report `BindShortcuts` as not implemented, so treat this as optional/experimental and keep other trigger paths available.

See the upstream portal interface docs for the precise method and signal
signatures.

## Using it with the VHK bus

The recommended wiring is:

1) Use **one** bus watcher with `dispatch: true`:

```yaml
bus_watchers:
  - name: hotkeys
    event: hotkey
    dispatch: true
```

2) Run the bus daemon:

```bash
vhk busd /path/to/project
```

3) Run the portal hotkey bridge:

```bash
vhk portal-hotkeys /path/to/project --bus-event hotkey
```

When a shortcut fires, `portal-hotkeys` emits a bus event with these keys:

- `macro`: macro name (from project bindings)
- `vars`: binding vars
- `binding`: human name
- `keys`: original chord string
- `require_window`: selector dict (when present)

This matches the default dispatch keys in `bus_watchers`.

## Converting keys to preferred_trigger

The portal accepts a `preferred_trigger` string defined by the
freedesktop "Shortcuts" specification.

VHK converts i3-style chords like `Mod4+Shift+p` into `LOGO+SHIFT+p`. It now
also translates several common punctuation keys into shortcuts-spec/xkbcommon
identifiers, for example `Ctrl+[` -> `CTRL+bracketleft`, `Ctrl+]` ->
`CTRL+bracketright`, and `Ctrl+;` -> `CTRL+semicolon`.

Not every key name maps cleanly today; if a trigger fails to parse, VHK skips
that binding from the generated portal catalog and `vhk lint-project` reports a
`PORTAL_TRIGGER_EXPORT_GAP` warning before export.

Because GlobalShortcuts is global by design, any binding `when:` selector also
remains runtime-only inside VHK after the portal activation signal arrives;
`vhk lint-project` now reports that boundary as `PORTAL_SCOPE_RUNTIME_ONLY`.
