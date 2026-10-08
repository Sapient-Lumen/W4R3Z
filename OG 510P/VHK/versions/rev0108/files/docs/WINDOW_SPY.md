# Window Spy (active-window inspector)

Many automation ecosystems ship a "Window Spy" helper (AutoHotkey's is the
classic example) that lets you quickly discover stable identifiers like window
class, executable, and title.

VHK's `pick-window` command provides this workflow on **X11** (click a window,
read `WM_CLASS`, title, etc.). On **Wayland**, click-to-inspect isn't reliably
available, so VHK also ships a focus-based inspector.

## `vhk window-spy`

```bash
vhk window-spy --json
```

Returns a JSON object with:

- `wm`: detected compositor (`i3`, `sway`, `hyprland`, `kwin`)
- `active`: best-effort active-window info
- `suggested.stable`: a conservative `I3WindowSelector` mapping (usually class/app_id)
- `suggested.exact`: stable + exact title

The selector suggestions are intended to be copy/pasted into:

- `bindings[].when` / `hotstrings[].when`
- `vhk run --require-window '{...}'`

### Examples

Run a macro only when Firefox is focused:

```bash
vhk run ./my_project do_thing --require-window '{"class":"Firefox"}'
```

Generate Hyprland binds with the same gate (automatic when `when:` is present):

```bash
vhk gen-hyprland-config ./my_project
```

## Notes

- Window titles change frequently; prefer matching on `class` / `app_id` unless
  you need a single, stable window.
- i3/sway criteria treat class/instance/title as **regular expressions**; VHK
  selectors default to *exact strings* unless you set the `*_regex` flags.

### KDE (KWin)

On KDE Plasma, `vhk window-spy` uses `kdotool` when available to query the
focused window. This improves `--require-window` gates on KDE Wayland, even
though the rest of the window-management ecosystem is compositor-specific.
