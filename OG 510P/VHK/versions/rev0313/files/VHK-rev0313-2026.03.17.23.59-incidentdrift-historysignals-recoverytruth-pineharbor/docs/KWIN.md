# KDE KWin notes

VHK targets i3/X11 first, but on KDE Plasma you may want a window-manager-native
trigger surface.

## Reality check

KWin scripting is JavaScript-based and exposes a large API surface for window
management.

Historically, KWin scripts have not offered a “just run an arbitrary shell
command” primitive, and community guidance commonly suggests:

1) emit a **DBus signal** from the KWin script
2) have a small user service listen for that signal
3) forward it into your automation tool

This preserves a clean boundary:

- KWin script: WM-side logic + event detection
- VHK: macro engine + vision + automation

## VHK: DBus → bus bridge

VHK ships an experimental helper to forward DBus signals into the VHK bus:

```bash
vhk bridge-dbus-signal /path/to/project \
  --match "interface='org.vhk.Trigger',member='Fire'" \
  --bus-event hotkey
```

Pair it with a single dispatch bus watcher:

```yaml
bus_watchers:
  - name: hotkeys
    event: hotkey
    dispatch: true
```

And have your KWin script emit a signal whose first argument is JSON, e.g.
`{"macro":"sig","vars":{...}}`.

The bridge will auto-decode JSON for the first string arg.

## References

- KDE discussion: emit a DBus signal from a KWin script and react externally.
- KWin DBusCall / callDBus documentation.
