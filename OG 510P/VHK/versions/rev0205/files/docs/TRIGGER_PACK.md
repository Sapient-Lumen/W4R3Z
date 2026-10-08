# Trigger pack

`vhk gen-trigger-pack <project_dir>` generates a self-contained trigger-layer
export root, defaulting to `<project>/build/trigger_pack/`.

The goal is to stop treating Linux-native hotkey/remapper integration as a
series of unrelated one-off commands. Instead, the pack groups together the
exportable trigger surfaces that the planner already recommends:

- WM/compositor dispatch snippets for i3, sway, and Hyprland
- `sxhkd` hotkey-daemon config for X11-style deployments
- `keyd`, Kanata, and KMonad configs for remapper/helper layers
- planner-backed docs explaining where those configs fit
- a machine-readable JSON manifest
- a refresh script that regenerates the whole pack

Generated tree:

- `configs/wm/vhk.i3.conf`
- `configs/wm/vhk.sway.conf`
- `configs/wm/vhk.hyprland.conf`
- `configs/x11/vhk.sxhkdrc`
- `configs/remappers/vhk.keyd.conf`
- `configs/remappers/vhk.kanata.kbd`
- `configs/remappers/vhk.kmonad.kbd`
- `docs/VHK_TRIGGER_SURFACES.md`
- `docs/VHK_TRIGGER_MATRIX.md`
- `docs/VHK_TRIGGER_PACK.json`
- `scripts/vhk_refresh_trigger_pack.sh`

The docs in the pack are intentionally explicit about surfaces that do *not* map
cleanly to a static file artifact, such as portal/session-managed shortcut paths.
That keeps Linux support honest: some trigger layers are snippets, some are
services, and some are capability-mediated runtime integrations.
