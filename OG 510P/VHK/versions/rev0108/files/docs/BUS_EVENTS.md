# Bus events (IPC)

VHK includes a tiny **local event bus** so you can trigger macros from *anything* on Linux:

- window manager config (Hyprland dispatchers, i3 binds, etc.)
- shell scripts
- systemd --user services/timers
- other automation tools

The bus is intentionally simple: a **UNIX datagram socket** that receives newline-free messages.

## Why this exists

Linux automation is fragmented:

- On Wayland, input injection is compositor/portal dependent.
- On X11, grabbing hotkeys is easy but still varies by user stack.

A small IPC bus gives VHK a portable “escape hatch”: if something can run a command or send a
socket datagram, it can trigger VHK.

## Socket location

VHK resolves the bus socket path in this order:

1. `settings.bus_socket` (project.yaml)
2. `VHK_BUS_SOCKET` environment variable
3. `$XDG_RUNTIME_DIR/vhk/bus_<projecthash>.sock` (preferred)
4. `<project>/.vhk/bus.sock`

Print the resolved path:

```bash
vhk bus-path /path/to/project
```

If you run busd under **systemd socket activation**, systemd may pass multiple sockets.
VHK can select a specific activated socket by name using either:

- `settings.bus_fdname` (project.yaml)
- `VHK_BUS_FDNAME` environment variable

See: `docs/SOCKET_ACTIVATION.md`.

## Emitting events

Emit an event with an optional JSON payload:

```bash
vhk emit-bus /path/to/project my_event --data '{"hello": "world"}'
```

### Fast emitter (vhk-emit)

For hotkey daemons / compositor binds, you may prefer the lightweight emitter:

```bash
vhk-emit --socket "$(vhk bus-path /path/to/project)" my_event --data '{"hello": "world"}'
```

`vhk-emit` avoids importing the full `vhk` CLI stack and is intended for low-latency triggers.

The watcher process must be running and bound to the socket.

### Raw formats (for non-VHK senders)

The bus listener accepts:

- JSON object: `{ "name": "event_name", "data": ... }`
- Plain text: `event_name`
- Tab-delimited text: `event_name\tPAYLOAD_TEXT`

## Reserved events

VHK reserves the `vhk.*` namespace for internal control messages.

- `vhk.reload`: when running `vhk busd`, this event triggers a live reload (see `docs/BUS_DAEMON.md`).
- `vhk.stop`: when running `vhk busd`, this event requests shutdown (see `docs/BUS_DAEMON.md`).

If you already use `vhk.*` for your own events, consider renaming them to avoid collisions.

## bus_watchers in project.yaml

```yaml
bus_watchers:
  - name: on_build
    event: build_done
    macro: notify
    pattern: "success"   # optional regex against bus_text
    flags: [IGNORECASE]
    when:
      class: "Firefox"  # optional focused-window gate
    vars:
      source: bus
    consume: false     # optional: stop propagation when this watcher handles an event
```

Runtime variables available to the macro:

- `bus_event`: event name
- `bus_data`: parsed JSON payload (if provided)
- `bus_text`: string form of the payload (used for `pattern`)
- `watcher_name`: watcher name

If `pattern` matched:

- `bus_match`, `bus_groups`, `bus_groupdict`

## Dispatch mode (recommended for hotkeys)

If you want *many* hotkey bindings to trigger different macros, defining one bus watcher
per binding is clumsy.

Instead, set `dispatch: true` and send a JSON payload that includes the macro name:

```yaml
bus_watchers:
  - name: hotkeys
    event: hotkey
    dispatch: true
    # Optional: lock down which macros may be invoked.
    dispatch_allowed_macros: [open_terminal, screenshot, clipboard_cleanup]
```

Emit a hotkey event:

```bash
vhk-emit --socket "$(vhk bus-path /path/to/project)" hotkey \
  --data '{"macro":"screenshot","vars":{"mode":"region"},"binding":"Mod4+Shift+S"}'
```

### Per-binding `require_window`

Hotkey exporters can embed a selector in the payload:

```json
{"macro":"do_thing","require_window":{"class":"Firefox"}}
```

When present, the dispatch watcher will only run the macro if the currently focused
window matches that selector.


## Single-consumer note

The bus socket path can only be bound by **one process** at a time.

- If you only need one watcher (common with `dispatch: true`), `vhk watch-bus` is fine.
- If you want multiple bus watchers active for the same project, use `vhk busd`.

See `docs/BUS_DAEMON.md`.

## Running a bus watcher

```bash
vhk watch-bus /path/to/project on_build
```

This writes a JSONL watcher log under `settings.log_dir`.
