# Bus daemon (busd)

The VHK bus socket is a **UNIX datagram socket**, which means it is effectively **single-consumer**:
only one process can bind the socket path at a time.

If you run multiple `vhk watch-bus ...` processes for the same project, they will compete for the
socket and you may lose events.

`vhk busd` solves this by:

- binding the bus socket **once**
- evaluating **multiple bus_watchers** in *project order*
- optionally stopping propagation when a watcher sets `consume: true`

## Run all enabled bus watchers

```bash
vhk busd /path/to/project
```

## Run selected watchers

```bash
vhk busd /path/to/project --watcher hotkeys --watcher on_build
```

## consume: first-match rule style

```yaml
bus_watchers:
  - name: hotkeys
    event: hotkey
    dispatch: true
    consume: true

  - name: debug_log
    event: "*"
    macro: log_everything
```

With `consume: true`, an event handled by `hotkeys` will not be evaluated by later watchers.

## systemd user service

Generate a unit file:

```bash
vhk gen-vhk-busd-service /path/to/project --watcher hotkeys
```

Then follow the printed `systemctl --user ...` steps.

Tip: pair this with `--via-bus` exports (i3/sway/Hyprland/sxhkd) so keybinds only emit
fast bus events and the long-lived daemon does the heavier work.

## systemd socket activation

For a more Linux-native setup (and fewer startup races), you can use **systemd socket activation**:

```bash
vhk gen-vhk-busd-socket-units /path/to/project --watcher hotkeys
```

Then enable the `*.socket` unit as printed.

See: docs/SOCKET_ACTIVATION.md.

## Live reload

`busd` supports *live reload* so you can iterate on `project.yaml` / macros without
restarting the daemon.

### Reload via bus event

By default, `busd` treats the `settings.bus_reload_event` bus event (default:
`vhk.reload`) as an **internal control message**. When received, it reloads the
project from disk and continues.

Emit the event using:

```bash
vhk bus-reload /path/to/project
```

This is intentionally similar in spirit to `sxhkd`'s reload-on-signal workflow
(SIGUSR1) but works without a PID file because it uses the same bus socket.

### Reload via signals

Optionally, `vhk busd --reload-signals` installs SIGUSR1/SIGHUP handlers to
request reload (only works in the main thread).

## Stop / shutdown

`busd` also supports a portable “please exit” control event.

- Event name: `settings.bus_stop_event` (default `vhk.stop`)

Emit it with:

```bash
vhk bus-stop /path/to/project
```

This is useful for systemd units or scripts that want a clean shutdown without
tracking PIDs.

## Related: external control surfaces

For webhooks / dashboards / Stream Deck controllers that can only do HTTP, see:

- `docs/HTTP_CONTROL.md` (`vhk httpd`)
