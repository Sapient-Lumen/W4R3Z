# Xremap

`vhk gen-xremap-config <project_dir>` generates an xremap YAML config that launches VHK macros from xremap key bindings. This is the Linux-native lane for app-aware remaps where **xremap owns trigger/input interception** and **VHK owns macro orchestration**.

## Basic usage

```bash
vhk gen-xremap-config /path/to/project --out ~/.config/xremap/vhk.yml
```

The generated config uses xremap `keymap:` entries with `launch:` actions. Each binding calls back into VHK, for example:

```yaml
keymap:
  - name: Launch macro
    exact_match: true
    remap:
      SUPER-Shift-p:
        launch: [vhk, run, /path/to/project, launch, --quiet]
```

## Scoped bindings

When a VHK binding has `when:`, the generator maps the subset xremap can express into `application:` and `window:` filters, then still passes `--require-window` to VHK so the original selector remains the final authority. Exact `title:` values become anchored xremap window regexes, while `title_regex: true` and `app_id_regex: true` are now preserved as xremap-native `/regex/` filters when possible. This keeps the export honest when compositor-specific app naming gets tricky.

## Useful options

- `--exact-match / --superset-match` controls whether extra modifiers are allowed.
- `--keypress-delay-ms` sets xremap `keypress_delay_ms` for apps that miss very fast synthetic keys.
- `--throttle-ms` sets xremap `throttle_ms` for slower Wayland apps.

## Notes

- xremap runs commands on key press for keymap combos; the generator does not pretend combo on-release behavior exists in the same form as Kanata/KMonad.
- Validate application/app_id names on the target desktop before claiming broad support. xremap’s own README points to different discovery methods for GNOME, KDE, Sway, Niri, COSMIC, and fallback logging paths.
- The generator is intentionally narrow: it targets launch-style bindings and app/window scoping, not every advanced xremap feature.

## Linting before export

`vhk lint-project` now warns when a binding's selector uses fields xremap cannot pre-filter itself (for example `workspace`, `pid`, or state flags like `focused`). Those fields still stay correct at runtime because VHK receives `--require-window`, but the lint warning makes the remapper-vs-runtime split explicit before you ship the config.
