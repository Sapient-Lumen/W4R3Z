# DBus signal waits

`WaitForDbusSignal` makes D-Bus signals a first-class one-shot runtime
primitive inside VHK macros.

Use it when the upstream producer already exposes a good event boundary over
D-Bus and adding a second bridge layer would just create more glue. Typical
examples include:

- MPRIS player state / metadata changes
- desktop or compositor scripts that emit a small signal to announce work
- service state changes surfaced over the session or system bus

## Shape

```yaml
- type: WaitForDbusSignal
  bus: session
  sender: org.mpris.MediaPlayer2.vlc
  interface: org.freedesktop.DBus.Properties
  member: PropertiesChanged
  path: /org/mpris/MediaPlayer2
  pattern: 'PlaybackStatus'
  timeout_ms: 10000
```

Outputs:

- `dbus_signal` (dict payload)
- `dbus_bus`
- `dbus_args`
- `dbus_sender`
- `dbus_path`
- `dbus_interface`
- `dbus_member`
- `dbus_text`
- `dbus_raw`

## When to use this vs `WaitForBusEvent`

Use `WaitForDbusSignal` when the signal already exists on D-Bus and the macro
only needs the next matching event.

Use `WaitForBusEvent` when you want to normalize many different producers into
one local project bus, or when a helper script / daemon is already translating a
backend-specific source into VHK bus events.

## Notes on helpers

VHK prefers `dbus-monitor` because it supports real match rules and exposes more
typed output.

When only `gdbus monitor` is available, VHK can still wait on signals, but the
fallback is intentionally narrower: it needs a sender/bus-name scope (`sender:`
or a raw `match:` rule containing `sender=...`) because `gdbus monitor` works
by monitoring one owner's objects rather than the whole bus with arbitrary
server-side match rules.

## Common patterns

### MPRIS player state

```yaml
- type: WaitForDbusSignal
  bus: session
  sender: org.mpris.MediaPlayer2.vlc
  interface: org.freedesktop.DBus.Properties
  member: PropertiesChanged
  path: /org/mpris/MediaPlayer2
  condition: "dbus_args[0] == 'org.mpris.MediaPlayer2.Player'"
  timeout_ms: 15000
```

### KWin / desktop script signal

```yaml
- type: WaitForDbusSignal
  bus: session
  interface: org.vhk.Trigger
  member: Fire
  pattern: '"macro": "capture"'
  timeout_ms: 5000
```

### system bus signal lane

```yaml
- type: WaitForDbusSignal
  bus: system
  sender: org.freedesktop.systemd1
  interface: org.freedesktop.DBus.Properties
  member: PropertiesChanged
  timeout_ms: 10000
```

For systemd-specific workflows, keep in mind that the manager's D-Bus API uses
`Subscribe()` to gate most signals. VHK does not auto-manage that yet, so a
specialized helper lane remains a good future extension.
