# Capability coverage matrix (`vhk plan-project`)

`vhk plan-project` now emits `capability_coverage`.

This surface sits between `toolchain_choices` and the higher-level target
comparisons.

- `toolchain_choices` answers: which concrete helper/toolchain should we prefer?
- `environment_diffs` answers: which desktop target fits the whole project best?
- `capability_coverage` answers: how does each capability travel across Linux
  targets, and where should VHK keep a boundary or fallback?

## What it contains

Each capability row includes:

- capability name and category
- `coverage_score`
- `coverage_class`
- `project_pressure`
- usage count + macros that currently rely on it
- current live-session status when `--session-check` is enabled
- strongest environments / limited environments / blocking environments
- recommended toolchain + fallbacks
- offload paths
- validation commands
- per-environment scenario statuses

## Coverage classes

The output intentionally uses a few blunt classes instead of pretending Linux
capability planning is perfectly precise.

- `portable`
  - survives the conservative portable-text lane
- `conditional`
  - viable, but still shaped by desktop choice or packaging decisions
- `desktop-boundary`
  - should be exported through WM/compositor/portal trigger surfaces instead of
    treated as generic core behavior
- `helper-boundary`
  - should sit behind a helper or consent/session seam
- `x11-first`
  - still behaves mostly like an X11-era capability
- `experimental`
  - should stay optional and heavily validated

## Why this matters

A Linux-native AHK-style system cannot just say:

- “Wayland supported”
- “X11 supported”
- “portal-aware”

That is too coarse.

Teams need to know which parts of a project are:

- broadly portable
- desktop-shaped
- helper-boundary work
- better off moved into exports/remappers/launchers/forms

That is the job of this surface.

## Example use

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
vhk doctor --json
vhk validate ./myproj --json
```

A good loop is:

1. inspect `capability_coverage`
2. compare it against `toolchain_choices`
3. verify with `doctor`
4. export the thin surfaces that should absorb the portability risk
