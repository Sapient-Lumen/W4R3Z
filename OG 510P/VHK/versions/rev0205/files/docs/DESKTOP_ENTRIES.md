# Desktop entry export

VHK can now export a Linux `.desktop` launcher for a project:

```bash
vhk export-desktop-entry /path/to/project
vhk export-desktop-entry /path/to/project /tmp/vhk-myproj.desktop
vhk export-desktop-entry /path/to/project --install
```

## What it exports

The main launcher entry opens the project's VHK palette:

- `Exec=vhk palette /path/to/project`
- `Path=/path/to/project`
- `TryExec=vhk`

When actions are enabled, VHK also emits desktop **quick actions** for the
most relevant visible launcher targets:

- macro runs
- preset runs (`macro@preset`)
- saved prompt-profile runs (`macro@preset#profile`)

That means the same palette/runtime concepts VHK already exposes through
launcher pickers can also surface in Linux menus, taskbars, and `drun`-style
launchers. When macros or presets declare `icon:` metadata, VHK now reuses that
for exported desktop quick-action icons too.

## Why this exists

Linux launchers already treat desktop entries as a standard integration point,
while tools like rofi and wofi also expose application-launcher modes that read
those entries. VHK should therefore treat launcher integration as part of the
runtime surface, not as a future Studio-only concern.

## Options

Useful options:

- `--install` writes to `$XDG_DATA_HOME/applications` (defaulting to
  `~/.local/share/applications`)
- `--actions/--no-actions` controls whether desktop quick actions are exported
- `--presets/--no-presets` controls preset actions
- `--profile-actions/--no-profile-actions` controls saved prompt-profile
  actions
- `--alpha` exports action rows alphabetically instead of recent-first
- `--max-actions N` limits submenu/jumplist size
- `--desktop-id` overrides the output basename / launcher id

## Notes

- Desktop actions are **best-effort**. The Desktop Entry Specification says
  launchers should expose them, but some shells or menus may ignore them.
- The spec recommends reverse-DNS desktop ids. VHK does not assume one for your
  project automatically, so `--desktop-id` exists for packagers who want a
  stricter naming convention.
- Exec lines use desktop-entry quoting rules, not shell quoting.

## Support metadata

Exported desktop entries now include custom `X-VHK-Support-*` keys so the
launcher entry carries its own support posture:

- headline + claim source
- reference/supported/caveated/experimental target lanes
- doc paths for `docs/VHK_PUBLIC_SUPPORT.md` and `docs/VHK_INSTALL_QUICKSTART.md`

The default `Comment=` line also incorporates the publish headline when one is
available, so menus and shell launchers surface the project's reference posture
without requiring a separate README lookup.
