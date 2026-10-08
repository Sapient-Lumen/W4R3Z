# WM Launcher Modes / Submaps

VHK can export a **launcher layer** for common tiling Wayland/X11 session WMs:

- i3 / sway: a `mode "..." { ... }` block
- Hyprland: a `submap = ...` block

This is different from `vhk gen-wm-config --mode-enter ...`.

- `gen-wm-config` turns existing project `bindings:` into a leader-key style mode.
- `export-wm-launcher-mode` turns the **project palette** into a leader-key style
  launcher surface.

That means one transient mode can expose:

- a dedicated launcher action (`vhk palette`, rofi custom mode, or launcher script)
- direct entry-id actions for the most relevant palette rows
- presets and saved prompt-profile actions, if enabled
- optional profile-management rows, if you deliberately include them

## CLI

```bash
vhk export-wm-launcher-mode ./my-project --wm i3 --mode-enter '$mod+Shift+o'
vhk export-wm-launcher-mode ./my-project --wm sway --mode-enter '$mod+Shift+o' \
  --launcher rofi-mode --rofi-mode-name 'Project Macros'
vhk export-wm-launcher-mode ./my-project --wm hyprland --mode-enter 'Mod4+Shift+o' \
  --launcher palette-command --uwsm-app
```

## Default shape

By default, VHK emits:

- launcher action on `p`
- direct palette-entry actions on `1,2,3,4,5,6,7,8,9,0`
- exit keys `Escape,Return`
- one-shot behavior

In practice this gives you a quick launcher layer:

- enter the mode/submap once
- hit a number for a top macro/preset/profile entry
- or hit `p` for the full launcher surface
- automatically return to normal bindings

## Example: sway

```bash
vhk export-wm-launcher-mode ./my-project --wm sway --mode-enter '$mod+Shift+o'
```

Typical output:

```conf
# VHK sway launcher mode for my-project
# Enter mode 'vhk-launch' with: $mod+Shift+o
bindsym $mod+Shift+o mode "vhk-launch"
mode "vhk-launch" {
    bindsym Escape mode "default"
    bindsym Return mode "default"
    bindsym --release p exec vhk palette /path/to/project; mode "default"  # Open VHK palette
    bindsym --release 1 exec vhk palette /path/to/project --entry-id deploy; mode "default"  # Release › deploy — Ship the current build
}
```

## Example: Hyprland

```bash
vhk export-wm-launcher-mode ./my-project --wm hyprland --mode-enter 'Mod4+Shift+o'
```

Typical output:

```conf
# VHK hyprland launcher submap for my-project
# Enter submap 'vhk-launch' with: Mod4+Shift+o
bind = SUPER SHIFT, O, submap, vhk-launch

submap = vhk-launch, reset
bind = , Escape, submap, reset
bind = , Return, submap, reset
bindrd = , P, Open VHK palette, exec, vhk palette /path/to/project
bindrd = , 1, Release › deploy — Ship the current build, exec, vhk palette /path/to/project --entry-id deploy
submap = reset
```

## Notes

- i3 / sway launcher commands are automatically quoted when they contain `,` or `;`
  so rofi `-modes ...,...` commands remain valid WM config.
- `--launcher palette-command` is the most portable fallback.
- `--launcher rofi-mode` is the richest fit when you already want a rofi custom mode.
- `--launcher launcher-script` is useful when you want one generated helper to work
  across multiple picker backends.
- `--profile-actions` is useful when prompted presets should appear as explicit
  saved-profile actions in the mode/submap.
- `--profile-management-actions` is intentionally opt-in because edit/copy/rename/delete
  rows are usually better suited to a full palette than a tiny transient layer.

See also `docs/WM_INCLUDES.md` if you want VHK to install launcher-mode snippets into a conventional WM include/source directory.
