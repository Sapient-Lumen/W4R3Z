# WM Integration Bundles

`export-wm-bundle` is the high-level installer/exporter that sits above:

- `export-launcher-script`
- `export-rofi-mode`
- `export-wm-bindings`
- `export-wm-launcher-mode`
- `export-wm-include`

Instead of asking the user to remember which helper to export first and where to
place the resulting snippet, VHK can now emit a **complete WM bundle**.

## What it writes

For launcher surfaces that need a helper (`rofi-mode` and `launcher-script`),
the bundle writes:

- a launcher helper script
- a WM snippet (`binding` or `launcher-mode`)
- a `BOOTSTRAP.txt` note with the exact parent-config line to add once
- a `vhk-wm-bundle.json` manifest
- bundle-local support docs + JSON posture snapshot

For `palette-command`, the bundle skips the helper and writes only the snippet +
bootstrap/manfiest files.

## CLI

```bash
vhk export-wm-bundle ./my-project ./bundle --wm i3 --launcher rofi-mode
vhk export-wm-bundle ./my-project ./bundle --wm sway --kind launcher-mode \
  --mode-enter '$mod+Shift+o' --launcher launcher-script
vhk export-wm-bundle ./my-project --wm hyprland --kind binding --launcher rofi-mode --install
```

## Bundle layout

By default, a bundle directory contains paths like:

```text
./bundle/
  bin/vhk-my-project-palette
  config/sway/vhk/vhk-my-project-launcher-mode.conf
  BOOTSTRAP.txt
  vhk-wm-bundle.json
  docs/VHK_PUBLIC_SUPPORT.md
  docs/VHK_INSTALL_QUICKSTART.md
  docs/VHK_BUNDLE_SUPPORT.json
```

## Install mode

When `--install` is used, VHK writes directly into conventional XDG locations:

- helper: `XDG_BIN_HOME` or `~/.local/bin`
- i3 snippets: `XDG_CONFIG_HOME/i3/vhk/`
- sway snippets: `XDG_CONFIG_HOME/sway/vhk/`
- Hyprland snippets: `XDG_CONFIG_HOME/hypr/vhk/`

The command still prints:

- where the files were written
- the exact `include` / `source =` line to add once
- a suggested reload command

## Why this exists

The lower-level exporters are still useful when you want one specific artifact.
The bundle command exists for the much more common workflow: "give me the helper
and the config fragment that go together."

See also:

- `docs/WM_BINDINGS.md`
- `docs/WM_LAUNCHER_MODES.md`
- `docs/WM_INCLUDES.md`
- `docs/ROFI_MODES.md`
- `docs/LAUNCHER_SCRIPTS.md`

## Support posture in bundle dirs

Self-contained WM bundles now consume the same publish/support data as the
main project bundle. That means recipients can inspect the generated bundle dir
and immediately see:

- the public support note
- the install quickstart
- a machine-readable support snapshot

The `vhk-wm-bundle.json` manifest now records those paths plus the support
headline, so future tooling can verify that outward-facing WM integrations are
not overclaiming support.
