# WM Modes and Submaps (Leader-key keymaps)

VHK can generate either **direct keybinds** (one bindsym/bind per macro) or a
**leader-key style keymap** using your window manager's built-in mechanism:

- **i3 / sway:** `mode "..." { ... }`
- **Hyprland:** `submap = ...`

This is a common pattern in the wild:

- i3's default config ships a **resize mode** entered via `Mod4+R`.
- Hyprland users frequently use **submaps** to keep global bindings short.

## Why use a mode/submap?

- Reduce global keybind conflicts
- Avoid grabbing complicated modifier chords
- Make a portable "macro layer" that feels similar across WMs

## Generate a mode/submap

Use `gen-wm-config` with `--mode-enter`:

```bash
vhk gen-wm-config /path/to/project --wm auto \
  --mode-enter 'Mod4+R' \
  --mode-name vhk
```

### One-shot (default)

By default, VHK generates a **one-shot** mode/submap:

- i3/sway: each macro bind ends with `; mode "default"`
- Hyprland: submap declaration is emitted as `submap = <name>, reset`

This "launch mode" style is handy for macro launchers: enter the mode, hit a
single key, and immediately return to normal.

To keep the mode active until you manually exit:

```bash
vhk gen-wm-config /path/to/project --wm i3 \
  --mode-enter 'Mod4+R' --mode-sticky
```

### Stripping a modifier prefix

When generating a keymap, you usually **don't want** to keep the main modifier
inside the mode (e.g. `Mod4+P` becomes `P`).

The generator strips a modifier prefix from each binding inside the mode:

```bash
vhk gen-wm-config /path/to/project --wm sway \
  --mode-enter 'Mod4+R' \
  --mode-strip-mods 'Mod4'
```

You can strip multiple modifiers:

```bash
vhk gen-wm-config /path/to/project --wm hyprland \
  --mode-enter 'Mod4+R' \
  --mode-strip-mods 'Mod4,Control'
```

### Exit keys

By default, VHK generates exit keys `Escape` and `Return`.

```bash
vhk gen-wm-config /path/to/project --wm i3 \
  --mode-enter 'Mod4+R' \
  --mode-exit-keys 'Escape,Return'
```

## Notes and caveats

- i3/sway `mode` blocks allow only binding-related subcommands (`bindsym`, etc.).
- Hyprland binds are comma-separated; avoid trailing commas.
- For Hyprland, `when:` selectors are implemented using VHK's `--require-window`
  gating (since Hyprland binds don't support i3-style criteria).

For palette-derived launcher layers (instead of project `bindings:`), see `docs/WM_LAUNCHER_MODES.md` and `vhk export-wm-launcher-mode`.
