# Deployable surfaces (`vhk plan-project`)

`vhk plan-project` now emits `deployable_surfaces`.

This sits one level above `artifact_blueprint`.

- `artifact_blueprint` says **which files/configs/services** should exist.
- `deployable_surfaces` says **which Linux-facing surfaces** users will actually
  install, wire up, and depend on.

That distinction matters because Linux automation usually ships as a mix of
runtime macros **and** native entrypoints:

- text packages
- desktop/menu launchers
- WM/compositor bindings
- remapper/helper seams
- user services
- selector/debug asset packs
- capability audits and fallback notes

## What it contains

Each surface entry includes:

- `id`, `title`, and `category`
- `entrypoint`
- `summary`
- `fit`
- `priority`
- linked `artifacts`
- `install_targets`
- `generator_commands`
- `validation_commands`
- `acceptance_checks`
- `related_capabilities`
- linked `related_surface_choices`
- `first_wave`
- `notes`

## Why this matters

A Linux-native automation project is not done when it can merely run a macro.
It feels done when the operator can answer:

- How does the user invoke this?
- What gets installed where?
- Which surfaces are optional versus required?
- Which surfaces are safe on conservative Wayland targets?
- Which verification commands prove the surface is really shippable?

`deployable_surfaces` turns the planner into that operational map.

## Example workflow

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
```

Then:

1. inspect `implementation_waves`
2. inspect `artifact_blueprint`
3. inspect `deployable_surfaces`
4. generate the high-priority surfaces first
5. run the linked validation commands before widening support claims

## Design intent

The goal is not more JSON for its own sake.
The goal is to keep the repo, exports, install docs, future setup flows, and a
future Studio all speaking the same deployment language.
