# Launcher script export

VHK can now export a launcher-friendly wrapper script for a project palette:

```bash
vhk export-launcher-script /path/to/project /tmp/vhk-my-project-palette
chmod +x /tmp/vhk-my-project-palette
```

The generated script is meant for Linux launcher ecosystems that already work in
stdin/stdout picker flows.

## What it does

- loads the project's palette model via `vhk palette --json`
- chooses an entry with a launcher-style picker
- executes the selected stable `entry_id` via `vhk palette --entry-id ...`
- can also list rows or print raw JSON for other wrappers
- auto-detects rofi script mode and emits `display` / `info` / `meta` / `icon` row metadata when launched by rofi

Supported launcher backends in the generated script:

- `rofi`
- `dmenu`
- `wofi`
- `fuzzel`
- `tofi`
- console fallback

## Environment overrides

The generated script supports lightweight runtime overrides:

- `VHK_LAUNCHER_BACKEND=rofi|dmenu|wofi|fuzzel|tofi|console`
- `VHK_LAUNCHER_CMD="custom picker command ..."`

`VHK_LAUNCHER_CMD` is useful when you want to force a wrapper such as a themed
launcher invocation without regenerating the script.

## Script usage

```bash
# interactive pick-and-run
./vhk-my-project-palette

# print palette rows as entry_id<TAB>label
./vhk-my-project-palette --list

# print the raw palette JSON
./vhk-my-project-palette --json

# print the embedded support posture
./vhk-my-project-palette --about
./vhk-my-project-palette --support-json

# pick interactively but only print the chosen entry id
./vhk-my-project-palette --print-entry-id

# run one stable entry directly
./vhk-my-project-palette deploy@prod#release
```

## Why this exists

`.desktop` export is useful for menus and taskbars, but Linux launchers also
have a strong script-first culture. Exporting a project launcher script keeps
VHK compatible with `rofi -dmenu`, `wofi --dmenu`, `fuzzel --dmenu`, `tofi`,
and similar picker-driven workflows without forcing users into a future GUI.

## Rofi script mode

The exported script now works in two launcher styles:

- generic picker wrapper mode (default)
- rofi script mode when `ROFI_RETV` is present

That means you can either run the script directly **or** expose it as a rofi
custom mode. Rofi script mode needs an explicit `name:script` mode spec, so the
correct shape is:

```bash
rofi -show vhk-my-project -modes "vhk-my-project:/absolute/path/to/vhk-my-project-palette" -show-icons
```

VHK now has a helper for this flow:

```bash
vhk export-rofi-mode /path/to/project --install
```

That command writes the launcher script and prints the exact `rofi -show ...
-modes ...` invocation to bind into i3/sway/hyprland keybindings or shell
aliases.

When rofi drives the script, VHK emits row metadata using stable `entry_id`
values plus `meta` search terms and optional row icons derived from macro or
preset `icon:` fields.

## Support posture

Generated launcher scripts now embed the project's current publish/support snapshot.
That means the helper itself can explain which desktop/session lanes are
reference, supported, caveated, or experimental.

The exported script understands:

- `--about` for a human-readable support summary
- `--support-json` for machine-readable support posture data

This keeps launcher helpers aligned with `vhk gen-publish-pack`, target-claim
audits, and bundle metadata instead of leaving support claims trapped in docs.
