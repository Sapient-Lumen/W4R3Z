# Artifact blueprint (`vhk plan-project`)

`vhk plan-project` now emits `artifact_blueprint`.

This is the missing bridge between the planner's strategy surfaces and the
actual Linux-facing files a project needs in order to feel native.

Earlier layers answer adjacent questions:

- `surface_choices`: which integration surface fits this project?
- `toolchain_choices`: which concrete Linux helper/toolchain fits each capability?
- `verification_gates`: what must be true before a capability is considered shippable?
- `implementation_waves`: what should the team build first?

`artifact_blueprint` turns those answers into a consolidated file/deployment map.

## What it contains

Each artifact entry includes:

- an `id` and `title`
- `category` (text export, trigger export, remap export, service, asset pack, audit, ...)
- `deployment_surface`
- `ownership`
- `path_hint`
- `install_hint`
- `priority`
- `first_wave`
- `generator_commands`
- `validation_commands`
- `related_capabilities`
- `related_surfaces`
- `toolchains`
- source references back to waves/playbooks/gates

## Why this matters

A Linux-native automation project usually stops being "just macros" long before
it becomes robust in practice.

Sooner or later it also needs some combination of:

- an Espanso package
- a desktop entry
- a launcher script
- WM/compositor snippets
- remapper configs
- user services
- selector assets
- portability notes and capability audits

Without an explicit artifact map, those pieces get rediscovered in ad-hoc docs,
terminal history, or setup scripts.

With `artifact_blueprint`, the repo can say:

- which artifacts are part of the shipping story
- which wave should create them first
- which commands generate them
- where they likely belong in a Linux deployment
- which capabilities they are protecting

## Example workflow

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
```

Then:

1. inspect `implementation_waves`
2. inspect `artifact_blueprint`
3. generate the high-priority export/service artifacts first
4. run the linked validation commands before widening desktop support claims

## Long-term direction

`artifact_blueprint` is meant to become the shared contract for future scaffold,
setup-wizard, and release-packaging flows.

The point is not only to describe VHK's architecture, but to make the Linux
installation/deployment story explicit enough that the CLI and future Studio can
converge on the same files and surfaces.
