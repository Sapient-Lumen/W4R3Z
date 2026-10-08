# sxhkd export

`sxhkd` is a lightweight X11 hotkey daemon (commonly used with bspwm/dwm and also usable alongside i3).

VHK does **not** try to replace sxhkd. Instead, VHK can **export** your project-level `bindings:` into an `sxhkdrc` so you can:

- keep hotkeys next to macros (in `project.yaml`)
- keep using sxhkd’s mature grabbing/reload behavior
- reload bindings instantly while iterating

> Wayland note: sxhkd is X11-only. On Wayland, prefer compositor binds or `vhk gen-kanata-config` / `vhk gen-keyd-config` / `vhk gen-kmonad-config`.

## Generate

```bash
vhk gen-sxhkd-config /path/to/project > ~/.config/sxhkd/sxhkdrc
```

Reload sxhkd:

```bash
pkill -USR1 -x sxhkd
```

(See `man sxhkd` for details.)

## Leader / chord mode

If you want to avoid collisions or keep all VHK macros behind a leader key, export as a **chord chain**:

```bash
vhk gen-sxhkd-config /path/to/project --leader "Mod4+Space" > ~/.config/sxhkd/sxhkdrc
```

This emits bindings like:

```
super + space ; super + shift + p
    vhk run /path/to/project sig --quiet
```

- `;` means the chain aborts after the tail chord (default behavior).
- `:` keeps the chain active until aborted (use `--sticky-leader`).

## Context filters (`when`)

`sxhkd` itself doesn’t do per-window criteria.

When a binding has a `when:` selector, the exporter adds `--require-window` so **VHK** enforces the condition at runtime.

### Faster triggers via bus dispatch

If you run a long-lived bus watcher (`vhk watch-bus ...`) you can export sxhkd bindings that
emit bus events instead of spawning a full `vhk run` for each key press:

```bash
vhk gen-sxhkd-config /path/to/project --via-bus > ~/.config/sxhkd/sxhkdrc
```

This expects a bus watcher with `dispatch: true` (see `docs/BUS_EVENTS.md`).

Bindings with `when:` will embed a `require_window` selector into the bus payload.

## on-release / passthrough

`sxhkd` supports:

- `@KEYSYM` to trigger on **key release** (`--on-release`)
- `~KEYSYM` to **replay** the captured key event to other clients (`--passthrough`)

These are useful when you want “release to run” behavior or when you want a hotkey that still types normally.

## Lint support

`vhk lint-project` now emits `SXHKD_SCOPE_RUNTIME_ONLY` when a binding uses
`when:` because `sxhkd` itself has no per-window criteria support, and
`SXHKD_X11_ONLY` when a project marked for Wayland is still planning to use the
`sxhkd` export lane.
