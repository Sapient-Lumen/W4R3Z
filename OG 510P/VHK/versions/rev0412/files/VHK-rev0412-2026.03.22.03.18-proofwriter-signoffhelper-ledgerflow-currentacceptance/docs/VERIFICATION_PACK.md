# Verification pack (`vhk gen-verification-pack`)

`vhk gen-verification-pack` turns the planning model into release-facing
verification artifacts for an existing project.

Generated files:

- `docs/VHK_VERIFICATION_PLAN.json`
- `docs/VHK_VERIFICATION_GUIDE.md`
- `docs/VHK_RELEASE_CHECKLIST.md`
- `scripts/vhk_verify_release.sh`

This sits one step beyond `vhk gen-operator-pack`.

- operator-pack artifacts are for **install / rollout / rollback handoff**
- verification-pack artifacts are for **release rehearsal / shipping review**

## Why this exists

`vhk plan-project` already knew how to describe:

- deployable surfaces
- setup recipes
- verification gates
- implementation waves
- toolchain choices

But those insights still had to be manually translated into a release packet.
That is a mismatch with the way Linux-native automation actually ships: helper
boundaries, services, remapper installs, launcher surfaces, and visual assets
need to be **rehearsed** before a release claim is believable.

`vhk gen-verification-pack` closes that gap by generating a guide, a release
checklist, a machine-readable verification plan, and a shell-oriented rehearsal
script from the same planner output.

## Session-aware vs session-agnostic

By default, `vhk gen-verification-pack` performs the same current-session
capability check used by `vhk plan-project`, so the generated pack can include
real session fit and mismatch notes.

Use `--no-session-check` when you want a capability-agnostic pack for code
review, CI, or hypothetical target planning.

## Suggested workflow

```bash
vhk doctor --json
vhk validate . --json
vhk plan-project . --json
vhk gen-verification-pack . --force
sh scripts/vhk_verify_release.sh
```

Review order:

1. `VHK_VERIFICATION_GUIDE.md`
2. `VHK_RELEASE_CHECKLIST.md`
3. `VHK_VERIFICATION_PLAN.json`
4. `scripts/vhk_verify_release.sh`

## Relationship to other planning surfaces

- `deployable_surfaces` says which Linux-facing surfaces must agree
- `setup_recipes` says which install/rollback seams must be rehearsed
- `verification_gates` says what must be true before shipping
- `implementation_waves` says which subsystems those gates depend on
- `gen-verification-pack` turns those layers into reviewable release artifacts

## Current scope

The verification pack currently emits docs, a machine-readable plan, and a
shell-style release rehearsal script.
It does **not** yet generate distro-specific CI configs, screenshots, or fully
self-healing release automation.

That is intentional. The goal is to make Linux-native release seams explicit
without pretending that one universal script can prove X11, GNOME Wayland, KDE
Wayland, wlroots, Hyprland, remapper daemons, and helper-backed input paths in
exactly the same way.
