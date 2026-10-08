# WM Binding Export

VHK can now export ready-to-paste binding snippets for:

- i3
- sway
- Hyprland

The goal is to bridge the new launcher exports into the way Linux users
actually trigger them: WM keybindings, not just standalone commands.

## CLI

```bash
vhk export-wm-bindings ./my-project --wm i3
vhk export-wm-bindings ./my-project --wm sway --launcher palette-command
vhk export-wm-bindings ./my-project --wm hyprland --launcher rofi-mode --uwsm-app
```

## Launcher surfaces

`--launcher rofi-mode`
: Emit a binding that launches the exported VHK rofi custom mode.

`--launcher launcher-script`
: Emit a binding that runs the exported VHK launcher helper directly.

`--launcher palette-command`
: Emit a binding that runs `vhk palette <project>` directly, letting the
  runtime chooser stack decide how to present the palette.

## Notes

- `i3` and `sway` snippets use `bindsym ... exec --no-startup-id ...`.
- `Hyprland` snippets use `bind = ..., exec, ...`.
- `--uwsm-app` is intended for Hyprland sessions launched under UWSM, where
  applications are often started through `uwsm app -- ...`.
- For `rofi-mode`, the snippet assumes you have already exported the helper
  script with `vhk export-rofi-mode` or that you are using the default helper
  path under `~/.local/bin` / `XDG_BIN_HOME`.

## Example

```bash
vhk export-rofi-mode ./my-project ~/.local/bin/vhk-my-project
vhk export-wm-bindings ./my-project --wm sway --launcher rofi-mode
```

Typical sway output:

```conf
# VHK launcher for my-project
bindsym $mod+Shift+p exec --no-startup-id rofi -show vhk-my-project -modes vhk-my-project:/home/me/.local/bin/vhk-my-project -show-icons
```

See also `docs/WM_LAUNCHER_MODES.md` if you want a transient mode/submap instead of a single top-level binding, and `docs/WM_INCLUDES.md` if you want VHK to target an include/source tree directly.
