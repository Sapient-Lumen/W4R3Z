# systemd socket activation for busd

VHK's project bus is a **UNIX datagram socket** (AF_UNIX / SOCK_DGRAM).

Running `vhk busd` as a plain user service is fine, but socket activation is a
nice Linux-native upgrade:

- systemd owns the socket path and can create it early
- the daemon can start *on demand* when the first event arrives
- avoids bind races during login/session startup

## How it works

When systemd starts a socket-activated service, it passes already-open file
 descriptors to the service using environment variables:

- `LISTEN_FDS`
- `LISTEN_PID`

Optionally, systemd may also pass descriptor names via:

- `LISTEN_FDNAMES` (colon-separated)

VHK detects socket activation and reads bus events from:

- **fd 3** (the first passed descriptor) by default
- a **named** descriptor when you set `settings.bus_fdname` (or `VHK_BUS_FDNAME`)

### Naming the descriptor (recommended)

If you set `FileDescriptorName=` in your `.socket` unit, systemd will populate
`LISTEN_FDNAMES`. This is useful when a service receives multiple descriptors.

VHK supports picking the right one by name:

- `project.yaml`: `settings.bus_fdname: vhk-bus`
- or environment override: `VHK_BUS_FDNAME=vhk-bus`

## Generate units

Generate a socket+service pair:

```bash
vhk gen-vhk-busd-socket-units /path/to/project --watcher hotkeys --fdname vhk-bus
```

Enable the socket:

```bash
systemctl --user daemon-reload
systemctl --user enable --now vhk-busd-<project>.socket
```

From now on:

- `vhk-emit` / WM keybind exports can send events to the bus socket
- systemd will start `vhk busd` automatically on first traffic

## Test without installing units

For quick iteration you can use `systemd-socket-activate`:

```bash
systemd-socket-activate \
  --listen-datagram="$XDG_RUNTIME_DIR/vhk/test_bus.sock" \
  --fdname=vhk-bus \
  vhk busd /path/to/project --watcher hotkeys
```

Then in another terminal:

```bash
vhk-emit --socket "$XDG_RUNTIME_DIR/vhk/test_bus.sock" hotkey --data '{"macro":"sig"}'
```

## Notes

- With socket activation, `--force` is usually unnecessary.
- Keep the bus socket under `%t` (`XDG_RUNTIME_DIR`) when possible.
- A single UNIX datagram path is single-consumer; use `busd` rather than running
  multiple `watch-bus` processes.
