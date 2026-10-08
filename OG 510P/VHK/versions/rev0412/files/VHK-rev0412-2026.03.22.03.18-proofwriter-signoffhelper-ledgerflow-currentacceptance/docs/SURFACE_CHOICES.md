# Candidate integration surfaces (`vhk plan-project`)

`vhk plan-project` now emits `surface_choices`.

This surface answers a more operational Linux question than the rest of the
planner:

> Which concrete integration surface should we try next, and what do we gain or
> lose by choosing it?

That matters because Linux automation is fragmented in productive ways. Many
projects do **not** want one universal runner process to own all of these jobs
at once:

- text expansion
- always-on hotkey dispatch
- low-latency remapping
- event/watcher packaging
- prompted launcher flows

## What it compares

The current planner scores concrete candidate surfaces and explains trade-offs:

- `espanso-text-package`
- `vhk-palette-launcher`
- `wm-native-dispatch`
- `sxhkd-dispatch`
- `portal-global-shortcuts`
- `keyd-remap`
- `kanata-remap`
- `kmonad-remap`
- `watcher-services`

Each item includes:

- `category`
- `score`
- `fit`
- `summary`
- `strengths`
- `tradeoffs`
- `commands`
- `learn_from`
- `evidence`

## Why this exists

VHK already had strategy surfaces such as product lanes, integration targets,
stack profiles, and desktop targets.

Those are useful, but teams still hit a harder decision during implementation:

- should snippet workflows leave the runner and become a package?
- should always-on triggers live in the WM, a hotkey daemon, or a portal path?
- should low-latency launch keys live in a remapper instead of Python?
- should event-driven projects be packaged as user services immediately?

`surface_choices` is the first attempt to encode those decisions directly.

## How to use it

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
```

A healthy loop now looks like this:

1. use `plan-project` to compare candidate surfaces
2. generate the top few likely exports
3. validate and doctor the target desktop
4. keep whichever surface best matches the real session

## Design stance

The point is not to crown one universal winner.

The point is to make VHK opinionated in a Linux-native way:

- text surfaces should often become text packages
- hotkey ownership should often move to the WM/compositor or a tiny daemon
- remappers should stay remappers
- watcher-heavy projects should look like services
- the runner should stay excellent at sequencing, inspection, and diagnostics
