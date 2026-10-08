# Setup recipes (`vhk plan-project`)

`vhk plan-project` now emits `setup_recipes`.

This sits one level above `deployable_surfaces`.

- `artifact_blueprint` says **which files/configs/services/assets** should exist.
- `deployable_surfaces` says **which Linux-facing surfaces** operators will depend on.
- `setup_recipes` says **which concrete install/review recipe** an author or
  operator should follow to make those surfaces real.

That distinction matters on Linux because the install story is often part of the
architecture:

- text expansion may need a package/service registration loop
- launcher entrypoints may need menu or drun placement
- WM bindings must be staged into compositor-specific config trees
- remapper/helper layers often need separate install and rollback notes
- watcher/bus automation should become user services, not terminal folklore
- selector packs and capability audits need explicit review loops, not just file generation

## Why this exists

The repo already had strong planning surfaces, but a gap remained between
"recommended surface" and "what should a human actually do next?"

Example:

- `deployable_surfaces` can say "use a remap/helper boundary"
- but teams still need an explicit recipe such as:
  1. generate the helper config
  2. review the boundary notes
  3. install into the correct config path
  4. verify layout compatibility
  5. keep rollback instructions ready

`setup_recipes` captures that install/review/handoff layer so future init,
scaffold, export, or Studio setup flows can consume it directly.

## Shape

Each recipe includes:

- `id`
- `title`
- `category`
- `audience`
- `priority`
- `when_to_use`
- `summary`
- `surface_ids`
- `surfaces`
- `artifacts`
- `install_targets`
- `generator_commands`
- `validation_commands`
- `acceptance_checks`
- `install_steps`
- `verify_steps`
- `rollback_steps`
- `related_capabilities`
- `first_wave`
- `playbooks`
- `notes`

## Current recipe families

Today the planner emits recipes such as:

- `text-package-install`
- `launcher-entrypoint-install`
- `wm-trigger-install`
- `remap-helper-install`
- `watcher-service-install`
- `selector-debug-review`
- `capability-audit-review`

These are now partially generators by themselves through `vhk gen-setup-pack`,
which renders project-specific docs plus runnable apply/verify scripts from the
same planner data. They remain a stable contract for future interactive or
more installer-like flows too.

## Usage

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
```

## Intended workflow

1. inspect `toolchain_choices`
2. inspect `artifact_blueprint`
3. inspect `deployable_surfaces`
4. inspect `setup_recipes`
5. generate/install the highest-priority surfaces first
6. verify against the linked acceptance checks and rollback notes

The point is to keep Linux-native deployment honest. A project is not truly
portable just because it can generate artifacts; it also needs a repeatable,
reviewable setup story.
