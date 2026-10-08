# keyd integration

`keyd` is a system-wide key remapping daemon that works across X11/Wayland/TTY.
VHK does **not** try to implement low-level key interception itself; instead it
can export your `bindings:` to a `keyd` config that **runs VHK macros**.

Why this exists:

- Wayland compositors intentionally restrict global key interception.
- Many users already run `keyd` for ergonomic remaps and want “run a command”
  bindings without rewriting their macro tooling.

## Generate a config

```bash
vhk gen-keyd-config /path/to/project > /tmp/vhk.conf
```

The output includes a required `[ids]` section. The default is `*` (match all
keyboards). For safety, you will usually want to scope this to a single device:

```bash
# find your keyboard id(s)
keyd monitor

# generate a file that matches exactly one id
vhk gen-keyd-config /path/to/project --id 046d:c31c > /etc/keyd/vhk.conf
sudo keyd reload
```

## Modifier handling

VHK's i3-style hotkeys (e.g. `Mod4+Shift+P`) map naturally onto keyd layers:

- `Mod4` → `meta`
- `Control` → `control`
- `Alt`/`Mod1` → `alt`
- `Shift` → `shift`

Multi-modifier combos become **composite layers** (e.g. `[meta+shift]`), which
keyd activates when both modifier layers are active.

## Important: keyd runs as root

keyd's `command(...)` action executes as the user running the keyd service
(usually **root**). This can be surprising:

- Wayland desktop portals and some notification daemons are user-session scoped.
- Your `$PATH` may differ from your interactive shell.

If your macros depend on user-session tools, consider using a wrapper and pass
it via `--command-prefix`:

```bash
vhk gen-keyd-config /path/to/project \
  --command-prefix 'sudo -u alice XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus' \
  > /etc/keyd/vhk.conf
```

This is deliberately flexible because the “right” prefix depends on distro,
systemd setup, and whether you need portal access.

## Window scoping

If a binding uses `when:`, VHK exports it as a normal keyd mapping that runs:

- `vhk run ... --require-window '{...}'`

So the key press always reaches VHK, and VHK decides whether the focused window
matches before performing side effects.

## Tips

- Use `keyd list-keys` to see valid key names.
- Use `keyd check /etc/keyd/vhk.conf` to validate the generated config.
