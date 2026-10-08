# uinput permissions (Wayland-friendly input injection)

A lot of Wayland-friendly automation tooling (ydotool, kanata, kmonad, etc.) uses the Linux **uinput** device to _emit_ synthetic keyboard/mouse events.

If `/dev/uinput` is missing, or it exists but is not writable by your user, those tools will fail unless you run them as root.

VHK does **not** require uinput by itself, but it can export hotkeys to tools that do (Kanata / KMonad / keyd), and it can integrate with ydotool.

## Generate starter rules

VHK can generate small udev snippets:

```bash
vhk gen-udev-uinput > 80-uinput-vhk.rules
```

Or write a small set of files into a directory:

```bash
vhk gen-udev-uinput --out-dir ./vhk_udev
# writes:
#   80-uinput-vhk.rules   (permissions rule)
#   uinput.conf           (modules-load snippet)
```

Then install them (as root) into the appropriate places:

- `/etc/udev/rules.d/80-uinput-vhk.rules`
- `/etc/modules-load.d/uinput.conf`

Reload:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

> Some distros load `uinput` lazily; explicitly loading the module at boot avoids a circular failure where permissions are never applied.

## Two common permission patterns

### 1) Group-owned `/dev/uinput` (explicit)

Most projects recommend a udev rule like:

```
KERNEL=="uinput", GROUP="uinput", MODE="0660", OPTIONS+="static_node=uinput"
```

…and then add your user to the `uinput` group.

This is explicit and easy to reason about, but recent `systemd-udevd` versions may ignore rules that reference a *non-system* group. If your `uinput` group has a gid >= 1000, recreate it as a system group.

### 2) `TAG+="uaccess"` ACLs (seat-based)

Some packages (notably Steam’s input rules) grant seat access using uaccess ACLs:

```
KERNEL=="uinput", SUBSYSTEM=="misc", TAG+="uaccess", OPTIONS+="static_node=uinput"
```

You can generate that variant with:

```bash
vhk gen-udev-uinput --uaccess
```

This can be convenient, but it also broadens who can write to `/dev/uinput` (any process running as the active seat user).

## Evdev read access (kmonad / kanata)

Tools that **remap** keys generally need read access to a real input device (`/dev/input/event*`) _in addition_ to uinput.

Joining the global `input` group works, but it gives wide access to *all* input events.

A narrower approach is a device-scoped udev rule that tags a specific keyboard with `uaccess`. VHK can generate a starter:

```bash
vhk gen-udev-uinput --out-dir ./vhk_udev \
  --evdev-name "AT Translated Set 2 keyboard"
```

You can also match by USB vendor/product ids:

```bash
vhk gen-udev-uinput --out-dir ./vhk_udev \
  --evdev-idvendor 046d --evdev-idproduct c31c
```

> Note: granting read access to keyboard events has security implications (keylogging). Keep these rules as narrow as possible.

## Related commands

- `vhk doctor --json` includes a `/dev/uinput` probe and will suggest `vhk gen-udev-uinput` when it detects permission issues.
- `vhk gen-kanata-config`, `vhk gen-kmonad-config`, `vhk gen-keyd-config` generate bindings for popular hotkey/remapping daemons.

## Daemon helpers

On Wayland, uinput-based injectors often use a background daemon for lower latency:

- `vhk gen-ydotoold-service` generates a systemd user service for `ydotoold`
  (so `ydotool` calls work without manually starting the daemon).
- `vhk gen-dotoold-service` generates a systemd user service for `dotoold`
  (so `dotoolc` can be used for snappy hotkey execution).
