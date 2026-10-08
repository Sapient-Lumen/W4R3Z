# Concrete toolchain choices (`vhk plan-project`)

`vhk plan-project` now emits `toolchain_choices`.

This surface is intentionally more concrete than the higher-level strategy
layers like `desktop_targets`, `surface_choices`, or `reference_patterns`.
Those layers answer questions such as:

- what product shape is this project becoming?
- which Linux integration surfaces should we lean into?
- which existing tools or patterns should VHK learn from?

`toolchain_choices` answers the next operational question:

> which concrete Linux toolchains should this project prefer for each
> capability right now?

## What it contains

Each item includes:

- capability (`text_injection`, `pointer_injection`, `screen_capture`,
  `global_hotkeys`, `window_introspection`, `input_capture`)
- category (`input`, `capture`, `trigger`, `context`)
- a scored recommendation
- the recommended toolchain
- fallback toolchains
- package hints / install-facing names
- rationale, risks, commands, and source patterns

## Why this matters

A Linux-native automation stack cannot stop at “support Wayland” or “prefer a
helper boundary”. Teams still need to decide things like:

- `xdotool` vs `wtype` vs `ydotool`/`dotool`
- portal capture vs compositor-native screenshot tools
- portal shortcuts vs compositor-native binds vs launcher fallbacks
- `wmctrl`/`xprop` vs `hyprctl`/`swaymsg`/`kdotool`

Those are not interchangeable implementation details. They affect latency,
permissions, portability, and how much of the product should stay in VHK core
versus exported helpers, remappers, or launchers.

## Design intent

The output is heuristic, not a promise that one binary is installed or that one
session definitely supports a path. It combines:

- project shape
- current desktop backend hint
- live session capability data when available
- known conservative defaults for X11 vs Wayland-family sessions

That makes it useful in both modes:

- planning without a live session (`--no-session-check`)
- refining a real deployment plan against `vhk doctor` / `vhk validate`

## Example uses

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
vhk doctor --json
vhk validate ./myproj --json
```

A good loop is:

1. `plan-project` to choose likely toolchains
2. `doctor` to see what the live session actually exposes
3. `validate` to catch mismatches between the project and the session
4. export or package the matching surfaces (`gen-espanso`, WM bundles,
   remapper configs, helper/service artifacts)
