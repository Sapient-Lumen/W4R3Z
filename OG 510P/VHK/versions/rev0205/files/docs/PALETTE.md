# Macro palette

VHK now has a launcher-friendly project palette:

```bash
vhk palette /path/to/project
```

This uses the same chooser stack as `ChooseFromList`, but applies it at the
**project** level:

- X11: `rofi`, then `dmenu`
- Wayland: `fuzzel`, then `tofi`, then `wofi`
- fallback: dialog helpers, then console

The palette is intentionally simple and script-friendly:

- default order is **recent-first** using recent `run_*.jsonl` history
- `--alpha` switches back to alphabetical order
- `--json` prints the palette model for other tools/UIs
- `--no-run` prints the chosen entry id without running it (`macro`, `macro@preset`, or `macro@preset#profile`)
- `--presets/--no-presets` controls whether saved parameter presets appear as separate launcher actions
- `--preset-prompts/--no-preset-prompts` controls whether preset-attached prompt forms run before execution
- `--include-hidden` includes macros marked `hidden: true` (and hidden presets)
- `--profile-actions/--no-profile-actions` controls whether saved prompt profiles appear as separate launcher actions for prompted presets

## Macro metadata

Macros can now carry lightweight metadata that improves palette and future
Studio surfaces:

```yaml
name: deploy_release
group: Release
description: Ship the current build
tags: [deploy, ci]
hidden: false
presets:
  - name: staging
    description: Deploy to staging
    vars:
      env: staging
      approve: false
  - name: prod
    description: Deploy to production
    vars:
      env: prod
      approve: true
    prompt_form:
      title: Deploy ${env}
      text: Collect release details
      fields:
        - name: version
          label: Version
        - name: ticket
          label: Ticket
steps:
  - type: PromptForm
    title: Deploy release
    out_var: form
    fields:
      - name: version
        label: Version
```

Supported top-level metadata:

- `description`: human summary for launcher UIs and future Studio lists
- `group`: group/prefix shown as `Group › macro_name`
- `icon`: optional icon name/path for palette rows, desktop quick actions, and launcher script integrations
- `tags`: lightweight search/organization hints
- `hidden`: omit from `vhk palette` by default (still runnable directly)
- `presets`: named saved parameter sets that become palette entries like `deploy_release@prod`
  - presets may also define `prompt_form`, which lets an action preload stable vars and then ask for a few run-time values before execution

## Why this exists

Linux users already expect searchable launchers to be the fastest way to pick
an action. VHK now treats that as a first-class runtime surface instead of a
future GUI-only feature.

## Preset merge semantics

When you select a preset entry, its `vars:` mapping becomes the initial variable
set for that run. Explicit CLI `--vars` values still win when the same key is
provided by both the preset and the command line.

## Prompted preset overlays

Presets can now define an optional `prompt_form:` block. When enabled, VHK applies
preset `vars:` first, merges CLI `--vars` next, then opens the prompt form and
merges the user's answers last. That keeps presets reusable while still allowing
small just-in-time parameters like version numbers, ticket ids, or release notes.

In palette JSON, palette entries now expose launcher-facing metadata such as `icon` and `search_terms`, and prompted preset entries also expose:

- `needs_prompt`: whether selecting the entry will open a prompt overlay
- `prompt_fields`: field names surfaced by that overlay
- `available_prompt_profiles`: named saved profiles available for that prompt key
- `prompt_profile_key`: the stable store key used to look up those profiles

When `--profile-actions` is enabled, palette rows may also carry `prompt_profile` and use entry ids like `deploy@prod#release`.

## Prompt profiles from the palette

Palette runs now participate in the same prompt-profile system as `vhk run`:

```bash
vhk palette /path/to/project --prompt-profile release
vhk palette /path/to/project --save-prompt-profile hotfix
```

That lets a launcher-driven action such as `deploy@prod` preload stable preset
vars, reuse the last or named prompt answers for fields like version/ticket, and
still let the user confirm or adjust them before execution. When a prompted preset
already has saved profiles, VHK can now surface actions like `deploy@prod#release`
directly in the palette so launchers can expose named workflows without extra CLI flags.


## Desktop launcher export

The palette model is also exportable into a `.desktop` launcher:

```bash
vhk export-desktop-entry /path/to/project --install
```

That launcher opens the project palette by default and can optionally expose
quick actions for visible macros, presets, and saved prompt-profile workflows.
This keeps the palette/runtime model aligned with Linux menus, taskbars, and
`drun` launchers instead of hiding it behind a future GUI-only concept.

## Launcher script export

VHK can also export a picker-native wrapper script:

```bash
vhk export-launcher-script /path/to/project --install
```

That script reuses the palette model, resolves stable `entry_id` values with
`vhk palette --entry-id`, and supports runtime overrides such as
`VHK_LAUNCHER_BACKEND` and `VHK_LAUNCHER_CMD`. It also auto-detects rofi
script mode (`ROFI_RETV` / `ROFI_INFO`) and emits icon/meta/info row metadata,
so the same project palette can serve generic dmenu-style pickers **and** richer
rofi script-mode integrations.
