# Operator pack (`vhk gen-operator-pack`)

`vhk gen-operator-pack` turns the planning model into operator-facing artifacts for
an existing project.

Generated files:

- `docs/VHK_OPERATOR_PLAN.json`
- `docs/VHK_OPERATOR_GUIDE.md`
- `docs/VHK_DEPLOYMENT_CHECKLIST.md`

This sits one step beyond `vhk init` starter artifacts.

- starter artifacts are for **authors beginning a project**
- operator-pack artifacts are for **authors/operators preparing install, review,
  rollout, and rollback**

## Why this exists

`vhk plan-project` already knew how to describe:

- deployable surfaces
- setup recipes
- verification gates
- implementation waves
- reference patterns

But those insights still had to be manually copied into docs or issue trackers.
That is a mismatch with the way Linux-native automation stacks are actually
shipped: operators need clear install steps, service/remapper boundaries,
verification commands, and rollback notes.

`vhk gen-operator-pack` closes that gap by generating a deployment handoff pack
from the same planner output.

## Session-aware vs session-agnostic

By default, `vhk gen-operator-pack` performs the same current-session capability
check used by `vhk plan-project`, so the generated pack can include real session
fit and mismatch notes.

Use `--no-session-check` when you want a capability-agnostic pack for code
review, CI, or hypothetical target planning.

## Suggested workflow

```bash
vhk doctor --json
vhk validate . --json
vhk plan-project . --json
vhk gen-operator-pack . --force
```

Review order:

1. `VHK_OPERATOR_GUIDE.md`
2. `VHK_DEPLOYMENT_CHECKLIST.md`
3. `VHK_OPERATOR_PLAN.json`

## Relationship to other planning surfaces

- `deployable_surfaces` says what operators will end up depending on
- `setup_recipes` says how those surfaces get installed/reviewed
- `verification_gates` says what must be true before shipping
- `implementation_waves` says what to build first
- `gen-operator-pack` turns those layers into files that can travel with the
  project

## Current scope

The operator pack currently emits docs + a machine-readable plan.
It does **not** yet generate distro-specific installers, package manifests, or
turn-key service enablement scripts.

That is intentional. The goal is to make Linux-native deployment seams explicit
without pretending that one generic install script can honestly fit X11, GNOME
Wayland, KDE Wayland, wlroots, Hyprland, remapper daemons, and helper-backed
input paths all at once.
