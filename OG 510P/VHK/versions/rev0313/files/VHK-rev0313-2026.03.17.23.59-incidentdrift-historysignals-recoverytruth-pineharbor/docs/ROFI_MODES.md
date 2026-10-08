# Rofi mode export

VHK can now export a project palette as a first-class rofi custom mode:

```bash
vhk export-rofi-mode /path/to/project --install
```

The command writes a launcher script and prints the exact rofi command needed to
run it, for example:

```bash
rofi -show vhk-my-project -modes "drun,run,vhk-my-project:/home/me/.local/bin/vhk-my-project-palette" -show-icons
```

## Why this exists

Rofi script mode is richer than plain dmenu-style integration:

- stable row ids via `info`
- invisible search metadata via `meta`
- row icons
- active/urgent row hints

That makes it a good fit for VHK palette rows, prompt-profile actions, and
future multi-step launcher workflows.

## Typical usage

```bash
# install script to ~/.local/bin or XDG_BIN_HOME
vhk export-rofi-mode /path/to/project --install

# custom mode name
vhk export-rofi-mode /path/to/project --install --mode-name "Project Macros"

# machine-readable manifest
vhk export-rofi-mode /path/to/project --install --json
```

## Notes

- `export-rofi-mode` is the correct rofi-specific export when you want a direct
  `rofi -show ...` workflow.
- `export-launcher-script` is still useful when you want one generic script that
  can drive rofi, fuzzel, wofi, tofi, or plain console selection.
- `export-desktop-entry` is still the better fit for app menus, docks, and task
  launchers that consume `.desktop` files.
