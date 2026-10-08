# VHK datacube — revision 0325 reshaping pass

## Product truth

VHK is now explicitly organized around **i3/X11-first desktop automation**.
The repo should optimize for one excellent lane instead of carrying equal-weight
product promises for many desktop stacks.

## Datacube layers

### 1. Core product lane

This is the active center of the repo:

- X11/i3 input, window, and workspace control
- recorder fidelity and segment truth
- cleanup/optimization passes that turn noisy recordings into readable macros
- replay/runtime discipline
- event guards, waits, and warm service ownership
- support/report/evidence surfaces that help explain runs
- scriptability for humans and a private LLM

### 2. Supporting infrastructure

These surfaces still matter because they make the core lane usable:

- bundles and publish/install packs
- readiness, host, and operator packs
- palette, prompt, and launcher surfaces
- watcher/event infrastructure
- i3 WM exports and session ownership

### 3. Secondary but retained

These are not the center, but still plausibly helpful:

- voice export lanes
- limited generic Linux deployment machinery
- helper/remapper research when it improves ownership or latency on an X11-first host

### 4. Vaulted / experimental

These are no longer part of the active default story:

- broad Wayland parity work
- portal-first shortcut and activation lanes
- Hyprland/KWin-specific product shaping
- app-native adapter packs (kitty/mpv/qutebrowser/wezterm/playerctl)

Their docs have been moved under `vault/docs/`, with small stubs left in `docs/`
so older references still resolve.

## Decision implications

### Support claims

- **Tier 1:** i3 on X11
- **Experimental / historical:** Wayland, portal-first activation, compositor-specific side lanes

### Runtime ownership

- default: **session-bound long-lived user service**
- still supported: **ad hoc CLI launch**
- avoided as a primary story: cold-launching everything and hoping input backends hide the latency

### Performance philosophy

Performance is owned by the whole runtime shape:

- thin emit/dispatch paths
- warm resident execution
- cleanup/optimization reducing replay noise
- choosing text backends honestly
- using waits and events instead of giant sleeps

### LLM posture

A first-class goal is letting a private LLM:

- generate macros
- revise macros after recorder output
- call VHK via CLI or warm runtime surfaces
- rely on readable project artifacts instead of brittle opaque blobs
